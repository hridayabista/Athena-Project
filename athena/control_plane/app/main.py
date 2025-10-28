# athena/control_plane/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import asyncio
import time
import logging
from sse_starlette.sse import EventSourceResponse # Import for SSE

from .db import get_db, engine, Base
from . import crud, models
from .models import ModelStatus
from .core_client import CoreClient # <-- IMPORT ADDED

# --- NEW: Imports for Metrics ---
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import threading
import queue
# --- END NEW: Imports for Metrics ---

# Make sure DB metadata exists (for local dev). In prod use alembic migrations.
Base.metadata.create_all(bind=engine)

# ----------------------------------------------------
# Core Client Initialization
# ----------------------------------------------------
# Initialize the client to communicate with the C++ core service.
# Target 'core:50051' is used when running inside a Docker/Kubernetes network.
core_client = CoreClient(target="athena-core:50051") # Changed from 'core:50051' to match docker-compose service name
# ----------------------------------------------------

# --- NEW: Metrics Definitions and State ---
# Metrics definitions
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['endpoint'])
ACTIVE_REQUESTS = Gauge('http_active_requests', 'Active HTTP Requests', ['endpoint'])
CORE_GRPC_REQUESTS = Counter('core_grpc_requests_total', 'Total gRPC Requests to Core', ['method'])
CORE_GRPC_LATENCY = Histogram('core_grpc_duration_seconds', 'gRPC Request Latency to Core', ['method'])

# Simple in-memory state for metrics (in production, use a more robust system)
request_times = queue.deque(maxlen=1000)  # Store last 1000 request times for P95 calc
queue_depth_gauge = Gauge('dispatcher_queue_depth', 'Estimated queue depth in C++ core dispatcher')

# --- NEW: Log Stream State ---
log_queue = queue.Queue(maxsize=1000) # Thread-safe queue for logs
# --- END NEW: Log Stream State ---

app = FastAPI(title="athena-control-plane", version="0.1.0")

class Health(BaseModel):
    status: str

class LoadModelReq(BaseModel):
    model_name: str
    version: str

class ModelOut(BaseModel):
    id: int
    name: str
    version: str
    status: str

# --- NEW: Metrics endpoint ---
@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    # In a real system, you'd collect actual P95, RPS, Queue Depth from your core/observability stack
    # Here, we'll use Prometheus client library for internal metrics and mock others based on our state
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# --- NEW: Mock Metrics Calculation Endpoint (for UI) ---
@app.get("/api/metrics", tags=["Observability"])
async def get_mock_metrics():
    # Calculate P95 latency from stored request times
    p95_latency = 0.0
    rps = 0.0
    queue_depth = 0 # Mock value - in reality, you'd get this from the C++ core via gRPC or shared memory
    if request_times:
        sorted_times = sorted(request_times)
        n = len(sorted_times)
        p95_index = int(0.95 * (n - 1))
        p95_latency = sorted_times[p95_index] * 1000 # Convert to ms

        # Calculate RPS based on the last 10 seconds of stored times
        now = time.time()
        recent_times = [t for t in sorted_times if now - t < 10]
        if recent_times:
             rps = len(recent_times) / 10.0

    # Update the queue depth gauge (mock)
    queue_depth_gauge.set(queue_depth)

    # Mock history for the chart (last 10 points)
    history = []
    for i in range(10):
        history.append({"t": f"T-{9-i}", "latency": p95_latency * (0.8 + 0.4 * (i/10))}) # Simulate slight variation

    return {
        "p95": f"{p95_latency:.2f}ms",
        "p95_delta": "+0.00ms", # Mock delta
        "rps": f"{rps:.2f}",
        "queue_depth": queue_depth,
        "history": history
    }
# --- END NEW: Mock Metrics Endpoint ---

# --- NEW: SSE Log Stream Endpoint ---
@app.get("/stream/logs", tags=["Observability"])
async def stream_logs():
    async def event_generator():
        while True:
            try:
                # Wait for a log message from the queue with a timeout
                log_msg = log_queue.get(timeout=1.0) # Wait 1 second, then loop again
                # Yield the log message as an SSE event
                yield {"event": "log", "data": log_msg}
            except queue.Empty:
                # Yield a ping event to keep the connection alive
                yield {"event": "ping", "data": "keepalive"}

    return EventSourceResponse(event_generator(), media_type="text/plain")
# --- END NEW: SSE Log Stream Endpoint ---

# --- NEW: List Models Endpoint ---
@app.get("/api/models", tags=["Models"], response_model=List[ModelOut])
async def list_models(db: Session = Depends(get_db)):
    db_models = crud.list_models(db)
    return [ModelOut(id=m.id, name=m.name, version=m.version, status=m.status.value) for m in db_models]
# --- END NEW: List Models Endpoint ---

@app.get("/", tags=["Root"])
def read_root():
    # Log the request
    log_queue.put(f"[INFO] Received request on /")
    return {"message": "Welcome to the Athena Control Plane! Use /docs for API details."}

@app.get("/health", response_model=Health, tags=["Health"])
async def health():
    # Log the request
    log_queue.put(f"[HEALTH] Health check requested")
    return {"status": "ok"}

@app.post("/models/load", tags=["Models"], response_model=ModelOut)
async def load_model(req: LoadModelReq, db: Session = Depends(get_db)):
    # Log the request
    log_queue.put(f"[MODEL] Loading model: {req.model_name}:{req.version}")

    # 1. Call core to load model via gRPC
    start_time = time.time()
    resp = core_client.load_model(req.model_name, req.version)
    grpc_latency = (time.time() - start_time) * 1000 # in ms
    CORE_GRPC_LATENCY.labels(method="LoadModel").observe(grpc_latency / 1000) # Prometheus
    CORE_GRPC_REQUESTS.labels(method="LoadModel").inc() # Prometheus

    # Check for success from the C++ core service
    if not resp.get("ok"):
        log_queue.put(f"[ERROR] Core failed to load model {req.model_name}:{req.version} - {resp.get('message')}")
        raise HTTPException(status_code=500, detail=f"core error: {resp.get('message')}")

    # 2. Persist model metadata as LOADED in the control plane DB
    model = crud.create_or_update_model(db, req.model_name, req.version, ModelStatus.LOADED)
    log_queue.put(f"[MODEL] Model {model.name}:{model.version} loaded successfully in DB")
    return ModelOut(id=model.id, name=model.name, version=model.version, status=model.status.value)

@app.post("/models/unload", tags=["Models"])
async def unload_model(req: LoadModelReq, db: Session = Depends(get_db)):
    # Log the request
    log_queue.put(f"[MODEL] Unloading model: {req.model_name}:{req.version}")

    # TODO: Call core_client.unload_model(req.model_name, req.version) here
    start_time = time.time()
    # resp = core_client.unload_model(req.model_name, req.version) # Uncomment when implemented
    grpc_latency = (time.time() - start_time) * 1000 # in ms
    # CORE_GRPC_LATENCY.labels(method="UnloadModel").observe(grpc_latency / 1000) # Prometheus
    # CORE_GRPC_REQUESTS.labels(method="UnloadModel").inc() # Prometheus

    # Persist model metadata as NOT_LOADED in the control plane DB
    model = crud.create_or_update_model(db, req.model_name, req.version, ModelStatus.NOT_LOADED)
    log_queue.put(f"[MODEL] Model {model.name}:{model.version} unloaded successfully in DB")
    return {"unloaded": f"{model.name}:{model.version}"}

@app.get("/models/{model_name}", tags=["Models"])
async def get_model(model_name: str, db: Session = Depends(get_db)):
    # Log the request
    log_queue.put(f"[MODEL] Getting status for model: {model_name}")
    model = crud.get_model_by_name(db, model_name)
    if not model:
        log_queue.put(f"[MODEL] Model {model_name} not found in DB")
        return {"model": model_name, "status": "not_loaded"}
    log_queue.put(f"[MODEL] Found model {model.name}:{model.version} with status {model.status.value}")
    return {"model": model.name, "version": model.version, "status": model.status.value}

# --- NEW: Middleware to capture request times for metrics ---
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(process_time)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    # Store the request time for P95 calculation
    request_times.append(process_time)
    return response
# --- END NEW: Middleware ---
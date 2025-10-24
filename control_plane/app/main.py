# control-plane/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="athena-control-plane", version="0.1.0")

class Health(BaseModel):
    status: str

class LoadModelReq(BaseModel):
    model_name: str
    version: str

@app.get("/", tags=["Root"])
def read_root():
    """Returns a simple greeting to confirm the service is operational."""
    return {"message": "Welcome to the Athena Control Plane! Use /docs for API details."}

@app.get("/health", response_model=Health, tags=["Health"])
async def health():
    return {"status": "ok"}

@app.post("/models/load", tags=["Models"])
async def load_model(req: LoadModelReq):
    # TODO: integrate with dispatcher/load logic
    # For now return a stubbed response
    return {"loaded": f"{req.model_name}:{req.version}"}

@app.get("/models/{model_name}", tags=["Models"])
async def get_model(model_name: str):
    # stub: return placeholder
    return {"model": model_name, "status": "not_loaded"}
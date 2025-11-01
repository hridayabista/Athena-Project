# control_plane/app/core_client.py
import os
import grpc
import time
from typing import List

# generated proto stubs — ensure you generated these with grpc_tools.protoc
try:
    from control_plane import inference_pb2, inference_pb2_grpc
except Exception:
    # fallback import path if module layout differs
    import inference_pb2, inference_pb2_grpc

DEFAULT_HOST = os.getenv("CORE_GRPC_HOST", "localhost")
DEFAULT_PORT = os.getenv("CORE_GRPC_PORT", "50051")
DEFAULT_TARGET = f"{DEFAULT_HOST}:{DEFAULT_PORT}"

class CoreClient:
    def __init__(self, target: str = None, timeout_s: float = 5.0):
        self.target = target or DEFAULT_TARGET
        self.timeout = timeout_s
        self.channel = grpc.insecure_channel(self.target)
        self.stub = inference_pb2_grpc.InferenceServiceStub(self.channel)

    def load_model(self, model_name: str, version: str):
        req = inference_pb2.ModelRef(model_name=model_name, version=version)
        try:
            resp = self.stub.LoadModel(req, timeout=self.timeout)
            return {"ok": resp.ok, "message": resp.message}
        except grpc.RpcError as e:
            return {"ok": False, "message": e.details() if hasattr(e, "details") else str(e)}

    def unload_model(self, model_name: str, version: str):
        req = inference_pb2.ModelRef(model_name=model_name, version=version)
        try:
            resp = self.stub.UnloadModel(req, timeout=self.timeout)
            return {"ok": resp.ok, "message": resp.message}
        except grpc.RpcError as e:
            return {"ok": False, "message": e.details() if hasattr(e, "details") else str(e)}

    def get_model_status(self, model_name: str, version: str):
        req = inference_pb2.ModelRef(model_name=model_name, version=version)
        try:
            resp = self.stub.GetModelStatus(req, timeout=self.timeout)
            return {"model_name": resp.model_name, "version": resp.version, "status": resp.status}
        except grpc.RpcError as e:
            return {"error": e.details() if hasattr(e, "details") else str(e)}

    def run_inference(self, request_id: str, inputs: List[float], model_name: str = "", model_version: str = ""):
        req = inference_pb2.InferenceRequest(
            request_id=request_id,
            inputs=inputs,
            model_name=model_name,
            model_version=model_version
        )
        start = time.time()
        try:
            resp = self.stub.RunInference(req, timeout=self.timeout)
            latency_ms = (time.time() - start) * 1000.0
            return {
                "request_id": resp.request_id,
                "outputs": list(resp.outputs),
                "latency_ms": latency_ms,
                "status": resp.status
            }
        except grpc.RpcError as e:
            return {"error": e.details() if hasattr(e, "details") else str(e)}

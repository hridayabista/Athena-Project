# tools/test_grpc_client.py
from control_plane.app.core_client import CoreClient
import time

def main():
    c = CoreClient()  # reads CORE_GRPC_HOST/PORT from env
    print("Target:", c.target)

    print("-> Load model")
    print(c.load_model("fraud-detector", "v0.1"))

    print("-> Get status")
    print(c.get_model_status("fraud-detector", "v0.1"))

    print("-> Run inference")
    r = c.run_inference("req-123", [1.0, 2.0, 3.0], "fraud-detector", "v0.1")
    print("inference result:", r)

if __name__ == "__main__":
    main()

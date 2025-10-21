# Athena-ultra-low-latency-real-time-inference-microservice
Athena is a ultra-low-latency inference microservice built to return ML model predictions almost instantly (P95 ≤ 50 ms). It runs the hot inference path in C++ for speed, uses dynamic batching to balance throughput vs latency, and deploys on Kubernetes with observability and autoscaling so predictions stay fast and reliable under spikes.

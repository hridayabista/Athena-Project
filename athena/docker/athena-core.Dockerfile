# athena/docker/athena-core.Dockerfile
# ---------------------
# Stage 1: Build
# ---------------------
FROM ubuntu:24.04 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git ca-certificates libstdc++6 pkg-config \
    libprotobuf-dev protobuf-compiler libprotoc-dev \
    libgrpc++-dev protobuf-compiler-grpc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy proto definition (assumed to be in root) and core source
COPY proto/ ./proto/ 
COPY athena/core/ ./core/ 

# Build your server binary (adjust if needed)
RUN mkdir -p core/build && cd core/build && \
    cmake .. && make -j$(nproc)

# ---------------------
# Stage 2: Runtime
# ---------------------
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates libstdc++6 libprotobuf-lite32 libgrpc++1.51 libgrpc29 libprotoc32 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/local/bin

# Copy the built binary and shared library from the builder stage
COPY --from=builder /app/core/build/server /usr/local/bin/server
COPY --from=builder /app/core/build/libathena_core.so /usr/lib/

RUN chmod +x /usr/local/bin/server

EXPOSE 50051

CMD ["/usr/local/bin/server"]
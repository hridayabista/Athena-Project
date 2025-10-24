# docker/athena-core.Dockerfile
FROM ubuntu:22.04 AS build
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git wget unzip pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY core/ ./core/
RUN mkdir -p core/build && cd core/build && cmake .. && cmake --build . -- -j$(nproc)

FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=build /work/core/build/libathena_core.so /usr/lib/
# If you produce an executable in core/build, copy it as well (example below)
# COPY --from=build /work/core/build/athena_core_exe /usr/local/bin/athena_core_exe
EXPOSE 50051
CMD ["/bin/bash", "-c", "echo 'athena core image: add runtime bin or entrypoint' && sleep infinity"]

# athena/docker/control-plane.Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl \
    && rm -rf /var/lib/apt/lists/*

ENV APP_HOME=/app
WORKDIR ${APP_HOME}

RUN useradd --create-home --shell /bin/bash appuser

# Copy proto definition (from root) and control plane source
COPY proto/ ${APP_HOME}/proto/
COPY athena/control_plane/requirements.txt ${APP_HOME}/requirements.txt
COPY athena/control_plane/ ${APP_HOME}/control_plane/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Generate stubs
RUN python -m grpc_tools.protoc -I ${APP_HOME}/proto --python_out=${APP_HOME}/control_plane --grpc_python_out=${APP_HOME}/control_plane ${APP_HOME}/proto/inference.proto || { echo "gRPC generation failed"; exit 1; }

# Fix relative import in generated gRPC file
RUN sed -i 's/import inference_pb2/from . import inference_pb2/g' ${APP_HOME}/control_plane/inference_pb2_grpc.py

# Ensure the /app directory is in the Python path so 'control_plane' can be imported as a package
ENV PYTHONPATH=/app:${PYTHONPATH}

EXPOSE 8000

USER appuser

# Adjust the Uvicorn command to look for the app instance correctly
# The app instance 'app' is defined in athena/control_plane/app/main.py
# So the module path relative to /app (where control_plane/ lives) is control_plane.app.main
CMD ["uvicorn", "control_plane.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
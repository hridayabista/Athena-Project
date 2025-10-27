# docker/control-plane.Dockerfile
FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create user & workdir
ENV APP_HOME=/app
WORKDIR ${APP_HOME}
RUN useradd --create-home --shell /bin/bash appuser

# FIX 1: Copy the *contents* of the 'control-plane/' folder 
# (which includes app/ and requirements.txt) directly into /app.
# This flattens the structure to: /app/app/main.py
# If using 'control-plane/.' causes issues, try 'control-plane/' which should also work for copying contents.
COPY control-plane/ ${APP_HOME}/

# Use a virtualenv inside the image
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python deps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8000

USER appuser
# FIX 2: Uvicorn now points to the flattened path: app.main
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
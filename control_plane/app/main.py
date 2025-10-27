# control_plane/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from .db import get_db, engine, Base
from . import crud, models
from .models import ModelStatus
from sqlalchemy.orm import Session

# Make sure DB metadata exists (for local dev). In prod use alembic migrations.
Base.metadata.create_all(bind=engine)

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

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Athena Control Plane! Use /docs for API details."}

@app.get("/health", response_model=Health, tags=["Health"])
async def health():
    return {"status": "ok"}

@app.post("/models/load", tags=["Models"], response_model=ModelOut)
async def load_model(req: LoadModelReq, db: Session = Depends(get_db)):
    # persist model metadata as LOADED (the actual load to dispatcher is TODO)
    model = crud.create_or_update_model(db, req.model_name, req.version, ModelStatus.LOADED)
    return ModelOut(id=model.id, name=model.name, version=model.version, status=model.status.value)

@app.post("/models/unload", tags=["Models"])
async def unload_model(req: LoadModelReq, db: Session = Depends(get_db)):
    model = crud.create_or_update_model(db, req.model_name, req.version, ModelStatus.NOT_LOADED)
    return {"unloaded": f"{model.name}:{model.version}"}

@app.get("/models/{model_name}", tags=["Models"])
async def get_model(model_name: str, db: Session = Depends(get_db)):
    model = crud.get_model_by_name(db, model_name)
    if not model:
        return {"model": model_name, "status": "not_loaded"}
    return {"model": model.name, "version": model.version, "status": model.status.value}

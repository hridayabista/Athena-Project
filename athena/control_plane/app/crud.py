# control_plane/app/crud.py
from sqlalchemy.orm import Session
from . import models
from .models import ModelStatus

def get_model_by_name(db: Session, name: str):
    return db.query(models.Model).filter(models.Model.name == name).order_by(models.Model.id.desc()).first()

def create_or_update_model(db: Session, name: str, version: str, status: ModelStatus):
    model = db.query(models.Model).filter(models.Model.name == name, models.Model.version == version).first()
    if model:
        model.status = status
    else:
        model = models.Model(name=name, version=version, status=status)
        db.add(model)
    db.commit()
    db.refresh(model)
    return model

def list_models(db: Session, limit: int = 100):
    return db.query(models.Model).order_by(models.Model.created_at.desc()).limit(limit).all()

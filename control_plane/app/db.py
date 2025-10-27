# control_plane/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/athena_dev")

# Use SQLAlchemy sync engine for simplicity (works well for control-plane)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

# each worker should use its own SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

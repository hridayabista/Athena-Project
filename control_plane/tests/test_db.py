# control_plane/tests/test_db.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from control_plane.app.db import Base
from control_plane.app import models, crud

# Use an in-memory SQLite for unit tests
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_and_get_model(db_session):
    m = crud.create_or_update_model(db_session, "fraud-detector", "v0.1", models.ModelStatus.LOADED)
    assert m.id is not None
    assert m.name == "fraud-detector"
    assert m.version == "v0.1"
    assert m.status == models.ModelStatus.LOADED

    fetched = crud.get_model_by_name(db_session, "fraud-detector")
    assert fetched is not None
    assert fetched.name == "fraud-detector"

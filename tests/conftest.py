#conftest.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Base, engine, get_db
from sqlalchemy.orm import Session

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as client:
        yield client

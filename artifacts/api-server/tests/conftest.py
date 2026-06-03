import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from backend.main import app

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")


@pytest.fixture(scope="session", autouse=True)
def db_cleanup():
    yield
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass


@pytest.fixture
def client():
    from backend.database import engine, Base
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c

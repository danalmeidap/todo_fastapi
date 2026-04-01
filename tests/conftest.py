import pytest
from fastapi.testclient import TestClient

from task_fastapi.app import app
from task_fastapi.routers.task import task_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clear_db():
    task_db.clear()

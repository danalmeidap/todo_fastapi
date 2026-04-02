import pytest
from fastapi.testclient import TestClient

from task_fastapi.app import app
from task_fastapi.routers.task import task_db
from task_fastapi.routers.user import user_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def clear_db():
    task_db.clear()
    user_db.clear()


@pytest.fixture
def user(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/users/", json=user_data)
    return response.json()

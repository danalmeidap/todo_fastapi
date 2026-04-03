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
    yield  # noqa: PT022


@pytest.fixture
def user(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/users/", json=user_data)
    return response.json()


@pytest.fixture
def task_no_owner(client):
    response = client.post(
        "/tasks/",
        json={"title": "Initial task",
               "description": "Sem dono",
         "owner_id": None}
    )
    return response.json()


@pytest.fixture
def task_with_owner(client, user):
    user_id = user["id"] if isinstance(user, dict) else user.id
    response = client.post(
        "/tasks/",
        json={
            "title": "Tarefa com Dono",
            "description": "Já nasce com dono",
            "owner_id": user_id
        }
    )
    return response.json()

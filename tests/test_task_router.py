from fastapi import status
from fastapi.testclient import TestClient


def test_create_task(client: TestClient):
    response = client.post('/tasks/',
        json={'title': 'Test Task',
        'description': 'This is a test task.'})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['title'] == 'Test Task'
    assert data['description'] == 'This is a test task.'
    assert data['completed'] is False


def test_read_tasks_list(client: TestClient):
    """Deve listar todas as tarefas (inicialmente vazia)."""
    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"tasks": []}


def test_read_specif_task(client: TestClient):
    create_res = client.post('/tasks/',
        json={'title': 'Test Task',
              'description': 'This is a test task.'})
    task_id = create_res.json()['id']
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['title'] == 'Test Task'
    assert data['description'] == 'This is a test task.'
    assert data['completed'] is False


def task_read_task_not_found(client: TestClient):
    response = client.get("/tasks/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Task not found"}


def test_update_task(client):
    create_res = client.post("/tasks/",
             json={"title": "Old Title",
             "description": "Old",
            "completed": False})
    task_id = create_res.json()["id"]
    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "New Title",
        "description": "Updated",
        "completed": True}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "New Title"
    assert response.json()["completed"] is True


def test_delete_task(client):
    create_res = client.post("/tasks/",
            json={"title": "To delete",
            "description": "...",
            "completed": False})
    task_id = create_res.json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Task not found"


def test_update_task_not_found(client):
    response = client.put(
        "/tasks/999",
        json={"title": "Inexistente",
        "description": "Não existe",
        "completed": False}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Task not found"

from fastapi import status
from fastapi.testclient import TestClient


def test_create_task_without_owner(client):
    response = client.post(
        '/tasks/', json={'title': 'Tarefa órfã', 'description': 'Sem dono'}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['owner_id'] is None


def test_create_task_with_owner(client: TestClient, user):
    response = client.post(
        '/tasks/',
        json={
            'title': 'Task with owner',
            'description': 'This task has an owner.',
            'owner_id': user['id'],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['title'] == 'Task with owner'
    assert data['description'] == 'This task has an owner.'
    assert data['completed'] is False
    assert data['owner_id'] == user['id']


def test_create_task_with_invalid_owner(client):
    response = client.post(
        '/tasks/', json={'title': 'Tarefa fantasma', 'owner_id': 999}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Owner not found'


def test_read_tasks_list(client: TestClient):
    """Deve listar todas as tarefas (inicialmente vazia)."""
    response = client.get('/tasks/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'tasks': []}


def test_read_specif_task(client: TestClient):
    create_res = client.post(
        '/tasks/',
        json={'title': 'Test Task', 'description': 'This is a test task.'},
    )
    task_id = create_res.json()['id']
    response = client.get(f'/tasks/{task_id}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['title'] == 'Test Task'
    assert data['description'] == 'This is a test task.'
    assert data['completed'] is False


def task_read_task_not_found(client: TestClient):
    response = client.get('/tasks/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


def test_update_task_owner_success(client, user, task_no_owner):
    task_id = task_no_owner['id']
    user_id = user['id']
    response = client.put(
        f'/tasks/{task_id}',
        json={
            'title': 'Agora tenho dono',
            'description': 'Desc',
            'completed': False,
            'owner_id': user_id,
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_update_task(client):
    create_res = client.post(
        '/tasks/',
        json={'title': 'Old Title', 'description': 'Old', 'completed': False},
    )
    task_id = create_res.json()['id']
    response = client.put(
        f'/tasks/{task_id}',
        json={
            'title': 'New Title',
            'description': 'Updated',
            'completed': True,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['title'] == 'New Title'
    assert response.json()['completed'] is True


def test_update_task_with_non_existent_owner(client, task_no_owner):
    task_id = task_no_owner['id']
    invalid_owner_id = 9999  # Um ID que certamente não existe
    response = client.put(
        f'/tasks/{task_id}',
        json={
            'title': 'Tentativa Inválida',
            'description': 'Este teste deve retornar 404',
            'completed': False,
            'owner_id': invalid_owner_id,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Owner not found'


def test_update_task_with_none_owner_success(client, task_with_owner):
    task_id = task_with_owner['id']

    response = client.put(
        f'/tasks/{task_id}',
        json={
            'title': 'Removendo dono',
            'description': 'Desc',
            'completed': False,
            'owner_id': None,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['owner_id'] is None


def test_delete_task(client):
    create_res = client.post(
        '/tasks/',
        json={'title': 'To delete', 'description': '...', 'completed': False},
    )
    task_id = create_res.json()['id']
    response = client.delete(f'/tasks/{task_id}')
    assert response.status_code == status.HTTP_200_OK
    get_res = client.get(f'/tasks/{task_id}')
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_task_not_found(client):
    response = client.delete('/tasks/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Task not found'


def test_update_task_not_found(client):
    response = client.put(
        '/tasks/999',
        json={
            'title': 'Inexistente',
            'description': 'Não existe',
            'completed': False,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Task not found'

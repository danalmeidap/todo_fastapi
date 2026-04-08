from unittest.mock import patch

from fastapi import status

from task_fastapi.models.task import Task


def test_create_task(client, user):
    """Testa a criação de uma tarefa com dono."""
    response = client.post(
        '/tasks/',
        json={
            'title': 'Test Task',
            'description': 'Task description',
            'is_completed': False,
            'owner_id': user['id'],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['title'] == 'Test Task'
    assert response.json()['owner_id'] == user['id']


def test_read_tasks_empty(client):
    """Testa a listagem quando não há tarefas."""
    response = client.get('/tasks/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'tasks': []}


def test_read_task_by_id(client, task_no_owner):
    """Testa a busca de uma tarefa específica."""
    task_id = task_no_owner['id']
    response = client.get(f'/tasks/{task_id}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == task_id


def test_read_task_not_found(client):
    """Testa error 404 ao buscar tarefa inexistente."""
    response = client.get('/tasks/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Task not found'


def test_read_tasks_by_user(client, user, task_with_owner):
    user_id = user['id']
    response = client.get(f'/tasks/user/{user_id}')
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()['tasks']
    assert len(tasks) > 0
    assert all(t['owner_id'] == user_id for t in tasks)


def test_update_task(client, task_no_owner):
    task_id = task_no_owner['id']
    response = client.put(
        f'/tasks/{task_id}',
        json={
            'title': 'Updated Title',
            'description': 'Updated Desc',
            'is_completed': True,
            'owner_id': None,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['title'] == 'Updated Title'
    assert response.json()['is_completed'] is True


def test_toggle_task_status(client, task_no_owner):
    task_id = task_no_owner['id']
    response = client.patch(f'/tasks/{task_id}/toggle')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['is_completed'] is True
    response = client.patch(f'/tasks/{task_id}/toggle')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['is_completed'] is False


def test_delete_task(client, task_no_owner):
    task_id = task_no_owner['id']
    response = client.delete(f'/tasks/{task_id}')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    get_res = client.get(f'/tasks/{task_id}')
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_get_completed_tasks_line_coverage(client, session, user):
    user_id = user['id'] if isinstance(user, dict) else user.id

    new_task = Task(
        title='Tarefa Completa',
        description='Teste de cobertura',
        is_completed=True,
        owner_id=user_id,
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    response = client.get('/tasks/completed')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'tasks' in data
    assert len(data['tasks']) >= 1

    assert data['tasks'][0]['is_completed'] is True
    assert data['tasks'][0]['title'] == 'Tarefa Completa'


def test_get_tasks_by_owner_line_coverage(client, session, user):
    user_id = user['id'] if isinstance(user, dict) else user.id

    session.add(
        Task(
            title='Owner Task',
            description='Owner task test',
            is_completed=False,
            owner_id=user_id,
        )
    )
    session.commit()

    response = client.get(f'/tasks/owner/{user_id}')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['tasks']) > 0


def test_get_incompleted_tasks_line_coverage(client, session, user):

    user_id = user['id'] if isinstance(user, dict) else user.id

    new_task = Task(
        title='Tarefa Incompleta',
        description='Teste de cobertura',
        is_completed=False,
        owner_id=user_id,
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    response = client.get('/tasks/pending')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert 'tasks' in data
    assert len(data['tasks']) >= 1

    assert data['tasks'][0]['is_completed'] is False
    assert data['tasks'][0]['title'] == 'Tarefa Incompleta'


def test_toggle_status_not_found_behavior(client):
    invalid_id = 99999
    response = client.patch(f'/tasks/{invalid_id}/toggle')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_toggle_status_success(client, session, user):
    user_id = user['id'] if isinstance(user, dict) else user.id
    new_task = Task(
        title='Tarefa para Toggle',
        description='Testando o caminho feliz',
        is_completed=False,
        owner_id=user_id,
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    task_id = new_task.id
    response = client.patch(f'/tasks/{task_id}/toggle')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['is_completed'] is True
    response_again = client.patch(f'/tasks/{task_id}/toggle')
    assert response_again.status_code == status.HTTP_200_OK
    assert response_again.json()['is_completed'] is False


def test_create_task_owner_not_found(client):
    invalid_owner_id = 99999
    payload = {
        'title': 'Tarefa Órfã',
        'description': 'should not exists',
        'is_completed': False,
        'owner_id': invalid_owner_id,
    }

    response = client.post('/tasks/', json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Owner not found'


def test_read_tasks_by_user_not_found(client):
    invalid_user_id = 9999
    response = client.get(f'/tasks/user/{invalid_user_id}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'User not found'


def test_update_tasks_by_user_not_found(client):
    invalid_user_id = 9999
    payload = {
        'title': 'Tarefa Órfã',
        'description': 'should not exists',
        'is_completed': False,
        'owner_id': invalid_user_id,
    }
    response = client.put(f'/tasks/{invalid_user_id}', json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Task not found'


def test_update_task_owner_not_found(client, session, user, taskDB):
    task_id = taskDB.id
    invalid_owner_id = 99999
    payload = {
        'title': 'Título Atualizado',
        'description': 'Tentando mudar para dono inexistente',
        'is_completed': False,
        'owner_id': invalid_owner_id,
    }
    response = client.put(f'/tasks/{task_id}', json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Owner not found'


def test_delete_task_not_found(client):
    task_id = 999
    response = client.delete(f'/tasks/{task_id}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Task not found'


def test_toggle_status_internal_error_router(client, taskDB):
    with patch(
        'task_fastapi.repositories.task.TaskRepository.update'
    ) as mock_update:
        mock_update.side_effect = Exception('Falha catastrófica no banco')
        response = client.patch(f'/tasks/{taskDB.id}/toggle')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'Error toggling task' in response.json()['detail']

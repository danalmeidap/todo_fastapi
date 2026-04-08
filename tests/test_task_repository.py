from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import not_

from task_fastapi.models.task import Task
from task_fastapi.models.user import User
from task_fastapi.repositories.task import TaskNotFoundError, TaskRepository


def test_get_by_owner_repository(session):
    user1 = User(username='user1', email='u1@test.com', hashed_password='123')
    user2 = User(username='user2', email='u2@test.com', hashed_password='123')
    session.add_all([user1, user2])
    session.commit()
    session.refresh(user1)
    session.refresh(user2)
    t1 = Task(title='T1', description='D1', owner_id=user1.id)
    t2 = Task(title='T2', description='D2', owner_id=user2.id)
    session.add_all([t1, t2])
    session.commit()
    query = session.query(Task).filter(Task.owner_id == user1.id)
    results = query.all()
    assert len(results) == 1
    assert results[0].title == 'T1'
    assert results[0].owner_id == user1.id


def test_get_completed_tasks_repository(session):
    t_done = Task(title='Feita', description='...', is_completed=True)
    t_pending = Task(title='Pendente', description='...', is_completed=False)
    session.add_all([t_done, t_pending])
    session.commit()
    query = session.query(Task).filter(Task.is_completed)
    results = query.all()
    assert len(results) == 1
    assert results[0].title == 'Feita'
    assert results[0].is_completed is True


def test_get_pending_tasks_repository(session):
    t_done = Task(title='Feita', description='...', is_completed=True)
    t_pending = Task(title='Pendente', description='...', is_completed=False)
    session.add_all([t_done, t_pending])
    session.commit()
    query = session.query(Task).filter(not_(Task.is_completed))
    results = query.all()
    assert len(results) == 1
    assert results[0].title == 'Pendente'
    assert results[0].is_completed is False


def test_update_task_not_found_raises_exception():
    mock_db = MagicMock()
    repo = TaskRepository(mock_db)
    with patch.object(TaskRepository, 'get_by_id', return_value=None):
        with pytest.raises(TaskNotFoundError) as exc_info:
            repo.update(task_id=999, update_data={'title': 'Novo Título'})
        assert str(exc_info.value) == 'Task with id 999 not found'


def test_update_task_with_pydantic_schema(session, task_no_owner):
    repo = TaskRepository(session)
    task_id = task_no_owner['id']
    mock_pydantic_data = MagicMock()
    mock_pydantic_data.model_dump.return_value = {
        'title': 'Título via Pydantic',
        'completed': True,
    }
    updated_task = repo.update(task_id, mock_pydantic_data)

    assert updated_task.title == 'Título via Pydantic'
    assert updated_task.is_completed is True
    mock_pydantic_data.model_dump.assert_called_once_with(exclude_unset=True)


def test_update_task_with_plain_dict(session, task_no_owner):
    repo = TaskRepository(session)
    task_id = task_no_owner['id']

    plain_dict = {'title': 'Título via Dict', 'completed': False}

    # Executa o update passando um dicionário simples
    updated_task = repo.update(task_id, plain_dict)

    assert updated_task.title == 'Título via Dict'
    assert updated_task.is_completed is False


def test_update_task_success_logic(session, task_no_owner):
    repo = TaskRepository(session)
    task_id = task_no_owner['id']

    update_data = {'title': 'Sucesso', 'completed': True}

    result = repo.update(task_id, update_data)

    assert result.id == task_id
    assert result.title == 'Sucesso'
    assert result.is_completed is True


def test_toggle_status_task_not_found_raises_exception():
    mock_db = MagicMock()
    repo = TaskRepository(mock_db)
    with patch.object(TaskRepository, 'get_by_id', return_value=None):
        with pytest.raises(TaskNotFoundError) as exc_info:
            repo.toggle_status(task_id=999)
        assert str(exc_info.value) == 'Task with id 999 not found'


def test_delete_task_not_found_raises_exception():
    mock_db = MagicMock()
    repo = TaskRepository(mock_db)
    with patch.object(TaskRepository, 'get_by_id', return_value=None):
        with pytest.raises(TaskNotFoundError) as exc_info:
            repo.delete(task_id=999)
        assert str(exc_info.value) == 'Task with id 999 not found'


def test_toggle_task_status_success(session, task_no_owner):
    repo = TaskRepository(session)
    task_id = task_no_owner['id']
    assert task_no_owner['is_completed'] is False
    updated_task = repo.toggle_status(task_id)
    assert updated_task.is_completed is True
    re_updated_task = repo.toggle_status(task_id)
    assert re_updated_task.is_completed is False

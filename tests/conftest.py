from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from task_fastapi.app import app
from task_fastapi.routers.task import tasks_db
from task_fastapi.routers.user import users_db
from task_fastapi.settings.database import get_db, table_registry
from tests.test_deps import MockRepository


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(session):
    def _get_test_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clear_db():
    tasks_db.clear()
    users_db.clear()
    yield  # noqa: PT022


@pytest.fixture
def user(client):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
    }
    response = client.post('/users/', json=user_data)
    return response.json()


@pytest.fixture
def task_no_owner(client):
    response = client.post(
        '/tasks/',
        json={
            'title': 'Initial task',
            'description': 'Sem dono',
            'completed': False,
            'owner_id': None,
        },
    )
    return response.json()


@pytest.fixture
def task_with_owner(client, user):
    user_id = user['id'] if isinstance(user, dict) else user.id
    response = client.post(
        '/tasks/',
        json={
            'title': 'Tarefa com Dono',
            'description': 'Já nasce com dono',
            'completed': False,
            'owner_id': user_id,
        },
    )
    return response.json()


@pytest.fixture
def userDB(session):
    from task_fastapi.models.user import User  # noqa: PLC0415

    new_user = User(
        username='dbuser',
        email='db@example.com',
        hashed_password='hashed_password',
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@pytest.fixture
def taskDB(session, userDB):
    """Cria uma tarefa diretamente no banco vinculada ao userDB."""
    from task_fastapi.models.task import Task  # noqa: PLC0415

    new_task = Task(
        title='DB Task',
        description='Task criada diretamente no DB',
        is_completed=False,
        owner_id=userDB.id,
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task


@pytest.fixture
def SecondUserDB(session):
    from task_fastapi.models.user import User  # noqa: PLC0415

    new_user2 = User(
        username='dbuser2',
        email='db2@example.com',
        hashed_password='hashed_password2',
    )
    session.add(new_user2)
    session.commit()
    session.refresh(new_user2)
    return new_user2


@pytest.fixture
def mock_repo():
    return MagicMock(spec=MockRepository)

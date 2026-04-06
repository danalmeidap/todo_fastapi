from datetime import datetime

from sqlalchemy import select

from task_fastapi.models.task import Task
from task_fastapi.models.user import User

EXPECTED_TASK_COUNT = 2


def test_create_task(session):
    user = User(username="danilo",
                email="danilo@test.com",
                hashed_password="123")
    session.add(user)
    session.commit()

    new_task = Task(
        title="Minha primeira tarefa",
        description="Descrição detalhada",
        owner_id=user.id
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    assert new_task.id is not None
    assert new_task.title == "Minha primeira tarefa"
    assert new_task.owner_id == user.id
    assert isinstance(new_task.created_at, datetime)


def test_task_relationship_back_to_user(session):
    user = User(username="rel", email="rel@test.com", hashed_password="123")
    session.add(user)
    session.commit()

    task = Task(
        title="Relacionamento",
        description="Testando back_populates",
        owner_id=user.id
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    assert task.owner.id == user.id
    assert task.owner.username == "rel"


def test_user_tasks_list(session):
    user = User(username="list", email="list@test.com", hashed_password="123")
    session.add(user)
    session.commit()
    t1 = Task(title="T1", description="D1", owner_id=user.id)
    t2 = Task(title="T2", description="D2", owner_id=user.id)
    session.add_all([t1, t2])
    session.commit()
    session.refresh(user)
    assert len(user.tasks) == EXPECTED_TASK_COUNT
    assert any(t.title == "T1" for t in user.tasks)


def test_update_task_status(session):
    user = User(username="up", email="up@test.com", hashed_password="123")
    session.add(user)
    session.commit()

    task = Task(title="Original", description="...", owner_id=user.id)
    session.add(task)
    session.commit()
    task.is_completed = True
    session.commit()
    session.refresh(task)
    assert task.is_completed is True


def test_delete_task(session):
    user = User(username="del", email="del@test.com", hashed_password="123")
    session.add(user)
    session.commit()

    task = Task(title="Delete Me", description="...", owner_id=user.id)
    session.add(task)
    session.commit()
    tid = task.id
    session.delete(task)
    session.commit()
    res = session.execute(select(Task).where(Task.id == tid)).scalar()
    assert res is None

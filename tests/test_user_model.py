import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from task_fastapi.models.user import User


def test_create_user_instance(session):
    new_user = User(
        username='gemini',
        email='gemini@google.com',
        hashed_password='hashed_secret_123',
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    assert new_user.id is not None
    assert new_user.username == 'gemini'
    assert hasattr(new_user, 'created_at')


def test_user_unique_constraints(session):
    user1 = User(
        username='duplicado', email='unique@test.com', hashed_password='123'
    )
    session.add(user1)
    session.commit()
    user2 = User(
        username='duplicado', email='outro@test.com', hashed_password='456'
    )
    session.add(user2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_user_timestamps_auto_update(session):
    user = User(
        username='timer', email='timer@test.com', hashed_password='123'
    )
    session.add(user)
    session.commit()
    initial_updated_at = user.updated_at
    user.username = 'timer_updated'
    session.commit()
    session.refresh(user)
    assert user.updated_at >= initial_updated_at


def test_delete_user_cascade_tasks(session):
    from task_fastapi.models.task import Task  # noqa: PLC0415

    user = User(
        username='cascade', email='cascade@test.com', hashed_password='123'
    )
    session.add(user)
    session.commit()
    task = Task(title='Task do User', description='...', owner_id=user.id)
    session.add(task)
    session.commit()
    task_id = task.id
    session.delete(user)
    session.commit()
    res = session.execute(select(Task).where(Task.id == task_id)).scalar()
    assert res is None


def test_get_user_by_id(session):
    user = User(
        username='timer', email='timer@test.com', hashed_password='123'
    )
    session.add(user)
    session.commit()
    assert user.id == 1


def test_get_all_users_db(session):
    correct_len = 2
    users = [
        User(username='eve', email='eve@test.com', hashed_password='123'),
        User(
            username='frank', email='frank@test.com', hashed_password='secret'
        ),
    ]
    session.add_all(users)
    session.commit()
    users = session.scalars(select(User)).all()
    assert len(users) == correct_len
    assert users[0].username == 'eve'
    assert users[1].username == 'frank'

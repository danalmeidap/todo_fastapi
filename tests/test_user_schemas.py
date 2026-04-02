import pytest
from pydantic import ValidationError

from task_fastapi.schemas.user import UserDB, UserPublic, UserSchema


def test_user_schema_valid():
    data = {
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'password123',
    }
    user = UserSchema(**data)
    assert user.username == data['username']
    assert user.email == data['email']
    assert user.password == data['password']


def test_user_missing_fields():
    with pytest.raises(ValidationError):
        UserSchema(username='testuser', email='test@test.com')


def test_user_invalid_email():
    data = {
        'username': 'testuser',
        'email': 'invalid-email',
        'password': 'password123',
    }
    with pytest.raises(ValidationError):
        UserSchema(**data)


def test_user_public_structure():
    data = {
        'id': 1,
        'username': 'testuser',
        'email': 'test@test.com',
    }
    user = UserPublic(**data)
    assert user.id == 1
    assert not hasattr(user, 'password')


def test_user_db_inheritance():
    data = {
        'id': 1,
        'username': 'testuser',
        'email': 'test@test.com',
        'hashed_password': 'hashed_password123',
    }
    user = UserDB(**data)
    assert user.id == 1
    assert user.username == data['username']
    assert user.email == data['email']
    assert user.hashed_password == data['hashed_password']


def test_user_public_form_orm():
    class MockUser:
        def __init__(self, id, username, email):
            self.id = id
            self.username = username
            self.email = email

    mock_user = MockUser(id=1, username='testuser', email='test@test.com')
    user = UserPublic.model_validate(mock_user)
    assert user.id == 1
    assert user.username == 'testuser'
    assert user.email == 'test@test.com'

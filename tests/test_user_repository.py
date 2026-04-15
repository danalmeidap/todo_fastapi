from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from task_fastapi.repositories.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserRepository,
)
from task_fastapi.settings.security import verify_password


def test_update_user_not_found_raises_exception():
    mock_db = MagicMock()
    repo = UserRepository(mock_db)
    with patch.object(UserRepository, 'get_by_id', return_value=None):
        with pytest.raises(UserNotFoundError) as exc_info:
            repo.update(user_id=999, update_dict={'username': 'Novo Username'})
        assert str(exc_info.value) == 'User with id 999 not found'


def test_get_user_by_id_success(userDB):
    mock_session = MagicMock()
    mock_session.scalar.return_value = userDB
    user_repo = UserRepository(mock_session)
    found_user = user_repo.get_by_id(userDB.id)
    assert found_user is not None
    assert found_user.id == userDB.id
    assert found_user.username == userDB.username
    assert mock_session.scalar.called


def test_get_user_by_id_not_found():
    mock_session = MagicMock()
    mock_session.scalar.return_value = None
    user_repo = UserRepository(mock_session)
    found_user = user_repo.get_by_id(999)
    assert found_user is None
    assert mock_session.scalar.called


def test_update_user_integrity_error(userDB):
    mock_session = MagicMock()
    mock_session.scalar.return_value = userDB
    mock_session.commit.side_effect = IntegrityError(
        statement='UPDATE...', params={}, orig=Exception('duplicate key value')
    )
    user_repo = UserRepository(mock_session)
    update_data = MagicMock()
    update_data.model_dump.return_value = {
        'username': 'novo_username_duplicado',
        'email': 'email_ja_existente@teste.com',
    }
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        user_repo.update(user_id=userDB.id, update_dict=update_data)
    assert str(exc_info.value) == (
        'Update failed: email or username already exists'
    )
    assert mock_session.rollback.called
    assert not mock_session.refresh.called


def test_change_password_success(userDB):
    mock_session = MagicMock()
    query_mock = mock_session.query.return_value.filter.return_value
    query_mock.first.return_value = userDB
    user_repo = UserRepository(mock_session)
    raw_new_pass = 'new_secure_password_123'
    old_hash = userDB.hashed_password
    user_repo.change_password(user_id=userDB.id, new_raw_password=raw_new_pass)
    assert userDB.hashed_password != old_hash
    assert userDB.hashed_password != raw_new_pass
    assert verify_password(raw_new_pass, userDB.hashed_password) is True
    mock_session.commit.assert_called_once()


def test_change_password_user_not_found():
    mock_session = MagicMock()

    (
        mock_session.query.return_value.filter.return_value.first.return_value
    ) = None

    user_repo = UserRepository(mock_session)

    with pytest.raises(UserNotFoundError) as exc_info:
        user_repo.change_password(user_id=999, new_raw_password='any_password')
    assert 'User 999 not found' in str(exc_info.value)
    assert not mock_session.commit.called


def test_delete_user_not_found():
    mock_session = MagicMock()
    mock_session.scalar.return_value = None
    user_repo = UserRepository(mock_session)
    with pytest.raises(UserNotFoundError) as exc_info:
        user_repo.delete(user_id=999)
    assert 'User with id 999 not found' in str(exc_info.value)
    assert not mock_session.commit.called


def test_get_user_by_username_success(userDB):
    mock_session = MagicMock()
    mock_session.scalar.return_value = userDB
    user_repo = UserRepository(mock_session)
    found_user = user_repo.get_user_by_username(userDB.id)
    assert found_user is not None
    assert found_user.username == userDB.username
    assert mock_session.scalar.called


def test_update_user_using_plain_dict():
    mock_session = MagicMock()
    mock_user = MagicMock()
    mock_user.username = 'old_name'
    repo = UserRepository(mock_session)

    with patch.object(repo, 'get_by_id', return_value=mock_user):
        dados_atualizacao = {'username': 'new_name'}
        resultado = repo.update(1, dados_atualizacao)
        assert mock_user.username == 'new_name'
        mock_session.commit.assert_called_once()
        assert resultado == mock_user

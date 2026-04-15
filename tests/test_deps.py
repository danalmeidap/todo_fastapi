from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from jwt import DecodeError

from task_fastapi.deps import get_current_user


class MockRepository:
    def get_user_by_username(self, username):
        pass


def test_get_current_user_success(mock_repo):
    token = 'token_valido'
    payload = {'sub': 'alice@example.com'}
    mock_user = MagicMock()
    mock_user.username = 'alice@example.com'
    mock_repo.get_user_by_username.return_value = mock_user
    with patch('task_fastapi.deps.decode', return_value=payload):
        result = get_current_user(repository=mock_repo, token=token)

        assert result == mock_user
        mock_repo.get_user_by_username.assert_called_once_with(
            'alice@example.com'
        )


def test_get_current_user_no_sub_in_payload(mock_repo):
    token = 'token_sem_sub'
    payload = {'not_sub': 'anything'}

    with patch('task_fastapi.deps.decode', return_value=payload):
        with pytest.raises(HTTPException) as exc:
            get_current_user(repository=mock_repo, token=token)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == 'Could not validate credentials'


def test_get_current_user_decode_error(mock_repo):
    token = 'token_corrompido'
    with patch('task_fastapi.deps.decode', side_effect=DecodeError):
        with pytest.raises(HTTPException) as exc:
            get_current_user(repository=mock_repo, token=token)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == 'Could not validate credentials'


def test_get_current_user_raises_credentials_exception_on_decode_error():
    mock_repository = MagicMock()
    token = 'token_invalido'
    with patch('task_fastapi.deps.decode', side_effect=DecodeError):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(repository=mock_repository, token=token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == 'Could not validate credentials'
        assert exc_info.value.headers == {'WWW-Authenticate': 'Bearer'}


def test_get_current_user_raises_credentials_exception_when_sub_is_missing():
    mock_repository = MagicMock()
    token = 'token_sem_sub'
    payload_incompleto = {'outros_dados': 'teste'}

    with patch('task_fastapi.deps.decode', return_value=payload_incompleto):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(repository=mock_repository, token=token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_raises_credentials_exception_when_user_not_found():
    mock_repository = MagicMock()
    mock_repository.get_user_by_username.return_value = None

    token = 'token_valido'
    username_valido = 'usuario_teste'

    with patch(
        'task_fastapi.deps.decode', return_value={'sub': username_valido}
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(repository=mock_repository, token=token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        mock_repository.get_user_by_username.assert_called_once_with(
            username_valido
        )

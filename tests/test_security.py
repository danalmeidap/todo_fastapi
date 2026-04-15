from datetime import timedelta

import jwt
from jwt import decode

from task_fastapi.settings.security import get_password_hash, verify_password
from task_fastapi.settings.token import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
)


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)
    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_create_access_token_with_custom_expires():
    data = {'sub': 'test@example.com'}
    custom_delta = timedelta(minutes=10)
    token = create_access_token(data, expires_delta=custom_delta)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded['sub'] == data['sub']
    assert 'exp' in decoded


def test_token_contains_expiration():
    data = {'sub': 'user@test.com'}
    token = create_access_token(data)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert isinstance(decoded['exp'], int)


def test_get_password_hash():
    correct_answer = 10
    password = 'minha_senha_segura_123'
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert len(hashed_password) > correct_answer


def test_verify_password_correct():
    password = 'teste_de_senha'
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password) is True


def test_verify_password_incorrect():
    password = 'senha_original'
    wrong_password = 'senha_errada'
    hashed_password = get_password_hash(password)

    assert verify_password(wrong_password, hashed_password) is False


def test_password_hashes_are_different_for_same_password():
    password = 'senha_repetida'
    hash_1 = get_password_hash(password)
    hash_2 = get_password_hash(password)
    assert hash_1 != hash_2
    assert verify_password(password, hash_1) is True
    assert verify_password(password, hash_2) is True

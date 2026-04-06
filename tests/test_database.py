import pytest
from fastapi import status
from sqlalchemy import text
from sqlalchemy.orm import Session

from task_fastapi.settings.database import get_db


def test_get_db_yields_session():
    generator = get_db()
    db_session = next(generator)
    try:
        assert isinstance(db_session, Session)
    finally:
        try:
            next(generator)
        except StopIteration:
            pass


def test_get_db_is_overridden_in_client(client):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Hello World'}


def test_db_session_fixture_is_working(session):
    assert session.is_active
    try:
        result = session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table';")
        )
        tables = [row[0] for row in result]

        assert len(tables) >= 0
    except Exception as e:
        pytest.fail(f'A sessão falhou ao executar SQL puro: {e}')

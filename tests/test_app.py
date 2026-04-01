from fastapi import status
from fastapi.testclient import TestClient

from task_fastapi.app import app

client = TestClient(app)


def test_read_root_should_return_200():
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK


def test_read_root_should_return_message():
    response = client.get('/')
    assert response.json() == {'message': 'Hello, World!'}

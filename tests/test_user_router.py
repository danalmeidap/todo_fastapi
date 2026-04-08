from unittest.mock import patch

from fastapi import status


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'danilo',
            'email': 'danilo@example.com',
            'password': 'secure123',
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['username'] == 'danilo'
    assert 'id' in data
    assert data['id'] is not None


def test_create_user_duplicate_email(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'outro_nome',
            'email': user['email'],  # E-mail já criado pela fixture
            'password': 'password123',
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Email already registered'


def test_read_user_by_id(client, user):
    user_id = user['id']
    response = client.get(f'/users/{user_id}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == user['email']


def test_read_all_users(client, user):
    response = client.get('/users/')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'users' in data
    assert len(data['users']) >= 1


def test_update_user_success(client, user):
    user_id = user['id']
    update_data = {
        'username': 'danilo_updated',
        'email': 'danilo_new@example.com',
        'password': 'new_password_456',
    }
    response = client.put(f'/users/{user_id}', json=update_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'danilo_updated'
    assert response.json()['email'] == 'danilo_new@example.com'


def test_update_user_email_conflict(client, user):
    client.post(
        '/users/',
        json={'username': 'jose', 'email': 'jose@test.com', 'password': '123'},
    )

    response = client.put(
        f'/users/{user["id"]}',
        json={
            'username': user['username'],
            'email': 'jose@test.com',
            'password': '123',
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Email already in use' in response.json()['detail']


def test_delete_user_success(client, user):
    user_id = user['id']
    delete_res = client.delete(f'/users/{user_id}')
    assert delete_res.status_code == status.HTTP_204_NO_CONTENT
    get_res = client.get(f'/users/{user_id}')
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_user_not_found_operations(client):
    invalid_id = 9999
    response_get = client.get(f'/users/{invalid_id}')
    assert response_get.status_code == status.HTTP_404_NOT_FOUND
    response_put = client.put(
        f'/users/{invalid_id}',
        json={'username': 'a', 'email': 'a@a.com', 'password': '1'},
    )
    assert response_put.status_code == status.HTTP_404_NOT_FOUND
    response_delete = client.delete(f'/users/{invalid_id}')
    assert response_delete.status_code == status.HTTP_404_NOT_FOUND


def test_create_user_internal_error_router(client):
    user_payload = {
        'email': 'error_test@example.com',
        'username': 'erroruser',
        'password': 'password123',
    }

    with patch(
        'task_fastapi.repositories.user.UserRepository.create'
    ) as mock_create:
        mock_create.side_effect = Exception('Falha catastrófica no banco')

        response = client.post('/users/', json=user_payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'detail' in response.json()


def test_update_user_internal_error_router(client, user):
    user_id = user['id']
    user_payload = {
        'email': 'error_test@example.com',
        'username': 'erroruser',
        'password': 'password123',
    }

    with patch(
        'task_fastapi.repositories.user.UserRepository.update'
    ) as mock_create:
        mock_create.side_effect = Exception('Falha catastrófica no banco')
        response = client.put(f'/users/{user_id}', json=user_payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'detail' in response.json()


def test_delete_user_internal_error_router(client, user):
    user_id = user['id']
    with patch(
        'task_fastapi.repositories.user.UserRepository.delete'
    ) as mock_create:
        mock_create.side_effect = Exception('Falha catastrófica no banco')
        response = client.delete(f'/users/{user_id}')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'detail' in response.json()

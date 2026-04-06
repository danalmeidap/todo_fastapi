from fastapi import status


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['username'] == 'testuser'
    assert response.json()['email'] == 'testuser@example.com'


def test_get_users(client):
    client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
        },
    )
    response = client.get('/users/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['users']) == 1


def test_get_user_by_id(client, user):
    response = client.get(f'/users/{user["id"]}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'testuser'
    assert response.json()['email'] == 'test@example.com'


def test_get_user_not_found(client):
    response = client.get('/users/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'User not found'


def test_update_user(client, user):
    response = client.put(
        f'/users/{user["id"]}',
        json={
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'password': 'updatedpassword',
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'updateduser'
    assert response.json()['email'] == 'updateduser@example.com'


def test_update_user_not_found(client):
    response = client.put(
        '/users/999',
        json={
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'password': 'updatedpassword',
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'User not found'


def test_create_user_duplicate_email(client):
    client.post(
        '/users/',
        json={
            'username': 'testuser1',
            'email': 'testuser@example.com',
            'password': 'testpassword1',
        },
    )
    response = client.post(
        '/users/',
        json={
            'username': 'testuser2',
            'email': 'testuser@example.com',
            'password': 'testpassword2',
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Email already registered'


def test_create_user_duplicate_username(client):
    client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'testuser1@example.com',
            'password': 'testpassword1',
        },
    )
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'testuser2@example.com',
            'password': 'testpassword2',
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Username already taken'


def test_create_user_invalid_data(client):
    response = client.post(
        '/users/',
        json={
            'username': '',
            'email': 'invalidemail',
            'password': 'short',
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_user(client, user):
    response = client.delete(f'/users/{user["id"]}')
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_user_not_found(client):
    response = client.delete('/users/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND

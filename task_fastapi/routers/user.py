from fastapi import APIRouter, HTTPException, Response, status

from task_fastapi.deps import UserRepo
from task_fastapi.schemas.user import UserDB, UserList, UserPublic, UserSchema

user_router = APIRouter()

users_db: list[UserDB] = []


@user_router.post(
    '/', response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def create_user(user_data: UserSchema, repository: UserRepo):
    if repository.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered',
        )
    try:
        new_user = repository.create(user_data)
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error creating user: {str(e)}',
        )


@user_router.get('/', response_model=UserList, status_code=status.HTTP_200_OK)
def get_users(repository: UserRepo):
    users = repository.get_all()
    return {'users': users}


@user_router.get('/{user_id}', response_model=UserPublic)
def read_user(user_id: int, repository: UserRepo):
    user = repository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    return user


@user_router.put(
    '/{user_id}', response_model=UserPublic, status_code=status.HTTP_200_OK
)
def update_user(user_id: int, user_data: UserSchema, repository: UserRepo):
    user = repository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    existing_user = repository.get_by_email(user_data.email)
    if existing_user and existing_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already in use by another account',
        )
    try:
        updated_user = repository.update(user_id, user_data)
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error updating user: {str(e)}',
        )


@user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, repository: UserRepo):
    user = repository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    try:
        repository.delete(user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error deleting user: {str(e)}',
        )

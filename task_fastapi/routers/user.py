from fastapi import APIRouter, HTTPException, status

from task_fastapi.schemas.user import UserDB, UserList, UserPublic, UserSchema

user_router = APIRouter()

users_db: list[UserDB] = []


@user_router.post(
    '/', response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def create_user(user: UserSchema):
    if any(u.email == user.email for u in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered',
        )
    if any(u.username == user.username for u in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username already taken',
        )
    user_with_id = UserDB(
        id=len(users_db) + 1,
        username=user.username,
        email=user.email,
        hashed_password=user.password + 'hash',
    )
    users_db.append(user_with_id)
    return user_with_id


@user_router.get('/', response_model=UserList, status_code=status.HTTP_200_OK)
def get_users():
    return UserList(
        users=[
            UserPublic(id=u.id, username=u.username, email=u.email)
            for u in users_db
        ]
    )


@user_router.get('/{user_id}', response_model=UserPublic)
def read_user(user_id: int):
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    return user


@user_router.put(
    '/{user_id}', response_model=UserPublic, status_code=status.HTTP_200_OK
)
def update_user(user_id: int, user: UserSchema):
    for i, u in enumerate(users_db):
        if u.id == user_id:
            updated_user = UserDB(
                id=user_id,
                username=user.username,
                email=user.email,
                hashed_password=user.password + '_hashed',
            )
            users_db[i] = updated_user
            return updated_user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
    )


@user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    if user_id > len(users_db) or user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    del users_db[user_id - 1]
    return {'message': 'User deleted successfully'}

from typing import Any, Optional, Union

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from task_fastapi.models.user import User
from task_fastapi.schemas.user import UserSchema
from task_fastapi.settings.security import get_password_hash


class EntityNotFoundError(Exception):
    """Base exception for missing entities."""

    pass


class UserNotFoundError(EntityNotFoundError):
    pass


class TaskNotFoundError(EntityNotFoundError):
    pass


class EntityAlreadyExistsError(Exception):
    """Base exception for duplicate data."""

    pass


class UserAlreadyExistsError(EntityAlreadyExistsError):
    pass


class UserRepository:
    """Repository for managing User operations in the database."""

    # Fields allowed for profile updates (sensitive auth data excluded)
    ALLOWED_UPDATE_FIELDS = {'email', 'username', 'name', 'is_active'}

    def __init__(self, session: Session):
        self.session = session

    def get_all(self):
        return self.session.scalars(select(User)).all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.scalar(select(User).where(User.id == user_id))

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.scalar(select(User).where(User.email == email))

    def get_user_by_username(self, username: str):
        return self.session.scalar(
            select(User).where(User.username == username)
        )

    def exists(self, user_id: int) -> bool:
        return (
            self.session.scalar(
                select(func.count(User.id)).where(User.id == user_id)
            )
            > 0
        )

    def create(self, user_data: UserSchema):
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def update(self, user_id: int, update_dict: Union[dict, Any]) -> User:
        db_user = self.get_by_id(user_id)
        if not db_user:
            raise UserNotFoundError(f'User with id {user_id} not found')
        if hasattr(update_dict, 'model_dump'):
            data = update_dict.model_dump(exclude_unset=True)
        else:
            data = update_dict

        for key, value in data.items():
            if key in self.ALLOWED_UPDATE_FIELDS:
                setattr(db_user, key, value)
            elif key == 'password':
                db_user.hashed_password = get_password_hash(value)
        try:
            self.session.commit()
            self.session.refresh(db_user)
            return db_user
        except IntegrityError:
            self.session.rollback()
            raise UserAlreadyExistsError(
                'Update failed: email or username already exists'
            )

    def change_password(self, user_id: int, new_raw_password: str):
        user = self.session.query(User).filter(User.id == user_id).first()

        if not user:
            raise UserNotFoundError(f'User {user_id} not found')

        new_hash = get_password_hash(new_raw_password)

        user.hashed_password = new_hash

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f'User with id {user_id} not found')

        self.session.delete(user)
        self.session.commit()

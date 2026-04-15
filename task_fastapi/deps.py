from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode
from sqlalchemy.orm import Session

from task_fastapi.repositories.task import TaskRepository
from task_fastapi.repositories.user import UserRepository
from task_fastapi.settings.database import get_db
from task_fastapi.settings.settings import Settings


def get_user_repository(session: Session = Depends(get_db)) -> UserRepository:
    """Fábrica para o repositório de utilizadores."""
    return UserRepository(session)


def get_task_repository(session: Session = Depends(get_db)) -> TaskRepository:
    """Fábrica para o repositório de tarefas."""
    return TaskRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
TaskRepo = Annotated[TaskRepository, Depends(get_task_repository)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


settings = Settings()


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def get_current_user(
    repository: UserRepository = Depends(get_user_repository),
    token: str = Depends(oauth2_scheme),
):
    credentials_exepction = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exepction
    except DecodeError:
        raise credentials_exepction
    user = repository.get_user_by_username(username)
    if user is None:
        raise credentials_exepction
    return user

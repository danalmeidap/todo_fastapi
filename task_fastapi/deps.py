from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from task_fastapi.repositories.task import TaskRepository
from task_fastapi.repositories.user import UserRepository
from task_fastapi.settings.database import get_db


def get_user_repository(session: Session = Depends(get_db)) -> UserRepository:
    """Fábrica para o repositório de utilizadores."""
    return UserRepository(session)


def get_task_repository(session: Session = Depends(get_db)) -> TaskRepository:
    """Fábrica para o repositório de tarefas."""
    return TaskRepository(session)


UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
TaskRepo = Annotated[TaskRepository, Depends(get_task_repository)]

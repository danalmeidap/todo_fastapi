from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from task_fastapi.models.task import Task
from task_fastapi.schemas.task import TaskSchema


class EntityNotFoundError(Exception):
    pass


class TaskNotFoundError(EntityNotFoundError):
    pass


class TaskRepository:
    ALLOWED_UPDATE_FIELDS = {
        'title',
        'description',
        'is_completed',
        'completed',
    }

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Task]:
        return list(self.session.scalars(select(Task)).all())

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.session.scalar(select(Task).where(Task.id == task_id))

    def get_by_owner(self, owner_id: int) -> List[Task]:
        query = select(Task).where(Task.owner_id == owner_id)
        return list(self.session.scalars(query).all())

    def get_completed(self) -> List[Task]:
        query = select(Task).where(Task.is_completed)
        return list(self.session.scalars(query).all())

    def get_pending(self) -> List[Task]:
        query = select(Task).where(~Task.is_completed)
        return list(self.session.scalars(query).all())

    def create(self, task_data: TaskSchema) -> Task:
        db_task = Task(
            title=task_data.title,
            description=task_data.description or '',
            owner_id=task_data.owner_id,
            is_completed=task_data.is_completed,
        )
        self.session.add(db_task)
        self.session.commit()
        self.session.refresh(db_task)
        return db_task

    def update(self, task_id: int, update_data: Any) -> Task:
        db_task = self.get_by_id(task_id)
        if not db_task:
            raise TaskNotFoundError(f'Task with id {task_id} not found')

        if hasattr(update_data, 'model_dump'):
            data = update_data.model_dump(exclude_unset=True)
        else:
            data = update_data

        for key, value in data.items():
            field_name = 'is_completed' if key == 'completed' else key
            if field_name in self.ALLOWED_UPDATE_FIELDS:
                setattr(db_task, field_name, value)

        self.session.commit()
        self.session.refresh(db_task)
        return db_task

    def toggle_status(self, task_id: int) -> Task:
        db_task = self.get_by_id(task_id)
        if not db_task:
            raise TaskNotFoundError(f'Task with id {task_id} not found')

        db_task.is_completed = not db_task.is_completed
        self.session.commit()
        self.session.refresh(db_task)
        return db_task

    def delete(self, task_id: int) -> None:
        task = self.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(f'Task with id {task_id} not found')

        self.session.delete(task)
        self.session.commit()

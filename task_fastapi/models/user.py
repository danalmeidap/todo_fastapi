from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from task_fastapi.settings.database import table_registry

if TYPE_CHECKING:
    from task_fastapi.models.task import Task


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",
        init=False
    )

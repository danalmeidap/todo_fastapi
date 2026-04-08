from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskSchema(BaseModel):
    title: str
    description: str | None = None
    is_completed: bool = False
    owner_id: int | None = None


class TaskPublic(TaskSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    tasks: list[TaskPublic]


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    owner_id: Optional[int] = None

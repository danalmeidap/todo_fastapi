from pydantic import BaseModel, ConfigDict


class TaskSchema(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


class TaskPublic(TaskSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    tasks: list[TaskPublic]

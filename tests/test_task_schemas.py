import pytest
from pydantic import ValidationError

from task_fastapi.schemas.task import TaskPublic, TaskSchema


def test_task_schema_valido():
    data = {
        "title": "Minha primeira tarefa",
        "description": "This is a test task.",
        "completed": False
    }
    task = TaskSchema(**data)
    assert task.title == data["title"]
    assert task.description == data["description"]
    assert task.completed is False


def test_task_schema_default_values():
    data = {
        "title": "Minha segunda tarefa"
    }
    task = TaskSchema(**data)
    assert task.title == data["title"]
    assert task.description is None
    assert task.completed is False


def test_task_schema_missing_title():
    with pytest.raises(ValidationError):
        TaskSchema(description="This task has no title.")


def test_task_public_from_orm():
    class TaskModelMock:
        id = 1
        title = "Tarefa do Banco"
        description = "Persistida"
        completed = True

    mock_obj = TaskModelMock()
    task_pub = TaskPublic.model_validate(mock_obj)
    assert task_pub.id == 1
    assert task_pub.title == "Tarefa do Banco"

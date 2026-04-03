from typing import List

from fastapi import APIRouter, HTTPException, status

from task_fastapi.routers.user import user_db
from task_fastapi.schemas.task import (
    TaskList,
    TaskPublic,
    TaskSchema,
)

task_router = APIRouter()

task_db: List = []


@task_router.get('/', status_code=status.HTTP_200_OK, response_model=TaskList)
def read_tasks():
    return {'tasks': task_db}


@task_router.post(
    '/', status_code=status.HTTP_201_CREATED, response_model=TaskPublic
)
def create_task(task: TaskSchema):
    if task.owner_id is not None:
        user_exists = any(user.id == task.owner_id for user in user_db)
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner not found"
            )
    new_task = {**task.model_dump(), "id": len(task_db) + 1}
    task_db.append(new_task)
    return new_task


@task_router.get(
    '/{task_id}', status_code=status.HTTP_200_OK, response_model=TaskPublic
)
def read_task(task_id: int):
    if task_id > len(task_db) or task_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    return task_db[task_id - 1]


@task_router.put('/{task_id}', response_model=TaskPublic)
def update_task(task_id: int, task_update: TaskSchema):
    task_index = next(
        (
        i for i, t in enumerate(task_db) if t['id'] == task_id
        ),
          None
    )
    if task_index is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. Validar o Owner se ele for fornecido
    if task_update.owner_id is not None:
        user_exists = any(u.id == task_update.owner_id for u in user_db)
        if not user_exists:
            raise HTTPException(status_code=404, detail="Owner not found")
    updated_data = task_update.model_dump()
    task_db[task_index].update(updated_data)
    return task_db[task_index]


@task_router.delete('/{task_id}')
def delete_task(task_id: int):
    if task_id > len(task_db) or task_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    del task_db[task_id - 1]
    return {'message': 'Task deleted successfully'}

from fastapi import APIRouter, HTTPException, status

from task_fastapi.schemas.task import TaskList, TaskPublic, TaskSchema

task_router = APIRouter()

task_db = []


@task_router.get("/", status_code=status.HTTP_200_OK, response_model=TaskList)
def read_tasks():
    return {"tasks": task_db}


@task_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=TaskPublic
)
def create_task(task: TaskSchema):
    new_task = {"id": len(task_db) + 1, **task.model_dump()}
    task_db.append(new_task)
    return new_task


@task_router.get(
    "/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskPublic
)
def read_task(task_id: int):
    if task_id > len(task_db) or task_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task_db[task_id - 1]


@task_router.put('/{task_id}', response_model=TaskPublic,
                  status_code=status.HTTP_200_OK)
def update_task(task_id: int, task: TaskSchema):
    for i, t in enumerate(task_db):
        if t['id'] == task_id:
            updated_task = {'id': task_id, **task.model_dump()}
            task_db[i] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail='Task not found')


@task_router.delete(
    "/{task_id}")
@task_router.delete('/{task_id}')
def delete_task(task_id: int):
    if task_id > len(task_db) or task_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    del task_db[task_id - 1]
    return {"message": "Task deleted successfully"}

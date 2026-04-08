from fastapi import APIRouter, HTTPException, Response, status

from task_fastapi.deps import TaskRepo, UserRepo
from task_fastapi.models.task import Task
from task_fastapi.schemas.task import (
    TaskList,
    TaskPublic,
    TaskSchema,
)

tasks_db = []
task_router = APIRouter()


@task_router.get('/completed', response_model=TaskList)
def read_completed_tasks(repository: TaskRepo):
    tasks = repository.get_completed()
    return {'tasks': tasks}


@task_router.get('/pending', response_model=TaskList)
def read_pending_tasks(repository: TaskRepo):
    tasks = repository.get_pending()
    return {'tasks': tasks}


@task_router.get('/', status_code=status.HTTP_200_OK, response_model=TaskList)
def read_tasks(repository: TaskRepo):
    tasks = repository.get_all()
    return {'tasks': tasks}


@task_router.get('/owner/{owner_id}', response_model=TaskList)
def read_tasks_by_owner(owner_id: int, repository: TaskRepo):
    tasks = repository.get_by_owner(owner_id)
    return {'tasks': tasks}


@task_router.post(
    '/', status_code=status.HTTP_201_CREATED, response_model=TaskPublic
)
def create_task(
    task_data: TaskSchema, task_repository: TaskRepo, user_repository: UserRepo
):
    if task_data.owner_id:
        if not user_repository.get_by_id(task_data.owner_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Owner not found'
            )
    new_task = Task(
        title=task_data.title,
        description=task_data.description or '',
        is_completed=task_data.is_completed,
        owner_id=task_data.owner_id,
    )
    return task_repository.create(new_task)


@task_router.get(
    '/{task_id}', status_code=status.HTTP_200_OK, response_model=TaskPublic
)
def read_task(task_id: int, repository: TaskRepo):
    task = repository.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    return task


@task_router.get('/user/{user_id}', response_model=TaskList)
def read_tasks_by_user(
    user_id: int, task_repository: TaskRepo, user_repository: UserRepo
):
    if not user_repository.exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    tasks = [
        task for task in task_repository.get_all() if task.owner_id == user_id
    ]
    return {'tasks': tasks}


@task_router.put('/{task_id}', response_model=TaskPublic)
def update_task(
    task_id: int,
    task_data: TaskSchema,
    repository: TaskRepo,
    user_repository: UserRepo,
):
    db_task = repository.get_by_id(task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )

    if task_data.owner_id and not user_repository.exists(task_data.owner_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Owner not found'
        )
    update_data = {
        'title': task_data.title,
        'description': task_data.description,
        'is_completed': task_data.is_completed,
        'owner_id': task_data.owner_id,
    }

    return repository.update(task_id, update_data)


@task_router.delete('/{task_id}')
def delete_task(task_id: int, repository: TaskRepo):
    db_task = repository.get_by_id(task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    repository.delete(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@task_router.patch('/{task_id}/toggle', response_model=TaskPublic)
def toggle_task_status(task_id, repository: TaskRepo):
    db_task = repository.get_by_id(task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    new_status = not db_task.is_completed

    try:
        updated_task = repository.update(task_id, {'is_completed': new_status})
        return updated_task

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error toggling task: {str(e)}',
        )

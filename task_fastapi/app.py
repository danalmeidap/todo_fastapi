from fastapi import FastAPI

from task_fastapi.routers.task import task_router
from task_fastapi.routers.user import user_router

app = FastAPI()

# Registro dos routers
app.include_router(task_router, prefix='/tasks', tags=['tasks'])
app.include_router(user_router, prefix='/users', tags=['users'])


@app.get('/')
def read_root():
    return {'message': 'Hello World'}

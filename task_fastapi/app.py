from fastapi import FastAPI

from task_fastapi.routers.task import task_router

app = FastAPI()
app.include_router(task_router, prefix='/tasks', tags=['tasks'])


@app.get('/')
def read_root():
    return {'message': 'Hello, World!'}

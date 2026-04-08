from fastapi import FastAPI

from task_fastapi.routers.task import task_router
from task_fastapi.routers.user import user_router
from task_fastapi.settings.database import engine, table_registry

app = FastAPI()

# Registro dos routers
app.include_router(task_router, prefix='/tasks', tags=['tasks'])
app.include_router(user_router, prefix='/users', tags=['users'])
table_registry.metadata.create_all(bind=engine)


@app.get('/')
def read_root():
    return {'message': 'Hello World'}

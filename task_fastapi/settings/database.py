from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker

from task_fastapi.settings.settings import Settings

settings = Settings()
table_registry = registry()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from src.config import settings
from src.utils.logger import db_logger

# Engine con pool de conexiones
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    echo=(settings.LOG_LEVEL == 'DEBUG')
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db_logger.error("Database session error", error=e)
        db.rollback()
        raise
    finally:
        db.close()


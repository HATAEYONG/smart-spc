"""
Dependencies for dependency injection
"""
from typing import Generator
from sqlalchemy.orm import Session
from app.database import get_db as get_db_session


async def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

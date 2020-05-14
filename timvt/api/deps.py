"""timvt api deps."""

from typing import Generator

from timvt.db.session import SessionLocal


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

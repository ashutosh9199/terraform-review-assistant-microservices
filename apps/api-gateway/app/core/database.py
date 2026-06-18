from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()

if settings.database_url.startswith("sqlite:///"):
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    if db_path.parent != Path("."):
        db_path.parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models import domain  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_add_columns()


def _migrate_add_columns() -> None:
    """Lightweight auto-migration for SQLite dev databases.

    create_all() only creates missing tables, not missing columns on existing
    tables. This adds newly introduced nullable columns without touching
    existing data, so upgrading the app doesn't require deleting the dev DB.
    """
    inspector = inspect(engine)
    if "review_jobs" not in inspector.get_table_names():
        return
    existing = {col["name"] for col in inspector.get_columns("review_jobs")}
    if "executive_feedback" not in existing:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE review_jobs ADD COLUMN executive_feedback TEXT"))
    if "current_stage" not in existing:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE review_jobs ADD COLUMN current_stage VARCHAR(60)"))

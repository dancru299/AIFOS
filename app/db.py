from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _build_engine():
    settings = get_settings()
    database_url = settings.database_url

    if database_url.startswith("sqlite:///"):
        sqlite_path = database_url.replace("sqlite:///", "", 1)
        db_file = (settings.project_root / sqlite_path).resolve()
        db_file.parent.mkdir(parents=True, exist_ok=True)

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, future=True)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_columns()


def _ensure_sqlite_columns() -> None:
    if not get_settings().database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "jobs" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("jobs")}
    columns_to_add = {
        "is_good_job": "BOOLEAN",
        "budget_estimate": "VARCHAR(255)",
        "tech_stack": "JSON",
        "client_country": "VARCHAR(255)",
        "proposal_timeline": "VARCHAR(255)",
        "workspace_path": "VARCHAR(2048)",
        "delivery_path": "VARCHAR(2048)",
    }

    with engine.begin() as connection:
        for column_name, column_type in columns_to_add.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE jobs ADD COLUMN {column_name} {column_type}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

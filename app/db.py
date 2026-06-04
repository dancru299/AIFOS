import logging
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Columns added to existing tables after the initial schema. Local/dev databases
# are managed by create_all (see init_db), and create_all never ALTERs an
# existing table — so after a model adds a column, an older DB would be missing
# it and every ORM query on that table would fail with "no such column". We add
# known additive columns here so "just start the app" keeps working without a
# manual migration. Production (Postgres) uses Alembic instead.
_ADDITIVE_COLUMNS: dict[str, dict[str, str]] = {
    "jobs": {"total_cost_usd": "FLOAT NOT NULL DEFAULT 0"},
}


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
    """Create tables from the models.

    Convenient for local dev and tests. In production, schema changes are
    managed by Alembic (``alembic upgrade head``); ``create_all`` is a no-op
    against an already-migrated database.
    """
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _reconcile_additive_columns()


def _reconcile_additive_columns() -> None:
    """Add additive columns missing from a pre-existing create_all database.

    SQLite only (production uses Alembic). Idempotent and non-destructive: each
    column is added with a default, so existing rows keep their data.
    """
    if not engine.url.get_backend_name().startswith("sqlite"):
        return
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table, columns in _ADDITIVE_COLUMNS.items():
            if table not in existing_tables:
                continue
            present = {col["name"] for col in inspector.get_columns(table)}
            for column, ddl in columns.items():
                if column not in present:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
                    logger.info("Reconciled schema: added %s.%s", table, column)


def get_db() -> Iterator[Session]:
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

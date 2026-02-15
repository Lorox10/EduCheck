from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import Settings


_engine: Engine | None = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def _build_db_url(settings: Settings) -> str:
    return (
        "mysql+mysqlconnector://"
        f"{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


def _build_server_url(settings: Settings) -> str:
    return (
        "mysql+mysqlconnector://"
        f"{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/"
    )


def _ensure_database(settings: Settings) -> None:
    server_engine = create_engine(_build_server_url(settings), pool_pre_ping=True)
    with server_engine.connect() as connection:
        connection.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{settings.db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
            )
        )
    server_engine.dispose()


def init_db() -> None:
    global _engine
    if _engine is not None:
        return
    settings = Settings()
    _ensure_database(settings)
    _engine = create_engine(_build_db_url(settings), pool_pre_ping=True)
    SessionLocal.configure(bind=_engine)
    from models import Base as ModelBase

    ModelBase.metadata.create_all(_engine)
    _ensure_schema(_engine)


def _ensure_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("students"):
        return

    columns = {col["name"] for col in inspector.get_columns("students")}
    if "telefono_acudiente" not in columns:
        with engine.connect() as connection:
            connection.execute(
                text(
                    "ALTER TABLE students "
                    "ADD COLUMN telefono_acudiente VARCHAR(20) NULL"
                )
            )
    if "telegram_id" not in columns:
        with engine.connect() as connection:
            connection.execute(
                text(
                    "ALTER TABLE students "
                    "ADD COLUMN telegram_id VARCHAR(20) NULL"
                )
            )


def db_healthcheck() -> str:
    if _engine is None:
        return "not_initialized"
    try:
        with _engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"


@contextmanager
def get_session() -> Iterator[Session]:
    if _engine is None:
        init_db()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

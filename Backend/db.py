from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import Settings


_engine: Engine | None = None


def _build_db_url(settings: Settings) -> str:
    return (
        "mysql+mysqlconnector://"
        f"{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )


def init_db() -> None:
    global _engine
    if _engine is not None:
        return
    settings = Settings()
    _engine = create_engine(_build_db_url(settings), pool_pre_ping=True)


def db_healthcheck() -> str:
    if _engine is None:
        return "not_initialized"
    try:
        with _engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"

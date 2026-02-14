import os
from dataclasses import dataclass


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    db_host: str = _get_env("DB_HOST", "127.0.0.1")
    db_port: str = _get_env("DB_PORT", "3306")
    db_name: str = _get_env("DB_NAME", "edu_check")
    db_user: str = _get_env("DB_USER", "root")
    db_password: str = _get_env("DB_PASSWORD", "")

    app_env: str = _get_env("APP_ENV", "development")
    app_port: str = _get_env("APP_PORT", "5000")
    secret_key: str = _get_env("SECRET_KEY", "change-me")

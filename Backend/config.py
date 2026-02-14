import os
from dataclasses import dataclass
from pathlib import Path


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    base_dir: Path = Path(__file__).resolve().parent
    db_host: str = ""
    db_port: str = ""
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""
    qr_dir: Path = Path()
    uploads_dir: Path = Path()
    app_env: str = ""
    app_port: str = ""
    secret_key: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "db_host", _get_env("DB_HOST", "127.0.0.1"))
        object.__setattr__(self, "db_port", _get_env("DB_PORT", "3306"))
        object.__setattr__(self, "db_name", _get_env("DB_NAME", "edu_check"))
        object.__setattr__(self, "db_user", _get_env("DB_USER", "root"))
        object.__setattr__(self, "db_password", _get_env("DB_PASSWORD", ""))
        object.__setattr__(
            self,
            "qr_dir",
            Path(_get_env("QR_DIR", str(self.base_dir / "qr_codes"))),
        )
        object.__setattr__(
            self,
            "uploads_dir",
            Path(_get_env("UPLOADS_DIR", str(self.base_dir / "uploads"))),
        )
        object.__setattr__(self, "app_env", _get_env("APP_ENV", "development"))
        object.__setattr__(self, "app_port", _get_env("APP_PORT", "5000"))
        object.__setattr__(self, "secret_key", _get_env("SECRET_KEY", "change-me"))

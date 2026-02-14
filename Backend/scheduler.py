from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Settings
from db import get_session
from notifications import send_absence_alerts


_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return

    settings = Settings()
    hour, minute = _parse_time(settings.alert_time)

    scheduler = BackgroundScheduler(timezone=settings.timezone)
    scheduler.add_job(
        _run_absence_job,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=settings.timezone),
        id="absence_alerts",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler


def _parse_time(value: str) -> tuple[int, int]:
    parts = value.strip().split(":")
    if len(parts) != 2:
        return 7, 10
    return int(parts[0]), int(parts[1])


def _run_absence_job() -> None:
    settings = Settings()
    with get_session() as session:
        send_absence_alerts(session, settings)

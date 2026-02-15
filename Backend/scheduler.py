from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Settings
from db import get_session
from notifications import send_absence_alerts
from monthly_reports import generate_monthly_report


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
    
    # Agregar tarea para generar reporte mensual
    # Se ejecuta el día 1 de cada mes a las 23:59
    scheduler.add_job(
        _run_monthly_report_job,
        trigger=CronTrigger(day=1, hour=23, minute=59, timezone=settings.timezone),
        id="monthly_report",
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


def _run_monthly_report_job() -> None:
    print("[SCHEDULER] Ejecutando generación de reporte mensual")
    try:
        filepath = generate_monthly_report()
        if filepath:
            print(f"[SCHEDULER] Reporte mensual generado: {filepath}")
        else:
            print("[SCHEDULER] No hay datos de inasistentes para generar reporte")
    except Exception as e:
        print(f"[SCHEDULER] Error generando reporte mensual: {str(e)}")

from datetime import datetime

import pytz
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import Settings
from models import Attendance, NotificationLog, Student
from telegram import TelegramClient
from messages import build_absence_message


def _today_date(settings: Settings) -> datetime.date:
    tz = pytz.timezone(settings.timezone)
    return datetime.now(tz).date()


def _get_alert_time(settings: Settings) -> str:
    """Obtiene la hora configurada para alertas (ej: 07:10)"""
    return settings.alert_time


def send_absence_alerts(session: Session, settings: Settings) -> dict:
    today = _today_date(settings)
    alert_time = _get_alert_time(settings)

    attended_ids = session.scalars(
        select(Attendance.student_id).where(Attendance.fecha == today)
    ).all()
    attended_set = set(attended_ids)

    notified_ids = session.scalars(
        select(NotificationLog.student_id).where(NotificationLog.fecha == today)
    ).all()
    notified_set = set(notified_ids)

    students = session.scalars(select(Student)).all()
    client = TelegramClient(settings)

    sent = 0
    skipped = 0
    errors = 0

    for student in students:
        if student.id in attended_set:
            continue
        if student.id in notified_set:
            continue
        if not student.telegram_id:
            skipped += 1
            continue

        message = build_absence_message(student, alert_time)
        status, error = client.send_text(student.telegram_id, message)
        log = NotificationLog(
            student_id=student.id,
            fecha=today,
            status=status,
            error=error,
        )
        session.add(log)

        if status == "sent":
            sent += 1
        elif status == "skipped":
            skipped += 1
        else:
            errors += 1

    return {"sent": sent, "skipped": skipped, "errors": errors}

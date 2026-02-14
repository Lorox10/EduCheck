from datetime import datetime

import pytz
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import Settings
from models import Attendance, Student


def register_checkin(session: Session, documento: str) -> dict:
    settings = Settings()
    tz = pytz.timezone(settings.timezone)
    now = datetime.now(tz)
    today = now.date()

    student = session.scalar(select(Student).where(Student.documento == documento))
    if student is None:
        return {"error": "Estudiante no encontrado"}

    existing = session.scalar(
        select(Attendance)
        .where(Attendance.student_id == student.id)
        .where(Attendance.fecha == today)
    )
    if existing is not None:
        return {"status": "ya_registrado"}

    record = Attendance(
        student_id=student.id,
        fecha=today,
        hora_entrada=now.time(),
    )
    session.add(record)
    return {"status": "registrado"}

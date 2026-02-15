from datetime import datetime

import pytz
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import Settings
from models import Attendance, NotificationLog, Student
from telegram import TelegramClient
from messages import build_entry_message


def register_checkin(session: Session, documento: str) -> dict:
    settings = Settings()
    tz = pytz.timezone(settings.timezone)
    now = datetime.now(tz)
    today = now.date()
    hora_str = now.strftime("%H:%M")

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
    session.flush()

    # Enviar notificación de entrada al acudiente
    if student.telegram_id:
        client = TelegramClient(settings)
        message = build_entry_message(student, hora_str)
        status, error = client.send_text(student.telegram_id, message)
        
        # Registrar el envío de notificación
        log = NotificationLog(
            student_id=student.id,
            fecha=today,
            status=status,
            error=error,
        )
        session.add(log)
    
    return {"status": "registrado"}

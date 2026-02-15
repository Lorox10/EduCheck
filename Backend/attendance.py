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
    telegram_status = None
    telegram_error = None
    
    print(f"[ATTENDANCE] Enviando notificación - telegram_id={student.telegram_id}")
    
    if student.telegram_id:
        try:
            client = TelegramClient(settings)
            message = build_entry_message(student, hora_str)
            print(f"[TELEGRAM] Mensaje construido: {message[:50]}...")
            print(f"[TELEGRAM] Enviando a chat_id={student.telegram_id}")
            
            status, error = client.send_text(student.telegram_id, message)
            telegram_status = status
            telegram_error = error
            
            print(f"[TELEGRAM] Resultado: status={status}, error={error}")
            
            # Registrar el envío de notificación
            log = NotificationLog(
                student_id=student.id,
                fecha=today,
                status=status,
                error=error,
            )
            session.add(log)
        except Exception as e:
            print(f"[TELEGRAM] Excepción al enviar: {str(e)}")
            telegram_status = "error"
            telegram_error = str(e)
    else:
        print(f"[TELEGRAM] telegram_id vacío para estudiante {student.documento}")
    
    session.commit()
    return {
        "status": "registrado",
        "telegram_status": telegram_status,
        "telegram_error": telegram_error
    }

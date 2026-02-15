from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    students: Mapped[list["Student"]] = relationship(
        back_populates="grade", cascade="all, delete-orphan"
    )


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("documento", name="uq_students_documento"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_estudiante: Mapped[int] = mapped_column(Integer, nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(4), nullable=False)
    documento: Mapped[str] = mapped_column(String(32), nullable=False)
    correo: Mapped[str] = mapped_column(String(120), nullable=True)
    telefono_acudiente: Mapped[str | None] = mapped_column(String(20), nullable=True)
    telegram_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    qr_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.id"), nullable=False)
    grade: Mapped[Grade] = relationship(back_populates="students")


class UploadLog(Base):
    __tablename__ = "upload_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(255), nullable=False)
    grados: Mapped[str] = mapped_column(String(64), nullable=True)
    created_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("student_id", "fecha", name="uq_attendance_student_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora_entrada: Mapped[time] = mapped_column(Time, nullable=False)


class NotificationLog(Base):
    __tablename__ = "notification_logs"
    __table_args__ = (
        UniqueConstraint("student_id", "fecha", name="uq_notification_student_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

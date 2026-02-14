from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
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
    qr_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.id"), nullable=False)
    grade: Mapped[Grade] = relationship(back_populates="students")

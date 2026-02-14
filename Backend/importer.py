import csv
from io import TextIOWrapper
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Grade, Student
from qr import ensure_qr


EXPECTED_HEADERS = [
	"numero",
	"apellidos",
	"nombres",
	"tipo_documento",
	"documento",
	"correo",
	"grado",
]


def _normalize_header(value: str) -> str:
	return value.strip().lower()


def _normalize_tipo(value: str) -> str:
	cleaned = value.replace(".", "").replace(" ", "").upper()
	if cleaned in {"TI", "CC"}:
		return cleaned
	return cleaned


def _get_or_create_grade(session: Session, numero: int) -> Grade:
	grade = session.scalar(select(Grade).where(Grade.numero == numero))
	if grade is None:
		grade = Grade(numero=numero)
		session.add(grade)
		session.flush()
	return grade


def import_students(file_stream, session: Session, qr_dir: Path) -> dict:
	text_stream = TextIOWrapper(file_stream, encoding="utf-8-sig")
	reader = csv.DictReader(text_stream)

	headers = reader.fieldnames or []
	normalized = [_normalize_header(h) for h in headers]
	if normalized != EXPECTED_HEADERS:
		return {
			"error": "Encabezados invalidos",
			"esperados": EXPECTED_HEADERS,
			"recibidos": normalized,
		}

	created = 0
	updated = 0
	skipped = 0
	errors: list[dict] = []

	for idx, row in enumerate(reader, start=2):
		try:
			numero = int((row.get("numero") or "").strip())
			apellidos = (row.get("apellidos") or "").strip()
			nombres = (row.get("nombres") or "").strip()
			tipo_documento = _normalize_tipo((row.get("tipo_documento") or "").strip())
			documento = (row.get("documento") or "").strip()
			correo = (row.get("correo") or "").strip() or None
			grado = int((row.get("grado") or "").strip())

			if not (apellidos and nombres and documento and tipo_documento):
				skipped += 1
				continue

			grade = _get_or_create_grade(session, grado)
			student = session.scalar(
				select(Student).where(Student.documento == documento)
			)

			if student is None:
				student = Student(
					numero_estudiante=numero,
					apellidos=apellidos,
					nombres=nombres,
					tipo_documento=tipo_documento,
					documento=documento,
					correo=correo,
					grade=grade,
				)
				session.add(student)
				created += 1
			else:
				student.numero_estudiante = numero
				student.apellidos = apellidos
				student.nombres = nombres
				student.tipo_documento = tipo_documento
				student.correo = correo
				student.grade = grade
				updated += 1

			if not student.qr_path:
				student.qr_path = ensure_qr(qr_dir, documento)

		except Exception as exc:
			errors.append({"linea": idx, "error": str(exc)})

	return {
		"creados": created,
		"actualizados": updated,
		"omitidos": skipped,
		"errores": errors,
	}

import csv
from io import TextIOWrapper
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Grade, Student
from qr import ensure_qr


EXPECTED_HEADERS = [
	"numero",
	"primer_apellido",
	"segundo_apellido",
	"primer_nombre",
	"segundo_nombre",
	"tipo_documento",
	"documento",
	"correo",
	"telefono_acudiente",
	"telegram_id",
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
	
	# Leer una muestra para detectar el delimitador
	sample = text_stream.read(1024)
	text_stream.seek(0)
	
	# Detectar delimitador automáticamente (coma o punto y coma)
	try:
		sniffer = csv.Sniffer()
		delimiter = sniffer.sniff(sample).delimiter
	except:
		# Si falla la detección, usar punto y coma por defecto
		delimiter = ';'
	
	reader = csv.DictReader(text_stream, delimiter=delimiter)

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
	grades_seen: set[int] = set()
	errors: list[dict] = []

	for idx, row in enumerate(reader, start=2):
		try:
			numero = int((row.get("numero") or "").strip())
			primer_apellido = (row.get("primer_apellido") or "").strip()
			segundo_apellido = (row.get("segundo_apellido") or "").strip() or None
			primer_nombre = (row.get("primer_nombre") or "").strip()
			segundo_nombre = (row.get("segundo_nombre") or "").strip() or None
			tipo_documento = _normalize_tipo((row.get("tipo_documento") or "").strip())
			documento = (row.get("documento") or "").strip()
			correo = (row.get("correo") or "").strip() or None
			telefono = (row.get("telefono_acudiente") or "").strip() or None
			telegram_id = (row.get("telegram_id") or "").strip() or None
			grado = int((row.get("grado") or "").strip())

			if not (primer_apellido and primer_nombre and documento and tipo_documento):
				skipped += 1
				continue

			grade = _get_or_create_grade(session, grado)
			grades_seen.add(grado)
			student = session.scalar(
				select(Student).where(Student.documento == documento)
			)

			if student is None:
				student = Student(
					numero_estudiante=numero,
					primer_apellido=primer_apellido,
					segundo_apellido=segundo_apellido,
					primer_nombre=primer_nombre,
					segundo_nombre=segundo_nombre,
					tipo_documento=tipo_documento,
					documento=documento,
					correo=correo,
					telefono_acudiente=telefono,
					telegram_id=telegram_id,
					grade=grade,
				)
				session.add(student)
				created += 1
			else:
				student.numero_estudiante = numero
				student.primer_apellido = primer_apellido
				student.segundo_apellido = segundo_apellido
				student.primer_nombre = primer_nombre
				student.segundo_nombre = segundo_nombre
				student.tipo_documento = tipo_documento
				student.correo = correo
				student.telefono_acudiente = telefono
				student.telegram_id = telegram_id
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
		"grados": sorted(grades_seen),
	}

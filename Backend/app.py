import csv
import io
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Settings
from db import db_healthcheck, get_session, init_db
from scheduler import start_scheduler
from attendance import register_checkin
from importer import import_students
from models import Student, UploadLog
from qr import ensure_qr, render_qr_with_name
from sqlalchemy import select, desc


load_dotenv(Path(__file__).resolve().parent / ".env")


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    init_db()
    settings = Settings()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or os.environ.get("FLASK_RUN_FROM_CLI") != "true":
        start_scheduler()

    @app.get("/health")
    def health() -> tuple[dict, int]:
        db_status = db_healthcheck()
        status_code = 200 if db_status == "ok" else 503
        return {"status": "ok", "db": db_status}, status_code

    @app.get("/students/template")
    def download_template() -> Response:
        headers = [
            "numero",
            "apellidos",
            "nombres",
            "tipo_documento",
            "documento",
            "correo",
            "telefono_acudiente",
            "telegram_id",
            "grado",
        ]
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        content = output.getvalue()
        response = Response(content, mimetype="text/csv")
        response.headers["Content-Disposition"] = (
            "attachment; filename=estudiantes_template.csv"
        )
        return response

    @app.get("/students/<int:student_id>/qr")
    def download_student_qr(student_id: int):
        settings = Settings()
        settings.qr_dir.mkdir(parents=True, exist_ok=True)

        with get_session() as session:
            student = session.scalar(
                select(Student).where(Student.id == student_id)
            )
            if student is None:
                return {"error": "Estudiante no encontrado"}, 404

            if not student.qr_path:
                student.qr_path = ensure_qr(settings.qr_dir, student.documento)

            qr_path = Path(student.qr_path)
            if not qr_path.exists():
                student.qr_path = ensure_qr(settings.qr_dir, student.documento)
                qr_path = Path(student.qr_path)

            full_name = f"{student.apellidos} {student.nombres}".strip()
            image_stream = render_qr_with_name(qr_path, full_name)

        filename = f"qr_{student_id}.png"
        return send_file(
            image_stream,
            mimetype="image/png",
            as_attachment=True,
            download_name=filename,
        )

    @app.post("/students/import")
    def import_students_from_csv() -> tuple[dict, int]:
        if "file" not in request.files:
            return {"error": "Archivo CSV requerido"}, 400
        file = request.files["file"]
        if not file.filename:
            return {"error": "Nombre de archivo invalido"}, 400

        settings = Settings()
        settings.qr_dir.mkdir(parents=True, exist_ok=True)
        settings.uploads_dir.mkdir(parents=True, exist_ok=True)

        safe_name = secure_filename(file.filename) or "estudiantes.csv"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        stored_name = f"{timestamp}_{safe_name}"
        stored_path = settings.uploads_dir / stored_name
        file.save(stored_path)

        with get_session() as session:
            with open(stored_path, "rb") as stream:
                result = import_students(stream, session, settings.qr_dir)
            grades = result.get("grados", [])
            grades_label = ",".join(str(g) for g in grades)
            log = UploadLog(
                filename=safe_name,
                stored_path=str(stored_path),
                grados=grades_label,
                created_count=result.get("creados", 0),
                updated_count=result.get("actualizados", 0),
                skipped_count=result.get("omitidos", 0),
                errors_count=len(result.get("errores", [])),
            )
            session.add(log)
        return result, 200

    @app.get("/uploads/history")
    def upload_history() -> tuple[dict, int]:
        with get_session() as session:
            logs = session.scalars(
                select(UploadLog).order_by(desc(UploadLog.id))
            ).all()
            data = [
                {
                    "id": log.id,
                    "archivo": log.filename,
                    "ruta": log.stored_path,
                    "grados": log.grados,
                    "creados": log.created_count,
                    "actualizados": log.updated_count,
                    "omitidos": log.skipped_count,
                    "errores": log.errors_count,
                    "fecha": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ]
        return {"historial": data}, 200

    @app.post("/attendance/check-in")
    def attendance_check_in() -> tuple[dict, int]:
        payload = request.get_json(silent=True) or {}
        documento = (payload.get("documento") or "").strip()
        if not documento:
            return {"error": "Documento requerido"}, 400

        with get_session() as session:
            result = register_checkin(session, documento)
        if "error" in result:
            return result, 404
        return result, 200

    @app.post("/test/send-alerts")
    def test_send_alerts() -> tuple[dict, int]:
        """Endpoint de prueba para enviar notificaciones ahora (sin esperar 7:10 AM)"""
        from notifications import send_absence_alerts
        try:
            with get_session() as session:
                result = send_absence_alerts(session, settings)
                session.commit()
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    env = os.getenv("APP_ENV", "development").lower()
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=env == "development")

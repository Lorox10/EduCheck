import csv
import io
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Settings
from db import db_healthcheck, get_session, init_db
from importer import import_students
from models import UploadLog
from sqlalchemy import select, desc


load_dotenv(Path(__file__).resolve().parent / ".env")


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    init_db()

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

    return app


if __name__ == "__main__":
    app = create_app()
    env = os.getenv("APP_ENV", "development").lower()
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=env == "development")

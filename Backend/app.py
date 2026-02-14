import csv
import io
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from config import Settings
from db import db_healthcheck, get_session, init_db
from importer import import_students


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

        with get_session() as session:
            result = import_students(file.stream, session, settings.qr_dir)
        return result, 200

    return app


if __name__ == "__main__":
    app = create_app()
    env = os.getenv("APP_ENV", "development").lower()
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=env == "development")

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
    # Configurar CORS simple para desarrollo
    CORS(app, origins="*", methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"], 
         allow_headers=["Content-Type", "Authorization"])

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
        """Descarga plantilla CSV vacía con encabezados"""
        headers = [
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
        
        output = io.StringIO()
        # Usar punto y coma como delimitador para Excel en español
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        
        content = output.getvalue()
        
        # Agregar BOM UTF-8 para que Excel reconozca caracteres especiales
        content_with_bom = '\ufeff' + content
        
        response = Response(content_with_bom, mimetype="text/csv; charset=utf-8")
        response.headers["Content-Disposition"] = (
            "attachment; filename=estudiantes_plantilla.csv"
        )
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        return response

    @app.get("/students")
    def list_students() -> tuple[dict, int]:
        """Lista todos los estudiantes"""
        with get_session() as session:
            students = session.scalars(select(Student).order_by(Student.id)).all()
            data = [
                {
                    "id": s.id,
                    "numero_estudiante": s.numero_estudiante,
                    "primer_apellido": s.primer_apellido,
                    "segundo_apellido": s.segundo_apellido,
                    "primer_nombre": s.primer_nombre,
                    "segundo_nombre": s.segundo_nombre,
                    "documento": s.documento,
                    "grado": s.grade.numero,
                    "telefono_acudiente": s.telefono_acudiente,
                    "telegram_id": s.telegram_id,
                }
                for s in students
            ]
        return {"estudiantes": data, "total": len(data)}, 200

    @app.patch("/students/<int:student_id>/telegram")
    def update_telegram_id(student_id: int) -> tuple[dict, int]:
        """Actualiza el telegram_id de un estudiante"""
        payload = request.get_json(silent=True) or {}
        telegram_id = payload.get("telegram_id", "").strip()
        
        with get_session() as session:
            student = session.scalar(select(Student).where(Student.id == student_id))
            if student is None:
                return {"error": "Estudiante no encontrado"}, 404
            
            student.telegram_id = telegram_id if telegram_id else None
            session.commit()
            
        return {
            "id": student_id,
            "telegram_id": telegram_id,
            "mensaje": "Telegram ID actualizado"
        }, 200

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

            parts = [student.primer_apellido, student.segundo_apellido or "", 
                     student.primer_nombre, student.segundo_nombre or ""]
            full_name = " ".join(p for p in parts if p).strip()
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
        print(f"[ATTENDANCE] Raw payload: {payload}")
        print(f"[ATTENDANCE] Request headers: {dict(request.headers)}")
        documento = (payload.get("documento") or "").strip()
        print(f"[ATTENDANCE] Documento after strip: '{documento}'")
        if not documento:
            print(f"[ATTENDANCE] Error: documento vacío o no proporcionado")
            return {"error": "Documento requerido"}, 400

        print(f"[ATTENDANCE] Procesando documento: {documento}")
        with get_session() as session:
            result = register_checkin(session, documento)
        print(f"[ATTENDANCE] Resultado del registro: {result}")
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

    @app.get("/telegram/updates")
    def get_telegram_updates() -> tuple[dict, int]:
        """Obtiene los últimos mensajes del bot para ver el chat_id de usuarios"""
        import requests
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{settings.telegram_token}/getUpdates",
                timeout=10
            )
            response.raise_for_status()
            return response.json(), 200
        except Exception as e:
            return {"error": str(e)}, 500

    @app.delete("/test/clear-attendance")
    def clear_today_attendance() -> tuple[dict, int]:
        """Borra todos los registros de asistencia de hoy para testing"""
        from datetime import date
        from models import Attendance, NotificationLog
        try:
            with get_session() as session:
                # Borrar logs de notificación primero (por foreign key)
                session.query(NotificationLog).filter(
                    NotificationLog.fecha == date.today()
                ).delete()
                
                # Luego borrar asistencias
                deleted = session.query(Attendance).filter(
                    Attendance.fecha == date.today()
                ).delete()
                session.commit()
            return {"eliminados": deleted}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    env = os.getenv("APP_ENV", "development").lower()
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=env == "development")

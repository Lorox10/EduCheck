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
from models import Student, UploadLog, Attendance, Grade, ClassDays
from qr import ensure_qr, render_qr_with_name
from monthly_reports import generate_monthly_report, get_available_reports, REPORTS_DIR
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

    @app.get("/attendance/today")
    def get_attendance_today() -> tuple[dict, int]:
        """Obtiene estadísticas de asistencia de hoy"""
        from datetime import date
        try:
            with get_session() as session:
                today = date.today()
                
                # Contar presentes hoy
                presente_count = session.query(Attendance).filter(
                    Attendance.fecha == today
                ).count()
                
                # Contar total de estudiantes
                total_students = session.query(Student).count()
                
                # Ausentes = Total - Presentes
                ausente_count = total_students - presente_count
                
                # Obtener grados con asistencia registrada hoy
                grados_con_asistencia = session.query(Grade.numero).join(
                    Student, Student.grade_id == Grade.id
                ).join(
                    Attendance, Attendance.student_id == Student.id
                ).filter(
                    Attendance.fecha == today
                ).distinct().all()
                
                grados = sorted([g[0] for g in grados_con_asistencia])
                
                return {
                    "presente": presente_count,
                    "ausente": ausente_count,
                    "total": total_students,
                    "fecha": today.isoformat(),
                    "grados": grados
                }, 200
        except Exception as e:
            print(f"[ATTENDANCE] Error en get_attendance_today: {str(e)}")
            return {"error": str(e), "presente": 0, "ausente": 0, "total": 0, "grados": []}, 500

    @app.get("/attendance/<int:grado>")
    def get_attendance_by_grade(grado: int) -> tuple[dict, int]:
        """Obtiene estadísticas de asistencia de hoy por grado"""
        from datetime import date
        try:
            with get_session() as session:
                today = date.today()
                
                # Obtener el grado
                grade = session.query(Grade).filter(Grade.numero == grado).first()
                if not grade:
                    return {"error": f"Grado {grado} no encontrado"}, 404
                
                # Contar presentes del grado hoy
                presente_count = session.query(Attendance).join(
                    Student, Attendance.student_id == Student.id
                ).filter(
                    Attendance.fecha == today,
                    Student.grade_id == grade.id
                ).count()
                
                # Contar total de estudiantes del grado
                total_students = session.query(Student).filter(
                    Student.grade_id == grade.id
                ).count()
                
                # Ausentes del grado
                ausente_count = total_students - presente_count
                
                return {
                    "presente": presente_count,
                    "ausente": ausente_count,
                    "total": total_students,
                    "grado": grado,
                    "fecha": today.isoformat()
                }, 200
        except Exception as e:
            print(f"[ATTENDANCE] Error en get_attendance_by_grade: {str(e)}")
            return {"error": str(e)}, 500

    @app.get("/attendance/absences")
    def get_absence_history() -> tuple[dict, int]:
        """Obtiene histórico de ausencias de los últimos 7 días según días de clase configurados"""
        from datetime import date, timedelta, datetime
        try:
            with get_session() as session:
                today = date.today()
                week_ago = today - timedelta(days=7)
                
                # Obtener configuración de días de clase
                class_days_config = session.query(ClassDays).first()
                if not class_days_config:
                    # Si no existe, crear configuración por defecto
                    class_days_config = ClassDays()
                    session.add(class_days_config)
                    session.commit()
                
                # Mapeo de día de semana (0=lunes, 6=domingo)
                dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
                dias_config = {
                    0: class_days_config.lunes,
                    1: class_days_config.martes,
                    2: class_days_config.miercoles,
                    3: class_days_config.jueves,
                    4: class_days_config.viernes,
                    5: class_days_config.sabado,
                    6: class_days_config.domingo,
                }
                
                # Contar días de clase en los últimos 7 días
                dias_clase = 0
                for i in range(8):
                    check_date = today - timedelta(days=i)
                    if check_date >= week_ago:
                        dia_semana = check_date.weekday()
                        if dias_config[dia_semana]:
                            dias_clase += 1
                
                # Obtener todos los estudiantes
                students = session.query(Student).all()
                
                records = []
                for student in students:
                    # Contar asistencias reales en los últimos 7 días
                    asistencias_reales = session.query(Attendance).filter(
                        Attendance.student_id == student.id,
                        Attendance.fecha >= week_ago,
                        Attendance.fecha <= today
                    ).count()
                    
                    # Ausencias = días de clase - asistencias reales
                    ausencias_reales = dias_clase - asistencias_reales
                    
                    # Obtener las fechas de las últimas faltas (dentro de días de clase)
                    ultimas_faltas = []
                    for i in range(8):
                        check_date = today - timedelta(days=i)
                        if check_date >= week_ago:
                            dia_semana = check_date.weekday()
                            if dias_config[dia_semana]:  # Solo si es día de clase
                                if not session.query(Attendance).filter(
                                    Attendance.student_id == student.id,
                                    Attendance.fecha == check_date
                                ).first():
                                    ultimas_faltas.append(check_date.strftime('%d/%m/%Y'))
                    
                    records.append({
                        "id": student.id,
                        "primer_apellido": student.primer_apellido,
                        "segundo_apellido": student.segundo_apellido,
                        "primer_nombre": student.primer_nombre,
                        "segundo_nombre": student.segundo_nombre,
                        "grado": student.grade.numero,
                        "documento": student.documento,
                        "ausencias": max(0, ausencias_reales),  # No mostrar negativos
                        "ultimas_faltas": ultimas_faltas[:5]  # Mostrar últimas 5 faltas
                    })
                
                return {"records": records, "dias_clase": dias_clase}, 200
        except Exception as e:
            print(f"[ATTENDANCE] Error en get_absence_history: {str(e)}")
            return {"error": str(e)}, 500

    @app.get("/class-days")
    def get_class_days() -> tuple[dict, int]:
        """Obtiene configuración de días de clase"""
        try:
            with get_session() as session:
                class_days = session.query(ClassDays).first()
                if not class_days:
                    # Crear configuración por defecto
                    class_days = ClassDays()
                    session.add(class_days)
                    session.commit()
                
                return {
                    "lunes": class_days.lunes,
                    "martes": class_days.martes,
                    "miercoles": class_days.miercoles,
                    "jueves": class_days.jueves,
                    "viernes": class_days.viernes,
                    "sabado": class_days.sabado,
                    "domingo": class_days.domingo,
                }, 200
        except Exception as e:
            print(f"[CLASS_DAYS] Error en get_class_days: {str(e)}")
            return {"error": str(e)}, 500

    @app.post("/class-days")
    def update_class_days() -> tuple[dict, int]:
        """Actualiza configuración de días de clase"""
        try:
            data = request.get_json()
            with get_session() as session:
                class_days = session.query(ClassDays).first()
                if not class_days:
                    class_days = ClassDays()
                    session.add(class_days)
                
                # Actualizar los días
                if "lunes" in data:
                    class_days.lunes = data["lunes"]
                if "martes" in data:
                    class_days.martes = data["martes"]
                if "miercoles" in data:
                    class_days.miercoles = data["miercoles"]
                if "jueves" in data:
                    class_days.jueves = data["jueves"]
                if "viernes" in data:
                    class_days.viernes = data["viernes"]
                if "sabado" in data:
                    class_days.sabado = data["sabado"]
                if "domingo" in data:
                    class_days.domingo = data["domingo"]
                
                session.commit()
                return {
                    "message": "Configuración actualizada",
                    "lunes": class_days.lunes,
                    "martes": class_days.martes,
                    "miercoles": class_days.miercoles,
                    "jueves": class_days.jueves,
                    "viernes": class_days.viernes,
                    "sabado": class_days.sabado,
                    "domingo": class_days.domingo,
                }, 200
        except Exception as e:
            print(f"[CLASS_DAYS] Error en update_class_days: {str(e)}")
            return {"error": str(e)}, 500

    @app.get("/monthly-reports")
    def get_monthly_reports() -> tuple[dict, int]:
        """Obtiene lista de reportes mensuales disponibles"""
        try:
            reports = get_available_reports()
            return {"reports": reports}, 200
        except Exception as e:
            print(f"[MONTHLY_REPORTS] Error en get_monthly_reports: {str(e)}")
            return {"error": str(e)}, 500

    @app.post("/monthly-reports/generate")
    def post_generate_monthly_report() -> tuple[dict, int]:
        """Genera manualmente un reporte mensual"""
        try:
            filepath = generate_monthly_report()
            if filepath:
                return {"message": "Reporte generado exitosamente", "file": Path(filepath).name}, 200
            else:
                return {"error": "No hay datos de inasistentes para generar reporte"}, 400
        except Exception as e:
            print(f"[MONTHLY_REPORTS] Error en generate_monthly_report: {str(e)}")
            return {"error": str(e)}, 500

    @app.get("/monthly-reports/<filename>")
    def download_monthly_report(filename: str) -> Response:
        """Descarga un reporte mensual específico"""
        try:
            # Validar que el filename tenga el formato correcto
            if not filename.startswith("inasistentes_") or not filename.endswith(".pdf"):
                return {"error": "Archivo inválido"}, 400
            
            filepath = REPORTS_DIR / filename
            if not filepath.exists():
                return {"error": "Archivo no encontrado"}, 404
            
            return send_file(str(filepath), as_attachment=True, download_name=filename)
        except Exception as e:
            print(f"[MONTHLY_REPORTS] Error en download_monthly_report: {str(e)}")
            return {"error": str(e)}, 500

    @app.get("/reports/pdf")
    def download_attendance_pdf() -> Response:
        """Genera y descarga un PDF con las estadísticas de asistencia"""
        from datetime import date
        
        try:
            with get_session() as session:
                today = date.today()
                
                # Obtener estadísticas
                presente_count = session.query(Attendance).filter(
                    Attendance.fecha == today
                ).count()
                
                total_students = session.query(Student).count()
                ausente_count = total_students - presente_count
                percentage = (presente_count / total_students * 100) if total_students > 0 else 0
                
                # Crear contenido HTML simple que se descargue como PDF
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Reporte de Asistencia</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        h1 {{ color: #667eea; text-align: center; }}
                        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                        th {{ background-color: #667eea; color: white; }}
                        tr:nth-child(even) {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h1>📊 Reporte de Asistencia</h1>
                    <p><strong>Fecha:</strong> {today.strftime('%d/%m/%Y')}</p>
                    <table>
                        <tr>
                            <th>Métrica</th>
                            <th>Cantidad</th>
                        </tr>
                        <tr>
                            <td>Total de Estudiantes</td>
                            <td>{total_students}</td>
                        </tr>
                        <tr>
                            <td>Presentes</td>
                            <td>{presente_count}</td>
                        </tr>
                        <tr>
                            <td>Ausentes</td>
                            <td>{ausente_count}</td>
                        </tr>
                        <tr>
                            <td>Porcentaje Asistencia</td>
                            <td>{percentage:.1f}%</td>
                        </tr>
                    </table>
                </body>
                </html>
                """
                
                response = Response(html_content, mimetype='text/html')
                response.headers['Content-Disposition'] = f'attachment; filename=asistencia_{today}.html'
                return response
                
        except Exception as e:
            print(f"[REPORTS] Error en download_attendance_pdf: {str(e)}")
            return {"error": str(e)}, 500

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

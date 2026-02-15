from datetime import date, datetime, timedelta
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from sqlalchemy import and_
from db import get_session
from models import Student, Attendance, Grade


REPORTS_DIR = Path(__file__).parent / "monthly_reports"
REPORTS_DIR.mkdir(exist_ok=True)


def get_month_absent_students() -> dict:
    """
    Obtiene todos los estudiantes inasistentes del mes actual
    Retorna un diccionario con el formato: {grado: [estudiantes_inasistentes]}
    """
    try:
        with get_session() as session:
            today = date.today()
            month_start = date(today.year, today.month, 1)
            month_end = date(today.year, today.month, 28)  # Fallback a 28 para febrero
            
            # Ajustar mes_end al último día del mes
            if today.month == 12:
                month_end = date(today.year, today.month, 31)
            else:
                month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
            
            # Obtener todos los grados
            grades = session.query(Grade).order_by(Grade.numero).all()
            
            absent_by_grade = {}
            
            for grade in grades:
                # Obtener todos los estudiantes del grado
                students = session.query(Student).filter(
                    Student.grade_id == grade.id
                ).order_by(Student.primer_apellido, Student.segundo_apellido).all()
                
                if not students:
                    continue
                
                absent_students = []
                
                for student in students:
                    # Contar días de clase en el mes
                    # Para esto necesitamos verificar si el estudiante asistió esos días
                    # Primero, obtener todos los días únicos con asistencias en el mes
                    attendance_days = session.query(Attendance.fecha).filter(
                        and_(
                            Attendance.fecha >= month_start,
                            Attendance.fecha <= month_end
                        )
                    ).distinct().all()
                    
                    # Convertir a lista de fechas
                    dias_clase = [day[0] for day in attendance_days]
                    
                    # Contar asistencias del estudiante
                    student_attendance = session.query(Attendance).filter(
                        and_(
                            Attendance.student_id == student.id,
                            Attendance.fecha >= month_start,
                            Attendance.fecha <= month_end
                        )
                    ).count()
                    
                    # Calcular ausencias
                    dias_esperados = len(dias_clase)
                    ausencias = dias_esperados - student_attendance
                    
                    # Si tiene ausencias, agregarlo a la lista
                    if ausencias > 0:
                        full_name = f"{student.primer_apellido} {student.segundo_apellido or ''} {student.primer_nombre} {student.segundo_nombre or ''}".strip()
                        absent_students.append({
                            "nombre": full_name,
                            "documento": student.documento,
                            "ausencias": ausencias,
                            "total_dias": dias_esperados
                        })
                
                if absent_students:
                    absent_by_grade[grade.numero] = absent_students
            
            return absent_by_grade
    except Exception as e:
        print(f"[MONTHLY_REPORTS] Error en get_month_absent_students: {str(e)}")
        return {}


def generate_monthly_report() -> str | None:
    """
    Genera un PDF con los inasistentes del mes actual
    Retorna la ruta del archivo generado
    """
    try:
        today = date.today()
        absent_data = get_month_absent_students()
        
        if not absent_data:
            print("[MONTHLY_REPORTS] No hay inasistentes para reportar")
            return None
        
        # Crear nombre del archivo
        filename = f"inasistentes_{today.year:04d}_{today.month:02d}.pdf"
        filepath = REPORTS_DIR / filename
        
        # Crear documento PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#666666'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        grade_style = ParagraphStyle(
            'GradeTitle',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        # Título principal
        title = Paragraph(f"Reporte de Inasistentes - {today.strftime('%B %Y').capitalize()}", title_style)
        story.append(title)
        
        subtitle = Paragraph(
            f"Generado el {today.strftime('%d de %B de %Y')}",
            subtitle_style
        )
        story.append(subtitle)
        story.append(Spacer(1, 0.3*inch))
        
        # Por cada grado
        for grade_number in sorted(absent_data.keys()):
            students = absent_data[grade_number]
            
            # Título del grado
            grade_title = Paragraph(f"Grado {grade_number} - {len(students)} Inasistentes", grade_style)
            story.append(grade_title)
            
            # Tabla de estudiantes
            table_data = [
                ['Nombre Completo', 'Identificación', 'Ausencias']
            ]
            
            for student in students:
                table_data.append([
                    student['nombre'],
                    student['documento'],
                    f"{student['ausencias']} de {student['total_dias']}"
                ])
            
            table = Table(table_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                # Datos
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.4*inch))
        
        # Generar PDF
        doc.build(story)
        print(f"[MONTHLY_REPORTS] PDF generado: {filepath}")
        return str(filepath)
    
    except Exception as e:
        print(f"[MONTHLY_REPORTS] Error generando reporte: {str(e)}")
        return None


def get_available_reports() -> list[dict]:
    """
    Obtiene lista de reportes mensuales disponibles
    """
    try:
        reports = []
        if REPORTS_DIR.exists():
            for pdf_file in sorted(REPORTS_DIR.glob("inasistentes_*.pdf"), reverse=True):
                file_stat = pdf_file.stat()
                # Extraer año y mes del nombre del archivo
                parts = pdf_file.stem.split('_')
                if len(parts) >= 3:
                    year = int(parts[1])
                    month = int(parts[2])
                    month_name = date(year, month, 1).strftime('%B %Y').capitalize()
                    
                    reports.append({
                        "filename": pdf_file.name,
                        "date": f"{year}-{month:02d}",
                        "month_name": month_name,
                        "size": file_stat.st_size,
                        "created": file_stat.st_mtime
                    })
        return reports
    except Exception as e:
        print(f"[MONTHLY_REPORTS] Error obteniendo reportes: {str(e)}")
        return []

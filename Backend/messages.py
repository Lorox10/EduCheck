"""
Plantillas de mensajes para notificaciones.
Personaliza aquí los mensajes que reciben los acudientes.
"""


def build_entry_message(student, hora: str) -> str:
    """
    Construye el mensaje cuando el estudiante registra entrada (QR).
    
    Args:
        student: Objeto Student con datos
        hora: Hora en formato HH:MM
        
    Returns:
        Mensaje para el acudiente
    """
    # Construir nombre completo desde 4 campos separados
    name_parts = [student.primer_apellido]
    if student.segundo_apellido:
        name_parts.append(student.segundo_apellido)
    name_parts.append(student.primer_nombre)
    if student.segundo_nombre:
        name_parts.append(student.segundo_nombre)
    full_name = " ".join(name_parts)
    
    return (
        f"✅ Edu Check - Entrada Registrada\n\n"
        f"{full_name} con cédula {student.documento} "
        f"del grado {student.grade.numero} "
        f"registró su entrada a las {hora}."
    )


def build_absence_message(student, hora: str) -> str:
    """
    Construye el mensaje de ausencia (cuando NO registra entrada).
    
    Args:
        student: Objeto Student con datos
        hora: Hora límite en formato HH:MM (ej: 07:10)
        
    Returns:
        Mensaje para el acudiente
    """
    # Construir nombre completo desde 4 campos separados
    name_parts = [student.primer_apellido]
    if student.segundo_apellido:
        name_parts.append(student.segundo_apellido)
    name_parts.append(student.primer_nombre)
    if student.segundo_nombre:
        name_parts.append(student.segundo_nombre)
    full_name = " ".join(name_parts)
    
    return (
        f"⚠️ Edu Check - Reporte de Ausencia\n\n"
        f"{full_name} con cédula {student.documento} "
        f"del grado {student.grade.numero} "
        f"no ha registrado entrada hasta las {hora}."
    )

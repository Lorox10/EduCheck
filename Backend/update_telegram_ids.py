"""
Actualizar telegram_id de estudiantes con el User ID real
"""
from db import get_session
from sqlalchemy import update
from models import Student

TELEGRAM_USER_ID = "5936924064"

print("\n=== Actualizando telegram_id de estudiantes ===\n")

with get_session() as session:
    # Actualizar todos los estudiantes
    result = session.execute(
        update(Student).values(telegram_id=TELEGRAM_USER_ID)
    )
    session.commit()
    
    print(f"✅ {result.rowcount} estudiantes actualizados")
    print(f"   Nuevo telegram_id para todos: {TELEGRAM_USER_ID}\n")

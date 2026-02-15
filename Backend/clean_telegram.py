"""
Script para limpiar telegram_id de prueba de la base de datos
"""
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text, create_engine
from config import Settings

load_dotenv(Path(__file__).resolve().parent / ".env")

def clean_telegram_ids():
    settings = Settings()
    db_url = (
        "mysql+mysqlconnector://"
        f"{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )
    
    engine = create_engine(db_url, pool_pre_ping=True)
    
    with engine.connect() as conn:
        # Solo mantener los telegram_id de los estudiantes ID 11 y 12 (los reales)
        # Limpiar el resto
        print("Limpiando telegram_id de prueba...")
        
        result = conn.execute(text("""
            UPDATE students 
            SET telegram_id = NULL 
            WHERE id NOT IN (11, 12)
            AND telegram_id IS NOT NULL
        """))
        conn.commit()
        
        print(f"✅ {result.rowcount} registros limpiados")
        
        # Mostrar los que quedaron
        remaining = conn.execute(text("""
            SELECT id, primer_nombre, primer_apellido, telegram_id 
            FROM students 
            WHERE telegram_id IS NOT NULL
        """))
        
        print("\nTelegram IDs que permanecen:")
        for row in remaining:
            print(f"  ID {row[0]}: {row[1]} {row[2]} -> {row[3]}")

if __name__ == "__main__":
    try:
        clean_telegram_ids()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

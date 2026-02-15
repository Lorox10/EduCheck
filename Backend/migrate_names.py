"""
Script de migración para separar apellidos y nombres en campos individuales
"""
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text, create_engine
from config import Settings

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent / ".env")

def migrate():
    settings = Settings()
    db_url = (
        "mysql+mysqlconnector://"
        f"{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )
    
    engine = create_engine(db_url, pool_pre_ping=True)
    
    with engine.connect() as conn:
        # Verificar si ya existe la nueva estructura
        result = conn.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'students' 
            AND COLUMN_NAME = 'primer_apellido'
        """))
        
        if result.fetchone() is not None:
            print("✓ Las columnas ya están migradas")
            return
        
        print("Iniciando migración de estructura de nombres...")
        
        # 1. Agregar nuevas columnas
        print("1. Agregando nuevas columnas...")
        conn.execute(text("""
            ALTER TABLE students
            ADD COLUMN primer_apellido VARCHAR(50) AFTER numero_estudiante,
            ADD COLUMN segundo_apellido VARCHAR(50) AFTER primer_apellido,
            ADD COLUMN primer_nombre VARCHAR(50) AFTER segundo_apellido,
            ADD COLUMN segundo_nombre VARCHAR(50) AFTER primer_nombre
        """))
        conn.commit()
        
        # 2. Migrar datos existentes (separar nombres y apellidos)
        print("2. Migrando datos existentes...")
        conn.execute(text("""
            UPDATE students
            SET primer_apellido = TRIM(SUBSTRING_INDEX(apellidos, ' ', 1)),
                segundo_apellido = NULLIF(TRIM(SUBSTRING_INDEX(apellidos, ' ', -1)), TRIM(SUBSTRING_INDEX(apellidos, ' ', 1))),
                primer_nombre = TRIM(SUBSTRING_INDEX(nombres, ' ', 1)),
                segundo_nombre = NULLIF(TRIM(SUBSTRING_INDEX(nombres, ' ', -1)), TRIM(SUBSTRING_INDEX(nombres, ' ', 1)))
            WHERE apellidos IS NOT NULL AND nombres IS NOT NULL
        """))
        conn.commit()
        
        # 3. Hacer las nuevas columnas NOT NULL (excepto segundo_apellido y segundo_nombre)
        print("3. Aplicando restricciones NOT NULL...")
        conn.execute(text("""
            ALTER TABLE students
            MODIFY COLUMN primer_apellido VARCHAR(50) NOT NULL,
            MODIFY COLUMN primer_nombre VARCHAR(50) NOT NULL
        """))
        conn.commit()
        
        # 4. Eliminar columnas antiguas
        print("4. Eliminando columnas antiguas...")
        conn.execute(text("""
            ALTER TABLE students
            DROP COLUMN apellidos,
            DROP COLUMN nombres
        """))
        conn.commit()
        
        print("✅ Migración completada exitosamente")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()

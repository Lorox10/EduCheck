"""
Script para resetear completamente la base de datos y archivos QR
"""
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text, create_engine
from config import Settings
import shutil

load_dotenv(Path(__file__).resolve().parent / ".env")

def reset_all():
    settings = Settings()
    db_url = (
        "mysql+mysqlconnector://"
        f"{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )
    
    engine = create_engine(db_url, pool_pre_ping=True)
    
    print("🔄 Iniciando reseteo completo...")
    
    with engine.connect() as conn:
        # 1. Eliminar registros de notificaciones (depende de students)
        print("\n1️⃣ Eliminando notificaciones...")
        result = conn.execute(text("DELETE FROM notification_logs"))
        print(f"   ✅ {result.rowcount} notificaciones eliminadas")
        
        # 2. Eliminar registros de asistencia (depende de students)
        print("\n2️⃣ Eliminando registros de asistencia...")
        result = conn.execute(text("DELETE FROM attendance"))
        print(f"   ✅ {result.rowcount} asistencias eliminadas")
        
        # 3. Eliminar estudiantes
        print("\n3️⃣ Eliminando estudiantes...")
        result = conn.execute(text("DELETE FROM students"))
        print(f"   ✅ {result.rowcount} estudiantes eliminados")
        
        # 4. Eliminar grados
        print("\n4️⃣ Eliminando grados...")
        result = conn.execute(text("DELETE FROM grades"))
        print(f"   ✅ {result.rowcount} grados eliminados")
        
        # 5. Eliminar historial de uploads
        print("\n5️⃣ Eliminando historial de importaciones...")
        result = conn.execute(text("DELETE FROM upload_logs"))
        print(f"   ✅ {result.rowcount} registros de upload eliminados")
        
        conn.commit()
    
    # 6. Eliminar archivos QR
    print("\n6️⃣ Eliminando archivos QR...")
    qr_dir = settings.qr_dir
    if qr_dir.exists():
        qr_files = list(qr_dir.glob("*.png"))
        for qr_file in qr_files:
            qr_file.unlink()
        print(f"   ✅ {len(qr_files)} archivos QR eliminados")
    else:
        print("   ℹ️  Directorio QR no existe")
    
    # 7. Eliminar archivos CSV de uploads
    print("\n7️⃣ Eliminando archivos CSV de uploads...")
    uploads_dir = settings.uploads_dir
    if uploads_dir.exists():
        csv_files = list(uploads_dir.glob("*.csv"))
        for csv_file in csv_files:
            csv_file.unlink()
        print(f"   ✅ {len(csv_files)} archivos CSV eliminados")
    else:
        print("   ℹ️  Directorio uploads no existe")
    
    print("\n" + "="*50)
    print("✅ RESETEO COMPLETO EXITOSO")
    print("="*50)
    print("\nLa base de datos está limpia y lista para empezar de nuevo.")
    print("Puedes importar nuevos estudiantes desde el módulo CSV.")

if __name__ == "__main__":
    import sys
    
    print("\n" + "⚠️ " * 20)
    print("ADVERTENCIA: Esto eliminará TODOS los datos:")
    print("  - Todos los estudiantes")
    print("  - Todos los grados")
    print("  - Toda la asistencia registrada")
    print("  - Todas las notificaciones")
    print("  - Todos los archivos QR")
    print("  - Todos los archivos CSV importados")
    print("⚠️ " * 20)
    
    respuesta = input("\n¿Estás seguro de continuar? (escribe 'SI' para confirmar): ")
    
    if respuesta.strip().upper() == "SI":
        try:
            reset_all()
        except Exception as e:
            print(f"\n❌ Error durante el reseteo: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n❌ Operación cancelada")

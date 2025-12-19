"""
Script para crear el primer usuario administrador

Uso:
    python create_admin.py
"""

import sys
from app.services.azure_sql_service import AzureSQLService
from app.services.auth_service import get_password_hash

def create_admin():
    """Crea un usuario administrador"""
    print("=" * 60)
    print("🔐 CREAR USUARIO ADMINISTRADOR")
    print("=" * 60)
    print()
    
    sql_service = AzureSQLService()
    
    if not sql_service.Session:
        print("❌ Error: No se pudo conectar a la base de datos")
        print("   Verifica que las variables AZURE_SQL_* estén en tu .env")
        sys.exit(1)
    
    # Verificar si ya hay administradores
    try:
        session = sql_service.Session()
        from sqlalchemy import text
        result = session.execute(
            text("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        )
        admin_count = result.scalar()
        session.close()
        
        if admin_count > 0:
            print(f"⚠️  Ya existen {admin_count} administrador(es) en el sistema")
            response = input("¿Deseas crear otro administrador? (s/N): ").strip().lower()
            if response != 's':
                print("Operación cancelada")
                sys.exit(0)
    except Exception as e:
        print(f"⚠️  No se pudo verificar administradores existentes: {str(e)}")
        print("   Continuando con la creación...")
        print()
    
    # Solicitar información
    print("Ingresa la información del administrador:")
    print()
    
    email = input("📧 Email: ").strip()
    if not email or "@" not in email:
        print("❌ Error: Email inválido")
        sys.exit(1)
    
    username = input("👤 Username: ").strip()
    if not username:
        print("❌ Error: Username requerido")
        sys.exit(1)
    
    password = input("🔑 Contraseña: ").strip()
    if len(password) < 6:
        print("❌ Error: La contraseña debe tener al menos 6 caracteres")
        sys.exit(1)
    
    # Validar límite de 72 bytes (límite de bcrypt)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        print("❌ Error: La contraseña no puede tener más de 72 caracteres")
        sys.exit(1)
    
    confirm_password = input("🔑 Confirmar contraseña: ").strip()
    if password != confirm_password:
        print("❌ Error: Las contraseñas no coinciden")
        sys.exit(1)
    
    # Verificar si el email ya existe
    if sql_service.email_exists(email):
        print(f"❌ Error: El email {email} ya está registrado")
        sys.exit(1)
    
    # Verificar si el username ya existe
    if sql_service.username_exists(username):
        print(f"❌ Error: El username {username} ya está en uso")
        sys.exit(1)
    
    # Crear administrador
    print()
    print("🔄 Creando administrador...")
    
    hashed_password = get_password_hash(password)
    user_id = sql_service.create_user(email, username, hashed_password, role="admin")
    
    if user_id:
        print()
        print("=" * 60)
        print("✅ ¡ADMINISTRADOR CREADO EXITOSAMENTE!")
        print("=" * 60)
        print()
        print(f"📧 Email: {email}")
        print(f"👤 Username: {username}")
        print(f"🆔 ID: {user_id}")
        print(f"👑 Rol: admin")
        print()
        print("💡 Ahora puedes iniciar sesión con estas credenciales")
        print()
    else:
        print("❌ Error: No se pudo crear el administrador")
        sys.exit(1)

if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print()
        print("\n⚠️  Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


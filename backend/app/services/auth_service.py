from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings
from app.services.azure_sql_service import AzureSQLService

# Instancia del servicio SQL
sql_service = AzureSQLService()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash usando bcrypt"""
    try:
        # bcrypt.checkpw espera bytes
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña usando bcrypt directamente
    
    Bcrypt tiene un límite de 72 bytes. Validamos antes de hashear.
    """
    # Validar que no exceda 72 bytes (límite de bcrypt)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncar a 72 bytes si excede
        password_bytes = password_bytes[:72]
    
    # Generar salt y hash usando bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Retornar como string (bcrypt retorna bytes)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Autentica un usuario y retorna sus datos si es válido"""
    user = sql_service.get_user_by_email(email)
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    if not user.get("is_active", True):
        return None
    
    # Retornar datos del usuario sin la contraseña
    return {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "role": user.get("role", "user"),
        "created_at": user["created_at"]
    }


def create_user(email: str, username: str, password: str, role: str = "user") -> Optional[dict]:
    """Crea un nuevo usuario"""
    try:
        # Verificar conexión a SQL
        if not sql_service.Session:
            raise ValueError("No hay conexión a la base de datos. Verifica las credenciales de Azure SQL.")
        
        # Verificar si el email ya existe
        if sql_service.email_exists(email):
            raise ValueError("El email ya está registrado")
        
        # Verificar si el username ya existe
        if sql_service.username_exists(username):
            raise ValueError("El username ya está en uso")
        
        # Hash de la contraseña
        try:
            hashed_password = get_password_hash(password)
        except Exception as e:
            print(f"Error hasheando contraseña: {str(e)}")
            raise ValueError(f"Error al procesar la contraseña: {str(e)}")
        
        # Crear usuario
        user_id = sql_service.create_user(email, username, hashed_password, role)
        if not user_id:
            raise ValueError("Error al crear el usuario en la base de datos")
        
        # Obtener el usuario creado
        user = sql_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("Error al obtener el usuario creado")
        
        return {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "role": user.get("role", "user"),
            "created_at": user["created_at"]
        }
    except ValueError:
        # Re-lanzar ValueError sin modificar
        raise
    except Exception as e:
        print(f"Error inesperado en create_user: {str(e)}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Error al crear usuario: {str(e)}")


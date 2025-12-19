from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import verify_token
from app.services.azure_sql_service import AzureSQLService

# OAuth2 scheme para extraer el token del header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
sql_service = AzureSQLService()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependencia para obtener el usuario actual desde el token JWT
    
    Usa esta dependencia en las rutas que requieren autenticación:
    
    @router.post("/endpoint")
    async def my_endpoint(current_user: dict = Depends(get_current_user)):
        user_id = current_user["id"]
        ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = sql_service.get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    
    return {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "role": user.get("role", "user")
    }


async def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependencia que requiere que el usuario sea administrador
    
    Usa esta dependencia en rutas que solo administradores pueden acceder:
    
    @router.post("/admin-only")
    async def admin_endpoint(admin: dict = Depends(require_admin)):
        ...
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    
    return current_user


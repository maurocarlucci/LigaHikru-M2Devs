from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.schemas import SignUpRequest, LoginRequest, Token, User
from app.services.auth_service import authenticate_user, create_user, create_access_token
from app.core.config import settings
from app.core.dependencies import oauth2_scheme

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest):
    """
    Registro de nuevo usuario
    
    - **email**: Email del usuario (debe ser único)
    - **username**: Nombre de usuario (debe ser único)
    - **password**: Contraseña (mínimo 6 caracteres recomendado)
    
    Nota: Todos los usuarios nuevos se crean con rol "user" por defecto.
    Solo un administrador puede crear otros administradores.
    """
    try:
        # Limpiar y validar contraseña
        password = request.password.strip()
        
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 6 caracteres"
            )
        
        # Bcrypt tiene un límite de 72 bytes para las contraseñas
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña no puede tener más de 72 caracteres"
            )
        
        if "@" not in request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )
        
        # Validar username
        username = request.username.strip()
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username es requerido"
            )
        
        if len(username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username debe tener al menos 3 caracteres"
            )
        
        # Crear usuario (siempre como "user", no "admin")
        # Usar la contraseña limpiada
        user_data = create_user(
            email=request.email.strip(),
            username=username,
            password=password,  # Usar la contraseña limpiada
            role="user"  # Los usuarios normales no pueden ser admin
        )
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_data["id"]), "email": user_data["email"], "role": user_data["role"]},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=User(
                id=user_data["id"],
                email=user_data["email"],
                username=user_data["username"],
                role=user_data["role"],
                created_at=user_data["created_at"],
                is_active=True
            )
        )
    
    except ValueError as e:
        # Log del error para debugging
        print(f"Error en signup (ValueError): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-lanzar HTTPExceptions (como las validaciones)
        raise
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        # Log del error completo para debugging
        print(f"Error en signup ({error_type}): {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Si el error menciona el límite de 72 bytes, dar un mensaje más claro
        if "72" in error_msg or "bytes" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña es demasiado larga. Por favor, usa una contraseña de máximo 72 caracteres."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {error_msg}"
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login de usuario (OAuth2 form)
    
    Usa OAuth2PasswordRequestForm que espera:
    - **username**: Email del usuario
    - **password**: Contraseña
    
    Retorna un token JWT que debe incluirse en el header:
    `Authorization: Bearer <token>`
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "email": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=User(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            role=user["role"],
            created_at=user["created_at"],
            is_active=True
        )
    )


@router.post("/login-json", response_model=Token)
async def login_json(request: LoginRequest):
    """
    Login de usuario (versión JSON)
    
    - **email**: Email del usuario
    - **password**: Contraseña
    
    Retorna un token JWT que debe incluirse en el header:
    `Authorization: Bearer <token>`
    """
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "email": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=User(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            role=user["role"],
            created_at=user["created_at"],
            is_active=True
        )
    )


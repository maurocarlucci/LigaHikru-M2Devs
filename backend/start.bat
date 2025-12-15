@echo off
echo ========================================
echo   LigaHikru - Iniciando Backend
echo ========================================
echo.

REM Verificar que existe .env
if not exist .env (
    echo [ERROR] No se encontro el archivo .env
    echo Por favor, copia env.example a .env y configura tus credenciales
    pause
    exit /b 1
)

echo [1/2] Verificando dependencias...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Error instalando dependencias
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencias instaladas
)

echo.
echo [2/2] Iniciando servidor...
echo.
echo Backend disponible en: http://localhost:8000
echo Documentacion Swagger: http://localhost:8000/docs
echo.
echo Presiona CTRL+C para detener el servidor
echo.

uvicorn app.main:app --reload --port 8000

pause

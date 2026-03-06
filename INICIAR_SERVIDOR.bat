@echo off
echo ========================================
echo   SISTEMA SAC WEB - INICIANDO...
echo ========================================
echo.

REM Ir a la carpeta del proyecto
cd /d "%~dp0"

REM Verificar si existe Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado
    echo.
    echo Por favor instala Python desde:
    echo https://www.python.org/downloads/
    echo.
    echo O ejecuta el instalador en: instaladores\python-3.11.7-amd64.exe
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Activar entorno virtual
echo Activando entorno virtual...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Entorno virtual activado
) else (
    echo [AVISO] Entorno virtual no encontrado
    echo Creando nuevo entorno virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Instalando dependencias...
    pip install -r requirements.txt
    echo [OK] Entorno virtual creado e instalado
)

echo.

REM Iniciar servidor
echo ========================================
echo   INICIANDO SERVIDOR DJANGO...
echo ========================================
echo.
echo El sistema estara disponible en:
echo.
echo    http://127.0.0.1:8000
echo.
echo Abre tu navegador y ve a esa direccion
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

python manage.py runserver

pause

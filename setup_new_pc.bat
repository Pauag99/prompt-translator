@echo off
setlocal

echo.
echo ====================================================================
echo   PROMPT TRANSLATOR - SETUP PARA NUEVO PC
echo ====================================================================
echo.

cd /d "%~dp0"

set "PYTHON_CMD=py -3"
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    set "PYTHON_CMD=python"
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python no esta instalado o no esta en PATH.
        echo.
        echo Instala Python 3.10+ desde:
        echo https://www.python.org/downloads/
        echo.
        echo En Windows marca "Add Python to PATH" durante la instalacion.
        pause
        exit /b 1
    )
)

echo [OK] Python detectado:
%PYTHON_CMD% --version
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual .venv...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo [OK] Entorno virtual .venv ya existe.
)

echo.
echo Actualizando pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] No se pudo actualizar pip.
    pause
    exit /b 1
)

echo.
echo Instalando dependencias Python...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

set "OLLAMA_CMD=ollama"
ollama --version >nul 2>&1
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        set "OLLAMA_CMD=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
    ) else (
        echo.
        echo [ERROR] Ollama no esta instalado o no se puede encontrar.
        echo.
        echo Instala Ollama desde:
        echo https://ollama.com/download
        echo.
        echo Despues cierra esta ventana y ejecuta setup_new_pc.bat otra vez.
        pause
        exit /b 1
    )
)

echo.
echo [OK] Ollama detectado:
"%OLLAMA_CMD%" --version

echo.
echo Descargando/verificando modelo mistral...
echo Esto puede tardar 10-20 minutos la primera vez.
"%OLLAMA_CMD%" pull mistral
if errorlevel 1 (
    echo [ERROR] No se pudo descargar mistral.
    echo Comprueba tu conexion a internet y espacio en disco.
    pause
    exit /b 1
)

echo.
echo Validando instalacion...
".venv\Scripts\python.exe" validate_setup.py
if errorlevel 1 (
    echo.
    echo [AVISO] La validacion no fue completa.
    echo Si el unico problema es Ollama server, ejecuta:
    echo "%OLLAMA_CMD%" serve
    echo y despues:
    echo .venv\Scripts\python.exe validate_setup.py
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo [OK] NUEVO PC PREPARADO
echo ====================================================================
echo.
echo Para usar el proyecto:
echo   .venv\Scripts\python.exe demo.py
echo.
echo Si Ollama no responde, abre otra terminal y ejecuta:
echo   "%OLLAMA_CMD%" serve
echo.
pause

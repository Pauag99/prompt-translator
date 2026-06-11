@echo off
setlocal

echo.
echo ====================================================================
echo   PROMPT TRANSLATOR - INSTALADOR DE MISTRAL
echo ====================================================================
echo.

set "OLLAMA_CMD=ollama"
ollama --version >nul 2>&1
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        set "OLLAMA_CMD=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
    ) else (
        echo [ERROR] Ollama no esta instalado o no se puede encontrar.
        echo.
        echo Pasos:
        echo 1. Descarga Ollama desde https://ollama.com/download
        echo 2. Instala el programa
        echo 3. Cierra y abre PowerShell de nuevo
        echo 4. Ejecuta este script otra vez
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Ollama detectado:
"%OLLAMA_CMD%" --version
echo.

echo Descargando/verificando Mistral 7B...
echo Esto puede tardar 10-20 minutos la primera vez.
echo.

"%OLLAMA_CMD%" pull mistral

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo descargar Mistral.
    echo Comprueba:
    echo - Conexion a internet
    echo - Al menos 8 GB libres en disco
    echo - Que Ollama este instalado correctamente
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo [OK] MISTRAL ESTA LISTO
echo ====================================================================
echo.
echo Siguientes pasos:
echo 1. Ejecuta validate_setup.py:
echo    python validate_setup.py
echo.
echo 2. Ejecuta la demo:
echo    python demo.py
echo.
echo Si Ollama no responde, abre otra terminal y ejecuta:
echo    "%OLLAMA_CMD%" serve
echo.
pause

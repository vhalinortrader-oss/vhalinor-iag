@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   Vhalinor AI - Launcher
echo ==========================================
echo.

:: 1. Verificar se as dependencias estao instaladas (node_modules)
if not exist "node_modules" (
    echo [ERRO] Dependencias nao encontradas. Por favor, execute 'setup_windows.bat' primeiro.
    pause
    exit /b 1
)

:: 2. Iniciar o sistema
echo Iniciando Vhalinor AI...
echo.
echo Para acessar a interface, abra o navegador em: http://localhost:3000
echo.
call npm start

pause

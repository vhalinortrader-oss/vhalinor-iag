@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   Vhalinor AI - Windows Installer
echo ==========================================
echo.

:: 1. Verificar Node.js
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado. Por favor, instale em: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js detectado.

:: 2. Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Por favor, instale em: https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python detectado.

:: 3. Instalar dependencias Node
echo.
echo [1/3] Instalando dependencias do Frontend/Backend (Node)...
call npm install
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias Node.
    pause
    exit /b 1
)

:: 4. Instalar dependencias Python
echo.
echo [2/3] Instalando dependencias de IA (Python)...
call pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias Python.
    pause
    exit /b 1
)

:: 5. Build do Frontend
echo.
echo [3/3] Compilando interface Vhalinor...
call npm run build
if %errorlevel% neq 0 (
    echo [ERRO] Falha na compilacao do frontend.
    pause
    exit /b 1
)

:: 6. Criar atalho de inicializacao
echo.
echo Criando inicializador rapido...
(
echo @echo off
echo cd /d "%%~dp0"
echo echo Iniciando Vhalinor AI...
echo npm start
) > Iniciar_Vhalinor.bat

echo.
echo ==========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ==========================================
echo.
echo Use o arquivo 'Iniciar_Vhalinor.bat' para abrir o sistema.
echo.
pause

@echo off
REM ============================================
REM Build Script for PDF/Word → MediaWiki Converter
REM Creates standalone Windows executable
REM ============================================

echo.
echo ========================================
echo  Building Convertitore PDF/Word EXE
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Node.js is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js non trovato! Installare Node.js prima di continuare.
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python non trovato! Installare Python prima di continuare.
    pause
    exit /b 1
)

echo [1/5] Pulizia build precedente...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "frontend\dist" rmdir /s /q "frontend\dist"
echo       - Pulizia completata

echo.
echo [2/5] Building Angular frontend...
cd frontend
if not exist "node_modules" (
    echo       - Installazione dipendenze npm...
    call npm install
)
echo       - Compilazione frontend in modalita' produzione...
call npm run build -- --configuration production
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build frontend fallito!
    cd ..
    pause
    exit /b 1
)
cd ..
echo       - Frontend compilato con successo

echo.
echo [3/5] Verifica build frontend...
if not exist "frontend\dist\pdf-word-mediawiki\browser\index.html" (
    echo [ERROR] Build frontend non trovato in frontend\dist\pdf-word-mediawiki\browser\
    pause
    exit /b 1
)
echo       - Build frontend verificato

echo.
echo [4/5] Installazione PyInstaller...
cd backend
call uv pip install pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installazione PyInstaller fallito!
    cd ..
    pause
    exit /b 1
)
cd ..
echo       - PyInstaller installato

echo.
echo [5/5] Creazione eseguibile...
call uv run pyinstaller build_exe.spec --clean
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Creazione eseguibile fallito!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  BUILD COMPLETATO CON SUCCESSO!
echo ========================================
echo.
echo Eseguibile creato in: dist\ConvertitorePDF.exe
echo.
echo Dimensione eseguibile:
dir /s dist\ConvertitorePDF.exe | find "ConvertitorePDF.exe"
echo.
echo Per testare l'applicazione:
echo   1. Vai nella cartella dist\
echo   2. Esegui ConvertitorePDF.exe
echo.
pause

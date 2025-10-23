@echo off
REM ============================================
REM Build Script for PDF/Word → MediaWiki Converter
REM Creates standalone Windows executable
REM ============================================
REM
REM REQUISITI:
REM - Node.js e npm (per build Angular frontend)
REM - Python 3.13+ globale (C:\Python o simile)
REM - uv (per formattazione con ruff)
REM
REM COSA FA QUESTO SCRIPT:
REM 1. Pulisce build precedenti
REM 2. Compila frontend Angular in modalità produzione
REM 3. Formatta codice backend con ruff
REM 4. Verifica e installa dipendenze Python se necessario
REM 5. Crea eseguibile Windows con PyInstaller
REM
REM OUTPUT: dist\ConvertitorePDF.exe (~50MB)
REM ============================================

echo.
echo ========================================
echo  Building Convertitore PDF/Word EXE
echo ========================================
echo.
echo Script di build automatico per Windows
echo.
echo Requisiti:
echo   - Node.js e npm
echo   - Python 3.13+ globale
echo   - uv (per ruff formatter)
echo.
echo Questo processo puo' richiedere alcuni minuti...
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
echo [4/6] Formattazione codice backend con ruff...
call uv run ruff format backend/app
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Formattazione ruff fallita (continuando comunque...)
)
echo       - Codice formattato

echo.
echo [5/6] Verifica dipendenze Python globali...
python -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] PyInstaller non trovato, installazione in corso...
    python -m pip install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Installazione PyInstaller fallita!
        pause
        exit /b 1
    )
)
python -c "import pymupdf, docx, PIL, lxml" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Dipendenze backend mancanti, installazione in corso...
    python -m pip install pymupdf python-docx pillow lxml
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Installazione dipendenze fallita!
        pause
        exit /b 1
    )
)
echo       - Dipendenze verificate

echo.
echo [6/6] Creazione eseguibile con PyInstaller...
echo       (Usando Python globale: %PYTHON%)
python -m PyInstaller build_exe.spec --noconfirm
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
echo Eseguibile creato: dist\ConvertitorePDF.exe
echo.
echo Dimensione file:
for %%I in (dist\ConvertitorePDF.exe) do echo   %%~zI bytes (~%%~zI/1048576 MB)
echo.
echo ========================================
echo  COME USARE L'APPLICAZIONE
echo ========================================
echo.
echo 1. Esegui dist\ConvertitorePDF.exe
echo 2. Click su "Avvia Applicazione"
echo 3. Click su "Apri nel Browser"
echo 4. Carica un PDF o DOCX per convertirlo
echo.
echo L'applicazione include:
echo   - Server FastAPI integrato (porta 8001)
echo   - Frontend Angular
echo   - Conversione PDF/DOCX a MediaWiki
echo   - Estrazione e download immagini
echo.
echo ========================================
echo.
echo Per distribuire: copia solo ConvertitorePDF.exe
echo (Tutto e' incluso nell'eseguibile!)
echo.
pause

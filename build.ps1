# ============================================
# Build Script for PDF/Word → MediaWiki Converter
# PowerShell version
# Creates standalone Windows executable
# ============================================

Write-Host ""
Write-Host "========================================"
Write-Host " Building Convertitore PDF/Word EXE"
Write-Host "========================================"
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if Node.js is installed
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js non trovato! Installare Node.js prima di continuare." -ForegroundColor Red
    Write-Host "Download: https://nodejs.org/"
    Read-Host "Premi INVIO per uscire"
    exit 1
}

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python non trovato! Installare Python prima di continuare." -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host "[1/5] Pulizia build precedente..." -ForegroundColor Cyan
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "frontend\dist") { Remove-Item -Recurse -Force "frontend\dist" }
Write-Host "      - Pulizia completata" -ForegroundColor Green

Write-Host ""
Write-Host "[2/5] Building Angular frontend..." -ForegroundColor Cyan
Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "      - Installazione dipendenze npm..."
    npm install
}

Write-Host "      - Compilazione frontend in modalita' produzione..."
npm run build -- --configuration production

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build frontend fallito!" -ForegroundColor Red
    Set-Location ..
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Set-Location ..
Write-Host "      - Frontend compilato con successo" -ForegroundColor Green

Write-Host ""
Write-Host "[3/5] Verifica build frontend..." -ForegroundColor Cyan
if (-not (Test-Path "frontend\dist\pdf-word-mediawiki\browser\index.html")) {
    Write-Host "[ERROR] Build frontend non trovato in frontend\dist\pdf-word-mediawiki\browser\" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}
Write-Host "      - Build frontend verificato" -ForegroundColor Green

Write-Host ""
Write-Host "[4/5] Installazione PyInstaller..." -ForegroundColor Cyan
Set-Location backend
uv pip install pyinstaller

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Installazione PyInstaller fallito!" -ForegroundColor Red
    Set-Location ..
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Set-Location ..
Write-Host "      - PyInstaller installato" -ForegroundColor Green

Write-Host ""
Write-Host "[5/5] Creazione eseguibile..." -ForegroundColor Cyan
uv run pyinstaller build_exe.spec --clean

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Creazione eseguibile fallito!" -ForegroundColor Red
    Read-Host "Premi INVIO per uscire"
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host " BUILD COMPLETATO CON SUCCESSO!"
Write-Host "========================================"
Write-Host ""
Write-Host "Eseguibile creato in: dist\ConvertitorePDF.exe" -ForegroundColor Green
Write-Host ""

$exeSize = (Get-Item "dist\ConvertitorePDF.exe").Length / 1MB
Write-Host "Dimensione eseguibile: $([math]::Round($exeSize, 2)) MB" -ForegroundColor Yellow
Write-Host ""
Write-Host "Per testare l'applicazione:" -ForegroundColor Cyan
Write-Host "  1. Vai nella cartella dist\"
Write-Host "  2. Esegui ConvertitorePDF.exe"
Write-Host ""

Read-Host "Premi INVIO per uscire"

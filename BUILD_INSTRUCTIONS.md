# Istruzioni per Build dell'Eseguibile

## Requisiti

Prima di eseguire la build, assicurati di avere installato:

1. **Node.js** (v18+) - Per compilare il frontend Angular
   - Download: https://nodejs.org/
   - Verifica: `node --version` e `npm --version`

2. **Python 3.13+** (globale, non UV) - Per creare l'eseguibile
   - Download: https://www.python.org/downloads/
   - Verifica: `python --version`
   - **IMPORTANTE**: Deve essere installato in C:\Python o path simile, NON dentro un virtual environment

3. **uv** - Per formattazione codice con ruff
   - Installazione: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Verifica: `uv --version`

## Build dell'Eseguibile

### Metodo 1: Build Automatica (Raccomandato)

Esegui semplicemente:

```cmd
build.bat
```

Lo script farà automaticamente:
1. Pulizia build precedenti
2. Compilazione frontend Angular
3. Formattazione codice backend
4. Verifica/installazione dipendenze Python
5. Creazione eseguibile con PyInstaller

### Metodo 2: Build Manuale (Passo-passo)

Se preferisci eseguire manualmente:

```cmd
# 1. Pulisci build precedenti
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q frontend\dist

# 2. Compila frontend
cd frontend
npm install
npm run build
cd ..

# 3. Formatta backend
uv run ruff format backend/app

# 4. Verifica dipendenze Python
python -m pip install pyinstaller pymupdf python-docx pillow lxml

# 5. Crea eseguibile
python -m PyInstaller build_exe.spec --noconfirm
```

## Output

Dopo la build troverai:
- **Eseguibile**: `dist\ConvertitorePDF.exe` (~50MB)
- Questo file è completamente standalone - contiene tutto!

## Distribuzione

Per distribuire l'applicazione:
1. Copia `ConvertitorePDF.exe` sul computer di destinazione
2. Esegui il file - non serve installare nulla!

## Uso dell'Applicazione

1. Doppio-click su `ConvertitorePDF.exe`
2. Click su "🚀 Avvia Applicazione"
3. Click su "🌐 Apri nel Browser"
4. Carica un PDF o DOCX per convertirlo in formato MediaWiki
5. Download del testo convertito o delle immagini estratte

## Risoluzione Problemi

### "PyInstaller non trovato"
```cmd
python -m pip install pyinstaller
```

### "Errore build frontend"
```cmd
cd frontend
rmdir /s /q node_modules
npm install
cd ..
```

### "Errore dipendenze Python"
```cmd
python -m pip install --upgrade pymupdf python-docx pillow lxml fastapi uvicorn
```

### "ruff non trovato"
```cmd
uv pip install ruff
```

## Note Tecniche

- **Porta server**: L'applicazione usa la porta 8001 (non 8000)
- **File temporanei**: Creati in `output/immagini/{job_id}/`
- **Python globale**: La build richiede Python GLOBALE, non in virtual environment
- **Tkinter**: Necessario per la GUI, incluso nel Python globale

## Struttura Output

```
output/
├── immagini/
│   └── {job_id}/          # Immagini estratte per job
│       ├── pdf_page1_img0-uuid.png
│       └── ...
└── testo_wiki/
    └── filename.wiki       # Testo convertito
```

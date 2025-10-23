# Guida Sviluppatore - Convertitore PDF/Word → MediaWiki Eseguibile

Documentazione tecnica per sviluppatori che vogliono modificare, estendere o contribuire al progetto.

---

## 🏗️ Architettura del Sistema

### Overview

Il progetto usa un'architettura ibrida:

```
┌─────────────────────────────────────────────────┐
│                launcher_gui.py                  │
│         (Tkinter GUI - Entry Point)             │
└────────────────┬────────────────────────────────┘
                 │ Avvia processo
                 ▼
┌─────────────────────────────────────────────────┐
│            backend/app/main.py                  │
│           (FastAPI + Uvicorn)                   │
├─────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────────┐    │
│  │   API REST   │  │  Static File Server  │    │
│  │   Routes     │  │  (Angular Build)     │    │
│  └──────────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│     frontend/dist/pdf-word-mediawiki/browser    │
│          (Angular App - Precompiled)            │
└─────────────────────────────────────────────────┘
```

### Componenti Principali

1. **GUI Launcher** (`launcher_gui.py`)
   - Framework: Tkinter (Python standard library)
   - Gestisce lifecycle del server FastAPI
   - Interfaccia user-friendly

2. **Backend API** (`backend/app/`)
   - Framework: FastAPI
   - Server: Uvicorn
   - Conversione PDF/DOCX → MediaWiki
   - Serve frontend come file statici

3. **Frontend Web** (`frontend/`)
   - Framework: Angular 18
   - Build output: `dist/pdf-word-mediawiki/browser/`
   - Interfaccia web per conversione

4. **PyInstaller** (`build_exe.spec`)
   - Packaging tool per creare eseguibile standalone
   - Include tutto: Python runtime, dipendenze, frontend

---

## 🔧 Setup Ambiente di Sviluppo

### 1. Clone Repository

```bash
git clone <repository-url>
cd trasf_x_wiki
```

### 2. Setup Backend

```bash
cd backend
uv venv
.venv\Scripts\activate  # Windows
uv sync
```

### 3. Setup Frontend

```bash
cd frontend
npm install
```

### 4. Verifica Setup

```bash
# Backend
cd backend
uv run uvicorn app.main:app --reload

# Frontend (in altro terminale)
cd frontend
npm start
```

---

## 🛠️ Sviluppo e Modifica

### Modificare la GUI

**File**: `launcher_gui.py`

Esempio: Aggiungere un nuovo pulsante

```python
def create_widgets(self) -> None:
    # ... existing code ...

    # Nuovo pulsante
    self.btn_custom = tk.Button(
        buttons_frame,
        text="🔧 Azione Custom",
        command=self.custom_action,
        width=25,
        height=2,
    )
    self.btn_custom.grid(row=3, column=0, padx=5, pady=5)

def custom_action(self) -> None:
    """Implementazione azione custom."""
    self.log("Azione custom eseguita")
    # ... tua logica ...
```

**Testare**: Esegui direttamente `python launcher_gui.py`

### Modificare il Backend

**File**: `backend/app/main.py`, `backend/app/routers/*.py`

Esempio: Aggiungere nuovo endpoint

```python
# backend/app/routers/custom.py
from fastapi import APIRouter

router = APIRouter(prefix="/custom", tags=["custom"])

@router.get("/hello")
async def hello_world():
    return {"message": "Hello from custom endpoint!"}
```

```python
# backend/app/main.py
from app.routers import custom

app.include_router(custom.router, prefix=config.api_prefix)
```

**Testare**: Esegui backend in dev mode con hot reload:
```bash
cd backend
uv run uvicorn app.main:app --reload
```

### Modificare il Frontend

**File**: `frontend/src/app/**/*.ts`

Sviluppo normale Angular:

```bash
cd frontend
npm start
# Modifiche riflesse automaticamente su http://localhost:4200
```

**Importante**: Il frontend comunica con backend via proxy (vedi `frontend/proxy.conf.json`)

---

## 📦 Build e Packaging

### Build Manuale Passo-passo

#### 1. Build Frontend

```bash
cd frontend
npm run build -- --configuration production
```

**Output**: `frontend/dist/pdf-word-mediawiki/browser/`

**Verifica**:
```bash
ls frontend/dist/pdf-word-mediawiki/browser/
# Deve contenere: index.html, main-*.js, polyfills-*.js, styles-*.css
```

#### 2. Test Backend con Frontend Integrato

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Apri browser su `http://localhost:8000` → Dovresti vedere il frontend Angular

#### 3. Test GUI Launcher

```bash
python launcher_gui.py
```

Click "Avvia Applicazione" → "Apri nel Browser" → Testa funzionalità

#### 4. Build Eseguibile

```bash
# Metodo 1: Script automatico
build.bat

# Metodo 2: Manuale
uv pip install pyinstaller
uv run pyinstaller build_exe.spec --clean
```

**Output**: `dist/ConvertitorePDF.exe`

---

## 🔍 Debugging

### Debug GUI Launcher

**Mostrare console per log**:

Modificare `build_exe.spec`:
```python
console=True,  # Invece di console=False
```

Oppure eseguire direttamente:
```bash
python launcher_gui.py
```

### Debug Backend

**Modalità sviluppo con hot reload**:
```bash
cd backend
uv run uvicorn app.main:app --reload --log-level debug
```

**Print debugging**: Usare `logging` invece di `print()`
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Messaggio debug")
logger.info("Informazione")
logger.error("Errore!")
```

### Debug Frontend

**DevTools Angular**:
```bash
cd frontend
npm start
# Browser: F12 → Console / Network / Sources
```

**Build Source Maps** (per debug in produzione):
```bash
ng build --source-map
```

---

## 🧪 Testing

### Test Backend

```bash
cd backend
uv pip install pytest pytest-asyncio httpx
uv run pytest
```

Esempio test:
```python
# backend/tests/test_convert.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Test Frontend

```bash
cd frontend
npm test
```

### Test Eseguibile

**Checklist test manuale**:
1. Esegui `ConvertitorePDF.exe`
2. Click "Avvia Applicazione" → Verifica server si avvia
3. Click "Apri nel Browser" → Verifica frontend si carica
4. Test conversione PDF → Verifica funziona
5. Test conversione DOCX → Verifica funziona
6. Click "Ferma Applicazione" → Verifica server si ferma
7. Chiudi finestra → Verifica cleanup corretto

---

## 📁 Struttura Progetto Dettagliata

```
trasf_x_wiki/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Entry point FastAPI
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py        # Configurazione
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── dto.py           # Pydantic models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── convert.py       # API conversione
│   │   │   ├── files.py         # API gestione file
│   │   │   └── health.py        # Healthcheck
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── extract_pdf.py   # Estrazione PDF
│   │       ├── extract_docx.py  # Estrazione DOCX
│   │       ├── convert_wikitext.py  # Conversione
│   │       └── storage.py       # Gestione file
│   ├── pyproject.toml           # Dipendenze uv
│   └── .venv/                   # Virtual environment
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.ts
│   │   │   ├── app.routes.ts
│   │   │   └── ...
│   │   ├── index.html
│   │   └── main.ts
│   ├── package.json
│   ├── angular.json
│   ├── proxy.conf.json          # Proxy per dev
│   └── dist/                    # Build output (generato)
│       └── pdf-word-mediawiki/
│           └── browser/
│               ├── index.html
│               ├── main-*.js
│               ├── polyfills-*.js
│               └── styles-*.css
│
├── immagini/                    # Immagini estratte
│
├── launcher_gui.py              # GUI entry point
├── build_exe.spec               # PyInstaller config
├── build.bat                    # Build script (Windows CMD)
├── build.ps1                    # Build script (PowerShell)
│
├── dist/                        # Output finale (generato)
│   └── ConvertitorePDF.exe      # ESEGUIBILE
│
├── build/                       # Temp PyInstaller (generato)
│
├── CLAUDE.md                    # Istruzioni Claude
├── programma.md                 # Analisi tecnica
├── README_ESEGUIBILE.md         # Docs utente finale
├── README_SVILUPPATORE.md       # Docs sviluppatore (questo file)
└── README.md                    # Docs generali
```

---

## ⚙️ Configurazione PyInstaller

### File: `build_exe.spec`

**Sezioni importanti**:

#### 1. Data Files (File da includere)

```python
datas=[
    # Angular frontend
    ('frontend/dist/pdf-word-mediawiki', 'frontend/dist/pdf-word-mediawiki'),

    # Backend code
    ('backend/app', 'backend/app'),

    # Images directory
    ('immagini', 'immagini'),
],
```

**Aggiungere nuovi file**:
```python
('path/to/source', 'path/in/exe'),
```

#### 2. Hidden Imports (Dipendenze non auto-rilevate)

```python
hiddenimports=[
    'uvicorn',
    'fastapi',
    # ... altri moduli
],
```

**Aggiungere nuove dipendenze** se PyInstaller non le trova:
```python
'new_module',
'new_module.submodule',
```

#### 3. Excludes (Ridurre dimensione exe)

```python
excludes=[
    'matplotlib',  # Non serve per questa app
    'numpy',       # Non serve
    # ... altri moduli da escludere
],
```

#### 4. Console Mode

```python
console=False,  # GUI mode (no console window)
console=True,   # Debug mode (mostra console)
```

---

## 🔧 Troubleshooting Build

### Errore: "Module not found" in exe

**Causa**: PyInstaller non ha incluso un modulo.

**Soluzione**: Aggiungi a `hiddenimports` in `build_exe.spec`:
```python
hiddenimports=[
    # ... existing ...
    'missing_module',
],
```

### Errore: "File not found" in exe

**Causa**: File non incluso in `datas`.

**Soluzione**: Aggiungi a `datas` in `build_exe.spec`:
```python
datas=[
    # ... existing ...
    ('source/file', 'dest/file'),
],
```

### Exe troppo grande

**Causa**: Troppi moduli inclusi.

**Soluzioni**:
1. Aggiungi moduli non necessari a `excludes`
2. Usa UPX compression: `upx=True`
3. Rimuovi dipendenze non usate dal `pyproject.toml`

### Frontend non si carica in exe

**Verifica**:
1. Build frontend completato? `frontend/dist/pdf-word-mediawiki/browser/index.html` esiste?
2. Path corretto in `main.py`?
   ```python
   frontend_build_path = Path(__file__).parent.parent.parent / "frontend" / "dist" / "pdf-word-mediawiki" / "browser"
   ```
3. `datas` include frontend in `build_exe.spec`?

---

## 🚀 Deploy e Distribuzione

### Versioning

**Incrementare versione**:

1. `backend/app/main.py`:
   ```python
   version="1.1.0",
   ```

2. `frontend/package.json`:
   ```json
   "version": "1.1.0",
   ```

3. Rifare build: `build.bat`

### Release Checklist

- [ ] Codice committato e pushato su Git
- [ ] Tag versione creato: `git tag v1.1.0`
- [ ] Build frontend: `cd frontend && npm run build`
- [ ] Build exe: `build.bat`
- [ ] Test exe su 2+ PC Windows
- [ ] README aggiornati
- [ ] CHANGELOG aggiornato
- [ ] Release notes scritte
- [ ] Exe uploadato su release GitHub

---

## 📚 Risorse Utili

### Documentazione

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Angular Docs](https://angular.io/docs)
- [PyInstaller Docs](https://pyinstaller.org/en/stable/)
- [Tkinter Docs](https://docs.python.org/3/library/tkinter.html)

### Tool

- [Postman](https://www.postman.com/) - Test API REST
- [Fiddler](https://www.telerik.com/fiddler) - Network debugging
- [VirusTotal](https://www.virustotal.com/) - Scan exe

---

## 🤝 Contribuire

### Fork e Pull Request

1. Fork repository
2. Crea branch: `git checkout -b feature/nuova-funzione`
3. Commit: `git commit -m "Aggiungi nuova funzione"`
4. Push: `git push origin feature/nuova-funzione`
5. Apri Pull Request

### Code Style

- **Python**: PEP 8 (usa `ruff format`)
- **TypeScript**: Angular style guide
- **Commit**: Conventional Commits

---

**Ultimo aggiornamento**: Ottobre 2025
**Versione documento**: 1.0

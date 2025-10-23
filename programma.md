# Analisi: Creazione Eseguibile Windows per il Convertitore PDF/Word → MediaWiki

## Domanda
È possibile ricavare dal progetto un "programma per Windows" (eseguibile .exe) che:
- Mostri una GUI/maschera all'avvio
- Permetta di avviare il WebService FastAPI con un pulsante
- Permetta di aprire il frontend con un altro pulsante
- Renda il lancio dell'applicazione il più comodo possibile

## Risposta: SÌ, è possibile

---

## ✅ SOLUZIONE CONSIGLIATA: GUI Python + Backend Unificato

### Architettura Proposta

1. **Build del frontend Angular** in modalità produzione → file statici
2. **FastAPI serve sia le API che il frontend** (eliminando la necessità di `ng serve`)
3. **GUI Python semplice** (Tkinter o PyQt) con pulsanti per:
   - Avviare il server (FastAPI + frontend integrato)
   - Aprire il browser su `http://localhost:8000`
   - Fermare il server
4. **PyInstaller** per creare l'eseguibile Windows

### Vantaggi

- ✅ **Un solo processo** da gestire (non più backend + frontend separati)
- ✅ **Nessuna dipendenza da Node.js** in produzione
- ✅ **Eseguibile standalone** con PyInstaller
- ✅ **Più veloce** all'avvio (no Angular dev server)
- ✅ **Più professionale** per distribuzione
- ✅ **Dimensioni contenute** dell'eseguibile (circa 40-60 MB con PyInstaller)
- ✅ **Facilità di distribuzione** - un solo file .exe

### Cosa Modificare

1. **Backend**: Configurare FastAPI per servire i file statici di Angular compilati
2. **GUI Launcher**: Creare una finestra Python con Tkinter (già incluso in Python)
3. **Build Frontend**: Eseguire una volta `ng build --configuration production`
4. **Packaging**: Configurare PyInstaller per includere tutto

### Mockup GUI Proposta

```
┌──────────────────────────────────────────┐
│  Convertitore PDF/Word → MediaWiki      │
├──────────────────────────────────────────┤
│                                          │
│  [🚀 Avvia Applicazione]                │
│                                          │
│  [🌐 Apri nel Browser]                  │
│                                          │
│  [⏹️  Ferma Applicazione]                │
│                                          │
│  Status: ● Pronto / ● In esecuzione     │
│                                          │
│  Porta: 8000                             │
│  URL: http://localhost:8000              │
└──────────────────────────────────────────┘
```

---

## Altre Opzioni (Alternative)

### Opzione 2: GUI con Subprocess (Due Processi Separati)

**Architettura**: Mantenere backend e frontend separati, GUI che lancia entrambi i processi con subprocess.

**Vantaggi**:
- Nessuna modifica all'architettura attuale
- Sviluppo più rapido (no refactoring)

**Svantaggi**:
- Richiede Node.js installato sul sistema target
- Più complesso gestire due processi (avvio, monitoraggio, chiusura)
- Tempi di avvio più lunghi (Angular dev server)
- Eseguibile meno "professionale"

### Opzione 3: Electron Wrapper

**Architettura**: Wrappare tutto in Electron per una GUI completa con frontend integrato.

**Vantaggi**:
- GUI moderna e cross-platform (Windows, Mac, Linux)
- Controllo totale sull'interfaccia
- Browser integrato (no dipendenza da Chrome/Edge)

**Svantaggi**:
- Eseguibile molto pesante (100-150+ MB)
- Overkill per questo caso d'uso
- Maggiore complessità di sviluppo
- Tempi di build più lunghi

### Opzione 4: PyWebView

**Architettura**: Usare PyWebView per creare una finestra nativa con il frontend Angular embedded.

**Vantaggi**:
- GUI nativa con webview integrato
- Più leggero di Electron
- No browser esterno richiesto

**Svantaggi**:
- Meno controllo sulla finestra del browser
- Possibili problemi di compatibilità con webview di Windows

---

## 🎯 Implementazione Soluzione Consigliata (Dettagli Tecnici)

### Passo 1: Modificare il Backend FastAPI

**File da modificare**: `backend/app/main.py`

Aggiungere il mount dei file statici Angular:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Dopo la configurazione del router API
app.mount("/assets", StaticFiles(directory="frontend/dist/browser/assets"), name="assets")

# Servire il frontend Angular per tutte le altre route
@app.get("/{full_path:path}")
async def serve_angular(full_path: str):
    file_path = os.path.join("frontend/dist/browser", full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse("frontend/dist/browser/index.html")
```

### Passo 2: Creare GUI Launcher

**Nuovo file**: `launcher_gui.py` (root del progetto)

```python
import tkinter as tk
from tkinter import messagebox
import subprocess
import webbrowser
import threading
import sys

class AppLauncher:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Convertitore PDF/Word → MediaWiki")
        self.window.geometry("400x300")
        self.server_process = None
        self.status_var = tk.StringVar(value="● Pronto")

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Titolo
        title = tk.Label(self.window, text="Convertitore PDF/Word → MediaWiki",
                        font=("Arial", 14, "bold"))
        title.pack(pady=20)

        # Pulsanti
        self.btn_start = tk.Button(self.window, text="🚀 Avvia Applicazione",
                                   command=self.start_server, width=25, height=2)
        self.btn_start.pack(pady=10)

        self.btn_open = tk.Button(self.window, text="🌐 Apri nel Browser",
                                 command=self.open_browser, width=25, height=2,
                                 state=tk.DISABLED)
        self.btn_open.pack(pady=10)

        self.btn_stop = tk.Button(self.window, text="⏹️ Ferma Applicazione",
                                 command=self.stop_server, width=25, height=2,
                                 state=tk.DISABLED)
        self.btn_stop.pack(pady=10)

        # Status
        status_frame = tk.Frame(self.window)
        status_frame.pack(pady=20)
        tk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        tk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

    def start_server(self):
        # Implementazione avvio server
        pass

    def open_browser(self):
        webbrowser.open("http://localhost:8000")

    def stop_server(self):
        # Implementazione stop server
        pass

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = AppLauncher()
    app.run()
```

### Passo 3: Build del Frontend

```bash
cd frontend
npm run build --configuration production
# Output: frontend/dist/browser/
```

### Passo 4: Configurare PyInstaller

**Nuovo file**: `build_exe.spec` (root del progetto)

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend/dist/browser', 'frontend/dist/browser'),
        ('backend/app', 'backend/app'),
        ('backend/.venv/Lib/site-packages', 'site-packages'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'pymupdf',
        'docx',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ConvertitorePDF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Nasconde la console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Opzionale: aggiungere un'icona
)
```

### Passo 5: Script di Build

**Nuovo file**: `build.bat` (Windows)

```batch
@echo off
echo ======================================
echo Building Convertitore PDF/Word EXE
echo ======================================

echo.
echo [1/4] Building Angular frontend...
cd frontend
call npm run build
cd ..

echo.
echo [2/4] Installing PyInstaller...
cd backend
call uv pip install pyinstaller
cd ..

echo.
echo [3/4] Creating executable...
pyinstaller build_exe.spec

echo.
echo [4/4] Done!
echo Executable created: dist/ConvertitorePDF.exe
pause
```

---

## Struttura File Finale

Dopo l'implementazione:

```
trasf_x_wiki/
├── launcher_gui.py              # GUI principale (nuovo)
├── build_exe.spec               # Configurazione PyInstaller (nuovo)
├── build.bat                    # Script di build (nuovo)
├── backend/
│   ├── app/
│   │   └── main.py              # Modificato per servire frontend statico
│   └── ...
├── frontend/
│   └── dist/
│       └── browser/             # Frontend compilato (generato da ng build)
│           ├── index.html
│           ├── main-*.js
│           └── assets/
└── dist/
    └── ConvertitorePDF.exe      # Eseguibile finale (generato)
```

---

## Utilizzo Finale

### Per l'Utente Finale:

1. **Doppio click** su `ConvertitorePDF.exe`
2. Appare la **GUI**
3. Click su **"Avvia Applicazione"**
4. Click su **"Apri nel Browser"**
5. Usa l'applicazione web normalmente
6. Quando finito: click su **"Ferma Applicazione"**

### Nessuna Installazione Richiesta:
- ❌ Non serve Python installato
- ❌ Non serve Node.js installato
- ❌ Non serve installare dipendenze
- ✅ Solo l'eseguibile è sufficiente

---

## Stima dei Tempi di Implementazione

- **Modifica Backend**: 30-60 minuti
- **Creazione GUI**: 1-2 ore
- **Configurazione PyInstaller**: 1-2 ore (testing e debugging inclusi)
- **Testing Completo**: 1 ora
- **Documentazione**: 30 minuti

**Totale stimato**: 4-6 ore di lavoro

---

## Dimensioni Stimate

- **Eseguibile finale**: ~50-80 MB (con tutte le dipendenze embedded)
- **Compresso (ZIP)**: ~25-35 MB

---

## Note Tecniche

### Compatibilità
- Windows 10/11 (64-bit)
- Possibile estendere a 32-bit se necessario
- Non cross-platform (solo Windows con questa soluzione)

### Limitazioni
- Prima esecuzione potrebbe essere bloccata da Windows SmartScreen (normale per eseguibili non firmati)
- Antivirus potrebbero segnalare false positive (comune con PyInstaller)
- Richiede circa 200MB di spazio su disco per l'estrazione temporanea

### Possibili Miglioramenti Futuri
- Firma digitale dell'eseguibile (elimina warning SmartScreen)
- Installer MSI professionale (con InstallForge o Inno Setup)
- Auto-update integrato
- Icona personalizzata
- Splash screen durante l'avvio

---

## Conclusione

✅ **È assolutamente fattibile** creare un eseguibile Windows professionale per questo progetto.

✅ **La soluzione consigliata** (GUI Python + Backend Unificato) è la più equilibrata in termini di:
- Semplicità implementativa
- Performance
- Facilità d'uso per l'utente finale
- Dimensioni contenute

✅ **Pronto per l'implementazione** quando richiesto.

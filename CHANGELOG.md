# Changelog

Tutte le modifiche importanti a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

---

## [1.0.0] - 2025-10-23

### Aggiunto - Eseguibile Windows Standalone

#### Nuove Funzionalità

- **GUI Launcher con Tkinter** (`launcher_gui.py`)
  - Interfaccia grafica user-friendly per avviare/fermare il server
  - Pulsante per aprire automaticamente il browser
  - Log output in tempo reale
  - Gestione sicura del lifecycle del server

- **Backend Unificato**
  - FastAPI ora serve sia le API REST che il frontend Angular compilato
  - Supporto automatico per file statici Angular
  - Fallback intelligente: serve API info se frontend non compilato
  - Catch-all routing per Angular client-side routing

- **Sistema di Build Automatico**
  - Script batch Windows (`build.bat`) per build completo
  - Script PowerShell alternativo (`build.ps1`)
  - Build automatico di frontend e backend
  - Creazione eseguibile standalone con PyInstaller

#### File Aggiunti

- `launcher_gui.py` - GUI launcher principale
- `build_exe.spec` - Configurazione PyInstaller
- `build.bat` - Script build per Windows CMD
- `build.ps1` - Script build per PowerShell
- `README_ESEGUIBILE.md` - Documentazione per utenti finali
- `README_SVILUPPATORE.md` - Documentazione per sviluppatori
- `CHANGELOG.md` - Questo file

#### Modifiche

- **backend/app/main.py**
  - Aggiunto supporto per servire file statici Angular
  - Aggiunto mount per cartella `assets/`
  - Modificato endpoint root `/` per servire `index.html` se disponibile
  - Aggiunto catch-all route per Angular routing

- **.gitignore**
  - Rimosso `*.spec` per mantenere `build_exe.spec` nel repo
  - Aggiunta sezione dedicata per build eseguibile
  - Aggiunta cartella `immagini/` agli ignore

#### Caratteristiche Tecniche

- Eseguibile standalone Windows (50-80 MB)
- Nessuna dipendenza esterna richiesta (Python, Node.js embedded)
- Porta di default: 8000
- Console mode disabilitato per GUI (modificabile per debug)
- UPX compression abilitato per ridurre dimensioni

#### Architettura

```
GUI Launcher (Tkinter)
    ↓
FastAPI Server (Uvicorn)
    ├── API REST Endpoints
    └── Static File Server
        └── Angular Frontend (Precompiled)
```

---

## [0.x.x] - Pre-release

### Funzionalità Base

- Conversione PDF → MediaWiki
- Conversione DOCX → MediaWiki
- Estrazione immagini da documenti
- API REST con FastAPI
- Frontend Angular
- Documentazione API (Swagger, ReDoc, Scalar)

---

## Note per le Release Future

### [1.1.0] - Prossima versione pianificata

#### Da Implementare

- [ ] Icona personalizzata per l'eseguibile
- [ ] Splash screen all'avvio
- [ ] Configurazione porta via GUI
- [ ] Installer MSI professionale
- [ ] Sistema di auto-update
- [ ] Firma digitale dell'eseguibile
- [ ] Supporto multi-lingua (EN/IT)
- [ ] Tray icon per minimizzazione
- [ ] Configurazione persistente (salva preferenze utente)

### [1.2.0] - Funzionalità avanzate

#### Da Considerare

- [ ] Batch conversion (conversione multipla)
- [ ] Conversione drag-and-drop
- [ ] Preview inline nel GUI
- [ ] Cronologia conversioni
- [ ] Template MediaWiki personalizzabili
- [ ] Export in formati aggiuntivi (HTML, Markdown)

---

## Link Utili

- **Repository**: [GitHub URL]
- **Documentazione**: Vedere README_*.md
- **Issues**: [GitHub Issues URL]
- **Releases**: [GitHub Releases URL]

---

**Formato Date**: YYYY-MM-DD
**Versioning**: Semantic Versioning (MAJOR.MINOR.PATCH)

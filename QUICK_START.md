# Quick Start - Eseguibile Windows

Guida rapida per creare e testare l'eseguibile Windows del Convertitore PDF/Word → MediaWiki.

---

## ⚡ Creazione Eseguibile (3 comandi)

### Opzione 1: Automatico (Consigliato)

```batch
build.bat
```

### Opzione 2: PowerShell

```powershell
.\build.ps1
```

### Cosa fa lo script

1. ✅ Pulisce build precedenti
2. ✅ Compila frontend Angular (produzione)
3. ✅ Installa PyInstaller
4. ✅ Crea eseguibile in `dist/ConvertitorePDF.exe`

**Tempo**: ~3-5 minuti (prima volta), ~1-2 minuti (successive)

---

## 🚀 Test Eseguibile

### 1. Avvia GUI

```batch
cd dist
ConvertitorePDF.exe
```

### 2. Usa l'Applicazione

1. Click **"🚀 Avvia Applicazione"** → Server si avvia
2. Click **"🌐 Apri nel Browser"** → Browser si apre su localhost:8000
3. **Usa l'app web** normalmente
4. Click **"⏹️ Ferma Applicazione"** quando finito

---

## 🔧 Test Sviluppo (Senza Build)

### Test GUI direttamente

```bash
python launcher_gui.py
```

### Test Backend con Frontend integrato

```bash
# Terminal 1: Build frontend (una volta)
cd frontend
npm run build

# Terminal 2: Avvia backend
cd backend
uv run uvicorn app.main:app

# Browser: http://localhost:8000
```

---

## 📁 File Generati

```
trasf_x_wiki/
├── dist/
│   └── ConvertitorePDF.exe    ← TUO ESEGUIBILE (50-80 MB)
│
├── frontend/dist/              ← Frontend compilato
│   └── pdf-word-mediawiki/
│       └── browser/
│
└── build/                      ← Temp PyInstaller (puoi eliminarlo)
```

---

## 🎯 Distribuzione

### Per Utenti Finali

**Distribuisci solo**: `dist/ConvertitorePDF.exe`

**Nessun altro file necessario!**

---

## ❓ Problemi Comuni

### Build Fallisce

**Verifica prerequisiti**:
```bash
python --version   # Deve essere 3.8+
node --version     # Deve essere 18+
npm --version
```

### Frontend non si Carica

**Verifica build frontend**:
```bash
dir frontend\dist\pdf-word-mediawiki\browser\index.html
```

Se non esiste, riesegui:
```bash
cd frontend
npm run build
```

### Server non si Avvia

**Verifica porta libera**:
- Chiudi altri programmi sulla porta 8000
- Oppure modifica porta in `launcher_gui.py` (riga: `self.port = 8000`)

---

## 📚 Documentazione Completa

- **Utenti finali**: [README_ESEGUIBILE.md](README_ESEGUIBILE.md)
- **Sviluppatori**: [README_SVILUPPATORE.md](README_SVILUPPATORE.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

## ✅ Checklist Build Produzione

Prima di distribuire:

- [ ] Build completato senza errori
- [ ] Eseguibile testato su almeno 2 PC diversi
- [ ] Conversione PDF testata
- [ ] Conversione DOCX testata
- [ ] Nessun crash o errore
- [ ] Versione aggiornata in codice
- [ ] Documentazione aggiornata

---

**Setup completato in**: < 5 minuti
**Dimensione finale**: ~50-80 MB
**Compatibilità**: Windows 10/11 (64-bit)

🎉 **Pronto per la distribuzione!**

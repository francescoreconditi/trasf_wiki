# Convertitore PDF/Word → MediaWiki - Eseguibile Windows

Guida completa per creare e distribuire l'eseguibile Windows standalone dell'applicazione.

---

## 📦 Prerequisiti per la Build

Per creare l'eseguibile, sono necessari:

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **uv** - Package manager Python (installato automaticamente)
4. **Git** (opzionale) - [Download](https://git-scm.com/)

---

## 🚀 Come Creare l'Eseguibile

### Metodo 1: Script Batch (Windows CMD)

```batch
build.bat
```

### Metodo 2: PowerShell

```powershell
.\build.ps1
```

### Processo di Build

Lo script esegue automaticamente i seguenti passi:

1. **Pulizia** - Rimuove build precedenti
2. **Build Frontend** - Compila Angular in modalità produzione
3. **Verifica Build** - Controlla che tutti i file siano stati creati
4. **Installazione PyInstaller** - Installa il tool di packaging
5. **Creazione EXE** - Genera l'eseguibile standalone in `dist/ConvertitorePDF.exe`

**Tempo stimato**: 3-5 minuti (prima build), 1-2 minuti (successive)

---

## 📂 Struttura File Generati

```
trasf_x_wiki/
├── dist/
│   └── ConvertitorePDF.exe    ← ESEGUIBILE FINALE (50-80 MB)
├── build/                       ← Cartella temporanea (può essere eliminata)
├── frontend/
│   └── dist/
│       └── pdf-word-mediawiki/
│           └── browser/         ← Frontend compilato
└── immagini/                    ← Cartella per immagini estratte
```

---

## 💻 Utilizzo per l'Utente Finale

### Installazione

**Nessuna installazione necessaria!** L'eseguibile è standalone.

1. Copiare `ConvertitorePDF.exe` su qualsiasi PC Windows
2. Eseguire con doppio click

### Primo Avvio

1. **Doppio click** su `ConvertitorePDF.exe`
2. Potrebbe apparire un avviso di Windows SmartScreen (normale per exe non firmati):
   - Click su **"Maggiori informazioni"**
   - Click su **"Esegui comunque"**
3. Si apre la finestra GUI dell'applicazione

### Interfaccia Grafica

```
┌──────────────────────────────────────────┐
│  Convertitore PDF/Word → MediaWiki      │
├──────────────────────────────────────────┤
│                                          │
│  [🚀 Avvia Applicazione]                │
│                                          │
│  [⏹️  Ferma Applicazione]                │
│                                          │
│  [🌐 Apri nel Browser]                  │
│                                          │
│  Status: ● In esecuzione                 │
│  URL: http://localhost:8000              │
│                                          │
│  Log Output:                             │
│  ┌──────────────────────────────────┐   │
│  │ 🚀 Avvio server in corso...      │   │
│  │ ✅ Server avviato con successo!  │   │
│  └──────────────────────────────────┘   │
└──────────────────────────────────────────┘
```

### Passo-passo

1. **Avvia Applicazione** - Click sul pulsante verde "🚀 Avvia Applicazione"
   - Il server si avvia automaticamente
   - Status diventa "● In esecuzione" (verde)

2. **Apri nel Browser** - Click sul pulsante blu "🌐 Apri nel Browser"
   - Si apre automaticamente il browser predefinito
   - URL: `http://localhost:8000`
   - Interfaccia web completa per convertire file

3. **Usa l'Applicazione Web**
   - Carica file PDF o Word
   - Converti in MediaWiki
   - Scarica risultati

4. **Ferma Applicazione** - Click sul pulsante rosso "⏹️ Ferma Applicazione"
   - Il server si arresta
   - Status torna a "● Pronto" (grigio)

---

## ⚙️ Configurazione Avanzata

### Personalizzazione Porta

Di default l'applicazione usa la porta **8000**. Per cambiarla:

1. Modificare `launcher_gui.py` alla riga:
   ```python
   self.port = 8000  # Cambiare questo valore
   ```
2. Ricreare l'eseguibile con `build.bat`

### Aggiungere un'Icona

1. Creare o scaricare un file `icon.ico`
2. Posizionarlo nella cartella root del progetto
3. Modificare `build_exe.spec` alla riga:
   ```python
   icon='icon.ico',  # Invece di icon=None
   ```
4. Ricreare l'eseguibile con `build.bat`

---

## 🐛 Risoluzione Problemi

### SmartScreen Blocca l'Eseguibile

**Causa**: Windows protegge gli eseguibili non firmati digitalmente.

**Soluzione**:
1. Click destro su `ConvertitorePDF.exe`
2. Proprietà → Generale
3. Spunta "Sblocca" (se presente)
4. Click su "OK"

Oppure:
- Click su "Maggiori informazioni" → "Esegui comunque"

### Antivirus Segnala Virus (Falso Positivo)

**Causa**: PyInstaller crea exe che alcuni antivirus considerano sospetti.

**Soluzioni**:
1. Aggiungere eccezione nell'antivirus per `ConvertitorePDF.exe`
2. Testare con [VirusTotal](https://www.virustotal.com/) per verificare
3. Firmare digitalmente l'exe (richiede certificato)

### Errore "Port Already in Use"

**Causa**: La porta 8000 è già occupata da un altro programma.

**Soluzioni**:
1. Chiudere altri programmi che usano la porta 8000
2. Cambiare porta (vedi "Configurazione Avanzata")

### Server non si Avvia

**Verifica**:
1. Controllare il log nella finestra GUI
2. Verificare che la cartella `immagini/` esista
3. Verificare che ci sia spazio su disco

### Frontend non si Carica nel Browser

**Verifica**:
1. Il frontend è stato compilato? Controllare `frontend/dist/pdf-word-mediawiki/browser/`
2. Rifare la build con `build.bat`
3. Controllare che il browser non blocchi `localhost`

---

## 📊 Dimensioni e Performance

| Aspetto | Valore |
|---------|--------|
| Dimensione eseguibile | 50-80 MB |
| Dimensione compressa (ZIP) | 25-35 MB |
| Tempo primo avvio | 3-5 secondi |
| Tempo avvii successivi | 1-2 secondi |
| RAM utilizzata | ~150-250 MB |
| Spazio su disco richiesto | ~200 MB (con temp files) |

---

## 📦 Distribuzione

### Metodo 1: File Singolo

1. Copiare `dist/ConvertitorePDF.exe` su una chiavetta USB
2. Distribuire agli utenti
3. Gli utenti eseguono direttamente l'exe

### Metodo 2: ZIP Compresso

1. Comprimere `dist/ConvertitorePDF.exe` in un file ZIP
2. Distribuire via email o cloud
3. Gli utenti estraggono ed eseguono

### Metodo 3: Installer MSI (Avanzato)

Usare tool come **Inno Setup** o **InstallForge** per creare un installer professionale:

1. Download [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Creare script di installazione
3. Generare file `.exe` installer
4. Distribuire l'installer

---

## 🔐 Sicurezza e Firma Digitale

### Firma Digitale (Opzionale)

Per eliminare i warning di SmartScreen:

1. **Acquistare certificato** di code signing (~€70-300/anno)
   - Provider: DigiCert, Sectigo, GlobalSign
2. **Firmare l'exe** con `signtool.exe` (Windows SDK)
   ```batch
   signtool sign /f certificato.pfx /p password /t http://timestamp.digicert.com ConvertitorePDF.exe
   ```
3. Distribuire l'exe firmato

**Costi**:
- Certificato individuale: €70-150/anno
- Certificato aziendale: €150-300/anno

---

## 🔄 Aggiornamenti

### Distribuire Nuove Versioni

1. Modificare il codice sorgente
2. Incrementare versione in `backend/app/main.py`:
   ```python
   version="1.1.0",  # Aggiornare qui
   ```
3. Ricreare exe con `build.bat`
4. Distribuire nuovo exe agli utenti

### Auto-Update (Futuro)

Possibile implementare sistema di auto-update:
- Check version su server remoto
- Download automatico nuove versioni
- Applicazione aggiornamento

---

## 🆘 Supporto

### Log di Debug

Per debugging avanzato:

1. Modificare `build_exe.spec`:
   ```python
   console=True,  # Mostra console per debug
   debug=True,    # Attiva debug mode
   ```
2. Ricreare exe
3. La console mostrerà log dettagliati

### Contatti

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: your-email@example.com
- **Documentazione**: [Wiki del progetto]

---

## 📝 Licenza

Vedere file `LICENSE` nel repository per dettagli sulla licenza.

---

## ✅ Checklist Build per Produzione

Prima di distribuire l'eseguibile:

- [ ] Build frontend completata senza errori
- [ ] Eseguibile testato su almeno 2 PC Windows diversi
- [ ] Funzionalità di conversione testate (PDF e DOCX)
- [ ] Nessun crash o errore critico
- [ ] Log verificati per warning importanti
- [ ] README e documentazione aggiornati
- [ ] Versione incrementata
- [ ] (Opzionale) Eseguibile firmato digitalmente
- [ ] (Opzionale) Antivirus scan completato
- [ ] (Opzionale) Installer MSI creato

---

**Ultimo aggiornamento**: Ottobre 2025
**Versione documento**: 1.0

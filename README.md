# Convertitore da PDF/Word a MediaWiki

Un'applicazione full-stack che converte documenti PDF e Word (.docx) in formato markup MediaWiki, estraendo sia il testo che le immagini.

> **Nota**: Per un'analisi dettagliata del progetto e dell'architettura, vedi [Analisi.md](Analisi.md)

## Avvio Rapido

### Opzione 1: Usando gli Script (Consigliato)

**Windows:**
```cmd
setup.bat          # Solo la prima volta
start-backend.bat  # Terminale 1
start-frontend.bat # Terminale 2
```

**Linux/Mac:**
```bash
chmod +x setup.sh start-backend.sh start-frontend.sh
./setup.sh          # Solo la prima volta
./start-backend.sh  # Terminale 1
./start-frontend.sh # Terminale 2
```

### Opzione 2: Manuale

```bash
# Backend
cd backend
uv venv && source .venv/bin/activate  # o .venv\Scripts\activate su Windows
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Frontend (in un nuovo terminale)
cd frontend
npm install
npm start
```

Apri http://localhost:4200 e inizia a convertire!

## Funzionalità

- **Conversione Documenti**: Converte file PDF e DOCX in markup MediaWiki
- **Estrazione Immagini**: Estrae e salva automaticamente le immagini dai documenti
- **Formattazione MediaWiki**: Gestisce titoli, tabelle, liste e formattazione di base del testo
- **Interfaccia User-Friendly**: Frontend Angular moderno con upload drag-and-drop
- **Documentazione API**: Documentazione API interattiva Scalar su `/scalar`
- **Galleria Immagini**: Galleria visuale di tutte le immagini estratte

## Stack Tecnologico

### Backend
- **FastAPI**: Framework web Python moderno
- **PyMuPDF (fitz)**: Estrazione testo e immagini da PDF
- **python-docx**: Elaborazione documenti DOCX
- **Pydantic**: Validazione dati e gestione configurazioni
- **uv**: Package manager Python veloce

### Frontend
- **Angular 18**: Framework web moderno con componenti standalone
- **TypeScript**: JavaScript type-safe
- **RxJS**: Programmazione reattiva

## Struttura del Progetto

```
.
├── backend/
│   ├── app/
│   │   ├── core/           # Configurazione
│   │   ├── models/         # DTO Pydantic
│   │   ├── services/       # Logica di business
│   │   ├── routers/        # Endpoint API
│   │   ├── static/         # File statici (immagini)
│   │   └── main.py         # App FastAPI
│   ├── uploads/            # Upload temporanei
│   ├── output/             # File convertiti
│   └── pyproject.toml      # Dipendenze Python
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # Componenti Angular
│   │   │   └── services/   # Servizi API
│   │   └── environments/   # Configurazioni ambiente
│   └── package.json        # Dipendenze Node
│
├── CLAUDE.md              # Linee guida sviluppo
└── README.md              # Questo file
```

## Installazione e Setup

### Prerequisiti

- **Python 3.12+**
- **Node.js 18+** e npm
- **uv** package manager per Python

#### Installare uv

Se non hai `uv` installato:

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Oppure tramite pip:
```bash
pip install uv
```

### Setup Backend

1. Vai alla directory backend:
```bash
cd backend
```

2. Crea ambiente virtuale con uv:
```bash
uv venv
```

3. Attiva ambiente virtuale:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Installa dipendenze:
```bash
uv sync
```

5. Installa ruff per la formattazione del codice:
```bash
uv pip install ruff
```

### Setup Frontend

1. Vai alla directory frontend:
```bash
cd frontend
```

2. Installa dipendenze:
```bash
npm install
```

## Eseguire l'Applicazione

### Avviare il Server Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Il backend sarà disponibile su:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Scalar Docs: http://localhost:8000/scalar
- ReDoc: http://localhost:8000/redoc

### Avviare il Server Frontend

```bash
cd frontend
npm start
```

Il frontend sarà disponibile su: http://localhost:4200

## Utilizzo

1. Apri http://localhost:4200 nel browser
2. Clicca "Choose File" e seleziona un file PDF o DOCX
3. Clicca "Convert to MediaWiki"
4. Visualizza il testo MediaWiki convertito nella textarea
5. Usa i pulsanti "Copy to Clipboard" o "Download as .wiki"
6. Visualizza le immagini estratte nella galleria sottostante

## Endpoint API

### Health Check
```
GET /api/health
```
Restituisce lo stato di salute del server.

### Converti Documento
```
POST /api/convert
Content-Type: multipart/form-data

file: <file PDF o DOCX>
```
Restituisce:
```json
{
  "id": "job-uuid",
  "filename": "document.pdf",
  "mediawiki_text": "= Titolo =\n\nContenuto testo...",
  "images": ["/immagini/img-123.png"],
  "warnings": []
}
```

### Scarica Output
```
GET /api/files/output/{job_id}
```
Scarica il file .wiki convertito.

### Immagini Statiche
```
GET /immagini/{filename}
```
Serve i file immagine estratti.

## Linee Guida per lo Sviluppo

Vedi [CLAUDE.md](CLAUDE.md) per le linee guida dettagliate di sviluppo incluse:
- Formattazione codice con ruff (obbligatorio)
- Uso di Pydantic invece di dataclasses
- Limiti lunghezza file (max 1000 righe)
- Best practices per Python e Angular

## Formattazione del Codice

Dopo aver modificato un file Python, esegui:
```bash
cd backend
uv run ruff format path/to/file.py
```

## Configurazione

La configurazione del backend è gestita in `backend/app/core/config.py`:

- `max_file_size_mb`: Dimensione massima upload (default: 50MB)
- `allowed_extensions`: Tipi di file supportati (default: .pdf, .docx)
- `cors_origins`: Origini CORS consentite (default: tutte)

## Regole di Conversione MediaWiki

Il convertitore applica queste regole di formattazione MediaWiki:

- **Titoli**: `= H1 =`, `== H2 ==`, ecc.
- **Grassetto**: `'''testo'''`
- **Corsivo**: `''testo''`
- **Liste**: Numerate (`#`) e puntate (`*`)
- **Tabelle**: formato `{| class="wikitable"`
- **Link**: `[http://url testo]`
- **Immagini**: `[[File:nomefile|thumb]]`

### Esempio Output

**Input** (DOCX con titolo "Introduzione"):
```
Introduzione
Questo è un documento di esempio con testo in grassetto e un link a https://example.com
```

**Output** (MediaWiki):
```wiki
== Introduzione ==

Questo è un documento di esempio con testo in grassetto e un link a [https://example.com]

== Immagini ==

[[File:docx_img0-a1b2c3d4.png|thumb|Immagine estratta]]
```

## Testare l'API

Puoi testare l'API direttamente usando curl o strumenti come Postman:

```bash
# Health check
curl http://localhost:8000/api/health

# Convertire un file
curl -X POST http://localhost:8000/api/convert \
  -F "file=@/percorso/al/documento.pdf"

# Scaricare output
curl http://localhost:8000/api/files/output/{job-id} -o output.wiki
```

## Limitazioni Note

- **Estrazione Testo PDF**: PDF scannerizzati senza OCR potrebbero non estrarre correttamente il testo
- **Tabelle Complesse**: Layout di tabelle molto complessi potrebbero non convertirsi perfettamente
- **Stili Font**: Il rilevamento grassetto/corsivo è limitato nell'estrazione PDF
- **Qualità Immagini**: Le immagini sono estratte così come sono; non viene eseguita ottimizzazione
- **File Grandi**: File oltre 50MB vengono rifiutati (configurabile)

## Risoluzione Problemi

### Problemi Backend

**Comando `uv` non trovato:**
```bash
# Assicurati che uv sia nel PATH o reinstalla
pip install uv
```

**Porta già in uso:**
```bash
# Usa una porta diversa
uv run uvicorn app.main:app --port 8001
```

**Errori di import o modulo non trovato:**
```bash
# Reinstalla dipendenze
cd backend
rm -rf .venv
uv venv
uv sync
```

**Installazione PyMuPDF fallisce su Windows:**
```bash
# Prova a installare prima gli strumenti di build
# Scarica da: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Poi esegui: uv sync
```

**"No module named 'app'":**
```bash
# Assicurati di essere nella directory backend
cd backend
uv run uvicorn app.main:app --reload
```

### Problemi Frontend

**Porta 4200 già in uso:**
```bash
# Usa una porta diversa
ng serve --port 4201
```

**Modulo non trovato o errori npm:**
```bash
# Pulisci cache e reinstalla
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Angular CLI non trovato:**
```bash
# Installa Angular CLI globalmente
npm install -g @angular/cli
```

**Errori proxy (problemi CORS):**
- Assicurati che il backend sia in esecuzione sulla porta 8000
- Controlla la configurazione di [proxy.conf.json](frontend/proxy.conf.json)
- Riavvia il server dev frontend dopo modifiche al backend

### Problemi Generali

**Immagini non si caricano:**
- Verifica che esista la directory `backend/app/static/immagini/`
- Verifica che CORS sia abilitato nel backend
- Controlla la console del browser per errori 404

**La conversione richiede troppo tempo:**
- PDF grandi con molte immagini possono richiedere tempo
- Controlla la console del backend per progressi/errori
- Considera di aumentare il timeout nel frontend se necessario

## Roadmap

Miglioramenti futuri (vedi [Analisi.md](Analisi.md) per dettagli):

- [ ] Supporto per formati ODT e RTF
- [ ] Integrazione OCR per PDF scannerizzati (Tesseract)
- [ ] Coda job asincrona per file grandi (Celery/RQ)
- [ ] Anteprima MediaWiki live nel frontend
- [ ] Autenticazione utenti (JWT)
- [ ] Elaborazione batch di file
- [ ] Configurazione regole di conversione personalizzate

## Contribuire

Segui le linee guida in [CLAUDE.md](CLAUDE.md) per stile del codice e best practices:

1. Usa `uv` per tutte le dipendenze Python
2. Usa modelli Pydantic invece di dataclasses
3. Esegui `ruff format` dopo aver modificato file Python
4. Mantieni i file sotto 1000 righe
5. Segui le convenzioni di type hints e docstring

## Licenza

Questo progetto è fornito così com'è per la conversione di documenti PDF e Word in formato MediaWiki.

## Struttura Directory Output

I file vengono salvati nelle seguenti posizioni:
- **Immagini**: `output/immagini/` - Tutte le immagini estratte
- **Testo wiki**: `output/testo_wiki/` - File convertiti denominati come `nome_file_originale.wiki`

Esempio: Se carichi `pippo.pdf`, il testo convertito sarà salvato come `output/testo_wiki/pippo.wiki`

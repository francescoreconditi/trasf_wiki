# Progetto: Trasformazione PDF/Word → MediaWiki con estrazione immagini

## Obiettivo

Realizzare un sistema che consenta di caricare un file **PDF** o **Word (.docx)**, estrarne **testo** e **immagini**, convertire il testo in **formato MediaWiki**, salvare le immagini nella directory **`immagini/`**, e mostrare il testo convertito nel **frontend Angular**.

---

# ARCHITETTURA (alto livello)

* **Frontend (Angular)**

  * UI per upload file (PDF/Word)
  * Chiamate REST al backend
  * Visualizzazione testo MediaWiki in textarea/preview
  * Galleria immagini (servite dallo static server del BE)
* **Backend (FastAPI)**

  * Endpoint REST separati per upload, conversione, download, stato job
  * Estrazione **testo** + **immagini** da PDF (PyMuPDF o pdfplumber + fitz) e da DOCX (python-docx / mammoth)
  * Conversione testo → **MediaWiki markup**
  * Storage su filesystem: `uploads/`, `immagini/`, `output/`
  * Documentazione **Scalar** basata su OpenAPI di FastAPI

```
[Angular] --HTTP--> [FastAPI] --parsers--> [Extractor] --files--> /uploads
                                          └--> [Converter] --> wikitext → /output
                                          └--> [ImageSaver] --> /immagini
```

---

# STRUTTURA REPO (monorepo opzionale)

```
root/
  backend/
    app/
      main.py
      core/
        config.py
        logging.py
      models/
        dto.py
      services/
        extract_pdf.py
        extract_docx.py
        convert_wikitext.py
        storage.py
      routers/
        convert.py
        files.py
        health.py
      static/
        immagini/            # <-- directory images esposte
      uploads/
      output/
    tests/
    pyproject.toml or requirements.txt
    Dockerfile
  frontend/
    angular.json
    src/
      app/
        services/api.service.ts
        components/upload/upload.component.ts
        components/result/result.component.ts
        components/gallery/gallery.component.ts
        app.routes.ts
      environments/
        environment.ts
    package.json
    Dockerfile
  docker-compose.yml
  README.md
```

---

# BACKEND (FastAPI)

## Dipendenze principali

* `fastapi`, `uvicorn`
* `python-multipart` (upload)
* **PDF**: `PyMuPDF` (alias `fitz`) per testo+immagini (robusto) oppure `pdfplumber` per testo, ma PyMuPDF basta da solo
* **DOCX**: `python-docx` per testo+immagini (o `mammoth` per migliore qualità testo, con estrazione immagini via zipfile)
* `pillow` per normalizzare immagini
* `pydantic` (DTO)
* `jinja2` (se servono template)
* **CORS**: `fastapi[all]` o `starlette.middleware.cors`

## Configurazione (core/config.py)

* Path base: `BASE_DIR`, `UPLOAD_DIR`, `IMAGES_DIR`, `OUTPUT_DIR`
* Limiti: estensioni consentite: `.pdf`, `.docx`; max size
* Flag: `KEEP_ORIGINAL_NAMES` (normalizzare nomi file)

## DTO (models/dto.py)

* `ConvertResponse`: `{ id: str, filename: str, mediawiki_text: str, images: list[str], warnings: list[str] }`
* `JobStatus`: `{ id: str, status: Literal["PENDING","RUNNING","DONE","ERROR"], error: Optional[str] }` (se si introduce modalità async)

## Servizi

### Estrazione PDF (services/extract_pdf.py)

* Apri con `fitz.open(stream=..., filetype="pdf")`
* Per ogni pagina:

  * Testo: `page.get_text("text")`
  * Immagini: `page.get_images(full=True)` → `doc.extract_image(xref)` → salva come PNG/JPEG in `static/immagini/`
* Restituisce: `Extracted(text:str, images:list[str], meta:dict)`

### Estrazione DOCX (services/extract_docx.py)

* Con `python-docx` per paragrafo/liste/tabelle
* Immagini via `doc.part.package` (o più semplice: aprire .docx come zip e leggere `/word/media/*`)
* Salvataggio immagini in `static/immagini/` con nomi univoci

### Conversione testo → MediaWiki (services/convert_wikitext.py)

Regole base (estendibili):

* Heading: mappa stili/gerarchie → `= H1 =`, `== H2 ==`, ...
* Bold: `**`/runs bold → `'''grassetto'''`
* Italic: `''corsivo''`
* Liste: numerate → `#`; puntate → `*`
* Tabelle: opzionale → `{| class="wikitable"` righe `|-` celle `|`/`!`
* Link: URL → `[http://... testo]`
* Immagini: `[[File:immagine.png|thumb|alt]]`
* Paragrafi separati da righe vuote

### Storage (services/storage.py)

* Genera UUID per job
* Funzioni: `save_upload(file)`, `save_image(bytes, ext)`, `save_output(job_id, text)`
* Sanitize filename, evita collisioni, ritorna path relativo per frontend

## Router & Endpoint

Organizzare per responsabilità.

### `routers/health.py`

* `GET /health` → `{status:"ok"}`

### `routers/convert.py`

* `POST /convert` (sync semplice)

  * Multipart: `file: UploadFile`
  * Logica: rileva estensione → estrai (PDF o DOCX) → converte in MediaWiki → salva immagini → ritorna `ConvertResponse`
* **Opzione async** (estensione futura):

  * `POST /convert/async` → crea job, subito `202 Accepted` con `job_id`
  * `GET /convert/{job_id}` → `JobStatus` + (se DONE) payload

### `routers/files.py`

* Serve statici

  * Monta `StaticFiles(directory="static/immagini", name="immagini")` su `/immagini`
  * (Opz.) `GET /output/{job_id}.txt` per scaricare wikitext

## Documentazione con **Scalar**

* Esporre OpenAPI JSON di FastAPI su `/openapi.json`
* Servire pagina Scalar su `/docs` (o `/scalar`) che carica l’OpenAPI:

  * Opzione A (CDN): creare route che restituisce HTML con `<script>` di Scalar che punta a `/openapi.json`.
  * Opzione B (package): usare un'integrazione (se disponibile) tipo `scalar_fastapi` per montare l’UI.
* Mantenere anche `/redoc` e/o `/docs` (Swagger) se utile.

## Esempio di `main.py` (stralcio)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from app.routers import convert, files, health

app = FastAPI(title="PDF/Word → MediaWiki API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(convert.router, prefix="/api")
app.include_router(files.router)

# Static per immagini
app.mount("/immagini", StaticFiles(directory="app/static/immagini"), name="immagini")

# Route Scalar (versione semplice via HTML)
from fastapi.responses import HTMLResponse

@app.get("/scalar", response_class=HTMLResponse)
def scalar_docs():
    return """
    <!doctype html>
    <html>
      <head><meta charset='utf-8'><title>API Docs</title></head>
      <body>
        <script id="api-reference" data-url="/openapi.json"></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
      </body>
    </html>
    """
```

## Esempio di `routers/convert.py` (stralcio)

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.extract_pdf import extract_pdf
from app.services.extract_docx import extract_docx
from app.services.convert_wikitext import to_wikitext
from app.services.storage import save_upload, save_output

router = APIRouter(prefix="/convert", tags=["convert"])

@router.post("/", summary="Converte PDF/DOCX in MediaWiki con estrazione immagini")
async def convert(file: UploadFile = File(...)):
    ext = (file.filename or "").lower().rsplit('.', 1)[-1]
    if ext not in ("pdf", "docx"):
        raise HTTPException(400, detail="Estensione non supportata")

    tmp_path = save_upload(file)

    if ext == "pdf":
        extracted = extract_pdf(tmp_path)
    else:
        extracted = extract_docx(tmp_path)

    wikitext, warnings = to_wikitext(extracted)
    out = save_output(wikitext)

    return {
        "filename": file.filename,
        "mediawiki_text": wikitext,
        "images": extracted.images,  # percorsi relativi sotto /immagini
        "warnings": warnings,
    }
```

---

# FRONTEND (Angular)

## Requisiti

* Angular 17+
* Moduli: `HttpClientModule`, `ReactiveFormsModule`
* Componenti:

  * `UploadComponent` (form upload)
  * `ResultComponent` (textarea + copia negli appunti)
  * `GalleryComponent` (griglia immagini da `/immagini/...`)
* Service: `ApiService` per chiamare `/api/convert`

## Flusso UI

1. Utente seleziona file (PDF/DOCX)
2. Click "Converti"
3. FE → `POST /api/convert` con `multipart/form-data`
4. Mostra spinner, attendi risposta
5. Visualizza `mediawiki_text` in textarea, galleria da `images[]`
6. Pulsanti: "Copia", "Scarica .txt", "Reset"

## Endpoint BE utilizzati

* `POST /api/convert` → `{ mediawiki_text, images[] }`
* Static: `/immagini/{filename}` (img `src`)

## ApiService (stralcio)

```ts
// src/app/services/api.service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface ConvertResponse {
  filename: string;
  mediawiki_text: string;
  images: string[]; // percorsi relativi (es. "/immagini/img-123.png")
  warnings: string[];
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = '/api'; // configurabile via environment
  constructor(private http: HttpClient) {}

  convert(file: File) {
    const form = new FormData();
    form.append('file', file, file.name);
    return this.http.post<ConvertResponse>(`${this.base}/convert`, form);
  }
}
```

## UploadComponent (stralcio)

```ts
// src/app/components/upload/upload.component.ts
import { Component } from '@angular/core';
import { ApiService, ConvertResponse } from '../../services/api.service';

@Component({
  selector: 'app-upload',
  template: `
  <form (submit)="onSubmit($event)">
    <input type="file" accept=".pdf,.docx" (change)="onFile($event)" required>
    <button type="submit" [disabled]="!file || loading">Converti</button>
  </form>

  <div *ngIf="loading">Elaborazione…</div>

  <app-result *ngIf="result" [text]="result.mediawiki_text"></app-result>
  <app-gallery *ngIf="result" [images]="result.images"></app-gallery>
  `
})
export class UploadComponent {
  file?: File;
  loading = false;
  result?: ConvertResponse;
  constructor(private api: ApiService) {}

  onFile(e: Event) {
    const input = e.target as HTMLInputElement;
    this.file = input.files?.[0] || undefined;
  }

  onSubmit(e: Event) {
    e.preventDefault();
    if (!this.file) return;
    this.loading = true;
    this.api.convert(this.file).subscribe({
      next: (res) => { this.result = res; this.loading = false; },
      error: () => { this.loading = false; alert('Errore di conversione'); }
    });
  }
}
```

## ResultComponent (stralcio)

```ts
// src/app/components/result/result.component.ts
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-result',
  template: `
    <label>Testo MediaWiki</label>
    <textarea [value]="text" rows="20" style="width:100%"></textarea>
    <button (click)="copy()">Copia</button>
    <a [href]="makeDownload()" download="output.wiki">Scarica .txt</a>
  `
})
export class ResultComponent {
  @Input() text = '';
  copy() { navigator.clipboard.writeText(this.text); }
  makeDownload(){ return 'data:text/plain;charset=utf-8,'+encodeURIComponent(this.text); }
}
```

## GalleryComponent (stralcio)

```ts
// src/app/components/gallery/gallery.component.ts
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-gallery',
  template: `
    <h3>Immagini estratte</h3>
    <div class="grid">
      <img *ngFor="let src of images" [src]="src" alt="Estratta" />
    </div>
  `,
  styles: [`.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}`]
})
export class GalleryComponent {
  @Input() images: string[] = [];
}
```

---

# CONVERSIONE IN MEDIAWIKI — Dettagli regole

1. **Titoli**: rilevare heading (DOCX: style name; PDF: euristica dimensione font)

   * Livelli 1–6 → `=`, `==`, …, `======`
2. **Paragrafi**: conserva interlinea con riga vuota
3. **Enfasi**: bold → `'''...'''`, italic → `''...''`
4. **Liste**: numerate `#`, puntate `*`, nested mantenendo livello
5. **Tabelle** (opz.):

   * Inizio `{| class="wikitable"}` / fine `|}`
   * Header `!`, celle `|` con `|-` per nuove righe
6. **Link**: pattern URL → `[URL titolo]` (se testo precedente immediato)
7. **Immagini**: per ogni immagine salvata → suggerire markup `[[File:filename|thumb]]`
8. **Note**: eventuali note a piè di pagina → `ref` (se identificabili)

---

# SICUREZZA & VALIDAZIONI

* **CORS** limitato a domini FE
* **Dimensione file** (es. 50MB)
* **MIME sniffing**: verificare magic bytes (PDF `%PDF`, DOCX zip)
* **Sanitizzazione nomi file**
* **Rate limit** (reverse proxy o middleware)
* **Logging** con `uvicorn.access` + app logger

---

# TEST

* Unit test per: estrazione PDF/DOCX, conversione regole, storage
* E2E: invio file → verifica wikitext atteso e immagini salvate

---

# DEPLOY

* **Docker** per FE/BE
* **Nginx** davanti a FastAPI per statici e proxy
* Variabili ambiente per path base
* Persistenza volumi: `uploads/`, `output/`, `static/immagini/`

---

# ROADMAP (estensioni)

* Supporto **ODT**, **RTF**
* Coda job (Celery/RQ) per file pesanti
* **Preview live** MediaWiki (renderer lato FE)
* OCR per PDF scansiti (Tesseract)
* Autenticazione (JWT) per uso protetto

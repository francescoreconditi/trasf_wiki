# 📖 Manuale Utente - Convertitore PDF/Word in MediaWiki

Guida semplice e completa per convertire i tuoi documenti PDF, Word, ODT e RTF in formato MediaWiki (Wikipedia).

---

## 📋 Cosa Serve

- **Computer Windows** (Windows 7 o superiore)
- **Un documento** da convertire (PDF, DOCX, ODT o RTF)
- **Pochi minuti** di tempo

**Non serve installare nulla!** Il programma funziona da solo.

---

## 🚀 Passo 1: Avviare il Programma

### Prima Volta

1. **Trova il file** `ConvertitorePDF.exe` sul tuo computer
2. **Doppio click** sul file per aprirlo
3. **Potrebbe apparire un avviso di Windows**:

   ```
   Windows ha protetto il PC
   L'esecuzione di questa app potrebbe mettere a rischio il PC
   ```

   **Non preoccuparti! È normale.** Windows mostra questo avviso perché il programma non è firmato digitalmente.

   **Cosa fare**:
   - Clicca su **"Ulteriori informazioni"** o **"Maggiori informazioni"**
   - Poi clicca su **"Esegui comunque"**

4. **Si apre una finestra** con il programma

### Volte Successive

Doppio click su `ConvertitorePDF.exe` e il programma si apre subito!

---

## 🎯 Passo 2: Aprire l'Applicazione Web

Quando si apre il programma, vedrai una finestra con 3 pulsanti principali:

1. **🚀 Avvia Applicazione** (pulsante verde)
2. **🌐 Apri nel Browser** (pulsante blu)
3. **⏹️ Ferma Applicazione** (pulsante rosso)

### Procedura

1. **Clicca sul pulsante verde** "🚀 Avvia Applicazione"
   - Aspetta qualche secondo
   - Vedrai nel log: "✅ Server avviato con successo!"
   - Lo status diventa **"In esecuzione"** (verde)

2. **Clicca sul pulsante blu** "🌐 Apri nel Browser"
   - Si apre automaticamente il tuo browser (Chrome, Firefox, Edge, ecc.)
   - Vedi l'interfaccia di conversione

**Ora sei pronto per convertire i tuoi documenti!**

---

## 📄 Passo 3: Convertire un Documento

### 3.1 Caricare il File

Nell'interfaccia web vedrai:

```
┌─────────────────────────────────────────┐
│  Upload Document                        │
│                                         │
│  Formati supportati:                    │
│  PDF, DOCX, ODT, RTF                   │
│                                         │
│  [ Scegli file ]  Nessun file          │
│                                         │
│  [ Convert to MediaWiki ]              │
└─────────────────────────────────────────┘
```

**Come fare**:

1. **Clicca su "Scegli file"** (o simile, dipende dal browser)
2. **Naviga** fino al tuo documento
3. **Seleziona** il file che vuoi convertire:
   - ✅ PDF (`.pdf`)
   - ✅ Word (`.docx`)
   - ✅ OpenDocument (`.odt`)
   - ✅ Rich Text (`.rtf`)
4. **Clicca "Apri"**

Vedrai il nome del file selezionato e la sua dimensione (es. "Documento.pdf (1.2 MB)").

### 3.2 Avviare la Conversione

1. **Clicca sul pulsante blu** "Convert to MediaWiki"
2. **Aspetta** che la conversione finisca (può richiedere alcuni secondi)
3. **Vedrai apparire il risultato** sotto

---

## 💾 Passo 4: Vedere e Salvare il Risultato

Dopo la conversione, vedrai due modalità di visualizzazione:

### 📝 Modalità "Raw Markup" (Testo Grezzo)

Mostra il codice MediaWiki da copiare. Vedrai qualcosa tipo:

```
== Titolo del Documento ==

Questo è il testo convertito.

* Lista puntata
* Altro elemento

{| class="zcsTable"
|-
| Cella 1 | Cella 2
|}
```

### 👁️ Modalità "Preview" (Anteprima)

Mostra come apparirà il documento su Wikipedia/MediaWiki, con:
- Titoli formattati
- Testo in grassetto e corsivo
- Liste puntate e numerate
- Tabelle
- **Immagini** (se presenti nel documento)

**Puoi passare da una modalità all'altra** cliccando sui pulsanti "Raw Markup" e "Preview".

---

## 📋 Passo 5: Copiare il Testo Convertito

Hai **due opzioni** per copiare il testo:

### Opzione A: Copia negli Appunti

1. **Assicurati di essere in modalità "Raw Markup"**
2. **Clicca sul pulsante** "📋 Copy to Clipboard"
3. **Vedrai un messaggio** "Text copied to clipboard!"
4. **Ora puoi incollare** il testo ovunque (Ctrl+V):
   - Editor MediaWiki
   - Wikipedia
   - Documento Word
   - Qualsiasi altra applicazione

### Opzione B: Scarica come File

1. **Clicca sul pulsante** "💾 Download .wiki file"
2. **Il file viene scaricato** automaticamente nella tua cartella Download
3. **Il nome del file** sarà uguale al documento originale ma con estensione `.wiki`
   - Esempio: `MioDocumento.pdf` → `MioDocumento.wiki`
4. **Apri il file** con Blocco Note o qualsiasi editor di testo per vedere/copiare il contenuto

---

## 🖼️ Passo 6: Salvare le Immagini

Se il tuo documento contiene immagini, il programma le estrae automaticamente.

### Dove si Trovano le Immagini?

Le immagini estratte vengono salvate in una cartella speciale chiamata **"immagini"** che si trova:

```
Nella stessa cartella dove hai messo ConvertitorePDF.exe

Esempio:
C:\Utenti\TuoNome\Desktop\ConvertitorePDF.exe
                        └─ immagini\
                           ├─ pdf_page1_img0.png
                           ├─ pdf_page2_img0.jpg
                           └─ ...
```

### Come Visualizzare le Immagini

**Metodo 1: Dalla Pagina Web**

1. Nella pagina web, **scorri in basso** dopo la conversione
2. Vedrai una sezione **"Extracted Images"** con tutte le immagini
3. **Clicca su un'immagine** per ingrandirla
4. **Click destro → "Salva immagine con nome"** per salvarla dove vuoi

**Metodo 2: Dalla Cartella**

1. **Apri Esplora File** di Windows
2. **Vai alla cartella** dove hai `ConvertitorePDF.exe`
3. **Apri la cartella "immagini"**
4. **Troverai tutte le immagini** estratte dai documenti convertiti
5. **Copia o sposta** le immagini dove preferisci

### Nomi delle Immagini

Le immagini hanno nomi automatici che indicano:
- **Tipo di documento**: `pdf_`, `docx_`
- **Numero pagina**: `page1_`, `page2_`
- **Numero immagine**: `img0`, `img1`, ecc.
- **Estensione**: `.png`, `.jpg`, `.jpeg`

**Esempio**: `pdf_page3_img2.png` = immagine n°2 dalla pagina 3 di un PDF

### Come Usare le Immagini su MediaWiki

Nel testo convertito, le immagini sono già inserite con il codice MediaWiki:

```
[[Immagine:pdf_page1_img0.png]]
```

**Per usarle su Wikipedia/MediaWiki**:

1. **Carica le immagini** su MediaWiki (usando la funzione "Carica file")
2. **Copia il testo convertito** (con i riferimenti alle immagini)
3. **Incolla** nella pagina wiki
4. Le immagini appariranno automaticamente (se caricate con lo stesso nome)

---

## 🔄 Convertire Altri Documenti

Vuoi convertire un altro documento? Facile!

1. **Scorri in alto** nella pagina web
2. Troverai il pulsante **"🔄 Convert Another Document"**
3. **Clicca** e riparti dal Passo 3

**Oppure**:

Ricarica la pagina del browser (F5 o Ctrl+R) per ricominciare.

---

## ⏹️ Chiudere il Programma

Quando hai finito:

1. **Chiudi il browser** (se vuoi)
2. **Torna alla finestra del programma**
3. **Clicca sul pulsante rosso** "⏹️ Ferma Applicazione"
4. **Aspetta che il server si fermi**
5. **Chiudi la finestra** del programma

**Importante**: Ricorda sempre di fermare l'applicazione prima di chiudere la finestra!

---

## ❓ Domande Frequenti (FAQ)

### ❓ Il programma non si apre. Cosa faccio?

**Prova queste soluzioni**:

1. **Fai click destro** su `ConvertitorePDF.exe` → **"Esegui come amministratore"**
2. **Verifica** che il file non sia bloccato:
   - Click destro → Proprietà
   - Tab "Generale"
   - Se vedi "Sblocca", spuntalo e clicca OK
3. **Disabilita temporaneamente l'antivirus** (alcuni antivirus bloccano il programma)

### ❓ Il browser non si apre automaticamente

**Soluzione manuale**:

1. Nella finestra del programma, cerca l'URL: **http://localhost:8000**
2. **Apri il browser manualmente** (Chrome, Firefox, Edge...)
3. **Scrivi nella barra degli indirizzi**: `http://localhost:8000`
4. Premi **Invio**

### ❓ Errore "Port Already in Use"

**Significa**: Un altro programma sta usando la porta 8000.

**Soluzioni**:
1. **Chiudi altri programmi** che potrebbero usare la porta 8000
2. **Riavvia il computer** e riprova
3. **Ferma e riavvia** l'applicazione

### ❓ La conversione fallisce o il testo è confuso

**Possibili cause**:
- **File danneggiato**: Prova a riaprire e salvare il documento originale
- **File protetto da password**: Rimuovi la password prima di convertire
- **Formato non supportato**: Verifica che sia PDF, DOCX, ODT o RTF
- **File troppo grande**: Il limite è 50 MB

**Soluzioni**:
- Prova a **salvare il documento in un altro formato** (es. da DOC a DOCX)
- **Riduci la dimensione** del file (comprimi le immagini)
- **Dividi documenti molto lunghi** in più file

### ❓ Le immagini non vengono estratte

**Nota**: Dipende dal formato:
- ✅ **PDF**: Immagini estratte
- ✅ **DOCX**: Immagini estratte
- ✅ **ODT**: Immagini estratte
- ❌ **RTF**: Immagini NON supportate

Se usi **RTF**, converti prima in DOCX per estrarre le immagini.

### ❓ Il testo convertito ha caratteri strani

**Causa**: Problemi di codifica o font speciali.

**Soluzioni**:
1. Copia il testo in **Blocco Note** prima
2. **Salva da Blocco Note** con codifica UTF-8
3. Poi copia su MediaWiki

### ❓ L'antivirus dice che è un virus!

**È un falso positivo**. Il programma è sicuro.

**Perché succede?**
Gli antivirus a volte segnalano programmi creati con PyInstaller come sospetti.

**Cosa fare?**:
1. **Aggiungi un'eccezione** nell'antivirus per `ConvertitorePDF.exe`
2. **Scarica una versione aggiornata** (se disponibile)
3. **Controlla su VirusTotal** per avere più opinioni

### ❓ Posso usare il programma offline?

**Sì!** Il programma funziona completamente offline, non serve connessione internet.

### ❓ Posso convertire più file alla volta?

**No**, puoi convertire un file alla volta. Per convertire più file:
1. Converti il primo
2. Salva immagini e testo
3. Clicca "Convert Another Document"
4. Ripeti per ogni file

### ❓ Dove vengono salvati i file convertiti?

- **Testo convertito**: Non viene salvato automaticamente. Devi copiarlo o scaricarlo manualmente.
- **Immagini**: Salvate automaticamente nella cartella `immagini\` accanto al programma.

### ❓ Posso copiare il programma su un'altra chiavetta USB?

**Sì!** Il programma è portatile:
1. Copia `ConvertitorePDF.exe` dove vuoi
2. Copia anche la cartella `immagini\` se vuoi mantenere le immagini estratte
3. Esegui da qualsiasi posizione

---

## 💡 Consigli Utili

### ✅ Per Risultati Migliori

1. **Usa documenti ben formattati**
   - Titoli definiti chiaramente
   - Formattazione consistente
   - Immagini di buona qualità

2. **Controlla il risultato**
   - Usa la modalità "Preview" per vedere l'anteprima
   - Verifica che tutto sia stato convertito correttamente
   - Correggi eventuali errori manualmente nel testo wiki

3. **Organizza le immagini**
   - Rinomina le immagini con nomi descrittivi prima di caricarle su MediaWiki
   - Elimina immagini non necessarie dalla cartella `immagini\`

4. **Salva regolarmente**
   - Copia il testo convertito in un file di testo
   - Fai backup della cartella `immagini\` se contiene file importanti

### ⚠️ Cosa NON Fare

- ❌ Non chiudere la finestra del programma senza fermare prima l'applicazione
- ❌ Non eliminare la cartella `immagini\` mentre il programma è in esecuzione
- ❌ Non cercare di convertire file protetti da password senza rimuovere prima la protezione
- ❌ Non aspettarti una conversione perfetta al 100% (potrebbero servire piccole correzioni manuali)

---

## 📞 Hai Bisogno di Aiuto?

Se hai problemi non risolti da questo manuale:

1. **Controlla la sezione FAQ** sopra
2. **Prova a riavviare** il programma
3. **Prova a riavviare** il computer
4. **Contatta il supporto** (se disponibile)

---

## 📝 Riepilogo Veloce

**In 5 minuti**:

1. **Apri** `ConvertitorePDF.exe`
2. **Clicca** 🚀 Avvia Applicazione
3. **Clicca** 🌐 Apri nel Browser
4. **Scegli file** da convertire
5. **Clicca** Convert to MediaWiki
6. **Copia** il testo o **scarica** il file .wiki
7. **Trova** le immagini nella cartella `immagini\`
8. **Chiudi** tutto quando hai finito

**Fine!** 🎉

---

## 📄 Esempio Pratico Completo

Mettiamo che tu voglia convertire una presentazione PowerPoint salvata come PDF chiamata **"RelazioneTrimestrale.pdf"**.

### Passaggi:

1. ✅ **Apri** `ConvertitorePDF.exe`
2. ✅ **Avvia** l'applicazione (pulsante verde)
3. ✅ **Apri** nel browser (pulsante blu)
4. ✅ **Clicca** "Scegli file" e seleziona "RelazioneTrimestrale.pdf"
5. ✅ **Clicca** "Convert to MediaWiki"
6. ✅ **Aspetta** 5-10 secondi per la conversione
7. ✅ **Vedi** il risultato in modalità Preview
8. ✅ **Passa** a Raw Markup
9. ✅ **Clicca** "Copy to Clipboard"
10. ✅ **Apri** il tuo editor MediaWiki/Wikipedia
11. ✅ **Incolla** (Ctrl+V) il testo
12. ✅ **Vai** alla cartella `immagini\` accanto al programma
13. ✅ **Trovi** le immagini estratte (es. `pdf_page1_img0.png`, `pdf_page1_img1.jpg`...)
14. ✅ **Carica** le immagini su MediaWiki con la funzione "Carica file"
15. ✅ **Pubblica** la pagina

**Il tuo documento è ora su MediaWiki!** 🎊

---

**Versione Manuale**: 1.0
**Data**: Novembre 2025
**Compatibilità**: Windows 7, 8, 10, 11

---

✨ **Buona conversione!** ✨

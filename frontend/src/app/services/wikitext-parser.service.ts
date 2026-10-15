import { Injectable } from '@angular/core';

/**
 * Servizio per il parsing di markup MediaWiki in HTML
 * Implementa le regole di conversione per i casi d'uso comuni
 */
@Injectable({
  providedIn: 'root'
})
export class WikitextParserService {

  /**
   * Converte markup MediaWiki in HTML renderizzabile
   * @param wikitext - Testo in formato MediaWiki
   * @returns HTML come stringa
   */
  parseToHtml(wikitext: string): string {
    if (!wikitext || wikitext.trim() === '') {
      return '<p class="empty">Nessun contenuto da visualizzare</p>';
    }

    try {
      let html = wikitext;

      // Applica le trasformazioni in ordine specifico
      html = this.parseHeaders(html);
      html = this.parseImages(html);
      html = this.parseTables(html);
      html = this.parseLists(html);
      html = this.parseLinks(html);
      html = this.parseFormatting(html);
      html = this.parseParagraphs(html);

      return html;
    } catch (error) {
      console.error('[WikitextParser] Errore durante il parsing:', error);
      return `<pre class="parse-error">${this.escapeHtml(wikitext)}</pre>`;
    }
  }

  /**
   * Converte headers MediaWiki in tag HTML h1-h6
   * Formato: = H1 =, == H2 ==, === H3 ===, etc.
   */
  private parseHeaders(text: string): string {
    // H6: ====== Title ======
    text = text.replace(/^======\s*(.+?)\s*======\s*$/gm, '<h6>$1</h6>');
    // H5: ===== Title =====
    text = text.replace(/^=====\s*(.+?)\s*=====\s*$/gm, '<h5>$1</h5>');
    // H4: ==== Title ====
    text = text.replace(/^====\s*(.+?)\s*====\s*$/gm, '<h4>$1</h4>');
    // H3: === Title ===
    text = text.replace(/^===\s*(.+?)\s*===\s*$/gm, '<h3>$1</h3>');
    // H2: == Title ==
    text = text.replace(/^==\s*(.+?)\s*==\s*$/gm, '<h2>$1</h2>');
    // H1: = Title =
    text = text.replace(/^=\s*(.+?)\s*=\s*$/gm, '<h1>$1</h1>');

    return text;
  }

  /**
   * Converte formattazione testo (grassetto, corsivo)
   * Bold: '''text''' -> <strong>
   * Italic: ''text'' -> <em>
   */
  private parseFormatting(text: string): string {
    // Bold + Italic: '''''text'''''
    text = text.replace(/'''''(.+?)'''''/g, '<strong><em>$1</em></strong>');

    // Bold: '''text'''
    text = text.replace(/'''(.+?)'''/g, '<strong>$1</strong>');

    // Italic: ''text''
    text = text.replace(/''(.+?)''/g, '<em>$1</em>');

    return text;
  }

  /**
   * Converte liste puntate e numerate, anche annidate e miste
   * * item -> <ul><li>
   * # item -> <ol><li>
   * #* item -> <ol><li><ul><li> (elenco puntato dentro un elenco numerato)
   */
  private parseLists(text: string): string {
    const lines = text.split('\n');
    const result: string[] = [];
    // Tipo di ogni livello di lista aperto (indice 0 = primo livello)
    const open: ('ul' | 'ol')[] = [];

    const closeTo = (depth: number) => {
      while (open.length > depth) {
        result.push(`</li></${open.pop()}>`);
      }
    };

    for (const line of lines) {
      const match = line.match(/^([*#]+)\s+(.+)$/);
      if (!match) {
        closeTo(0);
        result.push(line);
        continue;
      }

      const types = Array.from(match[1], c => (c === '#' ? 'ol' : 'ul') as 'ul' | 'ol');

      // Livelli già aperti con lo stesso tipo del nuovo prefisso
      let common = 0;
      while (common < open.length && common < types.length && open[common] === types[common]) {
        common++;
      }

      if (common === types.length) {
        // Stesso livello (eventualmente risalendo da un annidamento): nuova voce
        closeTo(types.length);
        result.push('</li>');
      } else {
        // Chiudi i livelli divergenti e apri quelli mancanti dentro la voce corrente
        closeTo(common);
        while (open.length < types.length) {
          const type = types[open.length];
          result.push(`<${type} class="${open.length ? 'wiki-list-nested' : 'wiki-list'}">`);
          open.push(type);
        }
      }
      result.push(`<li>${match[2]}`);
    }

    closeTo(0);
    return result.join('\n');
  }

  /**
   * Converte link esterni e interni
   * [http://url text] -> <a href>
   * [[PageName]] -> link interno
   */
  private parseLinks(text: string): string {
    // Link esterni con testo: [http://url text]
    text = text.replace(/\[(\S+:\/\/\S+)\s+([^\]]+)\]/g, '<a href="$1" target="_blank" rel="noopener">$2</a>');

    // Link esterni senza testo: [http://url]
    text = text.replace(/\[(\S+:\/\/\S+)\]/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');

    // Link a sezioni della pagina: [[#Sezione|Testo]] e [[#Sezione]]
    // L'id viene rimosso dal sanitizer di Angular: la sezione di destinazione
    // e' indicata nel title e risolta al click dal componente di anteprima
    text = text.replace(/\[\[#([^|\]]+)\|([^\]]+)\]\]/g, '<a href="#" class="wiki-anchor" title="$1">$2</a>');
    text = text.replace(/\[\[#([^\]]+)\]\]/g, '<a href="#" class="wiki-anchor" title="$1">$1</a>');

    // Link interni wiki: [[PageName|Display Text]]
    text = text.replace(/\[\[([^|\]]+)\|([^\]]+)\]\]/g, '<a href="#" class="wiki-link" title="$1">$2</a>');

    // Link interni wiki semplici: [[PageName]]
    text = text.replace(/\[\[([^\]]+)\]\]/g, '<a href="#" class="wiki-link" title="$1">$1</a>');

    return text;
  }

  /**
   * Converte immagini MediaWiki
   * [[File:name.png|thumb|alt text]] -> <img>
   */
  private parseImages(text: string): string {
    // [[File:name.png|thumb|alt text]]
    text = text.replace(
      /\[\[File:([^|\]]+)(\|thumb)?(\|[^\]]+)?\]\]/gi,
      (match, filename, thumb, alt) => {
        const altText = alt ? alt.replace('|', '').trim() : filename;
        const thumbClass = thumb ? ' wiki-thumb' : '';
        return `<figure class="wiki-image${thumbClass}">
          <img src="/immagini/${filename}" alt="${altText}" loading="lazy" />
          ${alt ? `<figcaption>${altText}</figcaption>` : ''}
        </figure>`;
      }
    );

    // [[Image:name.png]] (alias obsoleto)
    text = text.replace(
      /\[\[Image:([^|\]]+)\]\]/gi,
      (match, filename) => {
        return `<img src="/immagini/${filename}" alt="${filename}" class="wiki-image" loading="lazy" />`;
      }
    );

    return text;
  }

  /**
   * Converte tabelle MediaWiki
   * {| class="zcsTable"
   * |-
   * ! Header
   * |-
   * | Cell
   * |}
   */
  private parseTables(text: string): string {
    // Cerca tabelle MediaWiki
    const tableRegex = /\{\|([^\n]*)\n([\s\S]*?)\n\|\}/g;

    text = text.replace(tableRegex, (match, attributes, content) => {
      let html = '<table class="zcsTable">\n';

      const rows = content.split(/\n\|-/).filter((row: string) => row.trim() !== '');

      for (const row of rows) {
        html += '<tr>';

        // Header cells: ! content
        const headerCells = row.match(/^![ \t]*(.*?)(?=\n[!|]|\n|$)/gm);
        if (headerCells) {
          for (const cell of headerCells) {
            const cellContent = cell.replace(/^!\s*/, '').trim();
            html += `<th>${cellContent}</th>`;
          }
        }

        // Data cells: | content
        const dataCells = row.match(/^\|[ \t]*(.*?)(?=\n[!|]|\n|$)/gm);
        if (dataCells) {
          for (const cell of dataCells) {
            const cellContent = cell.replace(/^\|\s*/, '').trim();
            // Le celle vuote vanno mantenute per non disallineare le colonne
            if (!cellContent.startsWith('-')) {
              html += `<td>${cellContent}</td>`;
            }
          }
        }

        html += '</tr>\n';
      }

      html += '</table>';
      return html;
    });

    return text;
  }

  /**
   * Converte paragrafi separati da righe vuote
   */
  private parseParagraphs(text: string): string {
    // Dividi in blocchi separati da righe vuote
    const blocks = text.split(/\n\n+/);

    const result = blocks.map(block => {
      block = block.trim();

      // Non wrappare se è già un tag HTML
      if (block.match(/^<(h[1-6]|ul|ol|table|figure|pre|blockquote)/i)) {
        return block;
      }

      // Non wrappare righe vuote
      if (block === '') {
        return '';
      }

      // Wrappa in paragrafo
      return `<p>${block}</p>`;
    });

    return result.join('\n\n');
  }

  /**
   * Escape HTML per prevenire XSS
   */
  private escapeHtml(text: string): string {
    const map: { [key: string]: string } = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  }
}

import { Component, Input, OnChanges, SecurityContext } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { WikitextParserService } from '../../services/wikitext-parser.service';

/**
 * Componente per la visualizzazione renderizzata di markup MediaWiki
 * Converte il testo wiki in HTML e lo visualizza con stile Wikipedia-like
 */
@Component({
  selector: 'app-wikitext-preview',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './wikitext-preview.component.html',
  styleUrls: ['./wikitext-preview.component.css']
})
export class WikitextPreviewComponent implements OnChanges {
  /**
   * Testo MediaWiki da renderizzare
   */
  @Input() wikitext: string = '';

  /**
   * HTML renderizzato e sanitizzato pronto per visualizzazione
   */
  renderedHtml: SafeHtml = '';

  /**
   * Flag per mostrare errori di rendering
   */
  hasError: boolean = false;

  constructor(
    private parser: WikitextParserService,
    private sanitizer: DomSanitizer
  ) {}

  /**
   * Rileva cambiamenti nell'input e ri-renderizza
   */
  ngOnChanges(): void {
    this.renderPreview();
  }

  /**
   * Gestisce i link alle sezioni ([[#Sezione|Testo]]): scorre fino al titolo
   * con lo stesso testo invece di navigare (href="#" cambierebbe la route)
   */
  onPreviewClick(event: MouseEvent): void {
    const target = event.target as HTMLElement | null;
    const link = target?.closest('a.wiki-anchor') as HTMLAnchorElement | null;
    if (!link) {
      return;
    }

    event.preventDefault();
    const normalize = (text: string | null) => (text ?? '').replace(/\s+/g, ' ').trim();
    const section = normalize(link.getAttribute('title'));
    const container = event.currentTarget as HTMLElement;
    const headings = Array.from(container.querySelectorAll('h1, h2, h3, h4, h5, h6'));
    const heading = headings.find(h => normalize(h.textContent) === section);
    heading?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /**
   * Renderizza il markup MediaWiki in HTML
   */
  private renderPreview(): void {
    this.hasError = false;

    if (!this.wikitext || this.wikitext.trim() === '') {
      this.renderedHtml = '';
      return;
    }

    try {
      // Parse del markup MediaWiki
      const html = this.parser.parseToHtml(this.wikitext);

      // Sanitizzazione per sicurezza XSS
      const sanitized = this.sanitizer.sanitize(SecurityContext.HTML, html);

      if (sanitized) {
        this.renderedHtml = sanitized;
      } else {
        // Fallback in caso di sanitizzazione che rimuove tutto
        this.renderedHtml = '<p class="empty">Contenuto non visualizzabile</p>';
        this.hasError = true;
      }
    } catch (error) {
      console.error('[WikitextPreview] Errore durante il rendering:', error);
      this.renderedHtml = '<p class="error">Errore durante il rendering della preview</p>';
      this.hasError = true;
    }
  }
}

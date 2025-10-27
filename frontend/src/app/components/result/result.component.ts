import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ConvertResponse } from '../../services/api.service';
import { WikitextPreviewComponent } from '../wikitext-preview/wikitext-preview.component';

/**
 * Componente per visualizzare i risultati della conversione
 * Supporta due modalità: Raw Markup e Preview renderizzata
 */
@Component({
  selector: 'app-result',
  standalone: true,
  imports: [CommonModule, WikitextPreviewComponent],
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.css']
})
export class ResultComponent {
  @Input() result!: ConvertResponse;

  /**
   * Modalità di visualizzazione corrente
   * 'raw': mostra il markup MediaWiki grezzo in textarea
   * 'preview': mostra l'anteprima renderizzata stile Wikipedia
   */
  viewMode: 'raw' | 'preview' = 'raw';

  /**
   * Cambia la modalità di visualizzazione tra raw e preview
   */
  setViewMode(mode: 'raw' | 'preview'): void {
    this.viewMode = mode;
  }

  /**
   * Copia il testo MediaWiki negli appunti
   */
  copyToClipboard(): void {
    if (this.result?.mediawiki_text) {
      navigator.clipboard.writeText(this.result.mediawiki_text).then(() => {
        alert('Text copied to clipboard!');
      }).catch(err => {
        console.error('Failed to copy:', err);
      });
    }
  }

  /**
   * Scarica il testo MediaWiki come file .wiki
   */
  downloadAsFile(): void {
    if (this.result?.mediawiki_text) {
      const blob = new Blob([this.result.mediawiki_text], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${this.result.filename.replace(/\.[^.]+$/, '')}.wiki`;
      link.click();
      window.URL.revokeObjectURL(url);
    }
  }
}

import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ConvertResponse } from '../../services/api.service';

@Component({
  selector: 'app-result',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.css']
})
export class ResultComponent {
  @Input() result!: ConvertResponse;

  copyToClipboard(): void {
    if (this.result?.mediawiki_text) {
      navigator.clipboard.writeText(this.result.mediawiki_text).then(() => {
        alert('Text copied to clipboard!');
      }).catch(err => {
        console.error('Failed to copy:', err);
      });
    }
  }

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

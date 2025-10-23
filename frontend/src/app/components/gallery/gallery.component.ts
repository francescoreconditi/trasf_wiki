import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-gallery',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './gallery.component.html',
  styleUrls: ['./gallery.component.css']
})
export class GalleryComponent {
  @Input() images: string[] = [];
  @Input() jobId: string = '';

  constructor(private apiService: ApiService) {}

  downloadAllImages(): void {
    if (!this.jobId) {
      alert('Job ID not available');
      return;
    }

    const downloadUrl = this.apiService.downloadAllImages(this.jobId);

    // Create a temporary link and click it to trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `${this.jobId}_images.zip`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

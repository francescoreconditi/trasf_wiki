import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, ConvertResponse } from '../../services/api.service';
import { ResultComponent } from '../result/result.component';
import { GalleryComponent } from '../gallery/gallery.component';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, ResultComponent, GalleryComponent],
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  selectedFile?: File;
  loading = false;
  result?: ConvertResponse;
  error?: string;

  constructor(private apiService: ApiService) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.error = undefined;
      this.result = undefined;
    }
  }

  onSubmit(): void {
    if (!this.selectedFile) {
      this.error = 'Please select a file';
      return;
    }

    this.loading = true;
    this.error = undefined;

    this.apiService.convert(this.selectedFile).subscribe({
      next: (response) => {
        this.result = response;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'An error occurred during conversion';
        this.loading = false;
      }
    });
  }

  reset(): void {
    this.selectedFile = undefined;
    this.result = undefined;
    this.error = undefined;
    this.loading = false;
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ConvertResponse {
  id: string;
  filename: string;
  mediawiki_text: string;
  images: string[];
  warnings: string[];
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  convert(file: File): Observable<ConvertResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post<ConvertResponse>(`${this.baseUrl}/convert`, formData);
  }

  downloadOutput(jobId: string): string {
    return `${this.baseUrl}/files/output/${jobId}`;
  }
}

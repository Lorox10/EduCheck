import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ImportResult {
  creados: number;
  actualizados: number;
  omitidos: number;
  errores: string[];
  grados: number[];
}

export interface UploadHistory {
  id: number;
  archivo: string;
  ruta: string;
  grados: string;
  creados: number;
  actualizados: number;
  omitidos: number;
  errores: number;
  fecha: string;
}

@Injectable({
  providedIn: 'root'
})
export class CsvImportService {
  private apiUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  uploadCsv(file: File): Observable<ImportResult> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<ImportResult>(`${this.apiUrl}/students/import`, formData);
  }

  getUploadHistory(): Observable<{ historial: UploadHistory[] }> {
    return this.http.get<{ historial: UploadHistory[] }>(`${this.apiUrl}/uploads/history`);
  }

  downloadTemplate(): void {
    window.open(`${this.apiUrl}/students/template`, '_blank');
  }
}

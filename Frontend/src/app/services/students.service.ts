import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Student {
  id: number;
  numero_estudiante: number;
  primer_apellido: string;
  segundo_apellido: string | null;
  primer_nombre: string;
  segundo_nombre: string | null;
  documento: string;
  grado: number;
  telefono_acudiente: string | null;
  telegram_id: string | null;
}

export interface StudentsResponse {
  estudiantes: Student[];
  total: number;
}

@Injectable({
  providedIn: 'root'
})
export class StudentsService {
  private apiUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) { }

  getStudents(): Observable<StudentsResponse> {
    return this.http.get<StudentsResponse>(`${this.apiUrl}/students`);
  }

  getStudentQrUrl(studentId: number): string {
    return `${this.apiUrl}/students/${studentId}/qr`;
  }

  updateTelegramId(studentId: number, telegramId: string): Observable<any> {
    return this.http.patch(`${this.apiUrl}/students/${studentId}/telegram`, {
      telegram_id: telegramId
    });
  }
}

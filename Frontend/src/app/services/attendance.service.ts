import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface CheckInResponse {
  status: string;
  mensaje?: string;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AttendanceService {
  private apiUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {}

  checkIn(documento: string): Observable<CheckInResponse> {
    console.log('checkIn service: enviando documento=', documento);
    const payload = { documento };
    console.log('checkIn service: payload=', payload);
    return this.http.post<CheckInResponse>(`${this.apiUrl}/attendance/check-in`, payload);
  }
}

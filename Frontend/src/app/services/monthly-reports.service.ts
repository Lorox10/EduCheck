import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MonthlyReport {
  filename: string;
  date: string;
  month_name: string;
  size: number;
  created: number;
}

@Injectable({
  providedIn: 'root'
})
export class MonthlyReportsService {
  private apiUrl = 'http://localhost:5000/monthly-reports';

  constructor(private http: HttpClient) { }

  getAvailableReports(): Observable<{ reports: MonthlyReport[] }> {
    return this.http.get<{ reports: MonthlyReport[] }>(this.apiUrl);
  }

  generateMonthlyReport(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/generate`, {});
  }

  downloadReport(filename: string): void {
    const url = `${this.apiUrl}/${filename}`;
    window.open(url, '_blank');
  }
}

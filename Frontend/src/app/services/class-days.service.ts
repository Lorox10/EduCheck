import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ClassDaysConfig {
  lunes: boolean;
  martes: boolean;
  miercoles: boolean;
  jueves: boolean;
  viernes: boolean;
  sabado: boolean;
  domingo: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ClassDaysService {
  private apiUrl = 'http://localhost:5000/class-days';

  constructor(private http: HttpClient) { }

  getClassDays(): Observable<ClassDaysConfig> {
    return this.http.get<ClassDaysConfig>(this.apiUrl);
  }

  updateClassDays(config: Partial<ClassDaysConfig>): Observable<any> {
    return this.http.post<any>(this.apiUrl, config);
  }
}

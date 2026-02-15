import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AttendanceService } from '../../services/attendance.service';

interface AbsenceRecord {
  id: number;
  primer_apellido: string;
  segundo_apellido: string | null;
  primer_nombre: string;
  segundo_nombre: string | null;
  grado: number;
  documento: string;
  ausencias: number;
  ultimas_faltas: string[];
}

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.scss']
})
export class ReportsComponent implements OnInit {
  absenceRecords: AbsenceRecord[] = [];
  isLoading = true;
  selectedGrade = 'all';
  availableGrades: number[] = [8, 9, 10, 11];
  errorMessage = '';

  constructor(
    private attendanceService: AttendanceService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadAbsenceHistory();
  }

  loadAbsenceHistory() {
    this.isLoading = true;
    this.errorMessage = '';
    
    this.attendanceService.getAbsenceHistory().subscribe({
      next: (data: any) => {
        this.absenceRecords = data.records || [];
        
        // Obtener grados únicos de los registros
        const gradesSet = new Set(this.absenceRecords.map(r => r.grado));
        this.availableGrades = Array.from(gradesSet).sort();
        
        this.isLoading = false;
      },
      error: (err: any) => {
        console.error('Error loading absence history:', err);
        this.errorMessage = 'Error al cargar histórico de ausencias';
        this.isLoading = false;
      }
    });
  }

  filterByGrade(grade: string) {
    this.selectedGrade = grade;
  }

  get filteredRecords() {
    if (this.selectedGrade === 'all') {
      return this.absenceRecords;
    }
    return this.absenceRecords.filter(r => r.grado === parseInt(this.selectedGrade));
  }

  getFullName(record: AbsenceRecord): string {
    return `${record.primer_apellido} ${record.segundo_apellido || ''} ${record.primer_nombre} ${record.segundo_nombre || ''}`.trim();
  }

  goBack() {
    this.router.navigate(['/dashboard']);
  }

  getStudentsWithoutAbsences(): number {
    return this.filteredRecords.filter(r => r.ausencias === 0).length;
  }

  getTotalAbsences(): number {
    return this.filteredRecords.reduce((sum, r) => sum + r.ausencias, 0);
  }
}

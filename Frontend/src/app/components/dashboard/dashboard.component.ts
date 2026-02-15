import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, Router } from '@angular/router';
import { AttendanceService } from '../../services/attendance.service';
import { StudentsService } from '../../services/students.service';
import { ClassDaysService, ClassDaysConfig } from '../../services/class-days.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  totalStudents = 0;
  presentToday = 0;
  absentToday = 0;
  attendancePercentage = 0;
  selectedGrade = 'all';
  availableGrades: number[] = [];
  allGrades: number[] = [8, 9, 10, 11];
  isLoading = true;
  errorMessage = '';
  absentStudents: any[] = [];
  
  // Configuración de días de clase
  classDays: ClassDaysConfig = {
    lunes: true,
    martes: true,
    miercoles: true,
    jueves: true,
    viernes: true,
    sabado: false,
    domingo: false
  };
  showClassDaysConfig = false;

  constructor(
    private attendanceService: AttendanceService,
    private studentsService: StudentsService,
    private classDaysService: ClassDaysService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadDashboardData();
    this.loadClassDays();
  }

  loadDashboardData() {
    this.isLoading = true;
    this.errorMessage = '';
    this.selectedGrade = 'all'; // Resetear el filtro
    
    // Obtener estadísticas de hoy
    this.attendanceService.getAttendanceToday().subscribe({
      next: (data: any) => {
        this.presentToday = data.presente || 0;
        this.absentToday = data.ausente || 0;
        this.totalStudents = data.total || (this.presentToday + this.absentToday);
        this.attendancePercentage = this.totalStudents > 0 
          ? Math.round((this.presentToday / this.totalStudents) * 100) 
          : 0;
        
        // Obtener grados disponibles del backend
        this.availableGrades = data.grados || [];
        
        this.isLoading = false;
        this.loadAbsentStudents();
      },
      error: (err: any) => {
        console.error('Error loading attendance:', err);
        this.errorMessage = 'No hay datos de asistencia disponibles';
        this.availableGrades = [];
        this.isLoading = false;
      }
    });
  }

  loadAbsentStudents() {
    // Obtener lista de estudiantes del grado seleccionado
    this.studentsService.getStudentsByGrade(this.selectedGrade === 'all' ? null : parseInt(this.selectedGrade))
      .subscribe({
        next: (students: any[]) => {
          // Aquí se puede filtrar para mostrar solo ausentes si el backend lo proporciona
          this.absentStudents = students.slice(0, 10); // Mostrar primeros 10
        },
        error: (err: any) => {
          console.error('Error loading students:', err);
        }
      });
  }

  loadClassDays() {
    this.classDaysService.getClassDays().subscribe({
      next: (data: ClassDaysConfig) => {
        this.classDays = data;
      },
      error: (err: any) => {
        console.error('Error loading class days:', err);
      }
    });
  }

  toggleClassDay(day: keyof ClassDaysConfig) {
    this.classDays[day] = !this.classDays[day];
    this.classDaysService.updateClassDays(this.classDays).subscribe({
      next: () => {
        // Recargar datos de ausencias con la nueva configuración
        this.loadDashboardData();
      },
      error: (err: any) => {
        console.error('Error updating class days:', err);
      }
    });
  }

  toggleClassDaysConfig() {
    this.showClassDaysConfig = !this.showClassDaysConfig;
  }  changeGrade(grade: string) {
    this.selectedGrade = grade;
    this.isLoading = true;
    
    if (grade !== 'all') {
      this.attendanceService.getAttendanceByGrade(parseInt(grade)).subscribe({
        next: (data: any) => {
          this.presentToday = data.presente || 0;
          this.absentToday = data.ausente || 0;
          this.totalStudents = data.total || (this.presentToday + this.absentToday);
          this.attendancePercentage = this.totalStudents > 0 
            ? Math.round((this.presentToday / this.totalStudents) * 100) 
            : 0;
          this.isLoading = false;
          this.loadAbsentStudents();
        },
        error: (err: any) => {
          console.error('Error loading grade attendance:', err);
          this.errorMessage = `Error al cargar datos del grado ${grade}`;
          this.isLoading = false;
        }
      });
    } else {
      this.loadDashboardData();
    }
  }

  goToReports() {
    this.router.navigate(['/reports']);
  }

  downloadPDF() {
    this.attendanceService.downloadPDF();
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { StudentsService, Student } from '../../services/students.service';

interface GradeGroup {
  grado: number;
  estudiantes: Student[];
  expanded: boolean;
}

@Component({
  selector: 'app-students-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './students-management.component.html',
  styleUrl: './students-management.component.scss'
})
export class StudentsManagementComponent implements OnInit {
  gradeGroups: GradeGroup[] = [];
  filteredGradeGroups: GradeGroup[] = [];
  searchTerm = '';
  searchResults: Student[] = [];
  showSearchResults = false;
  isLoading = false;
  errorMessage = '';

  constructor(private studentsService: StudentsService) { }

  ngOnInit(): void {
    this.loadStudents();
  }

  loadStudents(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.studentsService.getStudents().subscribe({
      next: (response) => {
        this.groupStudentsByGrade(response.estudiantes);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar estudiantes:', error);
        this.errorMessage = 'Error al cargar estudiantes';
        this.isLoading = false;
      }
    });
  }

  groupStudentsByGrade(students: Student[]): void {
    const grouped = new Map<number, Student[]>();

    students.forEach(student => {
      if (!grouped.has(student.grado)) {
        grouped.set(student.grado, []);
      }
      grouped.get(student.grado)!.push(student);
    });

    this.gradeGroups = Array.from(grouped.entries())
      .map(([grado, estudiantes]) => ({
        grado,
        estudiantes: estudiantes.sort((a, b) => a.numero_estudiante - b.numero_estudiante),
        expanded: false
      }))
      .sort((a, b) => a.grado - b.grado);
    
    this.filteredGradeGroups = this.gradeGroups;
  }

  onSearchChange(): void {
    const term = this.searchTerm.toLowerCase().trim();
    
    if (!term) {
      this.searchResults = [];
      this.showSearchResults = false;
      this.filteredGradeGroups = this.gradeGroups;
      return;
    }

    // Buscar en todos los estudiantes de todos los grados
    const allStudents: Student[] = [];
    this.gradeGroups.forEach(gradeGroup => {
      gradeGroup.estudiantes.forEach(student => {
        allStudents.push(student);
      });
    });

    // Filtrar por nombre o documento
    this.searchResults = allStudents.filter(student => {
      const fullName = this.getFullName(student).toLowerCase();
      const documento = student.documento.toLowerCase();
      return fullName.includes(term) || documento.includes(term);
    });

    this.showSearchResults = true;
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.searchResults = [];
    this.showSearchResults = false;
    this.filteredGradeGroups = this.gradeGroups;
  }

  toggleGrade(grade: GradeGroup): void {
    grade.expanded = !grade.expanded;
  }

  getQrUrl(studentId: number): string {
    return this.studentsService.getStudentQrUrl(studentId);
  }

  getFullName(student: Student): string {
    const parts = [
      student.primer_apellido,
      student.segundo_apellido || '',
      student.primer_nombre,
      student.segundo_nombre || ''
    ];
    return parts.filter(p => p).join(' ');
  }

  printGrade(grade: GradeGroup): void {
    // Expandir el grado para que se vean los QRs
    grade.expanded = true;

    // Esperar un momento para que se carguen las imágenes
    setTimeout(() => {
      // Crear ventana de impresión
      const printWindow = window.open('', '', 'width=800,height=600');
      
      if (printWindow) {
        const qrElements = document.querySelectorAll(`#grade-${grade.grado} .qr-card`);
        
        let printContent = `
          <html>
            <head>
              <title>QR Codes - Grado ${grade.grado}</title>
              <style>
                body {
                  font-family: Arial, sans-serif;
                  margin: 20px;
                }
                .header {
                  text-align: center;
                  margin-bottom: 30px;
                }
                .qr-grid {
                  display: grid;
                  grid-template-columns: repeat(3, 1fr);
                  gap: 20px;
                  margin-top: 20px;
                }
                .qr-card {
                  page-break-inside: avoid;
                  text-align: center;
                  border: 2px solid #333;
                  padding: 15px;
                  border-radius: 8px;
                }
                .qr-card img {
                  max-width: 100%;
                  height: auto;
                }
                @media print {
                  .qr-grid {
                    grid-template-columns: repeat(3, 1fr);
                  }
                }
              </style>
            </head>
            <body>
              <div class="header">
                <h1>Códigos QR - Grado ${grade.grado}</h1>
                <p>Total de estudiantes: ${grade.estudiantes.length}</p>
              </div>
              <div class="qr-grid">
        `;

        grade.estudiantes.forEach(student => {
          const fullName = this.getFullName(student);
          const qrUrl = this.getQrUrl(student.id);
          
          printContent += `
            <div class="qr-card">
              <img src="${qrUrl}" alt="QR ${fullName}">
            </div>
          `;
        });

        printContent += `
              </div>
            </body>
          </html>
        `;

        printWindow.document.write(printContent);
        printWindow.document.close();
        
        // Esperar a que se carguen las imágenes antes de imprimir
        printWindow.onload = () => {
          setTimeout(() => {
            printWindow.print();
          }, 500);
        };
      }
    }, 300);
  }
}

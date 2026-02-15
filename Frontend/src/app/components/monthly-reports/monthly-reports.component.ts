import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MonthlyReportsService, MonthlyReport } from '../../services/monthly-reports.service';

@Component({
  selector: 'app-monthly-reports',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './monthly-reports.component.html',
  styleUrls: ['./monthly-reports.component.scss']
})
export class MonthlyReportsComponent implements OnInit {
  reports: MonthlyReport[] = [];
  isLoading = false;
  isGenerating = false;
  errorMessage = '';
  successMessage = '';

  constructor(private monthlyReportsService: MonthlyReportsService) {}

  ngOnInit() {
    this.loadReports();
  }

  loadReports() {
    this.isLoading = true;
    this.errorMessage = '';
    
    this.monthlyReportsService.getAvailableReports().subscribe({
      next: (data: any) => {
        this.reports = data.reports || [];
        this.isLoading = false;
      },
      error: (err: any) => {
        console.error('Error loading reports:', err);
        this.errorMessage = 'Error al cargar los reportes';
        this.isLoading = false;
      }
    });
  }

  generateReport() {
    this.isGenerating = true;
    this.errorMessage = '';
    this.successMessage = '';
    
    this.monthlyReportsService.generateMonthlyReport().subscribe({
      next: (data: any) => {
        this.successMessage = 'Reporte generado exitosamente';
        this.isGenerating = false;
        setTimeout(() => {
          this.loadReports();
          this.successMessage = '';
        }, 1500);
      },
      error: (err: any) => {
        console.error('Error generating report:', err);
        this.errorMessage = err.error?.error || 'Error al generar el reporte';
        this.isGenerating = false;
      }
    });
  }

  downloadReport(report: MonthlyReport) {
    this.monthlyReportsService.downloadReport(report.filename);
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  formatDate(timestamp: number): string {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}

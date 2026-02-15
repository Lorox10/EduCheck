import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CsvImportService, ImportResult, UploadHistory } from '../../services/csv-import.service';

@Component({
  selector: 'app-csv-import',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './csv-import.component.html',
  styleUrl: './csv-import.component.scss'
})
export class CsvImportComponent implements OnInit {
  isDragging = false;
  isUploading = false;
  selectedFile: File | null = null;
  uploadResult: ImportResult | null = null;
  uploadHistory: UploadHistory[] = [];
  errorMessage = '';
  successMessage = '';

  constructor(private csvService: CsvImportService) {}

  ngOnInit(): void {
    this.loadHistory();
  }

  loadHistory(): void {
    this.csvService.getUploadHistory().subscribe({
      next: (response) => {
        this.uploadHistory = response.historial;
      },
      error: (error) => {
        console.error('Error al cargar historial:', error);
      }
    });
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFile(files[0]);
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.handleFile(input.files[0]);
    }
  }

  handleFile(file: File): void {
    if (!file.name.endsWith('.csv')) {
      this.errorMessage = 'Por favor selecciona un archivo CSV';
      this.successMessage = '';
      return;
    }

    this.selectedFile = file;
    this.errorMessage = '';
    this.successMessage = '';
    this.uploadResult = null;
  }

  uploadFile(): void {
    if (!this.selectedFile) return;

    this.isUploading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.csvService.uploadCsv(this.selectedFile).subscribe({
      next: (result) => {
        this.isUploading = false;
        this.uploadResult = result;
        this.successMessage = `✓ Importación completada: ${result.creados} creados, ${result.actualizados} actualizados`;
        this.selectedFile = null;
        this.loadHistory();
      },
      error: (error) => {
        this.isUploading = false;
        this.errorMessage = error.error?.error || 'Error al importar el archivo';
        console.error('Error:', error);
      }
    });
  }

  downloadTemplate(): void {
    this.csvService.downloadTemplate();
  }

  cancelUpload(): void {
    this.selectedFile = null;
    this.errorMessage = '';
    this.successMessage = '';
    this.uploadResult = null;
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}

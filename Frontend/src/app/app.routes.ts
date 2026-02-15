import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { QrScannerComponent } from './components/qr-scanner/qr-scanner.component';
import { CsvImportComponent } from './components/csv-import/csv-import.component';
import { StudentsManagementComponent } from './components/students-management/students-management.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'scanner', component: QrScannerComponent },
  { path: 'import-csv', component: CsvImportComponent },
  { path: 'students', component: StudentsManagementComponent }
];

import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { QrScannerComponent } from './components/qr-scanner/qr-scanner.component';
import { CsvImportComponent } from './components/csv-import/csv-import.component';
import { StudentsManagementComponent } from './components/students-management/students-management.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { ReportsComponent } from './components/reports/reports.component';
import { MonthlyReportsComponent } from './components/monthly-reports/monthly-reports.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'scanner', component: QrScannerComponent },
  { path: 'import-csv', component: CsvImportComponent },
  { path: 'students', component: StudentsManagementComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'reports', component: ReportsComponent },
  { path: 'monthly-reports', component: MonthlyReportsComponent }
];

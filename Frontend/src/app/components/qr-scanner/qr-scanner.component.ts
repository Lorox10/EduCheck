import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AttendanceService } from '../../services/attendance.service';
import jsQR from 'jsqr';

@Component({
  selector: 'app-qr-scanner',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './qr-scanner.component.html',
  styleUrl: './qr-scanner.component.scss'
})
export class QrScannerComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('video', { static: false }) videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvas', { static: false }) canvasElement!: ElementRef<HTMLCanvasElement>;
  
  private canvasContext?: CanvasRenderingContext2D | null;
  private stream?: MediaStream;
  private animationFrame?: number;
  
  hasDevices: boolean = false;
  hasPermission: boolean = false;
  isInitializing: boolean = true;
  availableDevices: MediaDeviceInfo[] = [];
  currentDeviceId?: string;
  
  scanResult: string = '';
  isLoading: boolean = false;
  message: string = '';
  messageType: 'success' | 'error' | '' = '';
  permissionDenied: boolean = false;
  isScanning: boolean = false;

  constructor(private attendanceService: AttendanceService) {}

  ngOnInit(): void {
    this.requestCameraPermission();
  }

  ngAfterViewInit(): void {
    // El video/canvas se inicializan después de obtener permisos
  }

  ngOnDestroy(): void {
    this.stopScanning();
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }
  }

  async requestCameraPermission(): Promise<void> {
    try {
      // Primero obtiene la lista de cámaras
      const devices = await navigator.mediaDevices.enumerateDevices();
      this.availableDevices = devices.filter(device => device.kind === 'videoinput');
      this.hasDevices = this.availableDevices.length > 0;
      
      console.log('Cámaras disponibles:', this.availableDevices);

      // Selecciona cámara trasera por defecto, si no la primera disponible
      const backCamera = this.availableDevices.find(d => 
        d.label.toLowerCase().includes('back') || 
        d.label.toLowerCase().includes('trasera') ||
        d.label.toLowerCase().includes('environment')
      );
      this.currentDeviceId = backCamera?.deviceId || this.availableDevices[0]?.deviceId;

      // Solicita acceso a la cámara seleccionada
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: this.currentDeviceId ? { exact: this.currentDeviceId } : undefined }
      });
      
      this.hasPermission = true;
      this.isInitializing = false;
      
      // Espera a que el DOM se actualice con el video/canvas
      setTimeout(() => this.startCamera(), 100);

    } catch (error) {
      console.error('Error al acceder a la cámara:', error);
      this.permissionDenied = true;
      this.isInitializing = false;
      this.hasPermission = false;
    }
  }

  startCamera(): void {
    if (!this.videoElement || !this.canvasElement) {
      console.error('Video o canvas no disponibles');
      return;
    }

    const video = this.videoElement.nativeElement;
    video.srcObject = this.stream!;
    video.setAttribute('playsinline', 'true');
    
    video.onloadedmetadata = () => {
      video.play();
      this.setupCanvas();
      this.scanQRCode();
    };
  }

  setupCanvas(): void {
    const video = this.videoElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    this.canvasContext = canvas.getContext('2d', { willReadFrequently: true });
  }

  scanQRCode(): void {
    const video = this.videoElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    const context = this.canvasContext;

    if (!context || video.readyState !== video.HAVE_ENOUGH_DATA) {
      this.animationFrame = requestAnimationFrame(() => this.scanQRCode());
      return;
    }

    // Dibuja el frame del video en el canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Obtiene los datos de imagen del canvas
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    
    // Escanea el QR
    const code = jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: 'dontInvert'
    });

    if (code) {
      console.log('✓ QR detectado:', code.data);
      
      if (code.location) {
        // Dibuja el marco verde siguiendo el QR
        this.drawQRBox(context, code.location);
      }
      
      // Procesa el código detectado
      if (!this.isLoading && code.data !== this.scanResult) {
        console.log('→ Enviando a onScanSuccess:', code.data);
        this.onScanSuccess(code.data);
      }
    }

    // Continúa escaneando
    this.animationFrame = requestAnimationFrame(() => this.scanQRCode());
  }

  drawQRBox(context: CanvasRenderingContext2D, location: any): void {
    const {topLeftCorner, topRightCorner, bottomLeftCorner, bottomRightCorner} = location;

    // Dibuja el rectángulo verde siguiendo las esquinas del QR
    context.beginPath();
    context.moveTo(topLeftCorner.x, topLeftCorner.y);
    context.lineTo(topRightCorner.x, topRightCorner.y);
    context.lineTo(bottomRightCorner.x, bottomRightCorner.y);
    context.lineTo(bottomLeftCorner.x, bottomLeftCorner.y);
    context.lineTo(topLeftCorner.x, topLeftCorner.y);
    
    context.lineWidth = 4;
    context.strokeStyle = '#28a745';
    context.stroke();

    // Sombra verde brillante
    context.shadowColor = '#28a745';
    context.shadowBlur = 20;
    context.stroke();
    context.shadowBlur = 0;

    // Marca las esquinas
    [topLeftCorner, topRightCorner, bottomLeftCorner, bottomRightCorner].forEach(corner => {
      context.beginPath();
      context.arc(corner.x, corner.y, 5, 0, 2 * Math.PI);
      context.fillStyle = '#28a745';
      context.fill();
    });
  }

  stopScanning(): void {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
  }

  async requestPermission(): Promise<void> {
    await this.requestCameraPermission();
  }

  async onCameraChange(event: Event): Promise<void> {
    const select = event.target as HTMLSelectElement;
    this.currentDeviceId = select.value;
    
    // Detiene la cámara actual
    this.stopScanning();
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }

    // Inicia con la nueva cámara
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { deviceId: { exact: this.currentDeviceId } }
      });
      this.startCamera();
    } catch (error) {
      console.error('Error al cambiar de cámara:', error);
    }
  }

  onScanSuccess(decodedText: string): void {
    console.log('onScanSuccess called with:', decodedText);
    
    if (this.isLoading || decodedText === this.scanResult) {
      console.log('Skipping: isLoading=', this.isLoading, 'isDuplicate=', decodedText === this.scanResult);
      return;
    }

    this.isScanning = true;
    this.scanResult = decodedText;
    this.isLoading = true;
    this.message = 'Procesando...';
    this.messageType = '';

    console.log('→ Llamando a checkIn con documento:', decodedText);
    this.attendanceService.checkIn(decodedText).subscribe({
      next: (response) => {
        console.log('✓ Respuesta del servidor:', response);
        this.isLoading = false;
        if (response.status === 'registrado') {
          this.message = response.mensaje || 'Asistencia registrada correctamente ✓';
          this.messageType = 'success';
        } else {
          this.message = response.mensaje || 'Registro completado';
          this.messageType = 'success';
        }
        
        setTimeout(() => {
          this.scanResult = '';
          this.message = '';
          this.messageType = '';
          this.isScanning = false;
        }, 3000);
      },
      error: (error) => {
        console.error('✗ Error en checkIn:', error);
        this.isLoading = false;
        this.message = error.error?.error || 'Error al registrar asistencia';
        this.messageType = 'error';
        
        setTimeout(() => {
          this.scanResult = '';
          this.message = '';
          this.messageType = '';
          this.isScanning = false;
        }, 3000);
      }
    });
  }
}

# Edu Check

Sistema de control de asistencia escolar con notificación automática a padres.

## 📋 Descripción

Edu Check es un sistema automatizado que permite a los colegios:
- Registrar la asistencia de estudiantes mediante escaneo de carnets
- Notificar automáticamente a los padres vía WhatsApp cuando su hijo ingresa al colegio
- Alertar a padres si el estudiante no registra entrada antes del inicio de clases
- Generar reportes automáticos de estudiantes ausentes

## 🛠️ Tecnologías

### Backend
- Python 3.x
- Flask (Framework web)
- MySQL (Base de datos)
- SQLAlchemy (ORM)

### Frontend
- Angular
- Atomic Design (Arquitectura de componentes)
- Diseño responsive

## 📁 Estructura del Proyecto

```
Edu Check/
├── Backend/          # API REST en Python
└── Frontend/         # Aplicación web en Angular
```

## 🚀 Instalación

### Backend

1. Navegar a la carpeta Backend:
```bash
cd Backend
```

2. Crear entorno virtual:
```bash
python -m venv venv
```

3. Activar entorno virtual:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

5. Configurar variables de entorno:
- Copiar `.env.example` a `.env`
- Editar `.env` con tus credenciales

### Frontend

_(Instrucciones se agregarán cuando se inicialice el proyecto Angular)_

## 👥 Equipo

Proyecto desarrollado para la materia **Desarrollo Profesional de Soluciones Software**

## 📝 Licencia

Este proyecto es de uso académico.

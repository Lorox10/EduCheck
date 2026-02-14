# Edu Check

Sistema de control de asistencia escolar con notificacion automatica a padres.

## Descripcion

Edu Check es un sistema automatizado que permite a los colegios:
- Registrar la asistencia de estudiantes mediante escaneo de carnets
- Notificar automaticamente a los padres via WhatsApp cuando su hijo ingresa al colegio
- Alertar a padres si el estudiante no registra entrada antes del inicio de clases
- Generar reportes automaticos de estudiantes ausentes

## Estado del proyecto

En desarrollo. Este repositorio contiene la estructura base y la configuracion inicial.

## Tecnologias

### Backend
- Python 3.x
- Flask (framework web)
- MySQL (base de datos)
- SQLAlchemy (ORM)

### Frontend
- Angular
- Atomic Design (arquitectura de componentes)
- Diseno responsive

## Estructura del proyecto

```
Edu Check/
├── Backend/          # API REST en Python
└── Frontend/         # Aplicacion web en Angular
```

## Requisitos

- Python 3.10 o superior
- Node.js 18 o superior (cuando se inicialice el frontend)
- MySQL 8

## Instalacion

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

Las instrucciones se agregaran cuando se inicialice el proyecto Angular.

## Convenciones

- EOL en LF y formato consistente mediante .editorconfig
- Variables sensibles en archivos .env (no versionados)
- Commits en espanol y con mensajes claros

## Equipo

Proyecto desarrollado para la materia **Desarrollo Profesional de Soluciones Software**

## Licencia

Este proyecto es de uso academico.

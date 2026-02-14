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

Instala lo siguiente para que todo funcione en tu maquina:

- Python 3.10 o superior
- MySQL 8 (servidor)
- MySQL Workbench (opcional, para crear y administrar la base)
- Git
- Visual Studio Code
- Node.js 18 o superior (cuando se inicialice el frontend)

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

Incluye: Flask, Flask-CORS, python-dotenv, SQLAlchemy, mysql-connector, APScheduler, marshmallow, python-dateutil y pytz.

5. Configurar variables de entorno:

- Copiar `.env.example` a `.env`
- Editar `.env` con tus credenciales

### Ejecutar en Visual Studio Code (backend)

1. Verifica que MySQL este corriendo.
2. Crea la base de datos si no existe:

```sql
CREATE DATABASE edu_check CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

3. En VS Code, abre una terminal en la carpeta del proyecto.
4. Activa el entorno virtual:

- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

5. Ejecuta el servidor:

```bash
python Backend/app.py
```

6. Prueba el estado:

```bash
curl http://127.0.0.1:5000/health
```

Debe responder: `{"status":"ok","db":"ok"}`.

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

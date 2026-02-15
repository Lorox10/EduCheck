# Edu Check

Sistema de control de asistencia escolar con notificacion automatica a padres via Telegram.

## Descripcion

Edu Check es un sistema automatizado que permite a los colegios:

- Registrar la asistencia de estudiantes mediante escaneo de carnets
- Notificar automaticamente a los padres via Telegram Bot cuando su hijo ingresa al colegio
- Alertar a padres si el estudiante no registra entrada antes del inicio de clases
- Generar reportes automaticos de estudiantes ausentes
- Cargar listas de estudiantes mediante CSV

## Estado del proyecto

En desarrollo. Este repositorio contiene la estructura base y la configuracion inicial.

## Tecnologias

### Backend

- Python 3.x
- Flask (framework web)
- MySQL (base de d
- APScheduler (tareas programadas)
- Telegram Bot API (notificaciones)atos)
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

````bash
pip install -r requirements.txt
```, pytz, requests, qrcode, Pillow, pandas

Incluye: Flask, Flask-CORS, python-dotenv, SQLAlchemy, mysql-connector, APScheduler, marshmallow, python-dateutil y pytz.

5. Configurar variables de entorno:
 (base de datos y Telegram Bot)

#### Configuracion de Telegram Bot

1. **Crear el bot en Telegram:**
   - Abre Telegram y busca el usuario **@BotFather**
   - Envía el comando `/newbot`
   - Sigue los pasos y recibirás un **TOKEN**

2. **Obtener tu CHAT_ID:**
   - Inicia un chat con tu bot
   - Envía cualquier mensaje
   - Abre en el navegador: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Busca el campo `"chat":{"id":123456789}` - ese número es tu **CHAT_ID**

3. **Configurar variables en `.env`:**
````

TELEGRAM_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

````
- Copiar `.env.example` a `.env`
- Editar `.env` con tus credenciales

### Ejecutar en Visual Studio Code (backend)

1. Verifica que MySQL este corriendo.
2. Crea la base de datos si no existe:

```sql
CREATE DATABASE edu_check CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
````

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

Nota: El backend crea la base de datos y tablas automaticamente si no existen,
y agrega columnas nuevas basicas cuando es necesario.

### Formato CSV oficial

Descarga el formato desde: `GET /students/template`

Ejemplo de descarga en Windows (PowerShell):

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/students/template -OutFile estudiantes_template.csv
```

Columnas (separadas por coma):

- numero
- apellidos
- nombres
- tipo_documento (TI o CC)
- documento
- correo
- telefono_acudiente (opcional, solo numeros, ej: 3001234567)
- telegram_id (ID de Telegram del acudiente, obtenido con el bot, ej: 5936924064)
- grado (solo numero, ej: 10)

Regla de importacion:

- Si el `documento` ya existe, se actualiza el estudiante.
- Si no existe, se crea.
- El `telegram_id` es mandatorio para recibir notificaciones.
- El QR se genera en el backend si no existe para ese estudiante.
- El CSV subido se guarda en `Backend/uploads` y se registra en el historial.

Subir CSV (PowerShell):

```powershell
Invoke-WebRequest -Method Post -Uri http://127.0.0.1:5000/students/import -Form @{file=Get-Item .\estudiantes.csv}
```

Respuesta esperada:

````json
{
    "creados": 0,
    "actualizados": 0, via Telegram:

- Se ejecutan a la hora configurada en `ALERT_TIME` (default: 07:10 AM).
- Solo envian si el estudiante no tiene registro de entrada del dia.
- Requiere `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` configurados en `.env`.
- Las notificaciones se registran en la tabla `notification_logs` para auditoría.

Configuracion:

```env
ALERT_TIME=07:10           # Hora del dia para alertas (formato HH:MM)
TIMEZONE=America/Bogota    # Zona horaria (pytz compatible)
TELEGRAM_TOKEN=xxx         # Token del Telegram Bot
TELEGRAM_CHAT_ID=xxx       # Chat ID donde recibir notificaciones
````

```

Historial de cargas:

- Endpoint: `GET /uploads/history`
- Devuelve lista de archivos cargados con fecha y grados.

Descarga de QR individual:

- Endpoint: `GET /students/{id}/qr`
- Devuelve una imagen PNG con el QR y el nombre completo debajo.

Registro de asistencia:

- Endpoint: `POST /attendance/check-in`
- Body JSON: `{"documento":"1131110580"}`
- **Envía notificación inmediata** al acudiente cuando registra entrada (lectura de QR)

## Sistema de Notificaciones Mejorado

El sistema envía **2 tipos de notificaciones** a los acudientes:

### 1️⃣ Notificación de Entrada (Inmediata)

Se envía **cuando el estudiante registra entrada** (lee su QR):

```
✅ Edu Check - Entrada Registrada

Carlos Martinez con cédula 1131110583 del grado 11 
registró su entrada a las 07:45.
```

**Flujo:**
- Estudiante escanea su QR al llegar al colegio
- Sistema registra la entrada
- **Acudiente recibe Telegram INMEDIATAMENTE**

### 2️⃣ Notificación de Ausencia (Programada)

Se envía **a la hora configurada** (default: 07:10 AM) si el estudiante NO registró entrada:

```
⚠️ Edu Check - Reporte de Ausencia

Lucas García con cédula 1131110582 del grado 10 
no ha registrado entrada hasta las 07:10.
```

**Flujo:**
- Todos los días a las 07:10 AM (configurable)
- Sistema revisa quién NO llegó
- **Acudientes reciben Telegram de ausencia**

### Personalizar Mensajes

Los mensajes están en **Backend/messages.py**:

```python
def build_entry_message(student, hora: str) -> str:
    # Mensaje cuando registra entrada
    return f"✅ {student.apellidos} {student.nombres} con cédula {student.documento} ..."

def build_absence_message(student, hora: str) -> str:
    # Mensaje cuando NO registra entrada  
    return f"⚠️ {student.apellidos} {student.nombres} con cédula {student.documento} ..."
```

Edita estas funciones para personalizar los mensajes que reciben los padres.

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
```

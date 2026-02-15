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

✅ **Funcional** - Sistema de QR y notificaciones Telegram completamente operativo.

**Características implementadas:**

- ✅ Generación de QR con nombres integrados
- ✅ Lector de QR en tiempo real (cámara web)
- ✅ Registro automático de asistencia
- ✅ Notificaciones Telegram en tiempo real
- ✅ Gestión de estudiantes (búsqueda, impresión, grados)
- ✅ Importación de CSV con validación
- ✅ Base de datos MySQL

**Ready for production** con preparación adecuada de User IDs de Telegram.

## Tecnologias

### Backend

- Python 3.12
- Flask (framework web)
- MySQL (base de datos)
- SQLAlchemy (ORM)
- APScheduler (tareas programadas)
- Telegram Bot API (notificaciones)
- QRCode + Pillow (generación de QR con nombres)

### Frontend

- Angular 18
- TypeScript
- Atomic Design (arquitectura de componentes)
- Diseño responsive
- jsqr (lectura de QR)

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

## ⚡ Instalación Inicial (Una sola vez)

### Requisitos

Instala lo siguiente en tu máquina:

- **Python** 3.10 o superior
- **MySQL 8** (servidor local corriendo)
- **Git**
- **Node.js** 18 o superior
- **Visual Studio Code** (opcional pero recomendado)

### Instalación del Backend

1. **Clona este repositorio:**

    ```bash
    git clone [URL_DEL_REPOSITORIO]
    cd "Edu Check"
    ```

2. **Crea el Virtual Environment:**

    ```bash
    python -m venv .venv
    ```

3. **Activa el Virtual Environment:**
    - **Windows:** `.venv\Scripts\Activate.ps1`
    - **Linux/Mac:** `source .venv/bin/activate`

4. **Instala dependencias del Backend:**

    ```bash
    pip install -r Backend/requirements.txt
    ```

5. **Configura las variables de entorno:**

    ```bash
    cp Backend/.env.example Backend/.env
    ```

    Luego edita `Backend/.env` con tus valores:

    ```env
    MYSQL_USER=root
    MYSQL_PASSWORD=tu_contraseña
    MYSQL_HOST=localhost
    MYSQL_DB=edu_check
    TELEGRAM_TOKEN=tu_token_bot
    TELEGRAM_CHAT_ID=tu_chat_id
    ALERT_TIME=07:10
    TIMEZONE=America/Bogota
    ```

### Instalación del Frontend

1. **Instala dependencias:**

    ```bash
    cd Frontend
    npm install
    cd ..
    ```

2. **Verifica que Angular CLI esté disponible:**
    ```bash
    npx ng version
    ```

### Configurar Telegram Bot (Importante)

**Paso 1: Crear el Bot**

1. Abre Telegram y busca a **@BotFather**
2. Envía `/newbot`
3. Sigue las instrucciones y recibirás un **TELEGRAM_TOKEN**
4. Copia este token en `Backend/.env` en `TELEGRAM_TOKEN=`

**Ejemplo de token:** (no réveles esto públicamente)

```
***API_TOKEN_OCULTO***
```

⚠️ **NUNCA publiques tu token en GitHub - es como una contraseña**

**Paso 2: Obtener tu TELEGRAM_USER_ID (⚠️ MUY IMPORTANTE)**

⚠️ **NO confundas chat_id con User ID** - Son cosas diferentes.

**Método 1: Usando @getidsbot (Recomendado)**

1. Abre Telegram
2. Busca al bot: **@getidsbot**
3. Envía cualquier mensaje
4. El bot responderá con tu User ID (número privado)
5. Ese número es tu **TELEGRAM_USER_ID**
6. Copia en `Backend/.env` (no lo reveles públicamente)

**Método 2: Usando la API manualmente**

1. Inicia chat con tu bot
2. Envía cualquier mensaje
3. Abre en el navegador: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
4. Busca `"from":{"id":123456789}` - ese número es tu **User ID**
5. Copia en `Backend/.env`

**Verificación:**

```bash
curl "https://api.telegram.org/bot<TU_TOKEN>/getMe"
```

Debe devolver información de tu bot (no error).

**Ejemplo de .env configurado correctamente:**

```env
TELEGRAM_TOKEN=***xxxxxxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx***
TELEGRAM_CHAT_ID=***(tus_digitos_privados)***
MYSQL_PASSWORD=***(tu_contrasena_mysql)***
```

⚠️ **IMPORTANTE: NUNCA subes estas claves a Git - están en .env que es ignorado**

⚠️ **Para cada acudiente en el CSV, necesitas su TELEGRAM_USER_ID (no su teléfono)**

Si tienes 30 estudiantes con 30 acudientes diferentes, cada uno necesita:

1. Tener el Telegram Bot agregado
2. Enviar un mensaje al bot
3. Obtener su User ID vía @getidsbot
4. Incluir ese ID en la columna `telegram_id` del CSV

---`

## ⚙️ Cómo Ejecutar el Proyecto

Este proyecto tiene dos componentes que deben ejecutarse en paralelo: **Backend** (Python/Flask) y **Frontend** (Angular).

### Requisitos Previos

1. **MySQL debe estar corriendo** en tu computadora
2. **Virtual Environment DEBE estar activado** para ejecutar el Backend

### Activar el Virtual Environment (una sola vez por sesión)

Abre una terminal PowerShell en la raíz del proyecto y ejecuta:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verás `(.venv)` al inicio del prompt si está activo correcto.

---

## 🚀 Ejecutar SOLO el Backend

**Terminal 1** - Ejecuta el Backend (API REST en localhost:5000):

```bash
python Backend/app.py
```

**Resultado esperado:**

```
 * Serving Flask app
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**Prueba el backend:**

```powershell
curl http://127.0.0.1:5000/students
```

Debe devolver un JSON con la lista de estudiantes (vacío si acaba de resetear).

---

## 🎨 Ejecutar SOLO el Frontend

**Terminal 2** - Ejecuta el Frontend (aplicación Angular):

```bash
cd Frontend
npm start
```

**Resultado esperado:**

```
Initial chunk files | Names | Raw size
main.js             | main  | XX.XX kB

Application bundle generation complete.

Watch mode enabled. Watching for file changes...
➜  Local:   http://localhost:XXXX/
```

Accede a la URL mostrada en tu navegador (ej: `http://localhost:4200` o similar).

> Nota: Si el puerto 4200 está ocupado, Angular preguntará si deseas usar otro puerto.

---

## ▶️ Ejecutar Backend + Frontend Simultáneamente (Lo recomendado)

**Terminal 1 - Backend:**

```bash
python Backend/app.py
```

**Terminal 2 - Frontend:**

```bash
cd Frontend && npm start
```

Luego abre tu navegador en `http://localhost:4200` (o el puerto que indique Angular).

---

## 🗄️ Crear la Base de Datos Automáticamente

**El Backend crea la base de datos `edu_check` automáticamente al iniciarse.**

No necesitas ejecutar SQL manualmente. Si deseas crear la base manualmente:

```sql
CREATE DATABASE edu_check CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

Pero esto es **opcional** - el Backend lo hace automáticamente.

---

## ✅ Verificar que Todo Funciona

1. **Backend corriendo**, prueba:

    ```powershell
    curl http://127.0.0.1:5000/students
    ```

    Debe devolver JSON.

2. **Frontend corriendo**, abre en tu navegador:

    ```
    http://localhost:4200
    ```

    Debe cargar la aplicación sin errores.

3. **Ambos conectando correctamente** si:
    - Puedes ver la página web del Frontend
    - La página carga datos del Backend sin errores de CORS

---

## 🆘 Si algo no funciona

- **"Port 4200 is already in use"** → Angular pedirá usar otro puerto, acepta (sí)
- **Backend no responde** → Verifica que MySQL esté corriendo y activaste el `.venv`
- **Frontend no carga** → Abre la consola del navegador (F12) y busca errores

---

## 📋 Formato CSV Oficial

El sistema acepta archivos CSV con la siguiente estructura.

### Descargar la Plantilla

Desde cualquier navegador o PowerShell:

```powershell
curl http://127.0.0.1:5000/students/template -o estudiantes_template.csv
```

### Estructura de Columnas (11 columnas)

El CSV debe tener **exactamente estas columnas en orden**, separadas por **PUNTO Y COMA (;)**:

| Columna            | Tipo        | Ejemplo          | Obligatorio   |
| ------------------ | ----------- | ---------------- | ------------- |
| numero             | Número      | 1                | ✅ Sí         |
| primer_apellido    | Texto       | García           | ✅ Sí         |
| segundo_apellido   | Texto       | López            | ❌ Opcional   |
| primer_nombre      | Texto       | Carlos           | ✅ Sí         |
| segundo_nombre     | Texto       | Miguel           | ❌ Opcional   |
| tipo_documento     | TI ó CC     | CC               | ✅ Sí         |
| documento          | Número      | 1131110580       | ✅ Sí         |
| correo             | Email       | carlos@email.com | ❌ Opcional   |
| telefono_acudiente | Número      | 3001234567       | ❌ Opcional   |
| telegram_id        | ID Telegram | 5936924064       | ✅ IMPORTANTE |
| grado              | Número      | 10               | ✅ Sí         |

### Estructura de Ejemplo

```
numero;primer_apellido;segundo_apellido;primer_nombre;segundo_nombre;tipo_documento;documento;correo;telefono_acudiente;telegram_id;grado
1;García;López;Carlos;Miguel;CC;1000000001;estudiante1@domain.com;300****;***user_id_privado***;10
2;Martínez;;Juan;;CC;1000000002;estudiante2@domain.com;300****;***user_id_privado***;9
3;Ramírez;González;Ana;María;TI;1000000003;;300****;***user_id_privado***;11
```

### Notas Importantes

- **Separador:** PUNTO Y COMA (;) - NO comas
- **Codificación:** UTF-8 con BOM (para soportar acentos y caracteres especiales)
- **Segundo apellido y segundo nombre:** Pueden estar vacíos (dejar el espacio en blanco)
- **telegram_id:** OBLIGATORIO - Sin esto, NO recibirás notificaciones Telegram
    - ⚠️ NO es el número de teléfono del acudiente
    - ⚠️ NO es el chat_id del grupo
    - ✅ SÍ es el USUARIO ID personal (número como 5936924064)
- **Si el documento ya existe:** Se actualiza el estudiante con nuevos datos
- **Si es nuevo:** Se crea el estudiante y automáticamente se genera su QR

### Cómo Obtener el telegram_id Para Cada Acudiente

**Cada acudiente necesita su propio TELEGRAM_USER_ID:**

1. **El acudiente abre Telegram**
2. **Busca el bot Edu Check** (el que configuraste con @BotFather)
3. **Envía cualquier mensaje al bot** (puede ser solo "/start")
4. **El acudiente abre @getidsbot en Telegram**
5. **Envía un mensaje a @getidsbot**
6. **@getidsbot responde con su User ID** (ej: 5936924064)
7. **Copia ese ID en la columna `telegram_id` del CSV**

- **Los User IDs son números privados**

✅ Cada usuario tiene un ID único (no es su teléfono)
⚠️ NO publiques estos números - son datos privados

⚠️ **Cada acudiente diferente = ID diferente en el CSV**

### Subir el CSV

**Con PowerShell:**

```powershell
Invoke-WebRequest -Method Post -Uri http://127.0.0.1:5000/students/import `
  -Form @{file=Get-Item .\estudiantes.csv}
```

**O con curl:**

```bash
curl -X POST -F "file=@estudiantes.csv" http://127.0.0.1:5000/students/import
```

### Respuesta Esperada

```json
{
    "creados": 2,
    "actualizados": 1,
    "errores": 0,
    "qrs_generados": 3,
    "mensaje": "Importación exitosa"
}
```

### Ver Historial de Importaciones

```powershell
curl http://127.0.0.1:5000/uploads/history
```

Devuelve lista de archivos cargados, fecha y estudiantes importados.

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
```

```

Historial de cargas:

- Endpoint: `GET /uploads/history`
- Devuelve lista de archivos cargados con fecha y grados.

Descarga de QR individual:

- Endpoint: `GET /students/{id}/qr`
- Devuelve una imagen PNG con el QR y el nombre completo debajo.

Registro de asistencia:

- Endpoint: `POST /attendance/check-in`
- Body JSON: `{"documento":"1000000001"}`
- **Envía notificación inmediata** al acudiente cuando registra entrada (lectura de QR)

---

## 🖥️ Usando la Aplicación Web (Frontend)

### Navegación Principal

1. **Home** - Página de inicio con opciones principales
2. **Estudiantes** - Gestión de estudiantes, búsqueda y impresión de QRs
3. **Asistencia** - Lector de QR para registrar entrada de estudiantes
4. **Reportes** - Visualización de ausencias y asistencia

### Módulo de Gestión de Estudiantes

**Ubicación:** Menú → Estudiantes

**Funciones:**
- 🔍 **Buscar estudiante** - Escribe nombre o documento, los resultados aparecen mientras escribes
- 📋 **Ver por grado** - Expande/contrae los grados para ver estudiantes agrupados
- 🖨️ **Imprimir QRs** - Imprime todos los QRs de un grado en formato 3 columnas
- 📱 **Ver QR individual** - Cada estudiante muestra su código QR con nombre debajo

### Módulo de Asistencia (Lector de QR)

**Ubicación:** Menú → Asistencia

**Cómo funciona:**
1. Abre la cámara de tu dispositivo
2. Escanea el QR del estudiante
3. El sistema registra la entrada automáticamente
4. Telegram envía notificación inmediata al acudiente
5. Ves confirmación en pantalla

**Requisito:** Acceso a cámara web (acepta cuando el navegador lo pida)

### Características Principales

✅ Búsqueda **real-time** de estudiantes por nombre o documento
✅ QRs **con nombres integrados** (imprimibles)
✅ Lectura de QR con **cámara en tiempo real**
✅ Notificaciones automáticas vía **Telegram**
✅ Agrupación por **grado**
✅ Impresión **optimizada** para papel oficio

---

## � Endpoints de la API (Backend)

### Estudiantes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/students` | Listar todos los estudiantes |
| GET | `/students/{id}/qr` | Descargar QR de un estudiante |
| PATCH | `/students/{id}/telegram` | Actualizar telegram_id |
| GET | `/students/template` | Descargar CSV template |
| POST | `/students/import` | Importar estudiantes desde CSV |

### Asistencia

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/attendance/check-in` | Registrar entrada de estudiante por documento |
| GET | `/attendance/today` | Ver asistencia del día hoy |
| GET | `/attendance/{grado}` | Ver asistencia de un grado específico |

### Uploads

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/uploads/history` | Ver historial de importaciones CSV |

### Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Verificar estado del servidor y BD |

---

El sistema envía **2 tipos de notificaciones** a los acudientes vía Telegram:

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

````

**Flujo:**
- Todos los días a las 07:10 AM (configurable)
- Sistema revisa quién NO llegó
- **Acudientes reciben Telegram de ausencia**

### Personalizar Mensajes

Los mensajes están en **Backend/messages.py**. Usa los 4 campos de nombre separados:

```python
def build_entry_message(student, hora: str) -> str:
    # Mensaje cuando registra entrada
    full_name = f"{student.primer_apellido} {student.segundo_apellido or ''} {student.primer_nombre} {student.segundo_nombre or ''}".strip()
    return f"✅ Edu Check - Entrada Registrada\n\n{full_name} con cédula {student.documento} del grado {student.grado}\nregistró su entrada a las {hora}."

def build_absence_message(student, hora: str) -> str:
    # Mensaje cuando NO registra entrada
    full_name = f"{student.primer_apellido} {student.segundo_apellido or ''} {student.primer_nombre} {student.segundo_nombre or ''}".strip()
    return f"⚠️ Edu Check - Reporte de Ausencia\n\n{full_name} con cédula {student.documento} del grado {student.grado}\nno ha registrado entrada hasta las {hora}."
```

Edita estas funciones para personalizar los mensajes que reciben los padres.

---

## ✅ Verificación de Notificaciones Telegram

### Antes de Usar en Producción

Sigue este proceso para confirmar que Telegram funciona correctamente:

**1. Verifica tu configuración de .env:**

```bash
# Windows PowerShell
Get-Content Backend\.env | Select-String "TELEGRAM"
```

Debes ver:
```
TELEGRAM_TOKEN=8507219531:AAE...
TELEGRAM_CHAT_ID=5936924064
```

**2. Inicia el backend y frontend:**

```bash
# Terminal 1
python Backend/app.py

# Terminal 2
cd Frontend && npm start
```

**3. Importa un estudiante de prueba:**

```powershell
# Crea un CSV con un estudiante
@"
numero;primer_apellido;segundo_apellido;primer_nombre;segundo_nombre;tipo_documento;documento;correo;telefono_acudiente;telegram_id;grado
1;Prueba;;Test;;CC;1000000010;;300****;***id_privado***;10
"@ | Out-File -Encoding UTF8 test.csv

# Importa
curl -X POST -F "file=@test.csv" http://127.0.0.1:5000/students/import
```

**4. Prueba el escaneo de QR:**

- Abre http://localhost:XXXX en tu navegador
- Ve a la sección "Asistencia"
- Imprime el QR de prueba (Backend/qr/)
- Escanea el QR con tu cámara web

**5. Verifica que recibiste la notificación en Telegram:**

- Deberías recibir un mensaje como:
```
✅ Edu Check - Entrada Registrada

Test Prueba con cédula ********** del grado 10
registró su entrada a las 09:45.
```

### Si NO recibes notificación:

**Verificación 1: ¿Es el telegram_id correcto?**

```bash
mysql -u root -p tu_password edu_check -e "SELECT documento, primer_nombre, telegram_id FROM students WHERE documento='1000000001';"
```

⚠️ **NUNCA publiques tu contraseña - reemplaza con tu password real localmente**

Debe mostrar: `telegram_id = xxxxxxxxx` (tu User ID privado)

**Verificación 2: Revisar logs del backend:**

En la terminal del backend, busca:
```
[TELEGRAM] Enviando a chat_id=5936924064
[TELEGRAM.send_text] Response status: 200
```

Si ves `400` o `401`, el token o User ID es incorrecto.

**Verificación 3: Probar token manualmente:**

```bash
curl "https://api.telegram.org/bot<TU_TOKEN>/getMe"
```

Debe devolver información del bot, no error.

### Pasos para Producción Real:

1. **Recolecta User ID de cada acudiente:**
   - Envía link de Telegram con tu bot
   - Cada acudiente envía mensaje a @getidsbot
   - Obtiene su User ID
   - Tú agregás el ID al CSV

2. **Importa el CSV con todos los User IDs:**
   - Asegúrate que cada estudiante tiene el `telegram_id` correcto
   - Sistema enviará notificaciones a acudientes individuales

3. **Probá con algunos estudiantes reales**

4. **Monitorea logs inicialmente** para detectar problemas

---

## Convenciones

- EOL en LF y formato consistente mediante .editorconfig
- Variables sensibles en archivos .env (no versionados)
- Commits en espanol y con mensajes claros

## Equipo

Proyecto desarrollado para la materia **Desarrollo Profesional de Soluciones Software**

## Licencia

Este proyecto es de uso academico.

```

```
````

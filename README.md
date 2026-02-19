# 🏫 EduCheck

Sistema inteligente de control de asistencia escolar con notificaciones
automáticas

------------------------------------------------------------------------

## 📌 Descripción

**EduCheck** es una aplicación web full-stack diseñada para gestionar la
asistencia escolar mediante códigos QR y enviar notificaciones
automáticas a acudientes vía Telegram.

El sistema permite:

-   📷 Registro de asistencia mediante escaneo QR\
-   👨‍🎓 Gestión de estudiantes (importación CSV)\
-   📊 Visualización de reportes de asistencia\
-   📄 Generación de reportes en PDF\
-   📩 Notificaciones automáticas en tiempo real\
-   🔐 Autenticación de usuarios

Este proyecto fue desarrollado como solución real para entornos
educativos.

------------------------------------------------------------------------

## 🧠 Arquitectura del Sistema

Frontend (SPA) → API REST → Base de Datos → Servicio de Notificaciones

-   Frontend: Angular 18\
-   Backend: Flask (Python)\
-   Base de datos: MySQL\
-   Integración externa: Telegram Bot API

------------------------------------------------------------------------

## 🛠️ Tecnologías Utilizadas

### Frontend

-   Angular 18
-   TypeScript
-   HTML5
-   CSS3

### Backend

-   Python 3
-   Flask
-   SQLAlchemy
-   MySQL
-   JWT Authentication

### Otros

-   Telegram Bot API
-   Generación de PDF
-   Importación CSV

------------------------------------------------------------------------

## ⚙️ Instalación y Ejecución

### 1️⃣ Clonar el repositorio

``` bash
git clone https://github.com/Lorox10/EduCheck.git
cd EduCheck
```

------------------------------------------------------------------------

### 2️⃣ Backend

``` bash
cd backend
pip install -r requirements.txt
python app.py
```

Configurar variables de entorno:

    DB_HOST=
    DB_USER=
    DB_PASSWORD=
    DB_NAME=
    TELEGRAM_TOKEN=

------------------------------------------------------------------------

### 3️⃣ Frontend

``` bash
cd frontend
npm install
ng serve
```

La aplicación estará disponible en:

    http://localhost:4200

------------------------------------------------------------------------

## 📸 Capturas del Proyecto

(Aquí puedes agregar screenshots del dashboard, QR, reportes, etc.)

------------------------------------------------------------------------

## 🚀 Características Destacadas

✔ Arquitectura full-stack desacoplada\
✔ API REST estructurada\
✔ Integración con servicios externos\
✔ Manejo de autenticación\
✔ Sistema funcional aplicable en instituciones educativas

------------------------------------------------------------------------

## 📈 Mejoras Futuras

-   Implementación de pruebas unitarias\
-   Documentación Swagger para API\
-   Despliegue en entorno cloud\
-   Roles avanzados (administrador, docente, portería)

------------------------------------------------------------------------

## 👨‍💻 Autor

**Lorenzo Vargas**\
Ingeniería de Sistemas -- Docente de programación\
GitHub: https://github.com/Lorox10


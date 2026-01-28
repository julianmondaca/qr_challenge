# QR Code Management System 🚀

Este proyecto es una solución completa para la generación, gestión y seguimiento de códigos QR dinámicos, construida con **FastAPI**, **PostgreSQL** y **JWT Authentication**.

## ✨ Características

- **Autenticación segura**: Registro e inicio de sesión con JWT.
- **Códigos QR Dinámicos**: Cambia la URL de destino sin cambiar el código QR físico.
- **Personalización**: Configura el color (HEX) y el tamaño (píxeles) de tus QR.
- **Tracking en tiempo real**: Registra IP, país y zona horaria (timezone) de cada escaneo.
- **Redirección automática**: Redirección fluida al destino final.
- **Estadísticas detalladas**: Consulta el total de escaneos y logs históricos usando SQL nativo.
- **Documentación Interactiva**: Swagger UI integrado para probar la API.

## 🛠️ Tecnologías utilizadas

- **Backend**: FastAPI (Python 3.11+)
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Seguridad**: Passlib (bcrypt) + PyJWT
- **Generación de QR**: qrcode[pillow]

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd qr_challenge
```

### 2. Configurar el entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Mac/Linux
# venv\Scripts\activate   # En Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto (basado en `.env.base`):
```env
DATABASE_URL=postgresql://tu_usuario@localhost:5432/qr_challenge
JWT_SECRET_KEY=tu_clave_secreta_super_segura
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Configuración de la Base de Datos
El sistema crea automáticamente las tablas necesarias al iniciar la aplicación por primera vez. Asegúrate de que la base de datos especificada en el `.env` exista en tu servidor PostgreSQL.

---

## 🏃 Ejecución

Inicia el servidor de desarrollo con Uvicorn:
```bash
uvicorn app.src.main:app --reload
```
La API estará disponible en `http://localhost:8000`.

---

## 📖 Uso de la API

### Documentación
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Endpoints Principales

| Método | Endpoint | Descripción |
| :-- | :-- | :-- |
| `POST` | `/api/v1/auth/register` | Registro de usuario |
| `POST` | `/api/v1/auth/login` | Login (obtiene el Token) |
| `POST` | `/api/v1/qr-codes/` | Crea un QR y descarga la imagen |
| `GET` | `/api/v1/qr-codes/` | Lista tus códigos QR |
| `PATCH` | `/api/v1/qr-codes/{uuid}` | Actualiza un QR existente |
| `GET` | `/api/v1/qr-codes/{uuid}/stats` | Estadísticas detalladas de escaneos |
| `GET` | `/api/v1/scan/{uuid}` | Punto de escaneo (público) |

### Cómo Autenticarse
En Swagger o Postman, utiliza el token obtenido en el login como:
`Authorization: Bearer <tu_token_aqui>`

---

## 📄 Licencia
Este proyecto fue realizado como parte de un desafío técnico.

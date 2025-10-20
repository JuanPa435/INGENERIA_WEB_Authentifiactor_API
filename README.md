# API de Autenticación y Productos

API REST con autenticación JWT para gestión de productos con roles de usuario.

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/JuanPa435/INGENERIA_WEB_Authentifiactor_API.git
cd INGENERIA_WEB_Authentifiactor_API
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
FLASK_APP=Main.py
FLASK_ENV=development
JWT_SECRET_KEY=tu_clave_secreta
```

## Ejecución en Desarrollo

```bash
flask run
```

El servidor estará disponible en `http://localhost:5000`

## Ejecutar Pruebas

```bash
pytest Tests/
```

## Roles de Usuario

- **Admin**: Puede crear, editar y eliminar todos los productos
- **Cliente**: Puede ver todos los productos y editar/eliminar solo los propios

## Ejemplos de Token

Token JWT generado en login:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "cliente"
  }
}
```

## Flujo de Autenticación

1. Usuario se registra (`/api/auth/register`)
2. Usuario inicia sesión (`/api/auth/login`)
3. Recibe token JWT
4. Usa token en header: `Authorization: Bearer <token>`

## Endpoints

### Autenticación

| Método | Ruta | Descripción | Autenticación |
|--------|------|-------------|---------------|
| POST | /api/auth/register | Registro de usuario | No |
| POST | /api/auth/login | Inicio de sesión | No |
| GET | /api/auth/user-info | Info del usuario actual | Si |
| PUT | /api/auth/profile | Actualizar perfil | Si |

### Productos

| Método | Ruta | Descripción | Autenticación |
|--------|------|-------------|---------------|
| GET | /api/products | Listar productos | No |
| POST | /api/products | Crear producto | Si |
| GET | /api/products/{id} | Ver producto | No |
| PUT | /api/products/{id} | Editar producto | Si + Propietario/Admin |
| DELETE | /api/products/{id} | Eliminar producto | Si + Propietario/Admin |
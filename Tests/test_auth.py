import pytest
from Src.App import create_app
from Models.Models_API import db

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()

def test_register_and_login_success(client):
    """Test registro exitoso y login con credenciales válidas"""
    # Registro
    res = client.post("/api/auth/register", json={
        "email": "test@user.com",
        "password": "123456",
        "role": "cliente"
    })
    assert res.status_code == 201
    assert "Usuario registrado correctamente" in res.get_json()["msg"]

    # Login válido
    res = client.post("/api/auth/login", json={
        "email": "test@user.com",
        "password": "123456"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert data["msg"] == "Inicio de sesión exitoso"
    return data["access_token"]

def test_login_invalid_credentials(client):
    """Test login con credenciales inválidas"""
    # Login con email inválido
    res = client.post("/api/auth/login", json={
        "email": "noexiste@user.com",
        "password": "123456"
    })
    assert res.status_code == 401
    assert "Credenciales inválidas" in res.get_json()["msg"]

    # Login con contraseña inválida
    res = client.post("/api/auth/login", json={
        "email": "test@user.com",
        "password": "wrongpass"
    })
    assert res.status_code == 401
    assert "Credenciales inválidas" in res.get_json()["msg"]

def test_protected_routes_with_token(client):
    """Test acceso a rutas protegidas con y sin token"""
    # Primero registramos y obtenemos token
    token = test_register_and_login_success(client)

    # Acceso exitoso a ruta protegida con token
    res = client.get("/api/auth/user-info", 
                     headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    
    # Acceso denegado sin token
    res = client.get("/api/auth/user-info")
    assert res.status_code == 401

    # Acceso denegado con token inválido
    res = client.get("/api/auth/user-info", 
                     headers={"Authorization": "Bearer invalid.token.here"})
    assert res.status_code == 422

def test_refresh_token(client):
    """Test renovación de token de acceso usando refresh token"""
    # Login para obtener tokens
    res = client.post("/api/auth/login", json={
        "email": "test@user.com",
        "password": "123456"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "refresh_token" in data
    refresh_token = data["refresh_token"]

    # Usar refresh token para obtener nuevo access token
    res = client.post("/api/auth/refresh",
                      headers={"Authorization": f"Bearer {refresh_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert "Token refrescado exitosamente" in data["msg"]

def test_logout(client):
    """Test cierre de sesión e invalidación de token"""
    # Login para obtener token
    res = client.post("/api/auth/login", json={
        "email": "test@user.com",
        "password": "123456"
    })
    token = res.get_json()["access_token"]

    # Cerrar sesión
    res = client.post("/api/auth/logout",
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "Sesión cerrada exitosamente" in res.get_json()["msg"]

    # Intentar usar el token después de cerrar sesión
    res = client.get("/api/auth/user-info",
                     headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401  # Token debería estar en lista negra

def test_product_permissions(client):
    """Test permisos de productos según rol de usuario"""
    # Registrar usuario cliente
    token = test_register_and_login_success(client)
    
    # Crear producto (requiere autenticación)
    res = client.post("/api/products/",
                      headers={
                          "Authorization": f"Bearer {token}",
                          "Content-Type": "application/json"
                      },
                      json={
                          "name": "Test Product",
                          "description": "Test Description",
                          "price": 10.99,
                          "stock": 100
                      })
    assert res.status_code == 200
    product_id = res.get_json()["id"]
    
    # Verificar que el usuario puede editar su propio producto
    res = client.put(f"/api/products/{product_id}",
                     headers={
                         "Authorization": f"Bearer {token}",
                         "Content-Type": "application/json"
                     },
                     json={"name": "Updated Product"})
    assert res.status_code == 200

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

def test_register_and_login(client):
    # Registro
    res = client.post("/api/auth/register", json={
        "email": "test@user.com",
        "password": "123456",
        "role": "cliente"
    })
    assert res.status_code == 201

    # Login
    res = client.post("/api/auth/login", json={
        "email": "test@user.com",
        "password": "123456"
    })
    data = res.get_json()
    assert "access_token" in data

def test_protected_route(client):
    # Sin token
    res = client.get("/api/products")
    assert res.status_code == 401

import os
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

class Config:
    # ✅ Base de datos local con SQLite (simple y sin conexión externa)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔐 Clave secreta para sesiones y JWT
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')

    # 🧱 Mantener conexión estable
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

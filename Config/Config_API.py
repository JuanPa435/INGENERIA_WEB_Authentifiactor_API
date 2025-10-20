import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración de la base de datos SQLite
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'instance', 'auth.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'myjwtsecret')
    
    # Configuración de JWT
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 días
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

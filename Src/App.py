from flask import Flask, jsonify, send_from_directory, redirect
from flask_cors import CORS
from Config.Config_API import Config
from Controllers.Controllers_API import product_bp
from Controllers.Auth_Controller import auth_bp
from Models.database import db
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__, static_folder=None)
app.config.from_object(Config)

# Inicializar extensiones
CORS(app, resources={r"/api/*": {"origins": "*"}})
db.init_app(app)
jwt = JWTManager()
jwt.init_app(app)

# Asegurarse de que todas las tablas existan
with app.app_context():
    db.create_all()

# Registrar los blueprints
app.register_blueprint(product_bp, url_prefix="/api/products")
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# Crear la base de datos al iniciar (si no existe)
with app.app_context():
    db.create_all()

# ---------------------- FRONTEND ---------------------- #

@app.route('/frontend/<path:path>')
def serve_frontend(path):
    """
    Permite servir los archivos del frontend (HTML, JS, CSS).
    Ejemplo: http://127.0.0.1:5000/frontend/login.html
    """
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_dir, path)

@app.route('/')
def home():
    """
    Redirige automáticamente al login como página inicial.
    """
    return redirect('/frontend/login.html')

# ---------------------- RUN ---------------------- #

if __name__ == '__main__':
    app.run(debug=True)

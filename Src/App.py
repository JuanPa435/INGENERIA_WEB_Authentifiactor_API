from flask import Flask, jsonify, send_from_directory, redirect
from flask_cors import CORS
from Config.Config_API import Config
from Controllers.Controllers_API import product_bp
from Controllers.Auth_Controller import auth_bp
from Models.database import db
from flask_jwt_extended import JWTManager
import os
from Models.User_Model import User
from Models.Token_Model import TokenBlocklist

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

    # Asegurarse de que la columna created_by existe en la tabla product (sin migraciones formales)
    try:
        engine = db.get_engine(app)
        with engine.connect() as conn:
            res = conn.execute("PRAGMA table_info('product')")
            cols = [row[1] for row in res.fetchall()]
            if 'created_by' not in cols:
                try:
                    conn.execute("ALTER TABLE product ADD COLUMN created_by INTEGER")
                    print('Columna created_by añadida a product')
                except Exception:
                    pass
            if 'created_by_name' not in cols:
                try:
                    conn.execute("ALTER TABLE product ADD COLUMN created_by_name TEXT")
                    print('Columna created_by_name añadida a product')
                except Exception:
                    pass
    except Exception:
        pass
    # Asegurar columna username en users
    try:
        res = db.session.execute("PRAGMA table_info('users')").fetchall()
        user_cols = [r[1] for r in res]
        if 'username' not in user_cols:
            try:
                db.session.execute("ALTER TABLE users ADD COLUMN username TEXT")
                db.session.commit()
                print('Columna username añadida a users')
            except Exception:
                pass
    except Exception:
        pass

# Registrar los blueprints
app.register_blueprint(product_bp, url_prefix="/api/products")
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# Callback para verificar si un token está en la lista negra
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist).filter_by(jti=jti).scalar()
    return token is not None

# Handler para errores de JWT
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "El token ha expirado"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"msg": "Token inválido"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"msg": "Token no proporcionado"}), 401

# Crear la base de datos al iniciar (si no existe)
with app.app_context():
    db.create_all()

# Crear un usuario administrador por defecto si no existe ninguno (útil en desarrollo)
    try:
        admin_exists = User.query.filter_by(role='admin').first()
        if not admin_exists:
            admin = User(email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Usuario administrador (admin@example.com) creado por defecto')
    except Exception:
        # Si algo falla (por ejemplo, en producción con permisos), no interrumpimos el arranque
        pass

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

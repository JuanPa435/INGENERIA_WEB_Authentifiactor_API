from flask import Blueprint, request, jsonify
from Services.Auth_Service import AuthService
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth_bp', __name__)

# Registro de usuario
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'cliente')
    return AuthService.register_user(email, password, role)

# Inicio de sesión
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    return AuthService.login_user(email, password)

# Ruta protegida (opcional, para prueba)
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = get_jwt_identity()
    return jsonify({'user': user}), 200

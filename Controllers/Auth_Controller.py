from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    current_user
)
from Models.User_Model import User
from Models.Token_Model import TokenBlocklist
from Models.database import db
from datetime import datetime, timezone

auth_bp = Blueprint("auth_bp", __name__)

# Registro de usuario
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        username = data.get("username")
        role = data.get("role", "cliente")

        if not email or not password:
            return jsonify({"msg": "Faltan campos obligatorios"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"msg": "El usuario ya existe"}), 400

        new_user = User(email=email, username=username, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "msg": "Usuario registrado correctamente",
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error al registrar: {str(e)}"}), 500


# Inicio de sesión
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"msg": "Faltan campos obligatorios"}), 400

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Crear access token y refresh token
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return jsonify({
                "msg": "Inicio de sesión exitoso",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict()
            }), 200
        else:
            return jsonify({"msg": "Credenciales inválidas"}), 401
    except Exception as e:
        return jsonify({"msg": f"Error al iniciar sesión: {str(e)}"}), 500


# Obtener información del usuario actual
@auth_bp.route("/user-info", methods=["GET"])
@jwt_required()
def get_user_info():
    # get_jwt_identity() devuelve la id del usuario (string); buscamos en la BD y retornamos el objeto
    current_user_id = get_jwt_identity()
    try:
        uid = int(current_user_id)
    except Exception:
        return jsonify({'msg': 'Identidad inválida en token'}), 401

    user = User.query.get(uid)
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    return jsonify(user.to_dict()), 200

# Perfil (solo prueba)
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    try:
        uid = int(current_user_id)
    except Exception:
        return jsonify({'msg': 'Identidad inválida en token'}), 401

    user = User.query.get(uid)
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    return jsonify({"msg": "Perfil obtenido", "user": user.to_dict()}), 200


# Actualizar perfil (username)
@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    try:
        uid = int(current_user_id)
    except Exception:
        return jsonify({'msg': 'Identidad inválida en token'}), 401

    user = User.query.get(uid)
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404

    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'msg': 'Falta el campo username'}), 400

    try:
        user.username = username
        db.session.commit()
        return jsonify({'msg': 'Perfil actualizado', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error al actualizar: {str(e)}'}), 500

# Refrescar token
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify({
            "msg": "Token refrescado exitosamente",
            "access_token": access_token
        }), 200
    except Exception as e:
        return jsonify({"msg": f"Error al refrescar token: {str(e)}"}), 500

# Cerrar sesión (invalidar token)
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        
        # Añadir token a la lista negra
        token_block = TokenBlocklist(jti=jti)
        db.session.add(token_block)
        db.session.commit()
        
        return jsonify({"msg": "Sesión cerrada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error al cerrar sesión: {str(e)}"}), 500

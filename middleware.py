from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from Models.User_Model import User

def role_required(required_role):
    """
    Decorador que valida si el usuario autenticado tiene el rol requerido.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 404

            if user.role != required_role:
                return jsonify({"error": "No tienes permisos para acceder a esta ruta"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

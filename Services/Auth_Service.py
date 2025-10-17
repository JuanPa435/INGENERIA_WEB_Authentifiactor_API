from flask_jwt_extended import create_access_token
from datetime import timedelta
from Models.User_Model import User, db

class AuthService:
    @staticmethod
    def register_user(email, password, role='cliente'):
        if User.query.filter_by(email=email).first():
            return {'error': 'El usuario ya existe'}, 400

        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return {'message': 'Usuario registrado exitosamente'}, 201

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return {'error': 'Credenciales inválidas'}, 401

        access_token = create_access_token(
            identity={'email': user.email, 'role': user.role},
            expires_delta=timedelta(hours=1)
        )
        return {'access_token': access_token}, 200

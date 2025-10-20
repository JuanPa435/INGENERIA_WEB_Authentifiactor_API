from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.Product_Model import Product
from Models.User_Model import User
from Models.database import db

class ProductController:
    @staticmethod
    def get_all_products():
        try:
            products = Product.query.all()
            result = []
            for p in products:
                pd = p.to_dict()
                created_by_username = None
                if p.created_by:
                    user = User.query.get(p.created_by)
                    if user:
                        created_by_username = user.username or user.email
                # si existe created_by_name (nombre local o enviado), preferirlo
                if p.created_by_name:
                    created_by_username = p.created_by_name
                pd['created_by_username'] = created_by_username
                result.append(pd)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def create_product():
        # Permitir creación pública; si viene token, se registra el creador
        data = request.get_json()

        try:
            created_by = None
            try:
                # Intentamos obtener identity si el token viene en headers
                from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
                try:
                    verify_jwt_in_request(optional=True)
                    cid = get_jwt_identity()
                    if cid:
                        created_by = int(cid)
                except Exception:
                    created_by = None
            except Exception:
                created_by = None

            # soportar nombre del creador enviado desde frontend (anon/local)
            created_by_name = data.get('created_by_name')
            # si tenemos token y usuario, preferimos el username del usuario
            if created_by and not created_by_name:
                user = User.query.get(created_by)
                if user:
                    created_by_name = user.username or user.email

            new_product = Product(
                name=data['name'],
                description=data.get('description', ''),
                price=float(data['price']),
                stock=int(data['stock']),
                created_by=created_by,
                created_by_name=created_by_name
            )

            db.session.add(new_product)
            db.session.commit()

            return jsonify(new_product.to_dict()), 201
        except KeyError as e:
            return jsonify({'error': f'Falta el campo {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @jwt_required()
    def update_product(product_id):
        current_user_id = get_jwt_identity()
        try:
            uid = int(current_user_id)
        except Exception:
            return jsonify({'msg': 'Identidad inválida en token'}), 401

        user = User.query.get(uid)
        if not user:
            return jsonify({'msg': 'Usuario no encontrado'}), 404

        # Permitir editar si es admin o si es el creador del producto
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'msg': 'Producto no encontrado'}), 404

        if not (user.role == 'admin' or product.created_by == user.id):
            return jsonify({'msg': 'No tienes permisos para modificar este producto'}), 403
        data = request.get_json()
        
        try:
            if 'name' in data:
                product.name = data['name']
            if 'description' in data:
                product.description = data['description']
            if 'price' in data:
                product.price = float(data['price'])
            if 'stock' in data:
                product.stock = int(data['stock'])
            # permitir actualizar el nombre del creador solo si es admin
            if 'created_by_name' in data and user.role == 'admin':
                product.created_by_name = data.get('created_by_name')
            
            db.session.commit()
            return jsonify(product.to_dict()), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def get_product(product_id):
        try:
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'msg': 'Producto no encontrado'}), 404
            
            # Obtener información del creador
            pd = product.to_dict()
            created_by_username = None
            if product.created_by:
                user = User.query.get(product.created_by)
                if user:
                    created_by_username = user.username or user.email
            if product.created_by_name:
                created_by_username = product.created_by_name
            pd['created_by_username'] = created_by_username
            
            return jsonify(pd), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def delete_product(product_id):
        current_user_id = get_jwt_identity()
        try:
            uid = int(current_user_id)
        except Exception:
            return jsonify({'msg': 'Identidad inválida en token'}), 401

        user = User.query.get(uid)
        if not user or user.role != 'admin':
            return jsonify({'msg': 'Solo los administradores pueden eliminar productos'}), 403

        product = Product.query.get(product_id)
        if not product:
            return jsonify({'msg': 'Producto no encontrado'}), 404

        try:
            db.session.delete(product)
            db.session.commit()
            return jsonify({'msg': 'Producto eliminado correctamente'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
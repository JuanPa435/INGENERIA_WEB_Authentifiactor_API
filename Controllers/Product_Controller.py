from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.Product_Model import Product
from Models.User_Model import User
from Models.database import db

class ProductController:
    @staticmethod
    @jwt_required()
    def get_all_products():
        try:
            products = Product.query.all()
            return jsonify([product.to_dict() for product in products]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @jwt_required()
    def create_product():
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'msg': 'Solo los administradores pueden crear productos'}), 403

        data = request.get_json()
        
        try:
            new_product = Product(
                name=data['name'],
                description=data.get('description', ''),
                price=float(data['price']),
                stock=int(data['stock'])
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
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'msg': 'Solo los administradores pueden modificar productos'}), 403

        product = Product.query.get(product_id)
        if not product:
            return jsonify({'msg': 'Producto no encontrado'}), 404

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
            
            db.session.commit()
            return jsonify(product.to_dict()), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @jwt_required()
    def delete_product(product_id):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
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
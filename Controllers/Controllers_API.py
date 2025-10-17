from flask import Blueprint, request, jsonify
from Services.Services_API import ProductService
from flask_jwt_extended import jwt_required, get_jwt_identity

product_bp = Blueprint('product_bp', __name__)

# 🔹 Obtener todos los productos (todos los usuarios pueden)
@product_bp.route('/products', methods=['GET'])
@jwt_required(optional=True)
def get_products():
    products = ProductService.get_all_products()
    return jsonify([p.to_dict() for p in products]), 200

# 🔹 Obtener un producto por ID
@product_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required(optional=True)
def get_product(product_id):
    product = ProductService.get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify(product.to_dict()), 200

# 🔹 Crear producto (solo admin)
@product_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    user = get_jwt_identity()
    if user['role'] != 'admin':
        return jsonify({'error': 'Acceso denegado. Solo administradores pueden crear productos.'}), 403

    data = request.get_json()
    product = ProductService.create_product(data)
    return jsonify(product.to_dict()), 201

# 🔹 Actualizar producto (solo admin)
@product_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    user = get_jwt_identity()
    if user['role'] != 'admin':
        return jsonify({'error': 'Acceso denegado. Solo administradores pueden modificar productos.'}), 403

    data = request.get_json()
    product = ProductService.update_product(product_id, data)
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify(product.to_dict()), 200

# 🔹 Eliminar producto (solo admin)
@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user = get_jwt_identity()
    if user['role'] != 'admin':
        return jsonify({'error': 'Acceso denegado. Solo administradores pueden eliminar productos.'}), 403

    deleted = ProductService.delete_product(product_id)
    if not deleted:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify({'message': 'Producto eliminado exitosamente'}), 200

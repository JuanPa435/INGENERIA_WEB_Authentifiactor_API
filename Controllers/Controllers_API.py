from flask import Blueprint
from Controllers.Auth_Controller import *
from Controllers.Product_Controller import ProductController

# Crear los blueprints
product_bp = Blueprint('products', __name__)
auth_bp = Blueprint('auth', __name__)

# Rutas para productos
product_bp.route('/', methods=['GET'])(ProductController.get_all_products)
product_bp.route('/', methods=['POST'])(ProductController.create_product)
product_bp.route('/<int:product_id>', methods=['PUT'])(ProductController.update_product)
product_bp.route('/<int:product_id>', methods=['DELETE'])(ProductController.delete_product)

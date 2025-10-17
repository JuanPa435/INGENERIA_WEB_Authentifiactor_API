// Verificar si hay token de autenticación
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = 'login.html';
}

const API_BASE = window.location.origin + "/api";
let userRole = null;

// Función para decodificar el token JWT
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(window.atob(base64));
    } catch (e) {
        return null;
    }
}

// Verificar el rol del usuario
async function checkUserRole() {
    try {
        const response = await fetch(`${API_BASE}/auth/user-info`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        userRole = data.role;
        
        if (userRole === 'admin') {
            document.querySelectorAll('.admin-controls').forEach(el => {
                el.style.display = 'block';
            });
        }
    } catch (error) {
        console.error('Error al obtener información del usuario:', error);
    }
}

// Cargar productos
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error('Error al cargar productos:', error);
    }
}

// Mostrar productos en la interfaz
function displayProducts(products) {
    const grid = document.getElementById('products-grid');
    grid.innerHTML = '';

    products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <h3>${product.name}</h3>
            <p>${product.description || 'Sin descripción'}</p>
            <p class="product-price">$${product.price.toFixed(2)}</p>
            <p class="product-stock">Stock: ${product.stock}</p>
            ${userRole === 'admin' ? `
                <div class="admin-controls">
                    <button onclick="editProduct(${product.id})" class="edit-product-btn">Editar</button>
                    <button onclick="deleteProduct(${product.id})" class="delete-product-btn">Eliminar</button>
                </div>
            ` : ''}
        `;
        grid.appendChild(card);
    });
}

// Modal y formulario
const modal = document.getElementById('product-modal');
const closeBtn = document.querySelector('.close');
const addBtn = document.getElementById('add-product-btn');
const form = document.getElementById('product-form');
let isEditing = false;

addBtn?.addEventListener('click', () => {
    isEditing = false;
    document.getElementById('modal-title').textContent = 'Agregar Producto';
    form.reset();
    modal.style.display = 'block';
});

closeBtn?.addEventListener('click', () => {
    modal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Manejar envío del formulario
form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const productData = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value,
        price: parseFloat(document.getElementById('price').value),
        stock: parseInt(document.getElementById('stock').value)
    };

    try {
        const url = isEditing 
            ? `${API_BASE}/products/${document.getElementById('product-id').value}`
            : `${API_BASE}/products`;
            
        const method = isEditing ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(productData)
        });

        if (response.ok) {
            modal.style.display = 'none';
            loadProducts();
        } else {
            const error = await response.json();
            alert(error.msg || 'Error al guardar el producto');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al guardar el producto');
    }
});

// Editar producto
async function editProduct(id) {
    try {
        const response = await fetch(`${API_BASE}/products/${id}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const product = await response.json();
        
        document.getElementById('product-id').value = product.id;
        document.getElementById('name').value = product.name;
        document.getElementById('description').value = product.description || '';
        document.getElementById('price').value = product.price;
        document.getElementById('stock').value = product.stock;
        
        document.getElementById('modal-title').textContent = 'Editar Producto';
        isEditing = true;
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error al cargar el producto:', error);
        alert('Error al cargar el producto');
    }
}

// Eliminar producto
async function deleteProduct(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este producto?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/products/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            loadProducts();
        } else {
            const error = await response.json();
            alert(error.msg || 'Error al eliminar el producto');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar el producto');
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    checkUserRole();
    loadProducts();
});
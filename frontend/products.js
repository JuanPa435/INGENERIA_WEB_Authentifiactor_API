// Obtener token de autenticación (no redirigimos si falta: permitimos uso público)
const token = localStorage.getItem('token');

const API_BASE = window.location.origin + "/api";
let userRole = null;
let currentUserId = null;
let allProducts = [];
// nombre anónimo local que el usuario puede configurar
let anonName = localStorage.getItem('anon_name') || null;

// Para debugging - Mostrar el token decodificado
console.log('Token decodificado:', parseJwt(token));

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
        if (!token) {
            // Sin token: solo mostramos el botón y salimos
            const addProductBtn = document.getElementById('add-product-btn');
            if (addProductBtn) addProductBtn.style.display = 'flex';
            return;
        }

        const response = await fetch(`${API_BASE}/auth/user-info`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();
        console.log('Información del usuario:', data); // Para debugging
        
        // El rol viene dentro del objeto user en la respuesta
        userRole = data.role;
        
        // Obtener ID del usuario del token
        const decoded = parseJwt(token);
        if (decoded) {
            if (decoded.sub) {
                if (typeof decoded.sub === 'string' || typeof decoded.sub === 'number') {
                    currentUserId = parseInt(decoded.sub);
                } else if (typeof decoded.sub === 'object' && decoded.sub.id) {
                    currentUserId = parseInt(decoded.sub.id);
                }
            } else if (decoded.identity) {
                if (typeof decoded.identity === 'string' || typeof decoded.identity === 'number') {
                    currentUserId = parseInt(decoded.identity);
                } else if (typeof decoded.identity === 'object' && decoded.identity.id) {
                    currentUserId = parseInt(decoded.identity.id);
                }
            }
        }
        
        console.log('Rol del usuario:', userRole); // Para debugging
        console.log('ID del usuario:', currentUserId); // Para debugging

        // Mostrar link al perfil con username (y email si falta)
        const profileLink = document.getElementById('profile-link');
        if (profileLink) {
            const display = data.username || data.email || 'Usuario';
            profileLink.textContent = display;
            profileLink.style.display = 'inline';
        }

        // Mostrar botón de agregar producto solo para administradores
        const addProductBtn = document.getElementById('add-product-btn');
        if (addProductBtn) {
            addProductBtn.style.display = userRole === 'admin' ? 'flex' : 'none';
        }
    } catch (error) {
        console.error('Error al obtener información del usuario:', error);
        const addProductBtn = document.getElementById('add-product-btn');
        if (addProductBtn) addProductBtn.style.display = 'flex';
    }
}

// Cargar productos
async function loadProducts() {
    try {
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const response = await fetch(`${API_BASE}/products/`, { headers });
        const products = await response.json();
        allProducts = products;
        displayProducts(products);
    } catch (error) {
        console.error('Error al cargar productos:', error);
    }
}

// Mostrar productos en la interfaz
function displayProducts(products) {
    const grid = document.getElementById('products-grid');
    const noProducts = document.getElementById('no-products');
    grid.innerHTML = '';

    // Actualizar estadísticas
    document.getElementById('total-products').textContent = products.length;
    document.getElementById('low-stock').textContent = products.filter(p => p.stock < 10).length;

    if (products.length === 0) {
        const addFirstProductBtn = document.getElementById('add-first-product');
        
        // Mostrar/ocultar el botón de agregar primer producto según el rol
        if (addFirstProductBtn) {
            addFirstProductBtn.style.display = userRole === 'admin' ? 'flex' : 'none';
        }
        
        grid.style.display = 'none';
        noProducts.style.display = 'block';
        return;
    }

    grid.style.display = 'grid';
    noProducts.style.display = 'none';

    // currentUserId ya está establecido globalmente en checkUserRole

    products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        
        // El administrador puede editar todos los productos
        // Los usuarios normales solo pueden editar sus propios productos
        const isOwner = currentUserId && product.created_by && parseInt(product.created_by) === parseInt(currentUserId);
        const canEdit = userRole === 'admin' || isOwner; // admin puede editar todo
        
        if (canEdit) {
            card.classList.add('editable');
            // Añadir título para indicar que es editable
            card.setAttribute('title', 'Clic para editar');
        }
        
        const stockClass = product.stock < 10 ? 'low-stock' : product.stock > 50 ? 'high-stock' : '';

        const shortDesc = (product.description || 'Sin descripción').length > 120
            ? (product.description || 'Sin descripción').slice(0, 117) + '...'
            : (product.description || 'Sin descripción');

        card.innerHTML = `
            <div class="product-header">
                <h3 style="margin:0 0 6px 0">${product.name}</h3>
                ${ canEdit ? `
                    <div class="admin-controls">
                        <button class="delete-product-btn" title="Eliminar" data-id="${product.id}">
                            <span class="material-icons">delete</span>
                        </button>
                    </div>
                ` : ''}
            </div>
            <div style="margin-top:8px;color:#6b7280;font-size:0.9em;">Creado por: ${product.created_by_username || product.created_by_name || (anonName || 'Anónimo')}</div>
            <p class="product-description">${shortDesc}</p>
            <div class="product-details" style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;">
                <div class="price-badge" style="font-weight:700;color:#2d3748;">$${product.price.toFixed(2)}</div>
                <div class="product-stock ${stockClass}" style="font-size:0.95em;color:#4a5568;"> 
                    <span class="material-icons" style="vertical-align:middle;">${
                        product.stock < 10 ? 'warning' : 
                        product.stock > 50 ? 'inventory_2' : 'inventory'
                    }</span>
                    <span style="margin-left:6px;">Stock: ${product.stock}</span>
                </div>
            </div>
            ${canEdit ? `
                <div class="edit-overlay">
                    <span class="material-icons">edit</span>
                    ${userRole === 'admin' && !isOwner ? '<span class="admin-edit-badge">Admin</span>' : ''}
                </div>
            ` : ''}
        `;
        // Event listeners para editar/eliminar
        if (canEdit) {
            card.addEventListener('click', (e) => {
                // Si el clic fue en el botón de eliminar, no editar
                if (e.target.closest('.delete-product-btn')) return;
                editProduct(product.id);
            });
            
            // Manejar eliminación
            const deleteBtn = card.querySelector('.delete-product-btn');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', (e) => {
                    e.stopPropagation(); // Evitar que active la edición
                    deleteProduct(product.id);
                });
            }
        }
        
        grid.appendChild(card);
    });
}

// Modal y formulario
const modal = document.getElementById('product-modal');
const closeBtn = document.querySelector('.close');
const addBtn = document.getElementById('add-product-btn');
const form = document.getElementById('product-form');
const cancelBtn = document.getElementById('cancel-btn');
let isEditing = false;

// helper de toasts
function showToast(message, timeout = 3000) {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = message;
    container.appendChild(t);
    // forzar reflow para animación
    requestAnimationFrame(() => t.classList.add('show'));
    setTimeout(() => {
        t.classList.remove('show');
        setTimeout(() => t.remove(), 220);
    }, timeout);
}

addBtn?.addEventListener('click', () => {
    isEditing = false;
    document.getElementById('modal-title').textContent = 'Agregar Producto';
    form.reset();
    modal.setAttribute('aria-hidden', 'false');
});

closeBtn?.addEventListener('click', () => {
    modal.setAttribute('aria-hidden', 'true');
});

cancelBtn?.addEventListener('click', () => {
    modal.setAttribute('aria-hidden', 'true');
});

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.setAttribute('aria-hidden', 'true');
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
            : `${API_BASE}/products/`;
            
        const method = isEditing ? 'PUT' : 'POST';
        
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        // si no hay token y existe anonName, enviarlo como created_by_name
        if (!token && anonName && !isEditing) {
            productData.created_by_name = anonName;
        }

        const response = await fetch(url, {
            method,
            headers,
            body: JSON.stringify(productData)
        });

        if (response.ok) {
            modal.setAttribute('aria-hidden', 'true');
            const result = await response.json();
            if (isEditing) {
                // en edición, recargar toda la lista para tener datos frescos
                loadProducts();
            } else {
                // en creación, añadir al inicio de la lista actual
                allProducts.unshift(result);
                displayProducts(allProducts);
            }
            showToast(isEditing ? 'Producto actualizado' : 'Producto creado');
        } else {
            const error = await response.json();
            showToast(error.msg || 'Error al guardar el producto');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al guardar el producto');
    }
});

// Editar producto
async function editProduct(id) {
    try {
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const response = await fetch(`${API_BASE}/products/${id}`, { headers });
        
        if (!response.ok) {
            const error = await response.json();
            showToast(error.msg || 'Error al cargar el producto');
            return;
        }
        
        const product = await response.json();
        document.getElementById('product-id').value = product.id;
        document.getElementById('name').value = product.name;
        document.getElementById('description').value = product.description || '';
        document.getElementById('price').value = product.price;
        document.getElementById('stock').value = product.stock;
        
        // Verificar si es edición de admin en producto ajeno
        const isAdminEditingOther = userRole === 'admin' && 
            currentUserId && product.created_by && 
            parseInt(product.created_by) !== parseInt(currentUserId);
            
        document.getElementById('modal-title').textContent = 'Editar Producto';
        
        // Mostrar badge de admin si corresponde
        const adminBadge = document.querySelector('.admin-edit-badge-modal');
        if (adminBadge) {
            adminBadge.style.display = isAdminEditingOther ? 'inline-flex' : 'none';
        }
        
        isEditing = true;
        modal.setAttribute('aria-hidden', 'false');
    } catch (error) {
        console.error('Error al cargar el producto:', error);
        showToast('Error al cargar el producto');
    }
}

// Eliminar producto
async function deleteProduct(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este producto?')) {
        return;
    }

    try {
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const response = await fetch(`${API_BASE}/products/${id}`, {
            method: 'DELETE',
            headers
        });

        if (response.ok) {
            showToast('Producto eliminado correctamente');
            loadProducts(); // refrescar lista
        } else {
            const error = await response.json();
            showToast(error.msg || 'Error al eliminar el producto');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al eliminar el producto');
    }
}

// Función de búsqueda y filtrado
function filterProducts() {
    const searchTerm = document.getElementById('search-products').value.toLowerCase();
    const sortBy = document.getElementById('sort-by').value;
    
    let filtered = [...allProducts];

    // Aplicar búsqueda
    if (searchTerm) {
        filtered = filtered.filter(product => 
            product.name.toLowerCase().includes(searchTerm) ||
            product.description.toLowerCase().includes(searchTerm)
        );
    }

    // Aplicar ordenamiento
    switch(sortBy) {
        case 'name':
            filtered.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'price-asc':
            filtered.sort((a, b) => a.price - b.price);
            break;
        case 'price-desc':
            filtered.sort((a, b) => b.price - a.price);
            break;
        case 'stock':
            filtered.sort((a, b) => b.stock - a.stock);
            break;
    }

    displayProducts(filtered);
}

// Función de logout
function logout() {
    localStorage.removeItem('token');
    window.location.href = 'login.html';
}

// Event listeners
document.getElementById('search-products')?.addEventListener('input', filterProducts);
document.getElementById('sort-by')?.addEventListener('change', filterProducts);

document.getElementById('add-first-product')?.addEventListener('click', () => {
    isEditing = false;
    document.getElementById('modal-title').textContent = 'Agregar Producto';
    form.reset();
    modal.setAttribute('aria-hidden', 'false');
});

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    checkUserRole();
    loadProducts();
});
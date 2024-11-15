document.addEventListener('DOMContentLoaded', loadProducts);

const mesaId = document.querySelector('meta[name="mesa-id"]').content;

function loadProducts() {
    fetch('http://127.0.0.1:8000/api/products/all/')
        .then(response => response.json())
        .then(data => {
            displayProducts(data.products);
        })
        .catch(error => console.error('Error fetching products:', error));
}

function displayProducts(products) {
    const menu = document.querySelector('.menu');
    menu.innerHTML = '';

    products.forEach(product => {
        const productItem = document.createElement('div');
        productItem.classList.add('menu-item', `category-${product.categoria}`);

        let stockMessage = '';
        if (product.stock <= 0) {
            stockMessage = `<p class="out-of-stock">Agotado</p>`;
        }

        productItem.innerHTML = `
            <img src="path/to/${product.nombre.replace(/\s+/g, '-').toLowerCase()}.jpg" alt="${product.nombre}">
            <p>${product.nombre}</p>
            <p>${product.descripcion}</p>
            <p class="price">$${parseFloat(product.precio).toFixed(2)}</p>
            ${stockMessage}
            <button onclick="addToOrder(${product.id}, '${product.nombre}', ${parseFloat(product.precio).toFixed(2)})" 
                    ${product.stock <= 0 ? 'disabled' : ''}>Agregar a la Comanda</button>
        `;
        
        menu.appendChild(productItem);
    });
}

function filterCategory(category) {
    const allItems = document.querySelectorAll('.menu-item');
    allItems.forEach(item => {
        if (category === 'all' || item.classList.contains(`category-${category}`)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });

    document.querySelectorAll('.category-button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelector(`.category-button[onclick*="${category}"]`).classList.add('active');
}


function addToOrder(productId, productName, productPrice) {
    const orderItemsContainer = document.querySelector('.order-items');
    const orderItem = document.createElement('div');
    orderItem.classList.add('order-item');
    orderItem.setAttribute('data-id', productId); // Asegúrate de agregar data-id
    orderItem.innerHTML = `
        <p>${productName} - $${productPrice.toFixed(2)}</p>
        <button class="delete" onclick="removeOrderItem(this)">🗑️</button>
    `;
    orderItemsContainer.appendChild(orderItem);
    updateTotal();
}

function removeOrderItem(button) {
    button.parentElement.remove();
    updateTotal();
}

function updateTotal() {
    const orderItems = document.querySelectorAll('.order-item');
    let total = 0;
    orderItems.forEach(item => {
        const priceText = item.querySelector('p').textContent.split(' - ')[1];
        if (priceText) { // Asegúrate de que priceText no es null
            total += parseFloat(priceText.replace('$', ''));
        }
    });
    document.querySelector('.total').textContent = total.toFixed(2);
}

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Manejador para el botón de pagar
const payButton = document.querySelector('.pay');
if (payButton) {
    payButton.addEventListener('click', function () {
        const orderItemsContainer = document.querySelector('.order-items');
        const orderItems = orderItemsContainer.children.length;

        if (orderItems === 0) {
            alert('Por favor, agrega al menos un producto a la comanda antes de pagar.');
            return;
        }

        const orderItemsData = [...orderItemsContainer.children].map(item => {
            const priceText = item.querySelector('p').textContent.split(' - ')[1]; // Obtener el precio
            return {
                producto_id: parseInt(item.dataset.id),
                cantidad: 1,
                precio: parseFloat(priceText.replace('$', '').trim()) // Asegúrate de obtener el precio
            };
        });

        console.log('Datos a enviar:', {
            mesa_id: mesaId,
            items: orderItemsData
        });

        fetch('http://127.0.0.1:8000/api/pedido/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                mesa_id: mesaId,
                items: orderItemsData
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la red');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            if (data.mensaje) {
                alert(data.mensaje);
                displayRecentOrder(orderItemsData);
                orderItemsContainer.innerHTML = ''; 
                updateTotal(); 
            } else {
                alert(data.error);
            }
        })
        .catch(error => console.error('Error al crear el pedido:', error));
    });
}

// Función para mostrar el pedido reciente
function displayRecentOrder(orderItems) {
    const recentOrderDetails = document.querySelector('.recent-order-details');
    recentOrderDetails.innerHTML = ''; // Limpiar detalles anteriores

    let totalPrecio = 0; // Inicializar total de precio
    orderItems.forEach(item => {
        const orderDetail = document.createElement('div');
        orderDetail.innerHTML = `<p>Producto ID: ${item.producto_id} - Precio: $${item.precio.toFixed(2)}</p>`;
        recentOrderDetails.appendChild(orderDetail);
        totalPrecio += item.precio; // Sumar precio al total
    });

    const totalOrderDetail = document.createElement('div');
    totalOrderDetail.innerHTML = `<p>Total del Pedido: $${totalPrecio.toFixed(2)}</p>`;
    recentOrderDetails.appendChild(totalOrderDetail);
}

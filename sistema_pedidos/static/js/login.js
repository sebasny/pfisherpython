document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        const response = await fetch('http://127.0.0.1:8000/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        const result = await response.json();
        
        const messageDiv = document.getElementById('message');
        
        if (result.mensaje) {
            messageDiv.textContent = result.mensaje;
            setTimeout(() => {
                window.location.href = 'http://127.0.0.1:8000/'; // Redirigir a la página de pedidos
            }, 2000);
        } else {
            messageDiv.textContent = result.error;
        }
    });
});

// Función para obtener CSRF Token
function getCSRFToken() {
    const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
    return cookieValue ? cookieValue.pop() : '';
}

// Función para limpiar localStorage/cache después de logout
function clearAppCache() {
    localStorage.removeItem('sessionState');
    sessionStorage.clear();
    indexedDB.deleteDatabase('localforage');
}


// Funciones globales para SweetAlert2
window.showSuccessAlert = function(message, options = {}) {
    return Swal.fire({
        title: 'Éxito',
        text: message,
        icon: 'success',
        ...options
    });
};

window.showErrorAlert = function(message, options = {}) {
    return Swal.fire({
        title: 'Error',
        text: message,
        icon: 'error',
        ...options
    });
};
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

  
    if (window.djangoMessages) {
        Object.entries(window.djangoMessages).forEach(([type, messages]) => {
            if (messages.length > 0) {
                const options = {
                    icon: type,
                    html: messages.join('<br>'),
                    showConfirmButton: false,
                    timer: 3000
                };
                
                if (type === 'success') {
                    window.showSuccessAlert(messages.join('<br>'), options);
                } else {
                    window.showErrorAlert(messages.join('<br>'), options);
                }
            }
        });
    }
    function getCSRFToken() {
        const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
        return cookieValue ? cookieValue.pop() : '';
    }

    // Manejar formularios AJAX
    document.querySelectorAll('form[data-ajax]').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;

            try {
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    ${submitBtn.dataset.processingText || 'Procesando...'}
                `;
                submitBtn.disabled = true;

                const response = await fetch(form.action, {
                    method: form.method,
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCSRFToken()
                    }
                });

                const data = await response.json();

                if (data.success) {
                    window.showSuccessAlert(data.message, {
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => {
                        if(data.redirect_url) {
                            window.location.href = data.redirect_url;
                        }
                    });
                } else {
                    window.showErrorAlert(data.errors.join('<br>'), {
                        title: 'Error de validación'
                    });
                }
            } catch (error) {
                window.showErrorAlert('No se pudo contactar al servidor', {
                    title: 'Error de conexión'
                });
            } finally {
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    });

    // Toggle password visibility
    document.querySelectorAll('.password-toggle').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const input = button.previousElementSibling;
            const icon = button.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    });

    // Auto-ocultar mensajes después de 5 segundos
    setTimeout(() => {
        document.querySelectorAll('.toast').forEach(toast => {
            new bootstrap.Toast(toast).hide();
        });
    }, 5000);
});

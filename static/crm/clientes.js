document.addEventListener('DOMContentLoaded', () => {
    // ========== [CONSTANTES Y FUNCIONES UTILITARIAS] ==========
    const handleRowClick = () => {
        document.querySelectorAll('.clickable-row').forEach(row => {
            // Manejar clics
            row.addEventListener('click', (e) => {
                // Ignorar clicks en elementos interactivos
                if (e.target.closest('a, button, .actions-container')) {
                    return;
                }
                
                // Obtener URL y navegar
                const url = row.dataset.clientUrl;
                if (url) window.location.href = url;
            });

            // Manejar teclado (accesibilidad)
            row.addEventListener('keydown', (e) => {
                if (['Enter', ' '].includes(e.key)) {
                    e.preventDefault();
                    const url = row.dataset.clientUrl;
                    if (url) window.location.href = url;
                }
            });
        });
    };
    const ALERT_TIMEOUT = 3000;
    const DEBOUNCE_DELAY = 300;
    
    const getCSRFToken = () => {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    };

    const showAlert = (type, message, timer = ALERT_TIMEOUT) => {
        const icon = type === 'success' ? 'check-circle' : 'exclamation-triangle';
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer,
            timerProgressBar: true
        });
        
        Toast.fire({
            icon: type,
            title: message,
            iconHtml: `<i class="bi bi-${icon}"></i>`
        });
    };


    // ========== [FUNCIONALIDAD DE ELIMINACIÓN MEJORADA] ==========
    const handleDelete = async (url, rowElement) => {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Error en la respuesta del servidor');

            if (rowElement) {
                rowElement.remove();
                showAlert('success', 'Cliente eliminado exitosamente');
            }
            return true;

        } catch (error) {
            showAlert('error', 'No se pudo eliminar el cliente');
            console.error('Error:', error);
            return false;
        }
    };

    // ========== [MANEJO DE EVENTOS CON DELEGACIÓN] ==========
    document.addEventListener('click', (e) => {
        // Edición
        if (e.target.closest('.edit-client')) {
            e.preventDefault();
            const button = e.target.closest('.edit-client');
            loadEditForm(button.dataset.url);
        }

        // Eliminación
        if (e.target.closest('.delete-client')) {
            e.preventDefault();
            const button = e.target.closest('.delete-client');
            const row = button.closest('tr');
            const modal = new bootstrap.Modal('#deleteConfirmationModal');

            modal.show();
            document.getElementById('confirmDeleteButton').onclick = async () => {
                await handleDelete(button.dataset.href, row);
                modal.hide();
            };
        }
    });

    // ========== [INICIALIZACIÓN DE COMPONENTES] ==========
    const initComponents = () => {
        handleRowClick(); // Añadir esta línea
    // Tooltips
    new bootstrap.Tooltip(document.body, {
        selector: '[data-bs-toggle="tooltip"]',
        boundary: 'window'
        
    });
};

initComponents();
    // Limpieza de modal al cerrar
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', () => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
            
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '';
        });
    });

    // Cargar datos iniciales para elementos existentes
    document.querySelectorAll('[data-client-id]').forEach(row => {
        row.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
    });
});


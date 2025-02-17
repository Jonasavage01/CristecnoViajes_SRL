document.addEventListener('DOMContentLoaded', () => {
    /*** Funcionalidad de EDICIÓN ***/
   
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('hidden.bs.modal', () => {
        // Eliminar backdrop manualmente si persiste
        const backdrops = document.getElementsByClassName('modal-backdrop');
        while(backdrops.length > 0) {
            backdrops[0].parentNode.removeChild(backdrops[0]);
        }
        // Restaurar scroll del body
        document.body.style.overflow = 'visible';
        document.body.style.paddingRight = '0';
    });
});

// clientes.js (modificar la función loadEditForm)
const loadEditForm = async (url) => {
    try {
        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const html = await response.text();
        const modalElement = document.getElementById('clienteEditModal');
        const modal = new bootstrap.Modal(modalElement);
        const container = modalElement.querySelector('#formContainer');
        
        container.innerHTML = html;
        modal.show();
        
        // Disparar evento para inicialización
        document.dispatchEvent(new CustomEvent('ajaxFormLoaded', {
            detail: { form: container.querySelector('form') }
        }));
        
    } catch (error) {
        showAlert('error', `Error cargando formulario: ${error.message}`);
    }
};

document.querySelectorAll('.edit-client').forEach(button => {
    button.addEventListener('click', (e) => {
        e.preventDefault();
        loadEditForm(e.currentTarget.dataset.url);
    });
});


// Nueva función de inicialización
const initEditFormValidation = (modalElement) => {
    // Validación en tiempo real
    modalElement.querySelectorAll('input, select, textarea').forEach(field => {
        field.addEventListener('input', () => validateField(field));
    });

    // Manejar envío
    const form = modalElement.querySelector('#clienteEditForm');
    form.addEventListener('submit', handleFormSubmit);

    // Enfocar primer campo
    const firstInput = form.querySelector('input:not([type="hidden"])');
    firstInput?.focus();

    // Limpiar errores al cerrar
    modalElement.addEventListener('hidden.bs.modal', () => {
        modalElement.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
    });
};

    document.querySelectorAll('.edit-client').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            loadEditForm(e.currentTarget.dataset.url);
        });
    });

    /*** Funcionalidad de ELIMINACIÓN ***/
    let deleteTarget = null;
    const deleteModal = new bootstrap.Modal('#deleteConfirmationModal');

    document.querySelectorAll('.delete-client').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            deleteTarget = {
                url: e.currentTarget.dataset.href,
                row: e.target.closest('tr')
            };
            deleteModal.show();
        });
    });

    document.getElementById('confirmDeleteButton')?.addEventListener('click', async () => {
        if (!deleteTarget) return;

        try {
            const response = await fetch(deleteTarget.url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                deleteTarget.row?.remove();
                showAlert('success', 'Cliente eliminado exitosamente');
            } else {
                throw new Error('Error en la eliminación');
            }
        } catch (error) {
            showAlert('error', 'No se pudo eliminar el cliente');
            console.error('Error:', error);
        } finally {
            deleteModal.hide();
            deleteTarget = null;
        }
    });

    /*** Inicialización de Tooltips ***/
    new bootstrap.Tooltip(document.body, {
        selector: '[data-bs-toggle="tooltip"]'
    });
});
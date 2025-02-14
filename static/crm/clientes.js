document.addEventListener('DOMContentLoaded', () => {
    /*** Funcionalidad de EDICIÓN (mejorado) ***/
    document.querySelectorAll('.edit-client').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const url = e.currentTarget.dataset.url;
            
            try {
                const response = await fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCSRFToken()
                    }
                });
                
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                
                const html = await response.text();
                const modal = new bootstrap.Modal('#clienteEditModal');
                const container = document.querySelector('#clienteEditModal #formContainer');
                
                container.innerHTML = html;
                modal.show();
                
                // Reiniciar validaciones
                document.dispatchEvent(new CustomEvent('ajaxFormLoaded', {
                    detail: { form: container.querySelector('form') }
                }));
                
            } catch (error) {
                showAlert('error', `Error cargando formulario: ${error.message}`);
            }
        });
    });

    async function loadEditForm(url) {
        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                }
            });
    
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const html = await response.text();
            const modal = new bootstrap.Modal('#clienteEditModal');
            const container = document.querySelector('#clienteEditModal #formContainer');
            
            container.innerHTML = html;
            modal.show();
            
            // Disparar evento para validación
            document.dispatchEvent(new CustomEvent('ajaxFormLoaded', {
                detail: { form: container.querySelector('form') }
            }));
            
        } catch (error) {
            showAlert('danger', `Error cargando formulario: ${error.message}`);
        }
    }
    

    /*** Funcionalidad de ELIMINACIÓN ***/
    const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.content;
    const DELETE_MODAL_ELEMENT = document.getElementById('deleteConfirmationModal');
    const DELETE_MODAL = DELETE_MODAL_ELEMENT ? new bootstrap.Modal(DELETE_MODAL_ELEMENT) : null;

    // Inicialización de tooltips
    const initTooltips = () => {
        const tooltipElements = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipElements.forEach(el => new bootstrap.Tooltip(el));
    };

    // Configurar los eventos para eliminación
    const initDeleteHandlers = () => {
        let deleteTarget = null;

       // Inicializar al hacer clic en editar
document.querySelectorAll('.edit-client').forEach(button => {
    button.addEventListener('click', e => {
        e.preventDefault();
        loadEditForm(e.currentTarget.dataset.url);
    });
});

        const confirmBtn = document.getElementById('confirmDeleteButton');
        if (confirmBtn && DELETE_MODAL) {
            confirmBtn.addEventListener('click', async () => {
                if (!deleteTarget || !CSRF_TOKEN) {
                    console.error('Faltan parámetros para la eliminación');
                    DELETE_MODAL.hide();
                    return;
                }
                try {
                    const response = await fetch(deleteTarget.url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': CSRF_TOKEN,
                            'X-Requested-With': 'XMLHttpRequest',
                            'Accept': 'application/json'
                        },
                        credentials: 'same-origin'
                    });
                    await handleResponse(response, deleteTarget.row);
                } catch (error) {
                    handleError(error);
                } finally {
                    DELETE_MODAL.hide();
                    deleteTarget = null;
                }
            });
        }
    };

    const handleResponse = async (response, targetRow) => {
        if (response.redirected) {
            return window.location.assign(response.url);
        }
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        const contentType = response.headers.get('content-type');
        if (!contentType?.includes('application/json')) {
            throw new Error('Respuesta no JSON del servidor');
        }
        const data = await response.json();
        if (data.success) {
            handleSuccess(targetRow);
        } else {
            throw new Error(data.message || 'Error en la operación');
        }
    };

    const handleSuccess = (targetRow) => {
        if (targetRow?.parentNode) {
            targetRow.remove();
        } else {
            window.location.reload();
        }
    };

    const handleError = (error) => {
        console.error('Error en operación:', error);
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message || 'No se pudo completar la operación',
                confirmButtonColor: '#3085d6'
            });
        } else {
            alert(error.message || 'Error en la operación');
        }
    };

    // Inicialización general
    const init = () => {
        if (!CSRF_TOKEN) {
            console.error('CSRF token no encontrado');
            return;
        }
        initTooltips();
        initDeleteHandlers();
    };

    init();
});

/*** Validación en tiempo real del formulario ***/
function setupRealTimeValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('input', e => {
            const input = e.target;
            if (input.tagName.toLowerCase() === 'input') {
                validateField(input);
            }
        });

        form.addEventListener('submit', e => {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function validateField(input) {
    const formGroup = input.closest('.form-group') || input.closest('.mb-3');
    const errorElement = formGroup?.querySelector('.invalid-feedback');
    
    if (!input.checkValidity()) {
        input.classList.add('is-invalid');
        if (errorElement) errorElement.style.display = 'block';
    } else {
        input.classList.remove('is-invalid');
        if (errorElement) errorElement.style.display = 'none';
    }
}

// Inicializar validaciones cuando el DOM está listo
document.addEventListener('DOMContentLoaded', () => {
    setupRealTimeValidation();
});
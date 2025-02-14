document.addEventListener('DOMContentLoaded', () => {
    /*** Funcionalidad de EDICIÓN ***/
    // Manejar clic en botones de edición
    document.querySelectorAll('.edit-client').forEach(button => {
        button.addEventListener('click', e => {
            e.preventDefault();
            const url = button.dataset.url;
            loadEditForm(url);
        });
    });

    // Función para cargar el formulario de edición vía AJAX
    async function loadEditForm(url) {
        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (!response.ok) throw new Error('Error cargando formulario');
            
            const html = await response.text();
            const modalContent = document.querySelector('#clienteEditModal .modal-content');
            if (!modalContent) throw new Error('No se encontró el contenedor del modal de edición');
            
            modalContent.innerHTML = html;
            
            // Reiniciar validaciones (se asume que esta función existe)
            if (typeof setupRealTimeValidation === 'function') {
                setupRealTimeValidation();
            }
            
            new bootstrap.Modal(document.getElementById('clienteEditModal')).show();
        } catch (error) {
            console.error('Error:', error);
            if (typeof showErrorAlert === 'function') {
                showErrorAlert('Error cargando formulario de edición');
            } else {
                alert('Error cargando formulario de edición');
            }
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

        // Configurar evento en cada botón de eliminación
        document.querySelectorAll('.delete-client').forEach(btn => {
            btn.addEventListener('click', e => {
                e.preventDefault();
                if (!DELETE_MODAL) return;
                deleteTarget = {
                    url: btn.dataset.href,
                    row: btn.closest('tr')
                };
                console.debug('Delete target:', deleteTarget);
                DELETE_MODAL.show();
            });
        });

        // Confirmar eliminación al pulsar el botón del modal
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

    // Función para manejar la respuesta del servidor en la eliminación
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
        console.debug('Server response:', data);
        if (data.success) {
            handleSuccess(targetRow);
        } else {
            throw new Error(data.message || 'Error en la operación');
        }
    };

    // Función para manejar el éxito en la eliminación
    const handleSuccess = (targetRow) => {
        if (targetRow?.parentNode) {
            targetRow.remove();
            console.debug('Fila eliminada correctamente');
        } else {
            console.warn('Elemento no encontrado, recargando página...');
            window.location.reload();
        }
    };

    // Función para manejar errores en la eliminación
    const handleError = (error) => {
        console.error('Error en operación:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'No se pudo completar la operación',
            confirmButtonColor: '#3085d6'
        });
    };

    // Función de inicialización general
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

// static/crm/empresas.js
document.addEventListener('DOMContentLoaded', function() {
    const showErrorAlert = window.showErrorAlert;
    const showSuccessAlert = window.showSuccessAlert;
    const empresaForm = document.getElementById('empresaForm');
    const empresaModal = new bootstrap.Modal(document.getElementById('empresaModal'));
    let isSubmitting = false;

    // Manejar submit del formulario
    empresaForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (isSubmitting) return;
        isSubmitting = true;

        const formData = new FormData(empresaForm);
        const submitBtn = empresaForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        
        // Mostrar estado de carga
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spin me-2"></i>Guardando...';

        fetch(empresaForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) return response.json().then(err => { throw err; });
            return response.json();
        })
        .then(data => {
            if (data.success) handleSuccess(data);
            else handleFormErrors(data.errors, data.form_errors);
        })
        .catch(error => handleRequestError(error))
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
            isSubmitting = false;
        });
    });

    // Función para manejar éxito
    function handleSuccess(data) {
        showSuccessAlert(data.message, 3000);
        empresaModal.hide();
        
        // Actualizar tabla
        const empresasTable = document.getElementById('empresasTable');
        if (data.table_html && empresasTable) {
            empresasTable.innerHTML = data.table_html;
            initDynamicFeatures();
            highlightNewRow(data.empresa_data.id);
        }
        
        // Resetear formulario y actualizar UI
        resetFormAndUI();
        updateEmpresaCount();
    }

    // Función para resaltar nueva fila
    function highlightNewRow(empresaId) {
        const newRow = document.querySelector(`tr[data-empresa-id="${empresaId}"]`);
        if (newRow) {
            newRow.classList.add('new-row-highlight');
            setTimeout(() => newRow.classList.remove('new-row-highlight'), 2000);
        }
    }

    // Función para resetear formulario
    function resetFormAndUI() {
        if (!empresaForm.querySelector('#id_documento').files.length) {
            empresaForm.reset();
        }
        document.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
    }

    // Función para actualizar contador
    function updateEmpresaCount() {
        const countBadge = document.querySelector('.badge.text-info');
        if (countBadge) {
            const currentCount = parseInt(countBadge.textContent) || 0;
            countBadge.textContent = currentCount + 1;
        }
    }

    // Función para manejar errores
    function handleFormErrors(errors, formErrors) {
        // Limpiar errores previos
        empresaForm.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        empresaForm.querySelectorAll('.invalid-feedback').forEach(el => {
            el.style.display = 'none';
        });

        // Mostrar errores de campos
        if (formErrors) {
            Object.entries(formErrors).forEach(([fieldName, errors]) => {
                const input = document.querySelector(`[name="${fieldName}"]`);
                const errorContainer = input?.closest('.position-relative')?.querySelector('.invalid-feedback');
                
                if (input && errorContainer) {
                    input.classList.add('is-invalid');
                    errorContainer.textContent = errors[0].message;
                    errorContainer.style.display = 'block';
                }
            });
        }

        // Scroll al primer error y mostrar contador
        const firstErrorField = document.querySelector('.is-invalid');
        if (firstErrorField) {
            firstErrorField.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
        updateErrorCount(errors.length);
    }

    // Función para actualizar contador de errores
    function updateErrorCount(errorCount) {
        let errorBadge = document.getElementById('errorCountBadge');
        if (!errorBadge) {
            errorBadge = document.createElement('div');
            errorBadge.id = 'errorCountBadge';
            errorBadge.className = 'position-fixed bottom-0 end-0 mb-4 me-4 badge bg-danger';
            document.body.appendChild(errorBadge);
        }
        errorBadge.textContent = `${errorCount} error(es) por corregir`;
        setTimeout(() => errorBadge.remove(), 5000);
    }

    // Función para manejar errores de red/servidor
    function handleRequestError(error) {
        let errorMessage = 'Error en el servidor';
        if (error instanceof TypeError) errorMessage = 'Error de conexión';
        else if (error.errors) errorMessage = error.errors.join(', ');
        
        showErrorAlert(errorMessage);
    }

    // Inicializar características dinámicas
    function initDynamicFeatures() {
        // Tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl, { trigger: 'hover' });
        });

        // Eventos de edición/eliminación
        document.querySelectorAll('.edit-empresa').forEach(btn => {
            btn.addEventListener('click', handleEditEmpresa);
        });
        
        document.querySelectorAll('.delete-empresa').forEach(btn => {
            btn.addEventListener('click', handleDeleteEmpresa);
        });

        // Limpiar errores al ingresar datos
        empresaForm.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('input', () => {
                field.classList.remove('is-invalid');
                const errorContainer = field.closest('.position-relative')?.querySelector('.invalid-feedback');
                if (errorContainer) errorContainer.style.display = 'none';
            });
        });
    }

    // Obtener token CSRF
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Manejar edición de empresa
    function handleEditEmpresa(e) {
        e.preventDefault();
        const empresaId = this.dataset.pk;
        // Lógica de edición aquí...
    }



    // Inicializar características al cargar
    initDynamicFeatures();

    // Limpiar errores al abrir el modal
    empresaModal._element.addEventListener('shown.bs.modal', () => {
        empresaForm.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        document.querySelectorAll('.invalid-feedback').forEach(el => {
            el.style.display = 'none';
        });
    });
    document.querySelectorAll('.delete-empresa').forEach(btn => {
        btn.addEventListener('click', handleDeleteEmpresa);
    })
});

/* Editar empresa form */
// Manejar edición de empresas
document.addEventListener('DOMContentLoaded', function() {
    let editModal = null;
    
    // Delegación de eventos para botones de edición
    document.body.addEventListener('click', function(e) {
        if(e.target.closest('.edit-empresa')) {
            e.preventDefault();
            handleEditEmpresa(e.target.closest('.edit-empresa'));
        }
    });

    async function handleEditEmpresa(btn) {
        const url = btn.dataset.url;
        const empresaId = btn.dataset.pk;
        
        try {
            const response = await fetch(url, {
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });
            
            if (!response.ok) throw new Error('Error cargando formulario');
            
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const modalElement = doc.getElementById('empresaEditModal');
            
            // Eliminar modal existente si hay
            if (editModal) {
                editModal.dispose();
                document.getElementById('empresaEditModal')?.remove();
            }
            
            document.body.appendChild(modalElement);
            editModal = new bootstrap.Modal(modalElement);
            
            // Configurar evento submit
            modalElement.querySelector('form').addEventListener('submit', handleEditSubmit);
            editModal.show();
            
        } catch (error) {
            console.error('Error:', error);
            showErrorAlert('Error al cargar formulario de edición');
        }
    }

    async function handleEditSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const url = form.action;
        const empresaId = new URL(url).pathname.split('/').filter(Boolean).pop();
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        
        try {
            // Mostrar estado de carga
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spin me-2"></i>Guardando...';

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: formData
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.errors || 'Error al guardar cambios');
            }

            if (data.success) {
                // Actualizar la fila en la tabla
                updateEmpresaRow(data.empresa_data);
                editModal.hide();
                showSuccessAlert(data.message, 3000);
            }
            
        } catch (error) {
            console.error('Error:', error);
            handleEditErrors(error, form);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    }

    function updateEmpresaRow(empresaData) {
        const row = document.querySelector(`tr[data-empresa-id="${empresaData.id}"]`);
        
        if (row) {
            // Actualizar cada celda con los nuevos datos
            row.querySelector('.nombre-comercial').textContent = empresaData.nombre_comercial;
            row.querySelector('.razon-social').textContent = empresaData.razon_social;
            row.querySelector('.rnc code').textContent = empresaData.rnc;
            row.querySelector('.estado .badge').textContent = empresaData.estado_display;
            row.querySelector('.estado .badge').className = `badge badge-estado bg-${empresaData.estado_color}`;
            row.querySelector('.telefono').textContent = empresaData.telefono;
            row.querySelector('.direccion-electronica').textContent = empresaData.direccion_electronica;
            
            // Resaltar la fila actualizada
            row.classList.add('updated-row');
            setTimeout(() => row.classList.remove('updated-row'), 2000);
        }
    }

    function handleEditErrors(error, form) {
        // Limpiar errores previos
        form.querySelectorAll('.is-invalid').forEach(field => field.classList.remove('is-invalid'));
        form.querySelectorAll('.invalid-feedback').forEach(el => el.style.display = 'none');
    
        // Mostrar nuevos errores
        if (error.errors) {
            Object.entries(error.errors).forEach(([field, errors]) => {
                const input = form.querySelector(`[name="${field}"]`);
                const errorContainer = input?.closest('.position-relative')?.querySelector('.invalid-feedback');
                
                if (input && errorContainer) {
                    input.classList.add('is-invalid');
                    errorContainer.textContent = errors.map(e => e.message).join(', ');
                    errorContainer.style.display = 'block';
                }
            });
        }
        
        // Mostrar error general si no hay errores de campo específicos
        if (!error.errors || Object.keys(error.errors).length === 0) {
            showErrorAlert(error.message || 'Error al guardar cambios');
        }
    }

    // Helper para obtener CSRF Token
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
});

// Observador para nuevos elementos en la tabla
const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
        if (mutation.addedNodes.length) {
            initDynamicFeatures();
        }
    });
});

observer.observe(document.getElementById('empresasTable'), {
    childList: true,
    subtree: true
});



// static/crm/empresas.js - Manejo de eliminación
document.addEventListener('DOMContentLoaded', function() {
    // Configurar evento para los botones de eliminar
    document.querySelectorAll('.delete-empresa').forEach(btn => {
        btn.addEventListener('click', handleDeleteEmpresa);
    });

    // Configurar submit del formulario de eliminación
    document.getElementById('deleteEmpresaForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const form = e.target;
        const empresaId = document.getElementById('deleteEmpresaId').value;
        const deleteUrl = form.action;
        
        executeDelete(empresaId, deleteUrl);
    });
});

const handleDeleteEmpresa = (e) => {
    e.preventDefault();
    const btn = e.currentTarget;
    const empresaId = btn.dataset.empresaId;
    const empresaName = btn.dataset.empresaName;
    const documentosCount = btn.dataset.documentosCount || 0;
    const notasCount = btn.dataset.notasCount || 0;
    const deleteUrl = btn.dataset.deleteUrl;

    // Actualizar formulario
    const form = document.getElementById('deleteEmpresaForm');
    form.action = deleteUrl;
    document.getElementById('deleteEmpresaId').value = empresaId;

    // Actualizar contenido del modal
    document.getElementById('empresaDeleteName').textContent = empresaName;
    document.getElementById('documentosCount').textContent = 
        `${documentosCount} documento${documentosCount != 1 ? 's' : ''} adjunto${documentosCount != 1 ? 's' : ''}`;
    document.getElementById('notasCount').textContent = 
        `${notasCount} nota${notasCount != 1 ? 's' : ''} registrada${notasCount != 1 ? 's' : ''}`;
};

// Añadir función para obtener cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const executeDelete = async (empresaId, deleteUrl) => {
    const errorAlert = document.getElementById('deleteEmpresaError');
    const confirmBtn = document.getElementById('confirmEmpresaDelete');
    const spinner = confirmBtn.querySelector('.spinner-border');
    const submitText = confirmBtn.querySelector('.submit-text');
    const form = document.getElementById('deleteEmpresaForm');
    
    try {
        errorAlert.classList.add('d-none');
        confirmBtn.disabled = true;
        submitText.classList.add('d-none');
        spinner.classList.remove('d-none');

        // Obtener datos del formulario incluyendo CSRF
        const formData = new FormData(form);
        
        const response = await fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',  // Añadir content-type
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            },
            body: new URLSearchParams({
                'csrfmiddlewaretoken': getCookie('csrftoken'),  // Enviar token como parámetro POST
            })
        });

        // Manejar respuesta
        const contentType = response.headers.get('content-type');
        let data;
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            throw new Error('Respuesta no JSON del servidor');
        }

        if (!response.ok || !data.success) {
            throw new Error(data.message || 'Error en la solicitud');
        }

        // Eliminar fila si es exitoso
        const row = document.querySelector(`tr[data-empresa-id="${empresaId}"]`);
        if (row) {
            row.style.transition = 'opacity 0.5s';
            row.style.opacity = '0';
            setTimeout(() => row.remove(), 500);
        }
        
        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteEmpresaModal'));
        modal.hide();
        
        // Mostrar notificación
        if (typeof showSuccessAlert === 'function') {
            showSuccessAlert(data.message, 3000);
        }

    } catch (error) {
        console.error('Error:', error);
        errorAlert.querySelector('#errorEmpresaMessage').textContent = error.message;
        errorAlert.classList.remove('d-none');
    } finally {
        confirmBtn.disabled = false;
        submitText.classList.remove('d-none');
        spinner.classList.add('d-none');
    }
};

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}
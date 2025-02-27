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

    // Manejar eliminación de empresa
    function handleDeleteEmpresa(e) {
        e.preventDefault();
        // Lógica de eliminación aquí...
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
});
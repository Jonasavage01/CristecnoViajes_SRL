// static/crm/empresas.js

document.addEventListener('DOMContentLoaded', function() {
    const showErrorAlert = window.showErrorAlert;
    const showSuccessAlert = window.showSuccessAlert;
    const empresaForm = document.getElementById('empresaForm');
    const empresaModal = new bootstrap.Modal(document.getElementById('empresaModal'));
    
    // Manejar submit del formulario
    empresaForm.addEventListener('submit', function(e) {
        e.preventDefault();
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
                'X-CSRFToken': getCSRFToken(),  // ✅ Añadir esta línea
            },
            credentials: 'same-origin'
        })
        .then(response => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
            
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showSuccessAlert(data.message); // Usar función global ✅
                empresaModal.hide();
                refreshEmpresasTable();
                empresaForm.reset();
            
            } else {
                // Mostrar errores de validación
                handleFormErrors(data.errors, data.form_errors);
            }
        })
        .catch(error => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
            
            // Manejar error de respuesta del servidor
            if (error instanceof TypeError) {
                showErrorAlert('Error de conexión con el servidor');
            } else if (error.errors) {
                handleFormErrors(error.errors, error.form_errors);
            } else {
                showErrorAlert(error.message || 'Error en el servidor');
            }
        });
    });

    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Función para manejar errores del formulario
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
                const errorContainer = input.closest('.position-relative').querySelector('.invalid-feedback');
                
                if (input && errorContainer) {
                    input.classList.add('is-invalid');
                    errorContainer.textContent = errors[0].message;
                    errorContainer.style.display = 'block';
                }
            });
        }

        // Mostrar errores generales
        if (errors && errors.length > 0) {
            window.showErrorAlert(errors.join('<br>'));
        }
    }

    // Actualizar tabla después de éxito
    function refreshEmpresasTable() {
        const empresasTable = document.getElementById('empresasTable');
        if (empresasTable) {
            fetch(window.location.href, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newTable = doc.getElementById('empresasTable');
                if (newTable) {
                    empresasTable.innerHTML = newTable.innerHTML;
                }
            });
        }
    }

    // Limpiar errores al abrir el modal
    empresaModal._element.addEventListener('shown.bs.modal', () => {
        empresaForm.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        empresaForm.querySelectorAll('.invalid-feedback').forEach(el => {
            el.style.display = 'none';
        });
    });
});
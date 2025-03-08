// crm/formValidators.js
document.addEventListener('DOMContentLoaded', function() {
    const clienteForm = document.getElementById('clienteForm');
    const modal = new bootstrap.Modal(document.getElementById('clienteModal'));
    
    // Manejar envío del formulario
    clienteForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(clienteForm);
        const submitBtn = clienteForm.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner-border');
        const submitText = submitBtn.querySelector('.submit-text');
        
        // Mostrar spinner de carga
        submitBtn.disabled = true;
        spinner.classList.remove('d-none');
        submitText.textContent = 'Guardando...';
        
        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Éxito: resetear formulario y mostrar mensaje
                clienteForm.reset();
                showSuccessAlert(data.message || 'Cliente guardado correctamente', {
                    timer: 3000
                });
                modal.hide();
                
                // Recargar la página para actualizar la tabla
                setTimeout(() => window.location.reload(), 1500);
            } else {
                // Manejar errores de validación
                handleFormErrors(data.errors || [], data.form_errors || {});
            }
        } catch (error) {
            console.error('Error:', error);
            showErrorAlert('Error de conexión con el servidor');
        } finally {
            // Restaurar botón
            submitBtn.disabled = false;
            spinner.classList.add('d-none');
            submitText.textContent = 'Guardar Cliente';
        }
    });
    
    function handleFormErrors(generalErrors, fieldErrors) {
        // Limpiar errores previos
        clienteForm.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        clienteForm.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
    
        // Manejar errores por campo
        Object.entries(fieldErrors).forEach(([fieldName, errors]) => {
            if(fieldName === '__all__') return;  // Ignorar errores generales aquí
            
            const input = clienteForm.querySelector(`[name="${fieldName}"]`);
            if (!input) return;
    
            const errorContainer = input.closest('.position-relative')?.querySelector('.invalid-feedback') 
                                || input.closest('.mb-3')?.querySelector('.invalid-feedback');
            
            if (errorContainer) {
                input.classList.add('is-invalid');
                errorContainer.textContent = Array.isArray(errors) ? errors.join(', ') : errors;
            }
        });
    
        // Manejar errores generales
        if (generalErrors.length > 0) {
            showErrorAlert(generalErrors.join('<br>'), {
                title: 'Errores de validación',
                timer: 8000
            });
            
            // Scroll al inicio del modal para ver el error
            clienteModal.querySelector('.modal-body').scrollTo(0, 0);
        } else {
            // Scroll al primer error
            const firstError = clienteForm.querySelector('.is-invalid');
            firstError?.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    }
    
    // Manejar botones N/A (mejorado)
    clienteForm.querySelectorAll('button[data-na-target]').forEach(button => {
        // Modificar el evento click de los botones N/A
button.addEventListener('click', function(e) {
    e.preventDefault();
    const targetId = this.dataset.naTarget;
    const input = document.getElementById(targetId);
    if (input) {
        input.value = 'N/A';
        input.classList.remove('is-invalid');
        input.dispatchEvent(new Event('input'));
        // Limpiar error si existe
        const errorContainer = input.closest('.position-relative')?.querySelector('.invalid-feedback');
        if (errorContainer) {
            errorContainer.textContent = '';
        }
    }
});
    });
    
    // Validación en tiempo real mejorada
    const setupRealTimeValidation = (input, pattern, errorMessage) => {
        input.addEventListener('input', function() {
            const value = this.value.trim().toUpperCase();
            
            if (value === 'N/A') {
                this.value = 'N/A';
                this.setCustomValidity('');
                this.classList.remove('is-invalid');
                return;
            }
            
            if (pattern && !new RegExp(pattern).test(value)) {
                this.setCustomValidity(errorMessage);
                this.classList.add('is-invalid');
            } else {
                this.setCustomValidity('');
                this.classList.remove('is-invalid');
            }
        });
    };
    
    // Configurar validaciones
    const phonePattern = '^(\\+[1-9]\\d{1,14}|N/A)$';
    const emailPattern = '^([^@\\s]+@[^@\\s]+\\.[^@\\s]+|N/A)$';
    
    setupRealTimeValidation(clienteForm.querySelector('[name="telefono"]'), phonePattern, 'Formato de teléfono inválido');
    setupRealTimeValidation(clienteForm.querySelector('[name="movil"]'), phonePattern, 'Formato de móvil inválido');
    setupRealTimeValidation(clienteForm.querySelector('[name="email"]'), emailPattern, 'Formato de email inválido');
    
    // Validación de cédula/pasaporte
    const cedulaInput = clienteForm.querySelector('[name="cedula_pasaporte"]');
    if (cedulaInput) {
        setupRealTimeValidation(
            cedulaInput,
            '^[A-Z0-9-]{6,20}$',
            'Formato inválido (6-20 caracteres, mayúsculas, números y guiones)'
        );
    }
});

clienteForm.querySelectorAll('[required]').forEach(input => {
    input.addEventListener('blur', function() {
        if (!this.value.trim()) {
            this.classList.add('is-invalid');
            const errorContainer = this.closest('.position-relative')?.querySelector('.invalid-feedback');
            if (errorContainer) {
                errorContainer.textContent = 'Este campo es requerido';
            }
        }
    });
});
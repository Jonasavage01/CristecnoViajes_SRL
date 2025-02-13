document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('clienteForm');
    const modal = document.getElementById('clienteModal');
    
    // Configurar validación en tiempo real
    setupRealTimeValidation();
    
    // Manejar el reset del formulario al cerrar
    modal.addEventListener('hidden.bs.modal', () => {
        form.reset();
        clearValidationErrors();
    });
    
    // Manejar el envío del formulario
    form.addEventListener('submit', handleFormSubmit);
});

function setupRealTimeValidation() {
    document.querySelectorAll('.needs-validation input, .needs-validation select, .needs-validation textarea').forEach(field => {
        field.addEventListener('input', () => validateField(field));
        field.addEventListener('change', () => validateField(field));
    });
}

function validateField(field) {
    const errorElement = field.parentElement.querySelector('.invalid-feedback');
    
    if (field.required && !field.value.trim()) {
        showFieldError(field, errorElement, 'Este campo es obligatorio');
        return false;
    }
    
    // Validación específica para cédula/pasaporte
    if (field.id === 'id_cedula_pasaporte') {
        const cedulaRegex = /^[VEJPGvejpg]\d{3,8}$/i;
        if (!cedulaRegex.test(field.value.trim())) {
            showFieldError(field, errorElement, 'Formato inválido. Ejemplo: V-12345678');
            return false;
        }
    }
    
    // Validación de email
    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            showFieldError(field, errorElement, 'Ingrese un email válido');
            return false;
        }
    }
    
    clearFieldError(field, errorElement);
    return true;
}

function showFieldError(field, errorElement, message) {
    field.classList.add('is-invalid');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function clearFieldError(field, errorElement) {
    field.classList.remove('is-invalid');
    errorElement.textContent = '';
    errorElement.style.display = 'none';
}

function clearValidationErrors() {
    document.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    document.querySelectorAll('.invalid-feedback').forEach(error => {
        error.style.display = 'none';
    });
}

async function handleFormSubmit(e) {
    e.preventDefault();
    e.stopPropagation();
    
    let isValid = true;
    let errorMessages = [];
    
    document.querySelectorAll('.needs-validation input, .needs-validation select, .needs-validation textarea').forEach(field => {
        if (!validateField(field)) {
            isValid = false;
            if (!errorMessages.includes(field.labels[0].textContent)) {
                errorMessages.push(field.labels[0].textContent);
            }
        }
    });
    
    if (!isValid) {
        const errorList = errorMessages.map(msg => `<li>${msg}</li>`).join('');
        showErrorAlert(`Errores encontrados en:<ul>${errorList}</ul>`);
        return;
    }
    
    // Enviar formulario vía AJAX
    const formData = new FormData(this);
    try {
        const response = await fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessAlert(result.message);
            $('#clienteModal').modal('hide');
            window.location.reload();
        } else {
            showErrorAlert(result.errors.join('<br>'));
        }
    } catch (error) {
        showErrorAlert('Error de conexión. Intente nuevamente.');
    }
}
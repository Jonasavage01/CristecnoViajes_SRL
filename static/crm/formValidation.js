// Polyfill para FormData.entries() en navegadores antiguos
if (!FormData.prototype.entries) {
    FormData.prototype.entries = function* () {
        for (let pair of this) yield pair;
    };
}

/* ============================
   Funciones para Alertas
============================ */
function showErrorAlert(message) {
    // Elimina alerta previa si existe
    const existingAlert = document.getElementById('formAlert');
    if (existingAlert) {
        existingAlert.remove();
    }
    const alertDiv = document.createElement('div');
    alertDiv.id = 'formAlert';
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = message + '<button type="button" class="close" data-bs-dismiss="alert" aria-label="Cerrar"><span aria-hidden="true">&times;</span></button>';
    // Se inserta la alerta al inicio del body (o donde prefieras)
    document.body.prepend(alertDiv);
}

function showSuccessAlert(message) {
    // Elimina alerta previa si existe
    const existingAlert = document.getElementById('formAlert');
    if (existingAlert) {
        existingAlert.remove();
    }
    const alertDiv = document.createElement('div');
    alertDiv.id = 'formAlert';
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = message + '<button type="button" class="close" data-bs-dismiss="alert" aria-label="Cerrar"><span aria-hidden="true">&times;</span></button>';
    document.body.prepend(alertDiv);
}

/* ============================
   Funciones de Validación
============================ */
function validateField(field) {
    // Log de depuración para el campo a validar
    console.log(`[Debug] Validando campo ${field.name}:`, {
        value: field.value,
        required: field.required,
        valid: field.checkValidity()
    });
    
    const errorElement = field.parentElement.querySelector('.invalid-feedback');
    
    // Validación: Campo obligatorio
    if (field.required && !field.value.trim()) {
        showFieldError(field, errorElement, 'Este campo es obligatorio');
        return false;
    }
    
    // Validación específica para cédula/pasaporte
    if (field.id === 'id_cedula_pasaporte') {
        const cedulaRegex = /^[VEJPGvejpg][-]?\d{3,8}$/i; // Permite guión opcional
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
    
    // Aquí puedes agregar más validaciones específicas si lo requieres
    
    clearFieldError(field, errorElement);
    return true;
}

function showFieldError(field, errorElement, message) {
    field.classList.add('is-invalid');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

function clearFieldError(field, errorElement) {
    field.classList.remove('is-invalid');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }
}

function clearValidationErrors() {
    document.querySelectorAll('.is-invalid').forEach(field => field.classList.remove('is-invalid'));
    document.querySelectorAll('.invalid-feedback').forEach(error => error.style.display = 'none');
}

/* ============================
   Función de Validación en Tiempo Real
============================ */
function setupRealTimeValidation() {
    const fields = document.querySelectorAll('.needs-validation input, .needs-validation select, .needs-validation textarea');
    fields.forEach(field => {
        field.addEventListener('input', () => validateField(field));
        field.addEventListener('change', () => validateField(field));
    });
}

/* ============================
   Manejo del Envío del Formulario
============================ */
async function handleFormSubmit(e) {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('[Debug] Iniciando envío del formulario...');
    
    let isValid = true;
    let errorMessages = [];
    
    // Validar todos los campos del formulario
    const fields = document.querySelectorAll('.needs-validation input, .needs-validation select, .needs-validation textarea');
    console.log('[Debug] Campos a validar:', fields);
    
    fields.forEach(field => {
        console.log(`[Debug] Validando campo: ${field.name}`);
        if (!validateField(field)) {
            isValid = false;
            // Se asume que cada campo tiene una etiqueta asociada
            const label = field.labels && field.labels[0] ? field.labels[0].textContent.replace('*', '').trim() : field.name;
            console.log(`[Debug] Error en campo: ${field.name}`, field.value);
            if (!errorMessages.includes(label)) {
                errorMessages.push(label);
            }
        }
    });
    
    if (!isValid) {
        console.error('[Debug] Errores de validación:', errorMessages);
        const errorList = errorMessages.map(msg => `<li>${msg}</li>`).join('');
        showErrorAlert(`Errores en los campos:<ul class="text-start">${errorList}</ul>`);
        return;
    }
    
    try {
        const formData = new FormData(e.target);
        console.log('[Debug] Datos del formulario:', Object.fromEntries(formData.entries()));
        
        console.log('[Debug] Enviando datos al servidor...');
        const response = await fetch(e.target.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        console.log('[Debug] Respuesta recibida. Status:', response.status);
        console.log('[Debug] Headers:', response.headers);
        
        const responseContentType = response.headers.get('content-type');
        const isJson = responseContentType && responseContentType.includes('application/json');
        
        const result = isJson ? await response.json() : await response.text();
        console.log('[Debug] Respuesta del servidor:', result);
        
        if (!response.ok) {
            console.error('[Debug] Error en la respuesta:', result);
            throw new Error(result?.errors?.join('\n') || `Error HTTP: ${response.status}`);
        }
        
        if (result.success) {
            console.log('[Debug] Éxito del servidor:', result);
            showSuccessAlert(result.message);
            // Cierra el modal usando Bootstrap 5 Vanilla
            const modalElement = document.getElementById('clienteModal');
            if (modalElement) {
                let modalInstance = bootstrap.Modal.getInstance(modalElement);
                if (!modalInstance) {
                    modalInstance = new bootstrap.Modal(modalElement);
                }
                modalInstance.hide();
            }
            setTimeout(() => window.location.reload(), 1500);
        } else {
            console.error('[Debug] Errores del servidor:', result.errors);
            showErrorAlert(result.errors.join('<br>'));
        }
        
    } catch (error) {
        console.error('[Debug] Error en el envío:', error);
        let errorMessage = 'Error de conexión. Verifique su red e intente nuevamente.';
        
        if (error.message.includes('HTTP')) {
            errorMessage = `Error del servidor: ${error.message}`;
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        showErrorAlert(`
            <div class="text-start">
                ${errorMessage}<br>
                <small class="text-muted">Si el problema persiste, contacte al soporte técnico</small>
            </div>
        `);
    }
}

/* ============================
   Inicialización al Cargar el DOM
============================ */
document.addEventListener('DOMContentLoaded', () => {
    // Se asume que el formulario tiene el id "clienteForm" o la clase "needs-validation"
    const form = document.getElementById('clienteForm') || document.querySelector('form.needs-validation');
    const modal = document.getElementById('clienteModal');
    
    setupRealTimeValidation();
    
    if (modal) {
        modal.addEventListener('hidden.bs.modal', () => {
            if (form) {
                form.reset();
                clearValidationErrors();
            }
        });
    }
    
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});
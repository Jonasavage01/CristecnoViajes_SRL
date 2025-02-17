/* ============================
   Polyfills y Utilidades
============================ */
if (!FormData.prototype.entries) {
    FormData.prototype.entries = function* () {
        for (let pair of this) yield pair;
    };
}

function getCSRFToken() {
    const metaToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    const cookieToken = document.cookie.match(/csrftoken=([^ ;]+)/)?.[1];
    
    if (!metaToken && !cookieToken) {
        console.error('CSRF token no encontrado');
        showAlert('error', 'Error de seguridad. Recargue la página.');
        return null;
    }
    return metaToken || cookieToken;
}

/* ============================
   Funciones para Alertas
============================ */
const swalConfig = {
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    customClass: {
        container: 'custom-swal-container'
    }
};

function showAlert(type, message) {
    Swal.fire({
        ...swalConfig,
        icon: type,
        title: message
    });
}

/* ============================
   Formateo de Teléfonos
============================ */
const formatPhoneNumber = (value) => {
    let formatted = value.replace(/[^0-9+]/g, '');
    
    // Eliminar múltiples símbolos +
    if ((formatted.match(/\+/g) || []).length > 1) {
        formatted = '+' + formatted.replace(/\+/g, '');
    }
    
    // Limitar longitud y asegurar + inicial opcional
    return formatted.slice(0, 15);
};

/* ============================
   Sistema de Validación
============================ */
const FieldValidators = {
    cedula_pasaporte: value => {
        if (!value) return false;
        const cleanedValue = value.trim().toUpperCase().replace(/-/g, '');
        return /^[A-Z0-9]{6,20}$/.test(cleanedValue);
    },
    telefono: value => {
        value = value.trim().toUpperCase();
        if (value === 'N/A') return true;
        return /^(\+?[1-9]\d{1,14})$/.test(value);
    },
    movil: value => {
        value = value.trim().toUpperCase();
        if (value === 'N/A') return true;
        return /^(\+?[1-9]\d{1,14})$/.test(value);
    },
    email: value => {
        if (value.toUpperCase() === 'N/A') return true;
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }
};

const validateField = (field) => {
    const errorElement = field.closest('.position-relative')?.querySelector('.invalid-feedback');
    field.classList.remove('is-invalid');
    if (errorElement) errorElement.style.display = 'none';

    const value = field.value.trim();
    let isValid = true;
    
    if (field.required && !value) {
        showFieldError(field, errorElement, 'Este campo es obligatorio');
        isValid = false;
    }
    else if (FieldValidators[field.name] && !FieldValidators[field.name](value)) {
        const messages = {
            cedula_pasaporte: 'Formato inválido. Ej: 40212345678 o PA1234567',
            email: 'Correo electrónico inválido',
            telefono: 'Formato inválido. Ej: 18091234567 ó +18091234567',
            movil: 'Formato inválido. Ej: 18091234567 ó +18091234567'
        };
        showFieldError(field, errorElement, messages[field.name]);
        isValid = false;
    }
    
    return isValid;
};

const showFieldError = (field, errorElement, message) => {
    field.classList.add('is-invalid');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
};

/* ============================
   Manejo de Formularios
============================ */
const handleFormSubmit = async (e) => {
    e.preventDefault();
    const form = e.target;
    
    // Validar todos los campos
    let isValid = true;
    form.querySelectorAll('input, select, textarea').forEach(field => {
        if (!validateField(field)) isValid = false;
    });
    
    if (!isValid) return showAlert('error', 'Por favor corrija los errores');

    try {
        const formData = new FormData(form);
        const isEditForm = form.id === 'clienteEditForm';
        
        // Configurar método HTTP para Django
        if (isEditForm) formData.append('_method', 'PUT');

        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        });

        const result = await response.json();
        
        if (response.ok && result.success) {
            showAlert('success', result.message);
            const modal = bootstrap.Modal.getInstance(form.closest('.modal'));
            
            if (modal) {
                modal.hide();
                
                // Actualización dinámica de la tabla
                if (isEditForm && result.cliente_data) {
                    const row = document.querySelector(`tr[data-client-id="${result.cliente_data.id}"]`);
                    if (row) {
                        // Actualizar cada campo específico
                        row.querySelector('.client-name').textContent = result.cliente_data.nombre;
                        row.querySelector('.client-status').textContent = result.cliente_data.estado;
                        row.querySelector('.client-status').className = `badge bg-${result.cliente_data.estado_color}`;
                        row.querySelector('.client-phone').textContent = result.cliente_data.telefono;
                        row.querySelector('.client-email').textContent = result.cliente_data.email;
                        row.querySelector('.client-cedula').textContent = result.cliente_data.cedula;
                        
                        // Actualizar tooltips si es necesario
                        const tooltip = bootstrap.Tooltip.getInstance(row);
                        if (tooltip) tooltip.dispose();
                    }
                } else {
                    // Recargar solo para nuevos registros
                    window.location.reload();
                }
            }
        } else {
            handleFormErrors(form, result);
        }
    } catch (error) {
        showAlert('error', 'Error de conexión. Intente nuevamente.');
        console.error('Error:', error);
    }
};

const handleFormErrors = (form, result) => {
    // Limpiar errores previos
    form.querySelectorAll('.is-invalid').forEach(field => field.classList.remove('is-invalid'));
    form.querySelectorAll('.invalid-feedback').forEach(el => el.style.display = 'none');

    // Mostrar nuevos errores
    if (result.form_errors) {
        Object.entries(result.form_errors).forEach(([field, errors]) => {
            const input = form.querySelector(`[name="${field}"]`);
            const errorElement = input?.closest('.position-relative')?.querySelector('.invalid-feedback');
            if (input && errorElement) {
                input.classList.add('is-invalid');
                errorElement.textContent = errors.map(e => e.message).join(', ');
                errorElement.style.display = 'block';
            }
        });
    }
    
    // Mostrar errores generales
    if (result.errors) {
        showAlert('error', result.errors.join('<br>'));
    } else if (result.message) {
        showAlert('error', result.message);
    } else {
        showAlert('error', 'Error desconocido');
    }
};
/* ============================
   Inicialización de Módulos
============================ */
const initPhoneInputs = (container = document) => {
    container.querySelectorAll('input[name="telefono"], input[name="movil"]').forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = formatPhoneNumber(e.target.value);
        });
    });
};

const initModalValidation = (modalElement) => {
    // Validación en tiempo real
    modalElement.querySelectorAll('input, select, textarea').forEach(field => {
        field.addEventListener('input', () => validateField(field));
    });

    // Limpieza al cerrar
    modalElement.addEventListener('hidden.bs.modal', () => {
        modalElement.querySelectorAll('.is-invalid').forEach(f => {
            f.classList.remove('is-invalid');
        });
    });
};

const initFormEvents = () => {
    document.addEventListener('submit', (e) => {
        if (e.target.matches('#clienteForm, #clienteEditForm')) {
            handleFormSubmit(e);
        }
    });
};

/* ============================
   Inicialización General
============================ */
const initFormValidation = () => {
    // Inicializar componentes principales
    initPhoneInputs();
    initFormEvents();

    // Manejar modales dinámicos
    document.addEventListener('ajaxFormLoaded', (e) => {
        const form = e.detail.form;
        initPhoneInputs(form);
        initModalValidation(form.closest('.modal'));
    });

    // Tooltips
    new bootstrap.Tooltip(document.body, {
        selector: '[data-bs-toggle="tooltip"]'
    });
};

document.addEventListener('DOMContentLoaded', initFormValidation);
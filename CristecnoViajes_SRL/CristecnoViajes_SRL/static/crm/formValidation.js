/* ============================
   Polyfills y Utilidades
============================ */
if (!FormData.prototype.entries) {
    FormData.prototype.entries = function* () {
        for (let pair of this) yield pair;
    };
}

function getCSRFToken() { // <- Modificar esta línea
    const metaToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    const cookieToken = document.cookie.match(/csrftoken=([^ ;]+)/)?.[1];
    
    if (!metaToken && !cookieToken) {
        console.error('CSRF token no encontrado');
        showAlert('error', 'Error de seguridad. Recargue la página.');
        return null;
    }
    return metaToken || cookieToken;
};

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

const formatPhoneNumber = (value) => {
    value = value.toUpperCase().replace(/\s/g, '');
    
    if (value === 'NA' || value === 'N/A') {
        return 'N/A';
    }
    
    if (value.startsWith('+')) {
        return `+${value.slice(1, 15)}`;
    }
    
    return value.length > 3 ? `+${value.slice(0, 15)}` : value;
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
        return /^\+[1-9]\d{1,14}$/.test(value);
    },
    movil: value => {
        value = value.trim().toUpperCase();
        if (value === 'N/A') return true;
        return /^\+[1-9]\d{1,14}$/.test(value);
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
            telefono: 'Formato inválido. Ej: +58 412 5555555',
            movil: 'Formato inválido. Ej: +58 412 5555555'
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
    const isEditForm = form.id === 'clienteEditForm';
    
    let isValid = true;
    form.querySelectorAll('input, select, textarea').forEach(field => {
        if (!validateField(field)) isValid = false;
    });
    
    if (!isValid) return showAlert('error', 'Por favor corrija los errores');

    try {
        const formData = new FormData(form);
        if (isEditForm) formData.set('_method', 'PUT');

        // Asegurar campos requeridos
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!formData.get(field.name)) {
                formData.set(field.name, 'N/A');
            }
        });

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
            bootstrap.Modal.getInstance(form.closest('.modal'))?.hide();
            setTimeout(() => window.location.reload(), 1500);
        } else {
            handleFormErrors(form, result);
        }
    } catch (error) {
        showAlert('error', 'Error de conexión. Intente nuevamente.');
        console.error('Error:', error);
    }
};

const handleFormErrors = (form, result) => {
    if (result.form_errors) {
        Object.entries(result.form_errors).forEach(([field, errors]) => {
            const input = form.querySelector(`[name="${field}"]`);
            const errorElement = input?.closest('.position-relative')?.querySelector('.invalid-feedback');
            if (input && errorElement) showFieldError(input, errorElement, errors[0]);
        });
    }
    showAlert('error', result.errors?.join('<br>') || 'Error desconocido');
};

/* ============================
   Inicialización General
============================ */
const initFormValidation = () => {
    // Event listeners para inputs de teléfono
    document.querySelectorAll('input[name="telefono"], input[name="movil"]').forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = formatPhoneNumber(e.target.value);
        });
    });

    // Manejo de formularios
    document.querySelectorAll('#clienteForm, #clienteEditForm').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });

    // Validación en tiempo real
    const debounce = (func, delay = 300) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    };

    document.addEventListener('ajaxFormLoaded', (e) => {
        e.detail.form.querySelectorAll('input, select, textarea').forEach(field => {
            if (field.readOnly || field.disabled) return;
            
            field.addEventListener('input', debounce(() => validateField(field)));
            field.addEventListener('blur', () => validateField(field));
        });
    });

    // Tooltips
    new bootstrap.Tooltip(document.body, {
        selector: '[data-bs-toggle="tooltip"]'
    });

    // Limpieza de modales
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', () => {
            modal.querySelectorAll('.is-invalid').forEach(f => f.classList.remove('is-invalid'));
            modal.querySelectorAll('.invalid-feedback').forEach(e => e.style.display = 'none');
        });
    });
};

document.addEventListener('DOMContentLoaded', initFormValidation);
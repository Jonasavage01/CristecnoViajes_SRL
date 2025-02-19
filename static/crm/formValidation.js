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
    
    if ((formatted.match(/\+/g) || []).length > 1) {
        formatted = '+' + formatted.replace(/\+/g, '');
    }
    
    return formatted.slice(0, 15);
};

/* ============================
   Sistema de Validación
============================ */
const FieldValidators = {
    nombre: value => {
        const trimmed = value.trim();
        return trimmed.length >= 2 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(trimmed);
    },
    
    apellido: value => {
        const trimmed = value.trim();
        return trimmed.length >= 2 && /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(trimmed);
    },

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
        const emailValue = value.trim().toUpperCase();
        if (emailValue === 'N/A') return true;
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailValue);
    },
    
    fecha_nacimiento: value => {
        if (!value) return true;
        const fecha = new Date(value);
        return !isNaN(fecha) && fecha <= new Date();
    },
    
    estado: value => {
        const estadosValidos = ['activo', 'inactivo', 'potencial'];
        return estadosValidos.includes(value.toLowerCase());
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
            movil: 'Formato inválido. Ej: 18091234567 ó +18091234567',
            nombre: 'Nombre inválido (mínimo 2 letras)',
            apellido: 'Apellido inválido (mínimo 2 letras)',
            estado: 'Estado inválido'
        };
        showFieldError(field, errorElement, messages[field.name] || 'Valor inválido');
        isValid = false;
    }
    
    return isValid;
};

/* ============================
   Actualización Dinámica de Tabla
============================ */
const updateClientRow = (row, clientData) => {
    const updateField = (selector, value) => {
        const element = row.querySelector(selector);
        if (element) element.textContent = value;
    };

    updateField('.client-name', `${clientData.nombre} ${clientData.apellido}`);
    
    const avatar = row.querySelector('.avatar');
    if (avatar && clientData.nombre) {
        avatar.textContent = clientData.nombre.charAt(0).toUpperCase();
    }

    const statusBadge = row.querySelector('.client-status');
    if (statusBadge) {
        statusBadge.textContent = clientData.estado_display;
        statusBadge.className = `badge bg-${clientData.estado_color} rounded-pill`;
    }

    updateField('.client-phone', clientData.telefono);
    updateField('.client-email', clientData.email);
    updateField('.client-cedula', clientData.cedula);
};

/* ============================
   Manejo de Fecha de Nacimiento
============================ */
const initDateInputs = () => {
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.addEventListener('change', function() {
            if (this.value) {
                const selectedDate = new Date(this.value);
                const today = new Date();
                selectedDate > today 
                    ? showFieldError(this, null, 'La fecha no puede ser futura')
                    : this.classList.remove('is-invalid');
            }
        });
    });
};

/* ============================
   Manejo de N/A
============================ */
const handleNASelection = (fieldId) => {
    const field = document.getElementById(fieldId);
    if (field) {
        field.value = 'N/A';
        validateField(field);
        field.dispatchEvent(new Event('input'));
    }
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
    
    let isValid = true;
    form.querySelectorAll('input, select, textarea').forEach(field => {
        if (!validateField(field)) isValid = false;
    });
    
    if (!isValid) return showAlert('error', 'Por favor corrija los errores');

    try {
        const formData = new FormData(form);
        const isEditForm = form.id === 'clienteEditForm';
        
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
            
            // Obtener instancia del modal correctamente
            const modalElement = form.closest('.modal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            
            if (modal) {
                modal.hide();
                
                if (isEditForm && result.cliente_data) {
                    const row = document.querySelector(`tr[data-client-id="${result.cliente_data.id}"]`);
                    if (row) updateClientRow(row, result.cliente_data);
                } else {
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
    form.querySelectorAll('.is-invalid').forEach(field => field.classList.remove('is-invalid'));
    form.querySelectorAll('.invalid-feedback').forEach(el => el.style.display = 'none');

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
    modalElement.querySelectorAll('input, select, textarea').forEach(field => {
        field.addEventListener('input', () => validateField(field));
    });

    modalElement.addEventListener('hidden.bs.modal', () => {
        modalElement.querySelectorAll('.is-invalid').forEach(f => f.classList.remove('is-invalid'));
    });

    initDateInputs();

    modalElement.querySelectorAll('[data-na-action]').forEach(button => {
        button.addEventListener('click', () => {
            const targetField = button.getAttribute('data-na-target');
            handleNASelection(targetField);
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
    initPhoneInputs();
    initFormEvents();
    initDateInputs();

    document.addEventListener('ajaxFormLoaded', (e) => {
        const form = e.detail.form;
        initPhoneInputs(form);
        initModalValidation(form.closest('.modal'));
    });

    new bootstrap.Tooltip(document.body, {
        selector: '[data-bs-toggle="tooltip"]'
    });
};

document.addEventListener('DOMContentLoaded', initFormValidation);
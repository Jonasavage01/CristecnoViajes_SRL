// formValidation.js - Versión final corregida

/* ============================
   Polyfills y Utilidades
============================ */
if (!FormData.prototype.entries) {
    FormData.prototype.entries = function* () {
        for (let pair of this) yield pair;
    };
}

const getCSRFToken = () => {
    const metaToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    const cookieToken = document.cookie.match(/csrftoken=([^ ;]+)/)?.[1];
    
    if (!metaToken && !cookieToken) {
        console.error('CSRF token no encontrado');
        showAlert('error', 'Error de seguridad. Recargue la página.');
    }
    return metaToken || cookieToken;
};
/* ============================
   Funciones para Alertas (Actualizado para SweetAlert2)
============================ */
function showAlert(type, message) {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    });
    
    Toast.fire({
        icon: type,
        title: message
    });
}

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
   Sistema de Validación Mejorado
============================ */
const FieldValidators = {
    
    
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
            cedula_pasaporte: 'Formato inválido. Ej: V-12345678',
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

// Event listeners para formato en tiempo real
document.querySelectorAll('input[name="telefono"], input[name="movil"]').forEach(input => {
    input.addEventListener('input', (e) => {
        e.target.value = formatPhoneNumber(e.target.value);
    });
});
/* ============================
   Manejo de Formularios
============================ */
const handleFormSubmit = async (e) => {
    e.preventDefault();
    const form = e.target;
    const isEditForm = form.id === 'clienteEditForm';
    
    // Validar todos los campos
    let isValid = true;
    form.querySelectorAll('input, select, textarea').forEach(field => {
        if (!validateField(field)) isValid = false;
    });
    
    if (!isValid) return showAlert('danger', 'Por favor corrija los errores');

    try {
        const formData = new FormData(form);
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
            bootstrap.Modal.getInstance(form.closest('.modal'))?.hide();
            setTimeout(() => window.location.reload(), 1500);
        } else {
            handleFormErrors(form, result);
        }
    } catch (error) {
        showAlert('danger', 'Error de conexión. Intente nuevamente.');
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
    showAlert('danger', result.errors?.join('<br>') || 'Error desconocido');
};

/* ============================
   Manejo de Eliminación
============================ */
const initDeleteHandlers = () => {
    let deleteTarget = null;
    const deleteModal = new bootstrap.Modal('#deleteConfirmationModal');

    document.querySelectorAll('.delete-client').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            deleteTarget = {
                url: e.currentTarget.dataset.href,
                row: e.target.closest('tr')
            };
            deleteModal.show();
        });
    });

    document.getElementById('confirmDeleteButton')?.addEventListener('click', async () => {
        if (!deleteTarget) return;

        try {
            const response = await fetch(deleteTarget.url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                deleteTarget.row?.remove();
                showAlert('success', 'Cliente eliminado exitosamente');
            } else {
                throw new Error('Error en la eliminación');
            }
        } catch (error) {
            showAlert('danger', 'No se pudo eliminar el cliente');
            console.error('Error:', error);
        } finally {
            deleteModal.hide();
            deleteTarget = null;
        }
    });
};

/* ============================
   Validación en Tiempo Real
============================ */
const setupRealTimeValidation = () => {
    const debounce = (func, delay = 300) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    };



    // Para formularios dinámicos
    document.addEventListener('ajaxFormLoaded', (e) => {
        e.detail.form.querySelectorAll('input, select, textarea').forEach(field => {
            if (field.readOnly || field.disabled) return;
            
            field.addEventListener('input', () => validateField(field));
            field.addEventListener('blur', () => validateField(field));
        });
    });
};

/* ============================
   Inicialización General
============================ */
document.addEventListener('DOMContentLoaded', () => {
    // Formularios
    document.querySelectorAll('#clienteForm, #clienteEditForm').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });

    // Validación en tiempo real
    setupRealTimeValidation();

    // Eliminación
    initDeleteHandlers();

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
});


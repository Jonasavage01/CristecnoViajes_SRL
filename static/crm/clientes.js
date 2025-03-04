document.addEventListener('DOMContentLoaded', () => {
    // ========== [CONSTANTES Y FUNCIONES UTILITARIAS] ==========
    const ALERT_TIMEOUT = 3000;
    const DEBOUNCE_DELAY = 300;
    
    const getCSRFToken = () => {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    };

    const showAlert = (type, message, timer = ALERT_TIMEOUT) => {
        const icon = type === 'success' ? 'check-circle' : 'exclamation-triangle';
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer,
            timerProgressBar: true
        });
        
        Toast.fire({
            icon: type,
            title: message,
            iconHtml: `<i class="bi bi-${icon}"></i>`
        });
    };

    // ========== [FUNCIONALIDAD DE EDICIÓN MEJORADA] ==========
    const updateClientRow = (clientId, data) => {
        const row = document.querySelector(`tr[data-client-id="${clientId}"]`);
        if (!row) return;
    
        // Actualizar campos principales
        const fieldsToUpdate = {
            '.client-name': `${data.nombre} ${data.apellido}`,
            '.client-email a': data.email,
            '.client-phone': data.telefono,
            '.client-cedula code': data.cedula_pasaporte,
            '.client-created': new Date(data.fecha_creacion).toLocaleString()
        };
    
        Object.entries(fieldsToUpdate).forEach(([selector, value]) => {
            const element = row.querySelector(selector);
            if (element) element.textContent = value || 'N/A';
        });
    
        // Actualizar avatar y estado
        const avatar = row.querySelector('.avatar');
        if (avatar) {
            avatar.textContent = data.nombre.charAt(0).toUpperCase();
            avatar.className = `avatar bg-${data.estado_color.replace('bg-', '')}`;
        }
    
        const statusBadge = row.querySelector('.badge');
        if (statusBadge) {
            statusBadge.className = `badge bg-${data.estado_color} rounded-pill`;
            statusBadge.innerHTML = `<i class="bi bi-circle-fill me-2"></i>${data.estado_display}`;
        }
    };
    
    const loadEditForm = async (url) => {
        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                }
            });

            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            const html = await response.text();
            const modalElement = document.getElementById('clienteEditModal');
            const container = modalElement.querySelector('#formContainer');
            
            container.innerHTML = html;
            initEditFormValidation(modalElement);
            
            new bootstrap.Modal(modalElement).show();
            return true;

        } catch (error) {
            showAlert('error', `Error cargando formulario: ${error.message}`);
            return false;
        }
    };

    const handleEditSubmit = async (form, clientId) => {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        try {
            submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Guardando...';
            submitBtn.disabled = true;

            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Error en la actualización');
            }

            // Actualizar UI sin recargar
            updateClientRow(clientId, data.cliente);
            showAlert('success', 'Cliente actualizado correctamente');
            bootstrap.Modal.getInstance('#clienteEditModal').hide();
            return true;

        } catch (error) {
            showAlert('error', error.message);
            return false;
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    };

    const initEditFormValidation = (modalElement) => {
        const form = modalElement.querySelector('form');
        if (!form) return;

        // Validación en tiempo real
        const validateField = (field) => {
            field.classList.remove('is-invalid');
            if (field.checkValidity()) return;
            
            field.classList.add('is-invalid');
            const errorContainer = field.nextElementSibling;
            if (errorContainer) {
                errorContainer.textContent = field.validationMessage;
            }
        };

        form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('input', () => validateField(field));
        });

        // Manejar envío del formulario
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const clientId = form.dataset.clientId;
            
            if (!form.checkValidity()) {
                form.classList.add('was-validated');
                return;
            }

            await handleEditSubmit(form, clientId);
        });
    };

    // ========== [FUNCIONALIDAD DE ELIMINACIÓN MEJORADA] ==========
    const handleDelete = async (url, rowElement) => {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Error en la respuesta del servidor');

            if (rowElement) {
                rowElement.remove();
                showAlert('success', 'Cliente eliminado exitosamente');
            }
            return true;

        } catch (error) {
            showAlert('error', 'No se pudo eliminar el cliente');
            console.error('Error:', error);
            return false;
        }
    };

    // ========== [MANEJO DE EVENTOS CON DELEGACIÓN] ==========
    document.addEventListener('click', (e) => {
        // Edición
        if (e.target.closest('.edit-client')) {
            e.preventDefault();
            const button = e.target.closest('.edit-client');
            loadEditForm(button.dataset.url);
        }

        // Eliminación
        if (e.target.closest('.delete-client')) {
            e.preventDefault();
            const button = e.target.closest('.delete-client');
            const row = button.closest('tr');
            const modal = new bootstrap.Modal('#deleteConfirmationModal');

            modal.show();
            document.getElementById('confirmDeleteButton').onclick = async () => {
                await handleDelete(button.dataset.href, row);
                modal.hide();
            };
        }
    });

    // ========== [INICIALIZACIÓN DE COMPONENTES] ==========
    // Tooltips
    new bootstrap.Tooltip(document.body, {
        selector: '[data-bs-toggle="tooltip"]',
        boundary: 'window'
    });

    // Limpieza de modal al cerrar
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('hidden.bs.modal', () => {
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
            
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '';
        });
    });

    // Cargar datos iniciales para elementos existentes
    document.querySelectorAll('[data-client-id]').forEach(row => {
        row.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
    });
});


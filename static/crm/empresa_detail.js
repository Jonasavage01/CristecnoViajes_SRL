document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes de Bootstrap
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    
    // Modales
    const notificationModalEl = document.getElementById('notificationModal');
    const notificationModal = new bootstrap.Modal(notificationModalEl);
    const confirmationModal = new bootstrap.Modal('#confirmationModal');
    let currentDeleteForm = null;

    // Función de notificación mejorada
    function showNotification(type, message) {
        const types = {
            success: {icon: 'bi-check-circle-fill', color: 'text-success'},
            error: {icon: 'bi-x-circle-fill', color: 'text-danger'},
            info: {icon: 'bi-info-circle-fill', color: 'text-info'}
        };
        
        const iconElement = notificationModalEl.querySelector('.notification-icon');
        const messageElement = notificationModalEl.querySelector('.notification-message');
        
        // Reset classes
        iconElement.className = `bi ${types[type].icon} ${types[type].color}`;
        messageElement.textContent = message;
        
        notificationModal.show();
    }

    // Manejo de eliminación con confirmación
    document.querySelectorAll('.delete-document, .delete-note').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            currentDeleteForm = this.closest('form');
            confirmationModal.show();
        });
    });

    // Confirmación de eliminación
    document.getElementById('confirmDelete').addEventListener('click', async () => {
        confirmationModal.hide();
        
        if (!currentDeleteForm) return;
        
        const item = currentDeleteForm.closest('[data-item-id]');
        const submitBtn = currentDeleteForm.querySelector('button[type="submit"]');
        
        try {
            submitBtn.disabled = true;
            const response = await fetch(currentDeleteForm.action, {
                method: 'POST',
                body: new FormData(currentDeleteForm),
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });

            if (response.ok) {
                item.remove();
                showNotification('success', 'Elemento eliminado correctamente');
                checkEmptyState();
            } else {
                const error = await response.json();
                showNotification('error', error.error || 'Error al eliminar');
            }
        } catch (error) {
            showNotification('error', 'Error de conexión');
        } finally {
            submitBtn.disabled = false;
            currentDeleteForm = null;
        }
    });

    // Validación de archivo
    function validateFileInput() {
        const fileInput = document.getElementById('fileInput');
        if (!fileInput.files.length) {
            showNotification('error', 'Por favor selecciona un archivo');
            fileInput.focus();
            return false;
        }
        return true;
    }

    // Manejo de subida de documentos
    const docForm = document.getElementById('documentUploadForm');
    if (docForm) {
        docForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            if (!validateFileInput()) return;
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Subiendo...';

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {'X-Requested-With': 'XMLHttpRequest'}
                });

                const data = await response.json();
                
                if (data.success) {
                    showNotification('success', 'Documento subido exitosamente');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    const errorMsg = data.errors ? Object.values(data.errors).join(' ') : 'Error al subir el documento';
                    showNotification('error', errorMsg);
                }
            } catch (error) {
                showNotification('error', 'Error de conexión');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-cloud-upload me-2"></i>Subir Archivo';
            }
        });
    }

    // Manejo de formulario de notas
    const noteForm = document.getElementById('newNoteForm');
    if (noteForm) {
        noteForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            
            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {'X-Requested-With': 'XMLHttpRequest'}
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification('success', 'Nota agregada correctamente');
                    this.reset();
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    const errorMsg = data.errors ? Object.values(data.errors).join(' ') : 'Error al guardar la nota';
                    showNotification('error', errorMsg);
                }
            } catch (error) {
                showNotification('error', 'Error de conexión');
            } finally {
                submitBtn.disabled = false;
            }
        });
    }

    // Verificación de estado vacío
    function checkEmptyState() {
        const docsContainer = document.getElementById('documentsContainer');
        const notesContainer = document.getElementById('notesContainer');
        
        const createEmptyState = (icon, title, message) => `
            <div class="empty-state text-center p-5 bg-light rounded-3 w-100">
                <i class="bi ${icon} display-4 text-muted opacity-50 mb-3"></i>
                <h5 class="text-muted fw-semibold mb-2">${title}</h5>
                <p class="text-muted mb-0 small">${message}</p>
            </div>`;

        if (docsContainer && !docsContainer.querySelector('.empty-state') && docsContainer.children.length === 0) {
            docsContainer.innerHTML = createEmptyState(
                'bi-folder-x',
                'No se encontraron documentos',
                'Utiliza el formulario superior para subir tu primer documento'
            );
        }
        
        if (notesContainer && !notesContainer.querySelector('.empty-state') && notesContainer.children.length === 0) {
            notesContainer.innerHTML = createEmptyState(
                'bi-journal-x',
                'No hay notas registradas',
                'Escribe la primera nota usando el formulario superior'
            );
        }
    }

    // Verificar estado vacío inicial
    checkEmptyState();
});
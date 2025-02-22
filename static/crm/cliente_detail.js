// cliente_detail.js
document.addEventListener('DOMContentLoaded', function() {
    // ========== [CONFIGURACIÓN INICIAL] ==========
    const clienteId = window.CLIENTE_ID;
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const DOCUMENTS_CONTAINER = document.getElementById('documentsContainer');
    const UPLOAD_FORM = document.getElementById('documentUploadForm');
    const NOTES_CONTAINER = document.getElementById('notesContainer');
    const NEW_NOTE_FORM = document.getElementById('newNoteForm');
    
    // Lightbox con verificación de carga
    let lightbox = null;
    if (typeof GLightbox !== 'undefined') {
        lightbox = GLightbox({ selector: '.glightbox' });
    }

    // ========== [FUNCIONES COMUNES] ==========
    const refreshTooltips = () => {
        tooltipTriggerList.forEach(tooltip => bootstrap.Tooltip.getInstance(tooltip)?.dispose());
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    };

    const handleFormSubmission = async (form, config) => {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalContent = submitBtn.innerHTML;
        const progressBar = form.querySelector('.progress-bar');
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = config.loadingState;

        try {
            const response = await fetch(form.action, {
                method: form.method,
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            // Manejo de errores HTTP
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Error en la operación');
            }

            await config.onSuccess(data);
            if (config.resetForm) form.reset();
            
            // Mostrar feedback al usuario
            Swal.fire({
                icon: 'success',
                title: 'Éxito',
                text: config.successMessage,
                timer: 2000,
                showConfirmButton: false
            });

        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message || 'Error de conexión',
                timer: 3000
            });
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalContent;
            if (progressBar) {
                progressBar.style.width = '0%';
            }
        }
    };

    // ========== [MANEJO DE DOCUMENTOS] ==========
    const getFileIcon = (extension) => {
        const iconMap = {
            'PDF': 'bi-file-earmark-pdf text-danger',
            'DOC': 'bi-file-earmark-word text-primary',
            'DOCX': 'bi-file-earmark-word text-primary',
            'JPG': 'bi-file-image text-success',
            'JPEG': 'bi-file-image text-success',
            'PNG': 'bi-file-image text-success'
        };
        return iconMap[extension.toUpperCase()] || 'bi-file-earmark text-secondary';
    };

    const getPreviewContent = (doc) => {
        const imageTypes = ['JPG', 'JPEG', 'PNG'];
        const pdfTypes = ['PDF'];
        
        if (imageTypes.includes(doc.type)) {
            return `<a href="${doc.url}" class="glightbox"><img src="${doc.url}" class="img-fluid preview-image"></a>`;
        }
        
        if (pdfTypes.includes(doc.type)) {
            return `<div class="pdf-preview-container"><iframe src="${doc.url}#view=fitH" class="pdf-preview"></iframe></div>`;
        }
        
        return `<div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted py-3">
                  <i class="bi ${getFileIcon(doc.type)} fs-1"></i>
                  <small class="mt-2">${doc.type}</small>
                </div>`;
    };

    const createDocumentElement = (doc) => {
        const previewContent = getPreviewContent(doc);
        return `<div class="col-md-4 mb-3 document-item" data-id="${doc.id}">
                  <div class="document-card border rounded p-3">
                    <div class="doc-thumbnail position-relative">
                      ${previewContent}
                      <span class="badge bg-dark position-absolute top-0 start-0 m-2">${doc.tipo_display}</span>
                      <div class="doc-actions position-absolute top-0 end-0 m-2">
                        <a href="${doc.url}" class="btn btn-sm btn-light shadow-sm" download="${doc.name}" 
                           data-bs-toggle="tooltip" title="Descargar">
                          <i class="bi bi-download"></i>
                        </a>
                        <button class="btn btn-sm btn-light shadow-sm delete-document" 
                                data-id="${doc.id}" data-bs-toggle="tooltip" title="Eliminar">
                          <i class="bi bi-trash text-danger"></i>
                        </button>
                      </div>
                    </div>
                    <div class="doc-meta mt-2">
                      <div class="d-flex justify-content-between align-items-center">
                        <div class="text-truncate">
                          <small class="text-muted">${doc.upload_date}</small>
                          <h6 class="mb-0 text-truncate">${doc.name}</h6>
                        </div>
                        <i class="${getFileIcon(doc.type)}"></i>
                      </div>
                    </div>
                  </div>
                </div>`;
    };

    // ========== [MANEJO DE NOTAS] ==========
    const escapeHTML = (str) => str.replace(/[<>]/g, c => ({'<':'&lt;', '>':'&gt;'}[c]));

    const createNoteElement = (note) => {
        return `<div class="note-item border-bottom pb-3 mb-3" data-id="${note.id}">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted">${note.fecha_creacion}</small>
                    <button class="btn btn-sm btn-danger delete-note" data-id="${note.id}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
               <p class="mb-0">${escapeHTML(note.contenido)}</p>
            </div>`;
    };

    // ========== [MANEJO DE EVENTOS] ==========
    const setupDeleteHandlers = (selector, endpointBase, successMessage) => {
        document.addEventListener('click', async (e) => {
            const deleteBtn = e.target.closest(selector);
            if (!deleteBtn) return;

            const result = await Swal.fire({
                title: '¿Estás seguro?',
                text: "Esta acción no se puede deshacer",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33'
            });

            if (result.isConfirmed) {
                try {
                    const response = await fetch(`${endpointBase}${deleteBtn.dataset.id}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    });
                    
                    if (response.ok) {
                        deleteBtn.closest('.document-item, .note-item').remove();
                        
                        // Actualizar estado si no hay elementos
                        if (selector === '.delete-document' && DOCUMENTS_CONTAINER.children.length === 0) {
                            DOCUMENTS_CONTAINER.innerHTML = `
                                <div class="col-12 text-center py-4">
                                    <i class="bi bi-folder-x fs-1 text-muted"></i>
                                    <p class="text-muted mt-2">No hay documentos adjuntos</p>
                                </div>`;
                        }
                        
                        Swal.fire('Éxito', successMessage, 'success');
                    }
                } catch (error) {
                    Swal.fire('Error', 'Error al eliminar el elemento', 'error');
                }
            }
        });
    };

    // ========== [INICIALIZACIÓN] ==========
    // Cargar documentos iniciales de forma segura
    const loadInitialDocuments = () => {
        try {
            const documentosScript = document.getElementById('documentos-data');
            if (documentosScript) {
                const documentosData = JSON.parse(documentosScript.textContent);
                DOCUMENTS_CONTAINER.innerHTML = documentosData.map(doc => 
                    createDocumentElement({
                        ...doc,
                        tipo_display: doc.tipo.charAt(0).toUpperCase() + doc.tipo.slice(1)
                    })
                ).join('');
            }
        } catch (error) {
            console.error('Error cargando documentos iniciales:', error);
            DOCUMENTS_CONTAINER.innerHTML = `
                <div class="col-12 text-center py-4">
                    <i class="bi bi-exclamation-triangle fs-1 text-danger"></i>
                    <p class="text-danger mt-2">Error cargando documentos</p>
                </div>`;
        }
    };

    // Inicializar componentes
    const init = () => {
        refreshTooltips();
        loadInitialDocuments();
        
        // Inicializar lightbox si existe
        if (lightbox) {
            lightbox.reload();
        }
    };

    // ========== [MANEJADORES DE EVENTOS] ==========
    if (UPLOAD_FORM) {
        UPLOAD_FORM.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleFormSubmission(UPLOAD_FORM, {
                loadingState: '<i class="bi bi-upload me-2"></i>Subiendo...',
                successMessage: 'Documento subido correctamente',
                resetForm: true,
                onSuccess: (data) => {
                    const hasPlaceholder = DOCUMENTS_CONTAINER.querySelector('.col-12.text-center');
                    if (hasPlaceholder) DOCUMENTS_CONTAINER.innerHTML = '';
                    
                    DOCUMENTS_CONTAINER.insertAdjacentHTML('afterbegin', 
                        createDocumentElement(data.document));
                    
                    if (lightbox) lightbox.reload();
                    refreshTooltips();
                }
            });
        });
    }

    if (NEW_NOTE_FORM) {
        NEW_NOTE_FORM.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleFormSubmission(NEW_NOTE_FORM, {
                loadingState: '<i class="bi bi-plus-circle me-2"></i>Creando...',
                successMessage: 'Nota creada correctamente',
                resetForm: true,
                onSuccess: (data) => {
                    if (NOTES_CONTAINER.querySelector('.no-notes')) {
                        NOTES_CONTAINER.innerHTML = '';
                    }
                    
                    NOTES_CONTAINER.insertAdjacentHTML('afterbegin', 
                        createNoteElement(data.nota));
                    
                    NOTES_CONTAINER.scrollTo({ top: 0, behavior: 'smooth' });
                    refreshTooltips();
                }
            });
        });
    }

    // Configurar manejadores de eliminación
    setupDeleteHandlers('.delete-document', `/clientes/${clienteId}/documentos/`, 'Documento eliminado');
    setupDeleteHandlers('.delete-note', `/clientes/${clienteId}/notas/`, 'Nota eliminada');

    // Iniciar la aplicación
    init();
});
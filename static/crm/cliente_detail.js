document.addEventListener('DOMContentLoaded', function() {
    // ========== [CONFIGURACIÓN INICIAL] ==========
    const clienteId = window.CLIENTE_ID;
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const DOCUMENTS_CONTAINER = document.getElementById('documentsContainer');
    const UPLOAD_FORM = document.getElementById('documentUploadForm');
    const NOTES_CONTAINER = document.getElementById('notesContainer');
    const NEW_NOTE_FORM = document.getElementById('newNoteForm');
    const imageTypes = ['JPG', 'JPEG', 'PNG'];
    const pdfTypes = ['PDF'];
    const wordTypes = ['DOC', 'DOCX'];

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
            const formData = new FormData(form);
            
            // Validación condicional de archivo
            const fileInput = form.querySelector('input[type="file"]');
            if (fileInput) { // Solo si el formulario tiene file input
                if (fileInput.files.length === 0) {
                    throw new Error('Debe seleccionar un archivo');
                }
            }
    
            const response = await fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });
    
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                const errorMsg = data.errors ? Object.values(data.errors).flat().join(', ') : data.error;
                throw new Error(errorMsg || 'Error en la operación');
            }
    
            await config.onSuccess(data);
            if (config.resetForm) form.reset();
            
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
            if (progressBar) progressBar.style.width = '0%';
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
        return `
        <a href="${doc.url}" target="_blank" class="document-preview-link">
            <div class="document-preview-content">
                ${(() => {
                    if (imageTypes.includes(doc.type)) {
                        return `<img src="${doc.url}" class="img-fluid" alt="Preview" loading="lazy">`;
                    }
                    if (pdfTypes.includes(doc.type)) {
                        return `
                            <div class="pdf-preview">
                                <i class="bi bi-file-pdf display-4 text-danger"></i>
                                <div class="mt-2">Ver PDF completo</div>
                            </div>`;
                    }
                    if (wordTypes.includes(doc.type)) {
                        return `
                            <div class="word-preview">
                                <i class="bi bi-file-earmark-word display-4 text-primary"></i>
                                <div class="mt-2">Descargar documento</div>
                            </div>`;
                    }
                    return `
                        <div class="default-preview">
                            <i class="bi ${getFileIcon(doc.type)} display-4"></i>
                            <small class="mt-2">${doc.type}</small>
                        </div>`;
                })()}
            </div>
        </a>`;
    };

    const createDocumentElement = (doc) => {
        const previewContent = getPreviewContent(doc);
        const tipoDisplay = doc.tipo_display || 'General';
        
        return `<div class="col-md-4 mb-3 document-item" data-id="${doc.id}">
            <div class="document-card border rounded p-3">
                <div class="doc-thumbnail position-relative">
                    ${previewContent}
                    <span class="badge bg-dark position-absolute top-0 start-0 m-2">
                        ${tipoDisplay}
                    </span>
                    <div class="doc-actions position-absolute top-0 end-0 m-2">
                        <a href="${doc.url}" class="btn btn-sm btn-light shadow-sm" 
                           download="${doc.name}" data-bs-toggle="tooltip" title="Descargar">
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
    const loadInitialDocuments = () => {
        try {
            const documentosScript = document.getElementById('documentos-data');
            if (documentosScript) {
                const documentosData = JSON.parse(documentosScript.textContent);
                DOCUMENTS_CONTAINER.innerHTML = '';
                
                documentosData.forEach(doc => {
                    const tipo = doc.tipo || 'general';
                    const tipoDisplay = tipo.charAt(0).toUpperCase() + tipo.slice(1);
                    const element = createDocumentElement({...doc, tipo_display: tipoDisplay});
                    DOCUMENTS_CONTAINER.insertAdjacentHTML('beforeend', element);
                });

                if (!documentosData.length) {
                    DOCUMENTS_CONTAINER.innerHTML = `
                        <div class="col-12 text-center py-4">
                            <i class="bi bi-folder-x fs-1 text-muted"></i>
                            <p class="text-muted mt-2">No hay documentos adjuntos</p>
                        </div>`;
                }
            }
        } catch (error) {
            console.error('Error cargando documentos:', error);
            DOCUMENTS_CONTAINER.innerHTML = `
                <div class="col-12 text-center py-4">
                    <i class="bi bi-exclamation-triangle fs-1 text-danger"></i>
                    <p class="text-danger mt-2">Error cargando documentos</p>
                </div>`;
        }
    };

    const init = () => {
        refreshTooltips();
        loadInitialDocuments();
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
                    DOCUMENTS_CONTAINER.insertAdjacentHTML('afterbegin', createDocumentElement(data.document));
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
                    if (NOTES_CONTAINER.querySelector('.no-notes')) NOTES_CONTAINER.innerHTML = '';
                    NOTES_CONTAINER.insertAdjacentHTML('afterbegin', createNoteElement(data.nota));
                    NOTES_CONTAINER.scrollTo({ top: 0, behavior: 'smooth' });
                    refreshTooltips();
                }
            });
        });
    }

    setupDeleteHandlers('.delete-document', `/clientes/${clienteId}/documentos/`, 'Documento eliminado');
    setupDeleteHandlers('.delete-note', `/clientes/${clienteId}/notas/`, 'Nota eliminada');

    init();
});
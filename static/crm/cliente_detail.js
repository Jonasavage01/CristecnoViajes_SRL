// cliente_detail.js
const clienteId = window.CLIENTE_ID; // Obtenemos el ID desde Django

document.addEventListener('DOMContentLoaded', function() {
    // Configuración inicial de tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Función auxiliar para manejo de formularios
    async function handleFormSubmission(form, config) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalContent = submitBtn.innerHTML;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = config.loadingState;

        try {
            const response = await fetch(form.action, {
                method: form.method,
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json',
                    'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                }
            });

            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Error en la operación');
            }

            await config.onSuccess(data);
            if(config.resetForm) form.reset();
            Swal.fire('Éxito', config.successMessage, 'success');
            
        } catch (error) {
            console.error('Error:', error);
            let errorMsg = 'Error de conexión';
            if (error instanceof SyntaxError) {
                errorMsg = 'Respuesta inválida del servidor';
            } else if (error.message) {
                errorMsg = error.message;
            }
            Swal.fire('Error', errorMsg, 'error');
            if(config.onError) config.onError(error);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalContent;
        }
    }

    // Manejo de subida de documentos
    const uploadForm = document.getElementById('documentUploadForm');
    if(uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleFormSubmission(uploadForm, {
                loadingState: '<i class="bi bi-upload me-2"></i>Subiendo...',
                successMessage: 'Documento subido correctamente',
                resetForm: true,
                onSuccess: (data) => {
                    const docContainer = document.getElementById('documentsContainer');
                    const emptyMsg = docContainer.querySelector('.text-center');
                    if(emptyMsg) emptyMsg.remove();
                
                    const newDoc = createDocumentElement(data.document);
                    docContainer.insertAdjacentHTML('afterbegin', newDoc);
                    refreshTooltips();
                }
            });
        });
    }

    // Manejo de nuevas notas
    const newNoteForm = document.getElementById('newNoteForm');
    if(newNoteForm) {
        newNoteForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleFormSubmission(newNoteForm, {
                loadingState: '<i class="bi bi-plus-circle me-2"></i>Creando...',
                successMessage: 'Nota creada correctamente',
                resetForm: true,
                onSuccess: (data) => {
                    const notesContainer = document.getElementById('notesContainer');
                    
                    // Limpiar completamente el contenedor si hay mensaje de "no hay notas"
                    if (notesContainer.querySelector('.no-notes')) {
                        notesContainer.innerHTML = '';
                    }
                    
                    // Crear elemento y asegurar la inserción correcta
                    const newNote = document.createElement('div');
                    newNote.innerHTML = createNoteElement(data.nota).trim();
                    
                    notesContainer.prepend(newNote.firstChild);
                }
            });
        });
    }

    // Funciones de creación de elementos
    // Función para crear elementos de documento (actualizada)
function createDocumentElement(doc) {
    const previewContent = getPreviewContent(doc);
    
    return `
        <div class="col-md-4 mb-3">
            <div class="document-card border rounded p-3">
                <div class="doc-thumbnail position-relative">
                    ${previewContent}
                    
                    <span class="badge bg-dark position-absolute top-0 start-0 m-2">
                        ${doc.tipo_display}
                    </span>
                    
                    <div class="doc-actions position-absolute top-0 end-0 m-2">
                        <a href="${doc.url}" 
                           class="btn btn-sm btn-light shadow-sm"
                           download="${doc.name}"
                           data-bs-toggle="tooltip" 
                           title="Descargar">
                            <i class="bi bi-download"></i>
                        </a>
                        <button class="btn btn-sm btn-light shadow-sm delete-document" 
                                data-id="${doc.id}"
                                data-bs-toggle="tooltip" 
                                title="Eliminar">
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
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Función para contenido de vista previa
function getPreviewContent(doc) {
    const imageTypes = ['JPG', 'JPEG', 'PNG'];
    const pdfTypes = ['PDF'];
    
    if (imageTypes.includes(doc.type)) {
        return `
            <a href="${doc.url}" class="glightbox">
                <img src="${doc.url}" 
                     alt="${doc.name}"
                     class="img-fluid preview-image">
            </a>`;
    }
    
    if (pdfTypes.includes(doc.type)) {
        return `
            <div class="pdf-preview-container">
                <iframe src="${doc.url}#view=fitH" 
                        class="pdf-preview" 
                        frameborder="0"></iframe>
            </div>`;
    }
    
    return `
        <div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted py-3">
            <i class="bi ${getFileIcon(doc.type)} fs-1"></i>
            <small class="mt-2">${doc.type}</small>
        </div>`;
}

// Inicializar GLightbox
const lightbox = GLightbox({
    selector: '.glightbox',
    zoomable: true,
    touchNavigation: true,
    loop: true
});

// Añadir estilos CSS adicionales
const style = document.createElement('style');
style.textContent = `
    .doc-thumbnail {
        height: 250px;
        overflow: hidden;
        border-radius: 8px;
        background: #f8f9fa;
        transition: transform 0.2s;
    }
    
    .doc-thumbnail:hover {
        transform: translateY(-5px);
    }
    
    .pdf-preview-container {
        width: 100%;
        height: 100%;
        position: relative;
    }
    
    .pdf-preview {
        width: 100%;
        height: 100%;
        border: none;
    }
    
    .preview-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .doc-actions .btn {
        backdrop-filter: blur(5px);
        background: rgba(255, 255, 255, 0.8);
    }
`;
document.head.appendChild(style);

// Hacer PDFs responsivos
function adjustPDFPreviews() {
    document.querySelectorAll('.doc-pdf-preview').forEach(iframe => {
        const container = iframe.closest('.doc-thumbnail');
        if (container) {
            iframe.style.height = container.offsetHeight + 'px';
        }
    });
}

window.addEventListener('resize', adjustPDFPreviews);
adjustPDFPreviews();
    
    function getFileIcon(type) {
        const iconMap = {
            // Extensiones de archivo
            'pdf': 'bi-file-earmark-pdf text-danger',
            'doc': 'bi-file-earmark-word text-primary',
            'docx': 'bi-file-earmark-word text-primary',
            'jpg': 'bi-file-image text-success',
            'jpeg': 'bi-file-image text-success',
            'png': 'bi-file-image text-success',
            'txt': 'bi-file-text text-secondary',
            
            // Mime types como fallback
            'application/pdf': 'bi-file-earmark-pdf text-danger',
            'application/msword': 'bi-file-earmark-word text-primary',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'bi-file-earmark-word text-primary',
            'image/jpeg': 'bi-file-image text-success',
            'image/png': 'bi-file-image text-success'
        };
        
        // Primero intentar por extensión
        const extension = type.split('.').pop().toLowerCase();
        if (iconMap[extension]) {
            return `<i class="bi ${iconMap[extension]} fs-4 me-2"></i>`;
        }
        
        // Si no, intentar por mime type
        const mimeType = type.split('/')[1]?.toLowerCase();
        return `<i class="bi ${iconMap[mimeType] || 'bi-file-earmark'} fs-4 me-2"></i>`;
    }

    function createNoteElement(note) {
        return `
            <div class="note-item border-bottom pb-3 mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted">${note.fecha_creacion}</small>
                    <button class="btn btn-sm btn-danger delete-note" data-id="${note.id}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
               <p class="mb-0">${note.contenido.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>
            </div>
        `;
    }

    // Manejo de eliminación de elementos
    function setupDeleteHandlers(selector, endpointBase, successMessage) {
        document.addEventListener('click', async (e) => {
            const deleteBtn = e.target.closest(selector);
            if(deleteBtn) {
                const id = deleteBtn.dataset.id;
                const endpoint = `${endpointBase}${id}/`;
                
                const result = await Swal.fire({
                    title: '¿Estás seguro?',
                    text: "Esta acción no se puede deshacer",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sí, eliminar'
                });

                if(result.isConfirmed) {
                    try {
                        const response = await fetch(endpoint, {
                            method: 'DELETE',
                            headers: {
                                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                            }
                        });
                        
                        const data = await response.json();
                        if(data.success) {
                            deleteBtn.closest('.document-card')?.remove();
                            deleteBtn.closest('.note-item')?.remove();
                            Swal.fire('Éxito', successMessage, 'success');
                        }
                    } catch(error) {
                        Swal.fire('Error', 'Error al eliminar el elemento', 'error');
                    }
                }
            }
        });
    }
    
    // Configurar handlers con nueva estructura de URLs
    setupDeleteHandlers('.delete-document', `/clientes/${clienteId}/documentos/`, 'Documento eliminado');
    setupDeleteHandlers('.delete-note', `/clientes/${clienteId}/notas/`, 'Nota eliminada');

    // Helper functions
    function refreshTooltips() {
        tooltipTriggerList.forEach(tooltip => bootstrap.Tooltip.getInstance(tooltip)?.dispose());
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
});
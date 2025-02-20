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
                    const newNote = createNoteElement(data.nota);
                    
                    if(notesContainer.querySelector('.no-notes')) {
                        notesContainer.innerHTML = '';
                    }
                    
                    notesContainer.prepend(newNote);
                }
            });
        });
    }

    // Funciones de creación de elementos
    function createDocumentElement(doc) {
        return `
            <div class="col-md-4 mb-3">
                <div class="document-card border rounded p-3">
                    <div class="d-flex align-items-center mb-2">
                        ${getFileIcon(doc.type)}
                        <span class="text-truncate">${doc.name}</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <small class="text-muted">${doc.upload_date}</small>
                        <div>
                            <a href="${doc.url}" 
                               class="btn btn-sm btn-outline-primary"
                               download>
                                <i class="bi bi-download"></i>
                            </a>
                            <button class="btn btn-sm btn-outline-danger delete-document" 
                                    data-id="${doc.id}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    function getFileIcon(type) {
        if (!type) return '<i class="bi bi-file-earmark fs-4 me-2"></i>';
        
        const fileType = type.split('/')[1] || 'unknown';
        const icons = {
            'pdf': 'bi-file-earmark-pdf text-danger',
            'doc': 'bi-file-earmark-word text-primary',
            'docx': 'bi-file-earmark-word text-primary',
            'jpg': 'bi-file-image text-success',
            'jpeg': 'bi-file-image text-success',
            'png': 'bi-file-image text-success'
        };
        return `<i class="bi ${icons[fileType] || 'bi-file-earmark'} fs-4 me-2"></i>`;
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
                <p class="mb-0">${note.contenido}</p>
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
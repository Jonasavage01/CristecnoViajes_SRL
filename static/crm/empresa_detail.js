// static/js/empresa_detail.js

document.addEventListener('DOMContentLoaded', function() {
    // Manejo de envío de notas
    const noteForm = document.getElementById('newNoteForm');
    if (noteForm) {
        noteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitNoteForm(this);
        });
        document.querySelectorAll('.preview-document').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                handleDocumentPreview(this);
            });
        });
    }


    // Manejo de subida de documentos
    const docForm = document.getElementById('documentUploadForm');
    if (docForm) {
        docForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitDocForm(this);
        });
    }

    // Inicializar tooltips
    initTooltips();
    
    // Manejar clics en filas de la tabla empresas
    handleTableRowClicks();
    
    // Configurar botones de copiar
    setupCopyButtons();
    
    // Manejar eliminaciones
    setupDeleteButtons();
});

// =============== FUNCIONES PRINCIPALES ===============

function submitNoteForm(form) {
    const formData = new FormData(form);
    const empresaId = window.location.pathname.split('/').filter(Boolean).pop();
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            addNewNote(data.nota);
            form.reset();
            showToast('Nota agregada exitosamente', 'success');
        } else {
            showFormErrors(form, data.errors);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error al guardar la nota: ' + error.message, 'danger');
    });
}

function submitDocForm(form) {
    const formData = new FormData(form);
    formData.append('csrfmiddlewaretoken', getCookie('csrftoken')); // Añadir esto
    
    const progressBar = createProgressBar(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest' // Mantener este header
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            addNewDocument(data.documento);
            form.reset();
            showToast('Documento subido exitosamente', 'success');
        } else {
            showFormErrors(form, data.errors);
        }
        progressBar.remove();
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error al subir el documento: ' + error.message, 'danger');
        progressBar.remove();
    });
}

function addNewNote(notaData) {
    const notesContainer = document.getElementById('notesContainer');
    const emptyState = notesContainer.querySelector('.empty-state');
    
    if (emptyState) emptyState.remove();

    const noteHtml = `
        <div class="note-item mb-3">
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            <small class="text-muted">
                                <i class="bi bi-clock me-1"></i>
                                ${notaData.fecha}
                            </small>
                            <small class="text-muted ms-2">
                                <i class="bi bi-person me-1"></i>
                                ${notaData.autor || 'Anónimo'}
                            </small>
                        </div>
                        <form method="post" action="/empresas/${notaData.empresa_id}/eliminar-nota/${notaData.id}/">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <button type="submit" class="btn btn-link text-danger btn-sm delete-note">
                                <i class="bi bi-trash"></i>
                            </button>
                        </form>
                    </div>
                    <p class="mb-0 text-muted">${notaData.contenido}</p>
                </div>
            </div>
        </div>
    `;
    
    notesContainer.insertAdjacentHTML('afterbegin', noteHtml);
    initTooltips();
    setupDeleteButtons();
}

function addNewDocument(docData) {
    const docsContainer = document.getElementById('documentsContainer');
    const emptyState = docsContainer.querySelector('.empty-state');
    
    if (emptyState) emptyState.remove();

    const previewHtml = docData.extension.match(/(jpg|jpeg|png)/) ? 
        `<div class="document-preview">
            <img src="${docData.url}" class="img-fluid rounded" alt="Preview" loading="lazy">
         </div>` : 
        `<div class="document-icon-container">
            <i class="bi ${getDocumentIcon(docData.url)} document-icon"></i>
         </div>`;

    const docHtml = `
        <div class="col-md-4">
            <div class="document-card card border-0 shadow-sm h-100">
                <div class="card-body">
                    ${previewHtml}
                    <div class="d-flex align-items-center gap-3">
                        <div class="flex-grow-1">
                            <h6 class="mb-1 text-truncate">${docData.nombre}</h6>
                            <small class="text-muted">
                                ${docData.tipo} · ${docData.fecha}
                            </small>
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-transparent border-0 d-flex gap-2">
                    <a href="${docData.url}" 
                       target="_blank"
                       class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-eye"></i>
                    </a>
                    
                    <a href="${docData.url}" 
                       download
                       class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-download"></i>
                    </a>
                    
                    <form method="post" action="/empresas/${docData.empresa_id}/eliminar-documento/${docData.id}/">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                        <button type="submit" class="btn btn-sm btn-outline-danger delete-document">
                            <i class="bi bi-trash"></i>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    docsContainer.insertAdjacentHTML('afterbegin', docHtml);
    initTooltips();
    setupDeleteButtons();
}

// =============== MEJORAS ADICIONALES ===============

function showFormErrors(form, errors) {
    // Limpiar errores previos
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());

    // Mostrar nuevos errores
    Object.entries(errors).forEach(([field, messages]) => {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            input.classList.add('is-invalid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = messages.join(' ');
            input.parentNode.appendChild(errorDiv);
        }
    });
}

function createProgressBar(form) {
    const progress = document.createElement('div');
    progress.className = 'progress mt-3';
    progress.innerHTML = `
        <div class="progress-bar progress-bar-striped progress-bar-animated" 
             role="progressbar" 
             style="width: 0%"
             aria-valuenow="0" 
             aria-valuemin="0" 
             aria-valuemax="100">
        </div>
    `;
    form.parentNode.insertBefore(progress, form.nextSibling); // Usar el formulario recibido
    return progress;
}

// =============== FUNCIONES AUXILIARES ===============

function handleTableRowClicks() {
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', (e) => {
            // Ignorar clics en botones de acciones
            if (!e.target.closest('.btn')) {
                window.location.href = row.dataset.detailUrl;
            }
        });
    });
}

function setupDeleteButtons() {
    document.querySelectorAll('.delete-document, .delete-note').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            showDeleteConfirmation(this);
        });
    });
}

function showDeleteConfirmation(button) {
    const form = button.closest('form');
    const isDocument = form.action.includes('documento');
    
    Swal.fire({
        title: '¿Confirmar eliminación?',
        text: `Esta acción eliminará ${isDocument ? 'el documento' : 'la nota'} permanentemente`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar'
    }).then((result) => {
        if (result.isConfirmed) {
            submitDeleteRequest(form);
        }
    });
}

function submitDeleteRequest(form) {
    fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Error en la respuesta del servidor');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Animación de eliminación
            const element = form.closest('.document-card, .note-item');
            element.style.transition = 'all 0.3s ease';
            element.style.opacity = '0';
            element.style.transform = 'translateX(-100px)';
            
            setTimeout(() => {
                element.remove();
                checkEmptyStates();
            }, 300);
            
            showToast(data.message, 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error al eliminar: ' + error.message, 'danger');
    });
}



// =============== UTILIDADES ===============

function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(t => new bootstrap.Tooltip(t));
}

function setupCopyButtons() {
    document.querySelectorAll('.btn-copy').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const text = this.dataset.copy;
            navigator.clipboard.writeText(text);
            showToast('Copiado al portapapeles', 'success');
        });
    });
}

function showToast(message, type = 'success') {
    const toastEl = document.getElementById('liveToast');
    const toast = new bootstrap.Toast(toastEl);
    const iconMap = {
        success: 'bi-check-circle-fill',
        danger: 'bi-x-circle-fill',
        warning: 'bi-exclamation-circle-fill'
    };

    // Resetear clases
    toastEl.className = 'toast position-fixed bottom-0 end-0 m-3';
    toastEl.classList.add(`text-bg-${type}`);
    
    // Configurar contenido
    const icon = toastEl.querySelector('.toast-icon');
    icon.className = `bi ${iconMap[type] || 'bi-info-circle-fill'} me-2`;
    
    toastEl.querySelector('.toast-message').textContent = message;
    
    // Mostrar con animación
    toast.show();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Añadir en empresa_detail.js
function getDocumentIcon(url) {
    const ext = url.split('.').pop().toLowerCase();
    const iconMap = {
        'pdf': 'bi-file-earmark-pdf text-danger',
        'doc': 'bi-file-earmark-word text-primary',
        'docx': 'bi-file-earmark-word text-primary',
        'jpg': 'bi-file-image text-success',
        'jpeg': 'bi-file-image text-success',
        'png': 'bi-file-image text-success'
    };
    return iconMap[ext] || 'bi-file-earmark text-secondary';
}


function checkEmptyStates() {
    const checkContainer = (containerId, emptyHtml) => {
        const container = document.getElementById(containerId);
        if (container.children.length === 0) {
            container.insertAdjacentHTML('beforeend', emptyHtml);
        }
    };

    // Para documentos
    checkContainer('documentsContainer', `
        <div class="col-12 text-center py-4">
            <i class="bi bi-cloud-arrow-up display-4 text-muted"></i>
            <p class="text-muted mt-2">No hay documentos adjuntos</p>
        </div>
    `);

    // Para notas
    checkContainer('notesContainer', `
        <div class="empty-state text-center py-4">
            <i class="bi bi-journal-x display-4 text-muted"></i>
            <h5 class="mt-3 text-muted">No hay notas registradas</h5>
        </div>
    `);
}
// static/js/empresa_detail.js

document.addEventListener('DOMContentLoaded', function() {
    // Manejo de envío de notas
    const noteForm = document.getElementById('newNoteForm');
    if (noteForm) {
        noteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitNoteForm(this);
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
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addNewNote(data.nota);
            form.reset();
            showToast('Nota agregada exitosamente', 'success');
        } else {
            showFormErrors(form, data.errors);
        }
    })
    .catch(error => console.error('Error:', error));
}

function submitDocForm(form) {
    const formData = new FormData(form);
    const progressBar = createProgressBar();
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
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
        progressBar.remove();
    });
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
        }
    })
    .then(response => {
        if (response.ok) {
            form.closest('.document-card, .note-item').remove();
            showToast('Eliminado exitosamente', 'success');
            checkEmptyStates();
        }
    })
    .catch(error => console.error('Error:', error));
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
                                ${notaData.autor}
                            </small>
                        </div>
                        <form method="post" action="/empresas/delete-nota/${notaData.id}/">
                            {% csrf_token %}
                            <button type="submit" class="btn btn-link text-danger btn-sm">
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
}

function addNewDocument(docData) {
    const docsContainer = document.getElementById('documentsContainer');
    const emptyState = docsContainer.querySelector('.empty-state');
    
    if (emptyState) emptyState.remove();

    const docHtml = `
        <div class="col-md-4">
            <div class="document-card card border-0 shadow-sm h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center gap-3">
                        <i class="bi ${getDocumentIcon(docData.url)} fs-2"></i>
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
                    <form method="post" action="/empresas/delete-documento/${docData.id}/">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-sm btn-outline-danger delete-document">
                            <i class="bi bi-trash"></i>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    docsContainer.insertAdjacentHTML('afterbegin', docHtml);
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
    const toast = new bootstrap.Toast(document.getElementById('liveToast'));
    const toastBody = document.querySelector('.toast-body');
    
    toastBody.textContent = message;
    document.getElementById('liveToast').classList.add(`text-bg-${type}`);
    toast.show();
    
    setTimeout(() => {
        document.getElementById('liveToast').classList.remove(`text-bg-${type}`);
    }, 3000);
}

function getCookie(name) {
    // Función estándar para obtener cookies
}

function createProgressBar() {
    // Lógica para barra de progreso de subida
}

function checkEmptyStates() {
    // Verificar si quedan documentos/notas y mostrar estado vacío
}
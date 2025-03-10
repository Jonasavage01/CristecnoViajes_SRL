// static/crm/empresas.js - Manejo de eliminación
document.addEventListener('DOMContentLoaded', function() {
    // Configurar evento para los botones de eliminar
    document.querySelectorAll('.delete-empresa').forEach(btn => {
        btn.addEventListener('click', handleDeleteEmpresa);
    });

    // Configurar submit del formulario de eliminación
    document.getElementById('deleteEmpresaForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const form = e.target;
        const empresaId = document.getElementById('deleteEmpresaId').value;
        const deleteUrl = form.action;
        
        executeDelete(empresaId, deleteUrl);
    });
});

const handleDeleteEmpresa = (e) => {
    e.preventDefault();
    const btn = e.currentTarget;
    const empresaId = btn.dataset.empresaId;
    const empresaName = btn.dataset.empresaName;
    const documentosCount = btn.dataset.documentosCount || 0;
    const notasCount = btn.dataset.notasCount || 0;
    const deleteUrl = btn.dataset.deleteUrl;

    // Actualizar formulario
    const form = document.getElementById('deleteEmpresaForm');
    form.action = deleteUrl;
    document.getElementById('deleteEmpresaId').value = empresaId;

    // Actualizar contenido del modal
    document.getElementById('empresaDeleteName').textContent = empresaName;
    document.getElementById('documentosCount').textContent = 
        `${documentosCount} documento${documentosCount != 1 ? 's' : ''} adjunto${documentosCount != 1 ? 's' : ''}`;
    document.getElementById('notasCount').textContent = 
        `${notasCount} nota${notasCount != 1 ? 's' : ''} registrada${notasCount != 1 ? 's' : ''}`;
};

// Añadir función para obtener cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const executeDelete = async (empresaId, deleteUrl) => {
    const errorAlert = document.getElementById('deleteEmpresaError');
    const confirmBtn = document.getElementById('confirmEmpresaDelete');
    const spinner = confirmBtn.querySelector('.spinner-border');
    const submitText = confirmBtn.querySelector('.submit-text');
    const form = document.getElementById('deleteEmpresaForm');
    
    try {
        errorAlert.classList.add('d-none');
        confirmBtn.disabled = true;
        submitText.classList.add('d-none');
        spinner.classList.remove('d-none');

        // Obtener datos del formulario incluyendo CSRF
        const formData = new FormData(form);
        
        const response = await fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',  // Añadir content-type
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            },
            body: new URLSearchParams({
                'csrfmiddlewaretoken': getCookie('csrftoken'),  // Enviar token como parámetro POST
            })
        });

        // Manejar respuesta
        const contentType = response.headers.get('content-type');
        let data;
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            throw new Error('Respuesta no JSON del servidor');
        }

        if (!response.ok || !data.success) {
            throw new Error(data.message || 'Error en la solicitud');
        }

        // Eliminar fila si es exitoso
        const row = document.querySelector(`tr[data-empresa-id="${empresaId}"]`);
        if (row) {
            row.style.transition = 'opacity 0.5s';
            row.style.opacity = '0';
            setTimeout(() => row.remove(), 500);
        }
        
        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteEmpresaModal'));
        modal.hide();
        
        // Mostrar notificación
        if (typeof showSuccessAlert === 'function') {
            showSuccessAlert(data.message, 3000);
        }

    } catch (error) {
        console.error('Error:', error);
        errorAlert.querySelector('#errorEmpresaMessage').textContent = error.message;
        errorAlert.classList.remove('d-none');
    } finally {
        confirmBtn.disabled = false;
        submitText.classList.remove('d-none');
        spinner.classList.add('d-none');
    }
};

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}
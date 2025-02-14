document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTrigger => new bootstrap.Tooltip(tooltipTrigger));

    // Manejo de eliminación con AJAX
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));
    let deleteUrl = '';
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrftoken = csrfMeta ? csrfMeta.content : '';
    if (!csrftoken) {
        console.error('CSRF token no encontrado en las meta tags.');
    }

    // Al hacer clic en cualquier botón de eliminar
    document.querySelectorAll('.delete-client').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Delete clicked, URL:', this.dataset.href); // Depuración
            deleteUrl = this.dataset.href;
            deleteModal.show();
        });
    });

    // Confirmar eliminación
    document.getElementById('confirmDeleteButton').addEventListener('click', function(e) {
        console.log("Enviando petición DELETE a:", deleteUrl);
        fetch(deleteUrl, {
            method: 'POST',
            credentials: 'same-origin', // Enviar cookies
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'  // Importante para detectar AJAX en el backend
            }
            // No se envía body ya que no es necesario
        })
        .then(response => {
            console.log('Response status:', response.status);
            // Manejar redirección inesperada
            if (response.redirected) {
                console.log('Redirigiendo a:', response.url);
                window.location.href = response.url;
                return;
            }
            if (!response.ok) {
                console.error('Error en respuesta:', response.statusText);
                return response.text().then(text => { 
                    throw new Error("Error HTTP " + response.status + ": " + text); 
                });
            }
            const contentType = response.headers.get("content-type");
            console.log("Content-Type de la respuesta:", contentType);
            if (contentType && contentType.indexOf("application/json") !== -1) {
                return response.json();
            } else {
                return response.text().then(text => {
                    console.error("Se esperaba JSON pero se recibió:", text);
                    throw new Error("Se esperaba una respuesta JSON, pero se recibió HTML.");
                });
            }
        })
        .then(data => {
            console.log('Respuesta JSON:', data);
            if (data.success) {
                // Actualizar la UI sin recargar: eliminar la fila correspondiente
                const deleteButton = document.querySelector(`.delete-client[data-href="${deleteUrl}"]`);
                if (deleteButton) {
                    const row = deleteButton.closest('tr');
                    if (row) {
                        row.remove();
                        console.log("Fila eliminada de la tabla.");
                    } else {
                        console.warn("No se encontró la fila contenedora. Se recargará la página.");
                        window.location.reload();
                    }
                } else {
                    console.warn("No se encontró el botón de eliminar. Se recargará la página.");
                    window.location.reload();
                }
                deleteModal.hide();
            } else {
                Swal.fire('Error', data.message || 'Error al eliminar el cliente', 'error');
            }
        })
        .catch(error => {
            console.error('Error en fetch:', error);
            Swal.fire('Error', 'No se pudo completar la solicitud: ' + error.message, 'error');
        })
        .finally(() => {
            // Asegurarse de cerrar el modal si aún está abierto
            deleteModal.hide();
        });
    });
});

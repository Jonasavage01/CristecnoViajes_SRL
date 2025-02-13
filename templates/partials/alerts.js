export function showErrorAlert(message) {
    Swal.fire({
        icon: 'error',
        title: 'Error al guardar',
        html: message,
        confirmButtonColor: '#2d70cc',
        background: '#1a1a1a',
        color: '#fff',
        customClass: {
            confirmButton: 'btn btn-info'
        }
    });
}

export function showSuccessAlert(message) {
    Swal.fire({
        icon: 'success',
        title: 'Éxito',
        text: message,
        confirmButtonColor: '#2d70cc',
        background: '#1a1a1a',
        color: '#fff',
        customClass: {
            confirmButton: 'btn btn-info'
        }
    });
}
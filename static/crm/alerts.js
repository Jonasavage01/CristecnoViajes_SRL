// alerts.js (versión sin módulos)
function showErrorAlert(message, options = {}) {
    Swal.fire({
        icon: 'error',
        title: options.title || 'Error al guardar',
        html: message,
        confirmButtonColor: options.confirmButtonColor || '#2d70cc',
        timer: options.timer || 5000,
        timerProgressBar: options.timerProgressBar !== undefined ? options.timerProgressBar : true,
        customClass: {
            confirmButton: options.confirmButtonClass || 'btn btn-info'
        },
        allowOutsideClick: options.allowOutsideClick !== undefined ? options.allowOutsideClick : false,
        ...options.swalOptions
    });
}

function showSuccessAlert(message, options = {}) {
    Swal.fire({
        icon: 'success',
        title: options.title || 'Éxito',
        text: message,
        confirmButtonColor: options.confirmButtonColor || '#2d70cc',
        timer: options.timer || 3000,
        timerProgressBar: options.timerProgressBar !== undefined ? options.timerProgressBar : true,
        customClass: {
            confirmButton: options.confirmButtonClass || 'btn btn-info'
        },
        allowOutsideClick: options.allowOutsideClick !== undefined ? options.allowOutsideClick : false,
        ...options.swalOptions
    });
}

// Asignar al objeto global window
window.showErrorAlert = showErrorAlert;
window.showSuccessAlert = showSuccessAlert;
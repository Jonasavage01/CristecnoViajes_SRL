export function showErrorAlert(message, options = {}) {
    Swal.fire({
        icon: 'error',
        title: options.title || 'Error al guardar',
        html: message,
        confirmButtonColor: options.confirmButtonColor || '#2d70cc',
        background: options.background || '#1a1a1a',
        color: options.color || '#fff',
        timer: options.timer || 5000,              // Tiempo en milisegundos (opcional)
        timerProgressBar: options.timerProgressBar !== undefined ? options.timerProgressBar : true,
        customClass: {
            confirmButton: options.confirmButtonClass || 'btn btn-info'
        },
        allowOutsideClick: options.allowOutsideClick !== undefined ? options.allowOutsideClick : false,
        ...options.swalOptions  // Permite incluir otras opciones de SweetAlert2
    });
}

export function showSuccessAlert(message, options = {}) {
    Swal.fire({
        icon: 'success',
        title: options.title || 'Éxito',
        text: message,
        confirmButtonColor: options.confirmButtonColor || '#2d70cc',
        background: options.background || '#1a1a1a',
        color: options.color || '#fff',
        timer: options.timer || 3000,              // Tiempo en milisegundos (opcional)
        timerProgressBar: options.timerProgressBar !== undefined ? options.timerProgressBar : true,
        customClass: {
            confirmButton: options.confirmButtonClass || 'btn btn-info'
        },
        allowOutsideClick: options.allowOutsideClick !== undefined ? options.allowOutsideClick : false,
        ...options.swalOptions
    });
}

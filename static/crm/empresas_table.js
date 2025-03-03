// static/js/empresas.js
document.addEventListener('DOMContentLoaded', function() {
    // Manejar clics en filas
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', (e) => {
            if (!e.target.closest('.btn')) {
                window.location.href = row.dataset.detailUrl;
            }
        });
    });

    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(t => new bootstrap.Tooltip(t));
    
    // Opcional: Manejar filtros si es necesario
    // ... (código adicional relacionado con la página de empresas)
});
// static/crm/empresas_filtros.js
document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('filterForm');
    const empresasTable = document.getElementById('empresasTable');
    const paginationContainer = document.querySelector('.pagination');
    const loadingIndicator = document.createElement('div');
    
    // Configurar indicador de carga
    loadingIndicator.className = 'loading-overlay';
    loadingIndicator.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
        </div>
    `;

    // Manejar submit del formulario de filtros
    filterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        applyFilters();
    });

    // Manejar cambios en los inputs de fecha
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.addEventListener('change', () => {
            if(input.value) applyFilters();
        });
    });

    // Mejorar la función applyFilters con manejo de errores
function applyFilters() {
    const formData = new FormData(filterForm);
    const params = new URLSearchParams(formData);
    
    // Mantener parámetros existentes en la URL
    const existingParams = new URLSearchParams(window.location.search);
    existingParams.forEach((value, key) => {
        if (!params.has(key)) params.append(key, value);
    });
    
    showLoading();
    
    fetch(`${window.location.pathname}?${params.toString()}&partial=1`, {
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.text();
    })
    .then(html => {
        const doc = new DOMParser().parseFromString(html, 'text/html');
        updateTableContent(doc);
        updatePagination(doc);
        initDynamicComponents();
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorAlert('Error al aplicar filtros');
    })
    .finally(() => hideLoading());
}

// Nueva función para actualizar la tabla
function updateTableContent(doc) {
    const newTable = doc.getElementById('empresasTable');
    if (newTable) {
        empresasTable.innerHTML = newTable.innerHTML;
        // Resaltar nuevas coincidencias
        empresasTable.querySelectorAll('tr').forEach(row => {
            row.classList.add('filter-highlight');
            setTimeout(() => row.classList.remove('filter-highlight'), 1000);
        });
    }
}

    // Mostrar/ocultar carga
    function showLoading() {
        document.body.appendChild(loadingIndicator);
    }

    function hideLoading() {
        if(document.body.contains(loadingIndicator)) {
            document.body.removeChild(loadingIndicator);
        }
    }

    // Actualizar botón de limpiar filtros
    function updateClearFilterButton() {
        const clearBtn = document.getElementById('clearFilters');
        const hasFilters = Array.from(filterForm.elements).some(
            el => el.name && el.value && el.name !== 'page'
        );
        
        if(hasFilters) {
            clearBtn.classList.remove('d-none');
        } else {
            clearBtn.classList.add('d-none');
        }
    }

    // Inicializar tooltips
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Manejar paginación
    document.querySelector('.pagination').addEventListener('click', function(e) {
        if(e.target.closest('.page-link')) {
            e.preventDefault();
            const page = new URL(e.target.closest('.page-link').href).searchParams.get('page');
            filterForm.page.value = page;
            applyFilters();
        }
    });

    // Inicializar
    initTooltips();
    updateClearFilterButton();
});
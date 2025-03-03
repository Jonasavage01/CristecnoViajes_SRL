// static/crm/empresas_filtros.js
document.addEventListener('DOMContentLoaded', function() {
    // Elementos principales con verificación de nulidad
    const filterForm = document.getElementById('filterForm');
    const empresasTable = document.getElementById('empresasTable');
    const paginationContainer = document.querySelector('.pagination');
    const loadingIndicator = createLoadingIndicator();
    
    // Solo inicializar si existen los elementos esenciales
    if (filterForm && empresasTable) {
        initEstadoFilterStyle();
        setupEventListeners();
        initTooltips();
        updateClearFilterButton();
    }

    function createLoadingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'loading-overlay';
        indicator.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>`;
        return indicator;
    }
    
    function setupEventListeners() {
        // Verificar existencia antes de agregar listeners
        if (filterForm) {
            filterForm.addEventListener('submit', handleFormSubmit);
            
            document.querySelectorAll('#filterForm input[type="date"]').forEach(input => {
                input.addEventListener('change', handleDateChange);
            });
        }

        if (paginationContainer) {
            paginationContainer.addEventListener('click', handlePaginationClick);
        }
    }

    function handleFormSubmit(e) {
        e.preventDefault();
        applyFilters();
    }

    function handleDateChange(e) {
        if(e.target.value) applyFilters();
    }

    async function applyFilters() {
        try {
            showLoading();
            const params = new URLSearchParams(new FormData(filterForm));
            const response = await fetchData(params);
            
            if (!response.ok) throw await handleErrorResponse(response);
            
            const html = await response.text();
            processResponse(html);
        } catch (error) {
            handleApplicationError(error);
        } finally {
            hideLoading();
        }
    }

    async function fetchData(params) {
        return fetch(`${window.location.pathname}?${params.toString()}&partial=1`, {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
    }

    async function handleErrorResponse(response) {
        const error = await response.json();
        return new Error(error.message || 'Error al aplicar filtros');
    }

    function processResponse(html) {
        const doc = new DOMParser().parseFromString(html, 'text/html');
        validateResponse(doc);
        updateUI(doc);
    }

    function validateResponse(doc) {
        const errorMessages = doc.querySelector('.alert-danger');
        if (errorMessages) {
            throw new Error(errorMessages.textContent);
        }
    }

    function updateUI(doc) {
        const newTable = doc.getElementById('empresasTable');
        const newPagination = doc.querySelector('.pagination');
        
        if (newTable) {
            empresasTable.innerHTML = newTable.innerHTML;
            highlightNewRows();
        }
        
        if (newPagination) {
            paginationContainer.innerHTML = newPagination.innerHTML;
            // Re-inicializar listeners de paginación
            initPaginationListeners();
        }
        
        initDynamicComponents();
    }

    function updateTableContent(doc) {
        const newTable = doc.getElementById('empresasTable');
        if (newTable) {
            empresasTable.innerHTML = newTable.innerHTML;
            highlightNewRows();
        }
    }

    function highlightNewRows() {
        empresasTable.querySelectorAll('tr').forEach(row => {
            row.classList.add('filter-highlight');
            setTimeout(() => row.classList.remove('filter-highlight'), 1000);
        });
    }

    function handlePaginationClick(e) {
        if (!e.target.closest('.page-link')) return;
        
        e.preventDefault();
        const page = new URL(e.target.closest('.page-link').href).searchParams.get('page');
        filterForm.page.value = page;
        applyFilters();
    }

    function initPaginationListeners() {
        if (paginationContainer) {
            paginationContainer.querySelectorAll('.page-link').forEach(link => {
                link.addEventListener('click', handlePaginationClick);
            });
        }
    }

    function updatePagination(doc) {
        const newPagination = doc.querySelector('.pagination');
        paginationContainer.innerHTML = newPagination?.innerHTML || '';
        
        if (newPagination) {
            paginationContainer.querySelectorAll('.page-link').forEach(link => {
                link.addEventListener('click', handlePaginationClick);
            });
        }
    }

    function initDynamicComponents() {
        initTooltips();
        updateClearFilterButton();
    }

    function showLoading() {
        document.body.appendChild(loadingIndicator);
    }

    function hideLoading() {
        if (document.body.contains(loadingIndicator)) {
            document.body.removeChild(loadingIndicator);
        }
    }

    function updateClearFilterButton() {
        const clearBtn = document.getElementById('clearFilters');
        const hasFilters = Array.from(filterForm.elements).some(el => 
            el.name && el.value && el.name !== 'page'
        );
        clearBtn?.classList.toggle('d-none', !hasFilters);
    }

    function initTooltips() {
        new bootstrap.Tooltip(document.body, {
            selector: '[data-bs-toggle="tooltip"]',
            trigger: 'hover'
        });
    }

    function initEstadoFilterStyle() {
        const estadoSelect = document.querySelector('select[name="estado"]');
        if (estadoSelect) {
            updateSelectStyle(estadoSelect);
            estadoSelect.addEventListener('change', () => updateSelectStyle(estadoSelect));
        }
    }

    function updateSelectStyle(select) {
        const selectedOption = select.options[select.selectedIndex];
        const color = selectedOption?.dataset.color || 'secondary';
        select.style.backgroundColor = `var(--bs-${color}-bg-subtle)`;
        select.style.borderColor = `var(--bs-${color}-border-subtle)`;
    }

    function handleApplicationError(error) {
        console.error('Error:', error);
        showErrorAlert(error.message);
    }

    function showErrorAlert(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger position-fixed top-0 end-0 m-3';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        setTimeout(() => alert.remove(), 5000);
    }
});
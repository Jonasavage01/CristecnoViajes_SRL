const debounce = (func, delay = 300) => {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
};

const updateURL = (baseURL, params) => {
    const url = new URL(baseURL);
    // Limpiar parámetros existentes primero
    Array.from(url.searchParams.keys()).forEach(key => url.searchParams.delete(key));
    
    // Agregar solo parámetros con valores
    Object.entries(params).forEach(([key, value]) => {
        if (value) url.searchParams.set(key, value);
    });
    return url;
};

document.addEventListener('DOMContentLoaded', () => {
    let isProcessing = false;
    
    const handleFilterUpdate = async (url) => {
        if (isProcessing) return;
        isProcessing = true;
        
        const loader = document.createElement('div');
        loader.className = 'ajax-loader';
        loader.innerHTML = '<div class="spinner-border text-primary"></div>';
        
        const applyButton = document.getElementById('applyFilters');
        const originalButtonHTML = applyButton.innerHTML;
        applyButton.innerHTML = '<i class="bi bi-funnel"></i> Aplicando...';
        applyButton.disabled = true;
        
        document.querySelector('.table-responsive').prepend(loader);
        
        try {
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.errors || 'Error en la respuesta del servidor');
            }
            
            const data = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            
            // Actualizar componentes
            const updateComponents = (selector) => {
                const newElement = doc.querySelector(selector);
                const currentElement = document.querySelector(selector);
                if (newElement && currentElement) {
                    currentElement.outerHTML = newElement.outerHTML;
                }
            };
            
            updateComponents('.table-responsive');
            updateComponents('.pagination');
            
            // Actualizar URL sin recargar
            window.history.replaceState({}, '', url.toString());
            
            // Actualizar estado del botón limpiar
            const hasFilters = Array.from(new URL(url).searchParams.entries())
                .some(([key, value]) => key !== 'page' && value);
            
            const clearButton = document.getElementById('clearFilters');
            if (clearButton) {
                clearButton.style.display = hasFilters ? 'inline-block' : 'none';
            }
            
        } catch (error) {
            console.error('Error:', error);
            Swal.fire('Error', error.message || 'No se pudieron actualizar los resultados', 'error');
        } finally {
            loader.remove();
            applyButton.innerHTML = originalButtonHTML;
            applyButton.disabled = false;
            isProcessing = false;
        }
    };

    // Evento de búsqueda
    document.querySelector('input[name="q"]')?.addEventListener('input', debounce(e => {
        const params = Object.fromEntries(new URLSearchParams(window.location.search));
        const url = updateURL(window.location.href, { ...params, q: e.target.value });
        handleFilterUpdate(url);
    }, 300));

    // Eventos de fecha
    const handleDateChange = debounce(() => {
        const params = Object.fromEntries(new URLSearchParams(window.location.search));
        const fechaDesde = document.querySelector('input[name="fecha_creacion_desde"]').value;
        const fechaHasta = document.querySelector('input[name="fecha_creacion_hasta"]').value;
        
        if (fechaDesde && fechaHasta && fechaDesde > fechaHasta) {
            Swal.fire('Error', 'La fecha inicial no puede ser mayor a la final', 'error');
            return;
        }
        
        const newParams = { 
            ...params, 
            fecha_creacion_desde: fechaDesde,
            fecha_creacion_hasta: fechaHasta
        };
        
        const url = updateURL(window.location.href, newParams);
        handleFilterUpdate(url);
    }, 300);
    
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.addEventListener('change', handleDateChange);
    });

    // Evento de estado
    document.querySelector('select[name="estado"]')?.addEventListener('change', debounce(e => {
        const params = Object.fromEntries(new URLSearchParams(window.location.search));
        const url = updateURL(window.location.href, { ...params, estado: e.target.value });
        handleFilterUpdate(url);
    }, 300));

    // Botón limpiar
    document.getElementById('clearFilters')?.addEventListener('click', (e) => {
        e.preventDefault();
        const params = new URLSearchParams();
        if (window.location.search.includes('page')) {
            params.set('page', new URLSearchParams(window.location.search).get('page'));
        }
        const url = updateURL(window.location.href, Object.fromEntries(params));
        handleFilterUpdate(url);
    });

    // Validación de formulario
    document.getElementById('filterForm')?.addEventListener('submit', (e) => {
        const formData = new FormData(e.target);
        const isEmpty = Array.from(formData.entries()).every(([key, value]) => 
            !value || key === 'page'
        );
        
        if (isEmpty) {
            e.preventDefault();
            Swal.fire('Advertencia', 'Por favor ingresa al menos un criterio de filtrado', 'warning');
        }
    });

    // Paginación
    document.addEventListener('click', async (e) => {
        const pageLink = e.target.closest('.page-link');
        if (pageLink) {
            e.preventDefault();
            const params = Object.fromEntries(new URLSearchParams(window.location.search));
            const page = new URL(pageLink.href).searchParams.get('page');
            const url = updateURL(window.location.href, { ...params, page });
            await handleFilterUpdate(url);
        }
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const urlsDiv = document.getElementById('urls');
    
    // Verificar que el elemento y el dataset existen
    if (!urlsDiv || !urlsDiv.dataset.exportClientes) {
        console.error('Elemento con data-export-clientes no encontrado');
        return;
    }

    document.querySelectorAll('.export-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const formato = this.dataset.format;
            // Reemplazar directamente 'csv' por el formato seleccionado
            const baseUrl = urlsDiv.dataset.exportClientes.replace('csv', formato);
            
            // Obtener parámetros del formulario
            const form = document.getElementById('filterForm');
            const params = new URLSearchParams(new FormData(form)).toString();
            
            // Construir URL final
            const finalUrl = `${baseUrl}?${params}`;
            
            // Usar fetch para manejar posibles errores
            fetch(finalUrl)
                .then(response => {
                    if (!response.ok) throw new Error('Error en la exportación');
                    return response.blob();
                })
                .then(blob => {
                    // Crear enlace temporal
                    const tempLink = document.createElement('a');
                    tempLink.href = URL.createObjectURL(blob);
                    tempLink.download = `clientes_${new Date().toISOString().split('T')[0]}.${formato === 'excel' ? 'xlsx' : formato}`;
                    tempLink.style.display = 'none';
                    
                    // Trigger descarga
                    document.body.appendChild(tempLink);
                    tempLink.click();
                    URL.revokeObjectURL(tempLink.href);
                    document.body.removeChild(tempLink);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al exportar: ' + error.message);
                });
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const urlsDiv = document.getElementById('urls');
    
    // Verificar que existe el elemento con la URL de exportación
    if (!urlsDiv || !urlsDiv.dataset.exportEmpresas) {
        console.error('Elemento con data-export-empresas no encontrado');
        return;
    }

    // Manejar clic en botones de exportación
    document.querySelectorAll('.export-empresa-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const formato = this.dataset.format;
            // Construir URL base reemplazando 'csv' por el formato seleccionado
            const baseUrl = urlsDiv.dataset.exportEmpresas.replace('csv', formato);
            
            // Obtener parámetros del formulario de filtrado
            const form = document.getElementById('filterForm');
            const params = new URLSearchParams(new FormData(form)).toString();
            
            // Construir URL final con parámetros
            const finalUrl = `${baseUrl}?${params}`;
            
            // Realizar la solicitud de exportación
            fetch(finalUrl)
                .then(response => {
                    if (!response.ok) throw new Error('Error en la exportación');
                    return response.blob();
                })
                .then(blob => {
                    // Crear enlace temporal para descarga
                    const tempLink = document.createElement('a');
                    tempLink.href = URL.createObjectURL(blob);
                    tempLink.download = `empresas_${new Date().toISOString().split('T')[0]}.${formato === 'excel' ? 'xlsx' : formato}`;
                    tempLink.style.display = 'none';
                    
                    // Disparar la descarga
                    document.body.appendChild(tempLink);
                    tempLink.click();
                    URL.revokeObjectURL(tempLink.href);
                    document.body.removeChild(tempLink);
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al exportar: ' + error.message);
                });
        });
    });
});
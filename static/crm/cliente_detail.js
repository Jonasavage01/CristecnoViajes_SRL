document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    const tooltips = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltips.map(t => new bootstrap.Tooltip(t))
    
    // Control de pestañas
    const triggerTabList = [].slice.call(document.querySelectorAll('#clientTabs button'))
    triggerTabList.forEach(triggerEl => {
        const tabTrigger = new bootstrap.Tab(triggerEl)
        triggerEl.addEventListener('click', e => {
            e.preventDefault()
            tabTrigger.show()
        })
    })
    
    // Preview documentos
    const documentPreview = document.getElementById('documentPreview')
    if(documentPreview) {
        documentPreview.addEventListener('click', () => {
            if(documentPreview.dataset.url) {
                window.open(documentPreview.dataset.url, '_blank')
            }
        })
    }
    
    // Copiar datos al portapapeles
    document.querySelectorAll('[data-copy]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const text = btn.dataset.copy
            try {
                await navigator.clipboard.writeText(text)
                btn.innerHTML = '<i class="bi bi-check2"></i> Copiado!'
                setTimeout(() => {
                    btn.innerHTML = `<i class="bi bi-clipboard"></i> ${btn.dataset.originalText}`
                }, 2000)
            } catch(err) {
                console.error('Error al copiar:', err)
            }
        })
    })
})
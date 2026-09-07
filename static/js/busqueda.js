/**
 * SAC WEB - Motor de Búsqueda Universal para Tablas
 * Implementa filtrado inteligente con soporte para acentos y múltiples términos.
 */

function inicializarBusqueda(inputId, tablaId) {
    const searchInput = document.getElementById(inputId);
    const tabla = document.getElementById(tablaId);
    
    if (!searchInput || !tabla) return;

    // Función interna para normalizar texto (quitar acentos)
    function quitarAcentos(texto) {
        return texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    searchInput.addEventListener('input', function() {
        const filtro = quitarAcentos(this.value.toLowerCase().trim());
        const filas = tabla.querySelectorAll('tbody tr');
        
        if (!filtro) {
            filas.forEach(fila => fila.style.display = '');
            return;
        }

        const palabras = filtro.split(/\s+/);
        
        filas.forEach(fila => {
            // Ignorar filas de "sin datos" o totales si tienen una clase específica
            if (fila.classList.contains('no-filtrar')) return;

            const texto = quitarAcentos(fila.textContent.toLowerCase());
            
            // Todas las palabras del buscador deben estar en la fila
            const coincide = palabras.every(palabra => {
                // Mejora para números cortos (ej: apto 1, 2)
                if (/^\d{1,2}$/.test(palabra)) {
                    const regex = new RegExp('\\b' + palabra + '\\b');
                    return regex.test(texto);
                }
                return texto.includes(palabra);
            });

            fila.style.display = coincide ? '' : 'none';
        });
    });
}

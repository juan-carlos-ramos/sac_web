# 📸 Guía Rápida: Capturas de Pantalla para el Manual

## ✅ Manual Ya Actualizado

Las rutas de Gemini/IA han sido eliminadas. Ahora el manual apunta a:
```
documentacion/imagenes_manual/
```

---

## 🎯 6 Capturas Necesarias

### Preparación Inicial

1. **Iniciar servidor:**
   ```bash
   cd d:\Universidad\sac_web
   .\venv\Scripts\python.exe manage.py runserver
   ```

2. **Abrir navegador:**
   - Chrome, Firefox o Edge
   - Ir a: `http://127.0.0.1:8000`
   - Iniciar sesión

3. **Herramienta de captura:**
   - Presiona: `Windows + Shift + S`
   - O usa: Snipping Tool

---

## 📷 Captura 1: Dashboard Principal

**Archivo:** `dashboard.png`

**Pasos:**
1. Después de login, estás en el dashboard
2. Asegúrate de que se vea:
   - ✅ Navbar completo arriba
   - ✅ 4 tarjetas de estadísticas
   - ✅ Los 3 gráficos (si hay datos)
   - ✅ Botones de acceso rápido
3. Presiona `Windows + Shift + S`
4. Selecciona toda la ventana del navegador
5. Abre Paint y pega (`Ctrl + V`)
6. Guarda como: `d:\Universidad\sac_web\documentacion\imagenes_manual\dashboard.png`

**Qué debe verse:**
- Título "Panel de Control"
- Estadísticas: Total Inmuebles, Total Facturas, Total Recaudado, Deuda Pendiente
- Gráficos interactivos
- Botones: Gestionar Inmuebles, Ver Facturas, Registrar Pagos, etc.

---

## 📷 Captura 2: Lista de Inmuebles

**Archivo:** `lista_inmuebles.png`

**Pasos:**
1. Clic en "Inmuebles" en el navbar
2. Asegúrate de que se vea:
   - ✅ Título "Inmuebles"
   - ✅ Botón "📊 Exportar Excel"
   - ✅ Botón "+ Crear Inmueble"
   - ✅ Tabla con inmuebles
   - ✅ Botones Ver/Editar/Eliminar
3. Capturar pantalla completa
4. Guardar como: `lista_inmuebles.png`

**Qué debe verse:**
- Tabla con columnas: Número, Propietario, Documento, Email, Teléfono, Alícuota
- Al menos 2-3 inmuebles en la lista
- Botones de acción en cada fila

---

## 📷 Captura 3: Crear Factura

**Archivo:** `crear_factura.png`

**Pasos:**
1. Navbar → "Facturas" → "+ Crear Factura"
2. Asegúrate de que se vea:
   - ✅ Título "Crear Nueva Factura"
   - ✅ Campo de período
   - ✅ Sección de gastos (aunque esté vacía)
   - ✅ Botones Cancelar y Crear Factura
3. Capturar formulario completo
4. Guardar como: `crear_factura.png`

**Qué debe verse:**
- Formulario de creación
- Selector de período (YYYY-MM)
- Área para agregar gastos
- Botones al final

---

## 📷 Captura 4: Registrar Pago

**Archivo:** `registrar_pago.png`

**Pasos:**
1. Navbar → "Pagos" → "+ Registrar Pago"
2. Asegúrate de que se vea:
   - ✅ Título "Registrar Nuevo Pago"
   - ✅ Selector de inmueble
   - ✅ Selector de factura
   - ✅ Campos de monto, moneda, método
   - ✅ Resumen de deuda (si hay)
   - ✅ Botones Cancelar y Registrar Pago
3. Capturar formulario completo
4. Guardar como: `registrar_pago.png`

**Qué debe verse:**
- Formulario con todos los campos
- Selectores desplegables
- Radio buttons para moneda (BS/USD)
- Botón de cargar comprobante

---

## 📷 Captura 5: Recibo PDF

**Archivo:** `recibo_pdf.png`

**Pasos:**
1. Navbar → "Pagos"
2. Si hay pagos, clic en "Ver Recibo" de cualquier pago
3. Se abre el PDF en el navegador
4. Asegúrate de que se vea:
   - ✅ Encabezado "CONDOMINIO SANTA ANA DE CORO"
   - ✅ Título "RECIBO DE PAGO"
   - ✅ Información del pago
   - ✅ Tabla con detalles
   - ✅ Totales
5. Capturar el PDF completo
6. Guardar como: `recibo_pdf.png`

**Si no hay pagos registrados:**
- Primero registra un pago de prueba
- Luego genera el recibo

**Qué debe verse:**
- Diseño profesional del recibo
- Logo del condominio
- Datos del pago
- Firma o pie de página

---

## 📷 Captura 6: Panel de Auditoría

**Archivo:** `panel_auditoria.png`

**Pasos:**
1. Navbar → "Auditoría"
2. Asegúrate de que se vea:
   - ✅ Título "Auditoría"
   - ✅ Filtros (Usuario, Fecha, Modelo, Acción)
   - ✅ Botón "Exportar a Excel"
   - ✅ Tabla con logs de auditoría
   - ✅ Badges de colores (Crear/Editar/Borrar)
   - ✅ Paginación
3. Capturar pantalla completa
4. Guardar como: `panel_auditoria.png`

**Qué debe verse:**
- Filtros en la parte superior
- Tabla con registros de auditoría
- Columnas: Fecha/Hora, Usuario, Acción, Modelo, Descripción
- Badges de colores según tipo de acción

---

## ✅ Checklist Final

Después de tomar las 6 capturas:

- [ ] Todas las capturas están en: `d:\Universidad\sac_web\documentacion\imagenes_manual\`
- [ ] Los nombres son exactamente:
  - [ ] `dashboard.png`
  - [ ] `lista_inmuebles.png`
  - [ ] `crear_factura.png`
  - [ ] `registrar_pago.png`
  - [ ] `recibo_pdf.png`
  - [ ] `panel_auditoria.png`
- [ ] Las capturas son claras y legibles
- [ ] Se ve el contenido completo de cada pantalla
- [ ] No hay información sensible visible

---

## 🎯 Convertir a PDF

Una vez que tengas las capturas:

```bash
# Convertir el manual a PDF con las imágenes
pandoc MANUAL_USUARIO_SAC_WEB.md -o MANUAL_USUARIO_SAC_WEB.pdf --toc
```

---

## 💡 Consejos

**Para mejores capturas:**
- Usa resolución de pantalla alta (1920x1080 o superior)
- Asegúrate de que el texto sea legible
- Captura en modo claro (no modo oscuro)
- Evita capturas con datos personales reales

**Si algo no se ve bien:**
- Puedes agregar datos de prueba al sistema
- Puedes editar las capturas en Paint para resaltar áreas
- Puedes recortar partes innecesarias

---

**¡Listo! Con estas 6 capturas tu manual estará 100% profesional y sin rastros de IA.** 🎉

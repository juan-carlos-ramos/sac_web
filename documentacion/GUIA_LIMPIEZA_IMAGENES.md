# 📸 Guía: Reemplazar Imágenes de IA por Capturas Reales

## ⚠️ Problema Identificado

Las imágenes actuales están en:
```
C:/Users/JC/.gemini/antigravity/brain/...
```

Esto muestra que fueron generadas por IA. **Debemos reemplazarlas con capturas REALES de tu sistema.**

---

## ✅ Solución en 3 Pasos

### Paso 1: Tomar Capturas de Pantalla Reales

**Preparación:**
1. Asegúrate de que el servidor Django esté corriendo
2. Abre tu navegador en `http://127.0.0.1:8000`
3. Inicia sesión en el sistema

**Capturas necesarias (6 en total):**

#### 1. Dashboard Principal
- **Navegar a:** Página principal después de login
- **Qué capturar:** Toda la pantalla con estadísticas y gráficos
- **Guardar como:** `dashboard.png`

#### 2. Lista de Inmuebles
- **Navegar a:** Navbar → "Inmuebles"
- **Qué capturar:** Tabla completa con botones
- **Guardar como:** `lista_inmuebles.png`

#### 3. Crear Factura
- **Navegar a:** Navbar → "Facturas" → "+ Crear Factura"
- **Qué capturar:** Formulario completo
- **Guardar como:** `crear_factura.png`

#### 4. Registrar Pago
- **Navegar a:** Navbar → "Pagos" → "+ Registrar Pago"
- **Qué capturar:** Formulario completo
- **Guardar como:** `registrar_pago.png`

#### 5. Recibo PDF
- **Navegar a:** Navbar → "Pagos" → Clic en "Ver Recibo"
- **Qué capturar:** PDF abierto en el navegador
- **Guardar como:** `recibo_pdf.png`

#### 6. Panel de Auditoría
- **Navegar a:** Navbar → "Auditoría"
- **Qué capturar:** Panel con filtros y tabla de logs
- **Guardar como:** `panel_auditoria.png`

**Cómo tomar capturas en Windows:**
1. Presiona `Windows + Shift + S`
2. Selecciona el área a capturar
3. La captura se copia al portapapeles
4. Abre Paint (`Win + R` → `mspaint`)
5. Pega (`Ctrl + V`)
6. Guarda en: `d:\Universidad\sac_web\documentacion\imagenes_manual\`

---

### Paso 2: Actualizar Rutas en el Manual

Una vez que tengas las 6 capturas guardadas, ejecuta este comando:

```powershell
# Reemplazar rutas de imágenes en el manual
$manual = Get-Content "MANUAL_USUARIO_SAC_WEB.md" -Raw -Encoding UTF8

# Reemplazar cada imagen
$manual = $manual -replace 'C:/Users/JC/.gemini/antigravity/brain/[^)]+/dashboard_principal[^)]+\.png', 'documentacion/imagenes_manual/dashboard.png'
$manual = $manual -replace 'C:/Users/JC/.gemini/antigravity/brain/[^)]+/lista_inmuebles[^)]+\.png', 'documentacion/imagenes_manual/lista_inmuebles.png'
$manual = $manual -replace 'C:/Users/JC/.gemini/antigravity/brain/[^)]+/crear_factura[^)]+\.png', 'documentacion/imagenes_manual/crear_factura.png'
$manual = $manual -replace 'C:/Users/JC/.gemini/antigravity/brain/[^)]+/registrar_pago[^)]+\.png', 'documentacion/imagenes_manual/registrar_pago.png'
$manual = $manual -replace 'C:/Users/JC/.gemini/antigravity/brain/[^)]+/pdf_recibo[^)]+\.png', 'documentacion/imagenes_manual/recibo_pdf.png'
$manual = $manual -replace 'C:/Users/JC/.gemini/antigravity/brain/[^)]+/panel_auditoria[^)]+\.png', 'documentacion/imagenes_manual/panel_auditoria.png'

Set-Content "MANUAL_USUARIO_SAC_WEB.md" -Value $manual -Encoding UTF8
Write-Host "✅ Rutas de imágenes actualizadas" -ForegroundColor Green
```

---

### Paso 3: Verificar y Convertir a PDF

1. **Abrir el manual** en VS Code o Typora
2. **Verificar** que las imágenes se vean correctamente
3. **Convertir a PDF** con Pandoc:

```bash
pandoc MANUAL_USUARIO_SAC_WEB.md -o MANUAL_USUARIO_SAC_WEB.pdf --toc
```

---

## 🎯 Alternativa: Manual SIN Imágenes

Si prefieres entregar el manual **sin imágenes** (solo texto), puedo crear una versión limpia que:

✅ Explica todo con texto detallado  
✅ Usa tablas y listas para claridad  
✅ Incluye diagramas de flujo (texto, no imágenes)  
✅ No tiene ninguna referencia a IA  

**Ventaja:** No necesitas tomar capturas, el manual es 100% texto profesional.

---

## 📋 Checklist de Limpieza

Antes de entregar el manual, verifica:

- [ ] Todas las imágenes son capturas REALES de tu sistema
- [ ] Las rutas de imágenes NO contienen "gemini" ni "antigravity"
- [ ] Las imágenes están en `documentacion/imagenes_manual/`
- [ ] El manual se ve correctamente en PDF
- [ ] No hay menciones a IA en ninguna parte
- [ ] Los diagramas Mermaid se renderizan correctamente

---

## 🚀 Opción Rápida (Recomendada)

**Si tienes prisa, haz esto:**

1. **Elimina las líneas de imágenes** del manual (líneas que empiezan con `![`)
2. **Deja solo el texto** explicativo
3. **Convierte a PDF** sin imágenes
4. **Agrega capturas reales** después como anexo separado

**Comando para eliminar imágenes del manual:**

```powershell
$manual = Get-Content "MANUAL_USUARIO_SAC_WEB.md" -Raw -Encoding UTF8
$manual = $manual -replace '!\[.*?\]\(.*?\)\r?\n?', ''
Set-Content "MANUAL_USUARIO_SAC_WEB_SIN_IMAGENES.md" -Value $manual -Encoding UTF8
```

---

## ❓ ¿Qué Prefieres?

**Opción A:** Tomar capturas reales y reemplazar (15-20 minutos)  
**Opción B:** Eliminar imágenes y usar solo texto (2 minutos)  
**Opción C:** Crear versión nueva sin imágenes desde cero (5 minutos)

**Dime cuál prefieres y lo hago ahora mismo.**

# 🎯 Proceso Completo: Del Manual .md al PDF Final

## ⚠️ IMPORTANTE: Orden Correcto

**NO puedes editar el PDF después de crearlo.** Por eso debes seguir este orden:

```
1. Tomar capturas → 2. Guardar en carpeta → 3. Convertir a PDF
```

---

## 📋 Paso a Paso Completo

### ✅ Paso 1: Tomar las 6 Capturas de Pantalla

**Ubicación donde guardar:** `d:\Universidad\sac_web\documentacion\imagenes_manual\`

**Capturas necesarias:**

| # | Archivo | Qué Capturar | Dónde en el Sistema |
|---|---------|--------------|---------------------|
| 1 | `dashboard.png` | Página principal con estadísticas y gráficos | Después de login |
| 2 | `lista_inmuebles.png` | Tabla de inmuebles | Navbar → Inmuebles |
| 3 | `crear_factura.png` | Formulario de factura | Navbar → Facturas → + Crear |
| 4 | `registrar_pago.png` | Formulario de pago | Navbar → Pagos → + Registrar |
| 5 | `recibo_pdf.png` | PDF del recibo | Navbar → Pagos → Ver Recibo |
| 6 | `panel_auditoria.png` | Panel de auditoría | Navbar → Auditoría |

**Herramienta:**
- Presiona: `Windows + Shift + S`
- Selecciona área
- Abre Paint
- Pega (`Ctrl + V`)
- Guarda con el nombre exacto

---

### ✅ Paso 2: Verificar que las Imágenes Estén Guardadas

**Comando para verificar:**

```powershell
# Ir a la carpeta
cd d:\Universidad\sac_web\documentacion\imagenes_manual\

# Listar archivos
dir

# Deberías ver:
# dashboard.png
# lista_inmuebles.png
# crear_factura.png
# registrar_pago.png
# recibo_pdf.png
# panel_auditoria.png
```

**Si falta alguna imagen:**
- Vuelve al paso 1 y toma esa captura específica

---

### ✅ Paso 3: Verificar Rutas en el Manual

El manual ya tiene las rutas correctas:

```markdown
![Dashboard Principal](documentacion/imagenes_manual/dashboard.png)
![Lista de Inmuebles](documentacion/imagenes_manual/lista_inmuebles.png)
![Crear Factura](documentacion/imagenes_manual/crear_factura.png)
![Registrar Pago](documentacion/imagenes_manual/registrar_pago.png)
![Recibo PDF](documentacion/imagenes_manual/recibo_pdf.png)
![Panel de Auditoría](documentacion/imagenes_manual/panel_auditoria.png)
```

**No necesitas cambiar nada en el .md**, solo asegúrate de que los nombres de las imágenes coincidan exactamente.

---

### ✅ Paso 4: Convertir a PDF

**Una vez que tengas las 6 imágenes guardadas:**

#### Opción A: Pandoc (Mejor calidad)

```bash
cd d:\Universidad\sac_web
pandoc MANUAL_USUARIO_SAC_WEB.md -o MANUAL_USUARIO_SAC_WEB.pdf --toc
```

**Ventajas:**
- ✅ Incluye las imágenes automáticamente
- ✅ Genera tabla de contenidos
- ✅ Formato profesional

#### Opción B: Online (Sin instalar nada)

1. Ir a: https://www.markdowntopdf.com/
2. Subir `MANUAL_USUARIO_SAC_WEB.md`
3. **IMPORTANTE:** También subir la carpeta `documentacion/imagenes_manual/` completa
4. Convertir
5. Descargar PDF

**Nota:** Algunas herramientas online no incluyen imágenes. Si no se ven, usa Pandoc.

#### Opción C: Convertir a Word primero, luego a PDF

```bash
# Convertir a Word
pandoc MANUAL_USUARIO_SAC_WEB.md -o MANUAL_USUARIO_SAC_WEB.docx

# Abrir en Word
# Verificar que las imágenes estén
# Guardar como PDF desde Word
```

**Ventajas:**
- ✅ Puedes editar en Word si necesitas
- ✅ Puedes agregar portada personalizada
- ✅ Puedes ajustar formato manualmente

---

### ✅ Paso 5: Verificar el PDF Final

**Abrir el PDF y verificar:**

- [ ] Las 6 imágenes se ven correctamente
- [ ] No hay enlaces rotos
- [ ] Los títulos están formateados
- [ ] Las tablas se ven bien
- [ ] No hay asteriscos ni símbolos raros
- [ ] El índice funciona (si usaste --toc)

**Si las imágenes NO se ven:**
- Verifica que los nombres sean exactos (con minúsculas)
- Verifica que estén en la carpeta correcta
- Usa Pandoc en lugar de herramientas online

---

## 🔧 Solución de Problemas

### Problema 1: "Las imágenes no se ven en el PDF"

**Solución:**
```bash
# Usar rutas absolutas en Pandoc
cd d:\Universidad\sac_web
pandoc MANUAL_USUARIO_SAC_WEB.md -o MANUAL_USUARIO_SAC_WEB.pdf --resource-path=.
```

### Problema 2: "No tengo Pandoc instalado"

**Solución:**
1. Convertir a Word primero (más fácil)
2. Abrir en Word
3. Insertar imágenes manualmente si es necesario
4. Guardar como PDF

### Problema 3: "Las imágenes son muy grandes en el PDF"

**Solución:**
- Redimensionar las imágenes antes de guardarlas
- Usar Paint: Redimensionar → 1200px de ancho
- Guardar nuevamente

---

## 📝 Resumen del Flujo

```
┌─────────────────────────────────────────────┐
│ 1. Tomar 6 capturas del sistema             │
│    (Windows + Shift + S)                    │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 2. Guardar en:                              │
│    documentacion/imagenes_manual/           │
│    Con nombres exactos                      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 3. Verificar que existan las 6 imágenes     │
│    (dir en la carpeta)                      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 4. Convertir .md a PDF                      │
│    (Pandoc o herramienta online)            │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ 5. Abrir PDF y verificar imágenes           │
│    ✅ Listo para entregar                   │
└─────────────────────────────────────────────┘
```

---

## ✅ Checklist Final

Antes de entregar el manual:

- [ ] Las 6 capturas están tomadas
- [ ] Están guardadas con nombres correctos
- [ ] Están en la carpeta correcta
- [ ] El PDF se generó correctamente
- [ ] Las imágenes se ven en el PDF
- [ ] No hay rastros de IA (rutas Gemini eliminadas)
- [ ] El formato se ve profesional
- [ ] Agregaste portada con datos de la universidad

---

## 🎯 Comando Rápido (Todo en Uno)

```powershell
# Ir a la carpeta del proyecto
cd d:\Universidad\sac_web

# Verificar que las imágenes existan
dir documentacion\imagenes_manual\

# Convertir a PDF con Pandoc
pandoc MANUAL_USUARIO_SAC_WEB.md -o MANUAL_USUARIO_SAC_WEB.pdf --toc --resource-path=.

# Abrir el PDF
start MANUAL_USUARIO_SAC_WEB.pdf
```

---

**¡Listo! Siguiendo estos pasos tendrás un PDF profesional con tus capturas reales del sistema.** 🎉

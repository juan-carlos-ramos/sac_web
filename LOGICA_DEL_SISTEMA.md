# 🧠 Lógica del Sistema SAC WEB

**Documento Explicativo - Flujo Completo del Sistema**

---

## 📖 Índice

1. [Visión General](#visión-general)
2. [Los 3 Módulos Principales](#los-3-módulos-principales)
3. [Flujo Completo: De Gasto a Recibo](#flujo-completo)
4. [El Recibo Final: Qué Contiene y Por Qué](#el-recibo-final)
5. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🎯 Visión General

### ¿Qué problema resuelve SAC WEB?

**Problema:** Un condominio tiene gastos mensuales (limpieza, seguridad, mantenimiento) que deben ser divididos entre todos los apartamentos de forma justa.

**Solución:** SAC WEB automatiza:
1. El cálculo de cuánto debe pagar cada apartamento
2. El registro de quién ha pagado
3. La generación de recibos profesionales

---

### El Concepto Central: Alícuota

**Alícuota = Porcentaje de participación de cada apartamento en los gastos comunes**

**Ejemplo simple:**
```
Condominio con 20 apartamentos iguales:
- Cada uno tiene alícuota de 5% (0.05)
- Gastos del mes: Bs 10,000
- Cada apartamento paga: 10,000 × 0.05 = Bs 500
```

**¿Por qué alícuotas diferentes?**
- Un penthouse grande paga más que un apartamento pequeño
- Es justo porque usa más servicios comunes

---

## 🏗️ Los 3 Módulos Principales

### Módulo 1: INMUEBLES (Los Apartamentos)

**Propósito:** Registrar quién vive dónde y cuánto debe pagar de los gastos comunes.

**Datos que se guardan:**

| Campo | Para qué sirve | Ejemplo |
|-------|---------------|---------|
| **Número** | Identificar el apartamento | "1A", "2B", "PH-1" |
| **Propietario** | Saber a quién cobrar | "Juan Pérez" |
| **Email** | Enviar notificaciones | "juan@email.com" |
| **Teléfono** | Contactar al propietario | "0424-123-4567" |
| **Documento** | Identificación legal | "V-12345678" |
| **Alícuota** | **CLAVE:** Cuánto paga de los gastos | 0.0526 (5.26%) |
| **Notas** | Información adicional | "Cambió de dueño en Enero" |

**¿Por qué es importante la alícuota?**
Sin la alícuota, no podríamos calcular automáticamente cuánto debe pagar cada apartamento.

---

### Módulo 2: FACTURAS Y GASTOS (Los Gastos del Mes)

**Propósito:** Registrar en qué se gastó el dinero del condominio cada mes.

#### ¿Qué es una Factura?

Una **factura** es el período mensual que contiene todos los gastos.

**Estructura:**
```
Factura: Enero 2026
├── Gasto 1: Limpieza (Bs 600)
├── Gasto 2: Seguridad (Bs 1,200)
├── Gasto 3: Mantenimiento (Bs 800)
└── Gasto 4: Luz (Bs 400)
    TOTAL: Bs 3,000
```

#### Tipos de Gastos

**1. Gasto Común (Normal):**
- Todos los apartamentos lo pagan según su alícuota
- Ejemplo: Limpieza de áreas comunes

**2. Gasto No Común (Específico):**
- Solo un apartamento lo paga
- Ejemplo: Reparar tubería del apartamento 3B

**Datos de cada gasto:**

| Campo | Para qué sirve | Ejemplo |
|-------|---------------|---------|
| **Descripción** | Qué se pagó | "Limpieza de áreas comunes" |
| **Monto** | Cuánto costó | Bs 600.00 |
| **Categoría** | Tipo de gasto | Ordinario / Imprevisto / Extraordinario |
| **Proveedor** | A quién se le pagó | "Empresa Limpieza XYZ" |
| **Es gasto no común** | ¿Solo para un apto? | Sí / No |
| **Inmueble específico** | Si es no común, ¿cuál? | "3B" |

#### El Cálculo Automático

**Cuando creas una factura con gastos, el sistema calcula:**

```python
# Para cada apartamento:
Monto_a_pagar = (Total_gastos_comunes × Alícuota) + Gastos_no_comunes_propios

# Ejemplo para apartamento 1A (alícuota 5.26%):
Gastos_comunes = Bs 2,800
Gastos_no_comunes_1A = Bs 0
Monto_1A = (2,800 × 0.0526) + 0 = Bs 147.28

# Ejemplo para apartamento 3B (alícuota 5.26%):
Gastos_comunes = Bs 2,800
Gastos_no_comunes_3B = Bs 200 (reparación tubería)
Monto_3B = (2,800 × 0.0526) + 200 = Bs 347.28
```

**Este cálculo es automático e instantáneo.**

---

### Módulo 3: PAGOS Y RECIBOS (El Dinero que Entra)

**Propósito:** Registrar cuando un propietario paga y generar su comprobante (recibo).

#### ¿Qué es un Pago?

Un **pago** es cuando un propietario cancela (total o parcialmente) su deuda.

**Datos del pago:**

| Campo | Para qué sirve | Ejemplo |
|-------|---------------|---------|
| **Inmueble** | ¿Quién pagó? | "1A - Juan Pérez" |
| **Factura** | ¿Qué período está pagando? | "Enero 2026" |
| **Fecha** | ¿Cuándo pagó? | "15/01/2026" |
| **Monto** | ¿Cuánto pagó? | Bs 300.00 o $10 USD |
| **Moneda** | ¿En qué moneda? | BS / USD |
| **Tasa de cambio** | Si es USD, ¿a qué tasa? | 36.50 |
| **Método** | ¿Cómo pagó? | Transferencia / Efectivo / Pago Móvil / Zelle |
| **Comprobante** | Imagen del comprobante | (archivo adjunto) |

#### Cálculo de Conversión (Si paga en USD)

```python
# Si el pago es en dólares:
Monto_en_BS = Monto_USD × Tasa_de_cambio

# Ejemplo:
Pago_USD = $10
Tasa = 36.50
Monto_BS = 10 × 36.50 = Bs 365.00
```

#### Cálculo de Saldo

```python
# Después de registrar el pago:
Saldo_restante = Deuda_actual - Monto_pagado_en_BS

# Ejemplo:
Deuda_antes = Bs 450.00
Pago = Bs 300.00
Saldo_después = 450 - 300 = Bs 150.00
```

---

## 🔄 Flujo Completo: De Gasto a Recibo

### Paso 1: Configuración Inicial (Solo una vez)

```
1. Registrar todos los apartamentos del condominio
2. Asignar alícuota a cada uno
3. Verificar que la suma de alícuotas = 1.0 (100%)
```

---

### Paso 2: Inicio del Mes (Administrador)

**El día 1 del mes, el administrador:**

```
1. Va a "Facturas" → "+ Crear Factura"
2. Selecciona el período: "2026-02" (Febrero 2026)
3. Agrega cada gasto del mes:
   
   Gasto 1:
   - Descripción: "Limpieza de áreas comunes"
   - Monto: Bs 600
   - Categoría: Ordinario
   - Es gasto común: ✅ Sí
   
   Gasto 2:
   - Descripción: "Servicio de seguridad"
   - Monto: Bs 1,200
   - Categoría: Ordinario
   - Es gasto común: ✅ Sí
   
   Gasto 3:
   - Descripción: "Reparación tubería Apto 3B"
   - Monto: Bs 200
   - Categoría: Imprevisto
   - Es gasto común: ❌ No
   - Inmueble específico: 3B

4. Clic en "Crear Factura"
```

**El sistema automáticamente calcula:**
```
Total gastos comunes: Bs 1,800
Total gastos: Bs 2,000

Para cada apartamento:
- Apto 1A (alícuota 5.26%): debe Bs 94.68
- Apto 2B (alícuota 5.26%): debe Bs 94.68
- Apto 3B (alícuota 5.26%): debe Bs 94.68 + 200 = Bs 294.68
...y así con todos
```

---

### Paso 3: Durante el Mes (Propietarios Pagan)

**El propietario Juan Pérez (Apto 1A) realiza una transferencia bancaria.**

**El administrador registra el pago:**

```
1. Va a "Pagos" → "+ Registrar Pago"

2. Llena el formulario:
   - Inmueble: "1A - Juan Pérez"
   - Factura: "2026-02" (Febrero 2026)
   - Fecha de pago: "10/02/2026"
   - Monto pagado: Bs 94.68
   - Moneda: BS
   - Método de pago: "Transferencia Bancaria"
   - Comprobante: (sube imagen del comprobante)

3. El sistema muestra:
   - Deuda actual: Bs 94.68
   - Monto a pagar: Bs 94.68
   - Saldo restante: Bs 0.00

4. Clic en "Registrar Pago"
```

**El sistema automáticamente:**
1. Guarda el pago en la base de datos
2. Actualiza el saldo del apartamento
3. **Genera un recibo en PDF**
4. Crea una notificación
5. Registra la acción en auditoría

---

### Paso 4: Generación Automática del Recibo

**Cuando se registra el pago, el sistema:**

```python
# 1. Toma los datos del pago
pago_data = {
    'numero_recibo': '001-2026',
    'fecha': '10/02/2026',
    'inmueble': '1A',
    'propietario': 'Juan Pérez',
    'periodo': 'Febrero 2026'
}

# 2. Toma los datos de la factura
factura_data = {
    'descripcion': 'Cuota ordinaria Febrero 2026',
    'monto': 'Bs 94.68',
    'metodo_pago': 'Transferencia Bancaria'
}

# 3. Calcula totales
totales = {
    'total_pagado': 'Bs 94.68',
    'saldo_restante': 'Bs 0.00'
}

# 4. Genera el HTML del recibo usando una plantilla
html_recibo = generar_html(pago_data, factura_data, totales)

# 5. Convierte el HTML a PDF
pdf = WeasyPrint.HTML(html_recibo).write_pdf()

# 6. Muestra el PDF en el navegador o lo descarga
```

---

## 📄 El Recibo Final: Qué Contiene y Por Qué

### Estructura del Recibo PDF

```
┌─────────────────────────────────────────────┐
│  [LOGO]   CONDOMINIO SANTA ANA DE CORO     │
│           RECIBO DE PAGO                    │
├─────────────────────────────────────────────┤
│  No. Recibo: 001-2026                       │
│  Fecha: 10 de Febrero, 2026                 │
│  Propiedad: 1A                              │
│  Propietario: Juan Pérez                    │
│  Período de Pago: Febrero 2026              │
├─────────────────────────────────────────────┤
│  DETALLES DE FACTURA                        │
│  ┌──────────────────────────────────────┐  │
│  │ Descripción │ Monto │ Método │ Fecha │  │
│  ├──────────────────────────────────────┤  │
│  │ Cuota       │ Bs    │ Transf │ 10/02 │  │
│  │ Ordinaria   │ 94.68 │        │       │  │
│  └──────────────────────────────────────┘  │
├─────────────────────────────────────────────┤
│  Total Pagado:      Bs 94.68                │
│  Saldo Restante:    Bs 0.00                 │
├─────────────────────────────────────────────┤
│  Generado electrónicamente.                 │
│  Este documento es un recibo válido.        │
└─────────────────────────────────────────────┘
```

### ¿Por Qué Cada Dato en el Recibo?

| Dato | Por qué está | Para qué sirve |
|------|--------------|----------------|
| **Logo y nombre** | Identidad corporativa | Profesionalismo y reconocimiento |
| **No. Recibo** | Número único (001-2026) | Referencia y trazabilidad |
| **Fecha** | Cuándo se emitió | Registro temporal del pago |
| **Propiedad** | Qué apartamento | Identificar inequívocamente quién pagó |
| **Propietario** | Nombre del dueño | Validación de identidad |
| **Período** | Qué mes se está pagando | Saber a qué factura corresponde |
| **Descripción** | Qué se está pagando | Detalle del concepto |
| **Monto** | Cuánto se pagó | Valor del pago |
| **Método** | Cómo se pagó | Registro del medio de pago |
| **Fecha de pago** | Cuándo se recibió el dinero | Registro bancario |
| **Total Pagado** | Suma total | Claridad del monto |
| **Saldo Restante** | Cuánto falta por pagar | Información de deuda pendiente |
| **Nota legal** | Validez del documento | Respaldo legal |

---

## 🔗 Cómo se Relacionan los Datos

### Diagrama de Flujo de Datos

```
INMUEBLES (Base)
    │
    ├─ Alícuota (0.0526)
    │
    ▼
FACTURAS (Mensuales)
    │
    ├─ Gastos del mes
    ├─ Cálculo: Gasto × Alícuota = Deuda
    │
    ▼
PAGOS (Cuando pagan)
    │
    ├─ Monto pagado
    ├─ Cálculo: Deuda - Pago = Saldo
    │
    ▼
RECIBO (Automático)
    │
    └─ PDF con toda la información
```

---

## 💡 Ejemplo Completo Paso a Paso

### Caso Real: Apartamento 1A en Febrero 2026

**1. Datos del Inmueble (Base):**
```
Número: 1A
Propietario: Juan Pérez
Alícuota: 5.26% (0.0526)
```

**2. Se crea Factura de Febrero:**
```
Gastos comunes totales: Bs 1,800
- Limpieza: Bs 600
- Seguridad: Bs 1,200

Sistema calcula:
Deuda de 1A = 1,800 × 0.0526 = Bs 94.68
```

**3. Juan Pérez paga:**
```
Fecha: 10/02/2026
Monto: Bs 94.68
Método: Transferencia
```

**4. Sistema genera recibo:**
```
Recibo No. 001-2026
Propietario: Juan Pérez
Período: Febrero 2026
Monto pagado: Bs 94.68
Saldo: Bs 0.00
```

**5. Resultado:**
- Juan Pérez recibe su recibo en PDF
- El administrador confirma el pago
- El sistema actualiza los registros
- Auditoría registra la operación

---

## ❓ Preguntas Frecuentes

### ¿Por qué se necesita la alícuota?

**Sin alícuota:** Tendrías que calcular manualmente cuánto paga cada apartamento cada mes.

**Con alícuota:** El sistema calcula automáticamente. Si los gastos cambian, los montos se ajustan proporcionalmente.

---

### ¿Qué pasa si alguien paga parcialmente?

**Ejemplo:**
```
Deuda: Bs 94.68
Pago parcial: Bs 50.00
Saldo restante: Bs 44.68
```

El recibo mostrará:
- Total pagado: Bs 50.00
- Saldo restante: Bs 44.68

El propietario puede hacer otro pago después para completar.

---

### ¿Qué pasa si pagan en dólares?

**Ejemplo:**
```
Deuda: Bs 94.68
Pago: $3 USD
Tasa del día: 36.50
Conversión: 3 × 36.50 = Bs 109.50

Total pagado: Bs 109.50
Saldo: -Bs 14.82 (tiene crédito a favor)
```

El recibo muestra tanto los USD como los BS.

---

### ¿Por qué se guarda el método de pago?

**Razones:**
1. **Auditoría:** Saber cómo entró el dinero
2. **Conciliación bancaria:** Verificar movimientos
3. **Estadísticas:** Ver cuál método prefiere la gente
4. **Legal:** Respaldo en caso de disputas

---

### ¿El recibo se puede modificar después?

**No.** Una vez generado el recibo, es un documento legal.

**Si hay un error:** Se debe:
1. Anular el pago con el recibo erróneo
2. Crear un nuevo pago correcto
3. Generar un nuevo recibo

Esto mantiene la trazabilidad.

---

## 🎯 Resumen de la Lógica

**El sistema funciona en 3 pasos simples:**

1. **Entrada:** Registras gastos del mes
2. **Proceso:** Sistema calcula cuánto debe cada apartamento
3. **Salida:** Generas recibos cuando pagan

**La magia está en:**
- Cálculo automático usando alícuotas
- Generación automática de recibos profesionales
- Trazabilidad completa de todas las operaciones

**Todo está diseñado para:**
- ✅ Ahorrar tiempo
- ✅ Evitar errores de cálculo
- ✅ Mantener transparencia
- ✅ Generar documentos profesionales

---

**¡Y eso es toda la lógica del sistema SAC WEB!** 🎉

# 📐 DISEÑO Y ARQUITECTURA DEL SISTEMA

## Sistema de Administración de Condominios (SAC WEB)

**Documento de Arquitectura y Especificación Técnica**

---

## Índice

1. [Etapa de Inicio](#1-etapa-de-inicio)
2. [Etapa de Elaboración](#2-etapa-de-elaboración)
3. [Etapa de Construcción](#3-etapa-de-construcción)
4. [Etapa de Transferencia](#4-etapa-de-transferencia)

---

# 1. ETAPA DE INICIO

## 1.1 Visión del Proyecto

### Descripción General
SAC WEB es un sistema web diseñado para automatizar la gestión administrativa de condominios residenciales, específicamente orientado a las Residencias Santa Ana de Coro. El sistema permite el cálculo automático de gastos, registro de pagos y generación de recibos profesionales.

### Problema a Resolver
| Problema | Impacto | Solución Propuesta |
|----------|---------|-------------------|
| Cálculo manual de cuotas de condominio | Errores frecuentes, pérdida de tiempo | Automatización mediante alícuotas |
| Falta de control de pagos | Morosidad sin seguimiento | Sistema de registro y solvencia |
| Recibos manuales | Sin respaldo formal | Generación automática de PDFs |
| Sin trazabilidad | Imposible auditar | Sistema de auditoría completo |

### Objetivos del Sistema

**Objetivo General:**
Desarrollar un sistema web que automatice la gestión administrativa de condominios, incluyendo el cálculo de gastos, registro de pagos y generación de documentos.

**Objetivos Específicos:**
1. Gestionar el registro de inmuebles con sus respectivas alícuotas
2. Automatizar el cálculo de deudas mensuales por inmueble
3. Registrar pagos en múltiples monedas (Bolívares y Dólares)
4. Generar recibos de pago en formato PDF
5. Proporcionar reportes de solvencia y auditoría
6. Implementar sistema de roles y permisos

## 1.2 Alcance del Sistema

### Funcionalidades Incluidas
- ✅ Gestión completa de inmuebles (CRUD)
- ✅ Gestión de facturas y gastos mensuales
- ✅ Registro de pagos en BS y USD
- ✅ Generación de recibos en PDF
- ✅ Sistema de notificaciones
- ✅ Panel de auditoría
- ✅ Gestión de usuarios y roles
- ✅ Exportación a Excel
- ✅ Dashboard con estadísticas

### Funcionalidades Excluidas
- ❌ Aplicación móvil nativa
- ❌ Pasarela de pagos en línea
- ❌ Integración con sistemas bancarios
- ❌ Portal de autogestión para propietarios

## 1.3 Stakeholders (Interesados)

| Rol | Descripción | Interés Principal |
|-----|-------------|-------------------|
| Administrador del Condominio | Usuario principal del sistema | Gestionar pagos y generar recibos |
| Propietarios | Dueños de apartamentos | Recibir recibos de pago |
| Junta de Condominio | Órgano directivo | Reportes de solvencia |
| Equipo de Desarrollo | Desarrolladores | Implementar el sistema |
| Tutor Académico | Prof. Dilca Durán | Supervisar el proyecto |

## 1.4 Requisitos Iniciales

### Requisitos Funcionales
| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-01 | El sistema debe permitir registrar inmuebles | Alta |
| RF-02 | El sistema debe calcular automáticamente las deudas | Alta |
| RF-03 | El sistema debe registrar pagos en BS y USD | Alta |
| RF-04 | El sistema debe generar recibos en PDF | Alta |
| RF-05 | El sistema debe mostrar reportes de solvencia | Media |
| RF-06 | El sistema debe llevar auditoría de acciones | Media |
| RF-07 | El sistema debe enviar notificaciones | Baja |

### Requisitos No Funcionales
| ID | Requisito | Criterio |
|----|-----------|----------|
| RNF-01 | Usabilidad | Interfaz intuitiva, aprendizaje < 1 hora |
| RNF-02 | Rendimiento | Respuesta < 3 segundos |
| RNF-03 | Seguridad | Autenticación obligatoria |
| RNF-04 | Disponibilidad | 99% del tiempo operativo |
| RNF-05 | Portabilidad | Compatible con Chrome, Firefox, Edge |

---

# 2. ETAPA DE ELABORACIÓN

## 2.1 Arquitectura del Sistema

### Patrón de Arquitectura: MTV (Model-Template-View)
Django implementa una variación del patrón MVC conocida como MTV:

```
┌─────────────────────────────────────────────────────────────┐
│                        NAVEGADOR                             │
│                     (Cliente Web)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVIDOR WEB                             │
│                  (Django 6.0.1)                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   URLS.PY   │→ │  VIEWS.PY   │→ │     TEMPLATES       │ │
│  │  (Router)   │  │(Controlador)│  │  (Presentación)     │ │
│  └─────────────┘  └──────┬──────┘  └─────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│                   ┌─────────────┐                           │
│                   │  MODELS.PY  │                           │
│                   │   (Datos)   │                           │
│                   └──────┬──────┘                           │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │  SQLite3    │
                   │ (Base Datos)│
                   └─────────────┘
```

### Stack Tecnológico

| Capa | Tecnología | Versión |
|------|------------|---------|
| Backend | Django | 6.0.1 |
| Lenguaje | Python | 3.13 |
| Base de Datos | SQLite3 | - |
| Frontend | HTML/CSS/JS | - |
| PDFs (Principal) | Puppeteer | 22.15.0 |
| PDFs (Administrativo) | WeasyPrint | 67.0 |
| Excel | openpyxl | 3.1.2 |
| Runtime Node.js | Node.js | 22.x |

## 2.2 Modelo de Datos

### Diagrama Entidad-Relación

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   INMUEBLE   │       │   FACTURA    │       │    GASTO     │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │◄──────│ id (PK)      │
│ numero_apto  │       │ periodo      │       │ factura (FK) │
│ propietario  │       │ creada_en    │       │ descripcion  │
│ email        │       └──────────────┘       │ monto        │
│ telefono     │              │               │ categoria    │
│ documento    │              │               │ es_no_comun  │
│ alicuota     │              │               │ inmueble(FK) │
│ notas        │              │               └──────────────┘
│ fecha_ingreso│              │
└──────────────┘              │
       │                      │
       │                      │
       ▼                      ▼
┌──────────────────────────────────┐
│              PAGO                │
├──────────────────────────────────┤
│ id (PK)                          │
│ inmueble (FK) ───────────────────┼──► INMUEBLE
│ factura (FK) ────────────────────┼──► FACTURA
│ fecha_pago                       │
│ monto                            │
│ moneda (BS/USD)                  │
│ tasa_cambio                      │
│ metodo_pago                      │
│ referencia                       │
│ comprobante                      │
│ notas                            │
└──────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  PROVEEDOR   │       │ ACTIVIDAD    │       │ NOTIFICACION │
├──────────────┤       │    LOG       │       ├──────────────┤
│ id (PK)      │       ├──────────────┤       │ id (PK)      │
│ nombre       │       │ id (PK)      │       │ usuario (FK) │
│ rif          │       │ usuario (FK) │       │ actividad(FK)│
│ telefono     │       │ accion       │       │ leida        │
│ email        │       │ modelo       │       │ fecha        │
│ direccion    │       │ objeto_id    │       └──────────────┘
└──────────────┘       │ descripcion  │
                       │ fecha_hora   │
                       └──────────────┘

┌────────────────────┐
│  DATOS_CONDOMINIO  │
├────────────────────┤
│ id (PK)            │
│ nombre_condominio  │
│ rif_condominio     │
│ direccion          │
│ tasa_cambio_dolar  │
└────────────────────┘
```

### Descripción de Entidades

| Entidad | Descripción | Registros Estimados |
|---------|-------------|---------------------|
| Inmueble | Apartamentos del condominio | 20-100 |
| Factura | Períodos mensuales | 12/año |
| Gasto | Gastos por factura | 5-15/mes |
| Pago | Pagos realizados | Variable |
| Proveedor | Empresas de servicios | 10-30 |
| ActividadLog | Registro de auditoría | Ilimitado |
| Notificacion | Alertas al usuario | Variable |
| DatosCondominio | Configuración (único) | 1 |

## 2.3 Casos de Uso Principales

### CU-01: Registrar Pago
```
Actor: Administrador
Precondición: Usuario autenticado, factura existente
Flujo Principal:
  1. Administrador selecciona "Registrar Pago"
  2. Sistema muestra formulario
  3. Administrador selecciona inmueble y factura
  4. Sistema calcula deuda automáticamente
  5. Administrador ingresa monto y método de pago
  6. Sistema registra pago y genera recibo
Postcondición: Pago registrado, recibo disponible
```

### CU-02: Crear Factura Mensual
```
Actor: Administrador
Precondición: Usuario autenticado
Flujo Principal:
  1. Administrador selecciona "Crear Factura"
  2. Sistema solicita período (año-mes)
  3. Administrador agrega gastos del mes
  4. Sistema calcula deuda por inmueble automáticamente
Postcondición: Factura creada con gastos distribuidos
```

### CU-03: Generar Recibo PDF
```
Actor: Administrador
Precondición: Pago registrado
Flujo Principal:
  1. Administrador solicita generar recibo
  2. Sistema renderiza HTML del recibo
  3. Puppeteer convierte HTML a PDF
  4. Sistema entrega PDF para descarga
Postcondición: PDF generado y descargable
```

## 2.4 Prototipos de Interfaz

### Dashboard Principal
```
┌─────────────────────────────────────────────────────────────┐
│  SAC WEB  │ Inicio │ Inmuebles │ Facturas │ Pagos │ 👤 Admin│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Total    │  │ Total    │  │ Total    │  │ Deuda    │   │
│  │Inmuebles │  │ Facturas │  │Recaudado │  │Pendiente │   │
│  │    20    │  │    12    │  │Bs 50,000 │  │Bs 5,000  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Tasa BCV: Bs 375.08  [          ] [Actualizar]      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# 3. ETAPA DE CONSTRUCCIÓN

## 3.1 Estructura del Proyecto

```
sac_web/
├── manage.py                 # Script de gestión Django
├── requirements.txt          # Dependencias Python
├── package.json              # Dependencias Node.js
├── db.sqlite3                # Base de datos
│
├── sac_web/                  # Configuración del proyecto
│   ├── settings.py           # Configuración general
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # Servidor WSGI
│
├── nucleo/                   # Aplicación principal
│   ├── models.py             # Modelos de datos (695 líneas)
│   ├── views.py              # Vistas/Controladores (2,051 líneas)
│   ├── urls.py               # Rutas de la app (119 líneas)
│   ├── forms.py              # Formularios
│   ├── utils.py              # Funciones auxiliares
│   ├── admin.py              # Panel de administración
│   └── templates/            # Plantillas HTML
│       └── nucleo/
│           ├── base.html
│           ├── login.html
│           ├── dashboard.html
│           ├── inmuebles/
│           ├── facturas/
│           ├── pagos/
│           ├── recibos/
│           ├── usuarios/
│           └── auditoria/
│
├── static/                   # Archivos estáticos
│   ├── css/
│   │   └── estilos.css
│   ├── img/
│   └── js/
│
├── scripts/                  # Scripts auxiliares
│   ├── generate_pdf.js       # Generación PDF con Puppeteer
│   └── setup_roles.py        # Configuración de roles
│
└── documentacion/            # Documentación del proyecto
    ├── FINAL/
    └── LEGACY/
```

## 3.2 Módulos Implementados

### Módulo de Autenticación
- Login con credenciales
- Logout seguro
- Cambio de contraseña
- Recuperación por preguntas de seguridad
- Sesiones seguras

### Módulo de Inmuebles
- Listado con búsqueda
- Crear/Editar/Eliminar inmuebles
- Cálculo automático de alícuotas
- Validación de suma de alícuotas = 100%

### Módulo de Facturas y Gastos
- Crear facturas por período (YYYY-MM)
- Agregar gastos (comunes y no comunes)
- Categorías: Ordinario, Imprevisto, Extraordinario
- Cálculo automático de deuda por inmueble

### Módulo de Pagos
- Registro de pagos en BS y USD
- Conversión automática con tasa BCV
- Múltiples métodos: Transferencia, Pago Móvil, Efectivo, Zelle
- Adjuntar comprobantes

### Módulo de Recibos
- Visualización de recibos en HTML
- Generación de PDF con Puppeteer
- Diseño profesional con logo

### Módulo de Notificaciones
- Notificaciones en tiempo real
- Marcar como leídas
- Contador en navbar

### Módulo de Auditoría
- Registro de todas las acciones (CREAR, EDITAR, BORRAR, GENERAR)
- Filtros por fecha, usuario, acción, modelo
- Exportación a Excel

### Módulo de Usuarios
- Gestión de usuarios
- Roles: Administrador, Operador
- Permisos por módulo
- Activar/Desactivar usuarios

## 3.3 Generación de PDFs

### Motor Principal: Puppeteer
```javascript
// Flujo de generación:
1. Django genera token temporal de acceso
2. Construye URL del recibo con token
3. Ejecuta script Node.js con Puppeteer
4. Puppeteer abre Chrome headless
5. Navega a la URL del recibo
6. Genera PDF con estilos exactos
7. Django lee el PDF y lo retorna al usuario
```

### Motor Secundario: WeasyPrint
- Usado para PDFs administrativos simples
- Reportes de inmuebles
- Documentos internos

## 3.4 Fórmulas de Cálculo

### Cálculo de Deuda por Inmueble
```python
deuda = (gastos_comunes * alicuota) + gastos_no_comunes_propios

# Ejemplo:
gastos_comunes = Bs 3,000
alicuota = 0.05 (5%)
gasto_no_comun_propio = Bs 200

deuda = (3,000 * 0.05) + 200 = Bs 350
```

### Conversión de Moneda
```python
monto_bs = monto_usd * tasa_cambio

# Ejemplo:
monto_usd = $10
tasa_cambio = 375.08

monto_bs = 10 * 375.08 = Bs 3,750.80
```

---

# 4. ETAPA DE TRANSFERENCIA

## 4.1 Requisitos de Instalación

### Software Necesario
| Software | Versión Mínima | Propósito |
|----------|---------------|-----------|
| Python | 3.13+ | Lenguaje backend |
| Node.js | 22.x+ | Generación de PDFs |
| Git | 2.40+ | Control de versiones |
| Chrome/Chromium | Último | Motor de renderizado PDF |

### Dependencias Python
```
Django==6.0.1
weasyprint==67.0
openpyxl==3.1.2
pillow==12.1.0
```

### Dependencias Node.js
```
puppeteer==^22.15.0
```

## 4.2 Guía de Instalación

### Paso 1: Clonar el Proyecto
```bash
git clone [URL_REPOSITORIO]
cd sac_web
```

### Paso 2: Crear Entorno Virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Paso 3: Instalar Dependencias Python
```bash
pip install -r requirements.txt
```

### Paso 4: Instalar Dependencias Node.js
```bash
npm install
```

### Paso 5: Configurar Base de Datos
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Paso 6: Iniciar Servidor
```bash
python manage.py runserver
```

## 4.3 Credenciales Iniciales

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | (definida en instalación) | Superusuario |

## 4.4 Capacitación de Usuarios

### Plan de Capacitación
| Sesión | Duración | Contenido |
|--------|----------|-----------|
| 1 | 1 hora | Introducción y navegación |
| 2 | 1 hora | Gestión de inmuebles y facturas |
| 3 | 1 hora | Registro de pagos y generación de recibos |
| 4 | 30 min | Auditoría y reportes |

### Material de Soporte
- Manual de usuario (documento separado)
- Videos tutoriales (opcional)
- Soporte por correo electrónico

## 4.5 Mantenimiento

### Respaldo de Datos
```bash
# Respaldar base de datos
copy db.sqlite3 backup_YYYYMMDD.sqlite3

# Restaurar desde respaldo
copy backup_YYYYMMDD.sqlite3 db.sqlite3
```

### Actualización de Tasa BCV
- Acceder al Dashboard
- Ingresar nueva tasa en el campo correspondiente
- Clic en "Actualizar"

---

## Anexos

### A. Equipo de Desarrollo

| Nombre | Rol | Responsabilidad |
|--------|-----|-----------------|
| Juan Carlos Ramos | Líder de Proyecto | Arquitectura y Backend |
| Ricardo Salas | Metodología | Documentación y Procesos |
| Grecia Hernández | QA | Testing y Auditoría |
| Starlin Márquez | Backend | Base de Datos |
| Edxamir Suárez | Frontend | UI/UX |

**Tutor Académico:** Prof. Dilca Durán - UNEXCA

### B. Cronograma del Proyecto

| Fase | Duración | Actividades |
|------|----------|-------------|
| Inicio | 2 semanas | Levantamiento de requisitos |
| Elaboración | 4 semanas | Diseño y arquitectura |
| Construcción | 12 semanas | Desarrollo e implementación |
| Transferencia | 2 semanas | Pruebas y despliegue |

---

**Documento elaborado:** Febrero 2026  
**Versión:** 1.0  
**Sistema:** SAC WEB - Sistema de Administración de Condominios

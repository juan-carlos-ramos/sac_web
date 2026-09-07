# 🤖 MODO DE ATENCIÓN DE AGENTE: CONTEXTO DE PROYECTO
> [!IMPORTANT]
> **INSTRUCCIÓN PARA LA IA**: Estás interactuando con un proyecto de software existente.
> Lee atentamente este archivo `AI_CONTEXT.md` antes de responder.
> A partir de este momento, asumes el rol de **Socio Técnico y Desarrollador Experto** de este codebase específico.
> Adapta tus respuestas al stack detectado, la arquitectura detallada y el estilo de código del proyecto.
> No propongas dependencias innecesarias ni rompas la estructura existente.

# 📁 Ficha de Contexto del Proyecto: sac_web

## 🎯 Resumen Ejecutivo
Aplicación basada en sac-web-pdf-generator: PDF generator using Puppeteer for SAC WEB system

## ⚙️ Stack Tecnológico Detectado
- 🟢 **Node.js / JavaScript**
- 🐍 **Python (Django)**

## 🏛️ Patrón Arquitectónico Detectado
📦 **Estructura de Directorios Estándar / Scripting** (sin patrones complejos detectados)

## 🌳 Estructura de Carpetas Principal
```text
├── documentacion/
│   ├── FINAL/
│   │   └── 01_DISENO_DEL_SISTEMA.md (21.2 KB)
│   ├── imagenes_manual/
│   ├── GUIA_CAPTURAS.md (5.6 KB)
│   ├── GUIA_LIMPIEZA_IMAGENES.md (5.1 KB)
│   └── PROCESO_COMPLETO_PDF.md (7.6 KB)
├── media/
│   └── comprobantes/
│       ├── pago_movil_prueba.jpg (27.3 KB)
│       └── pago_movil_prueba_KFzu2be.jpg (27.3 KB)
├── nucleo/
│   ├── migrations/
│   │   ├── 0001_initial.py (4.1 KB)
│   │   ├── 0002_presupuesto_actividadlog_gasto_notificacion_pago_and_more.py (8.1 KB)
│   │   ├── 0003_tokenaccesotemporal.py (1.8 KB)
│   │   ├── 0004_inmueble_documento_identidad_inmueble_email_and_more.py (1.3 KB)
│   │   ├── 0005_perfilusuario.py (1.3 KB)
│   │   ├── 0006_datoscondominio_tasa_cambio_dolar.py
│   │   ├── 0007_add_fecha_ingreso_inmueble.py
│   │   ├── 0008_alter_inmueble_numero_apto.py
│   │   ├── 0009_alter_perfilusuario_respuesta_seguridad.py
│   │   └── __init__.py
│   ├── templates/
│   │   └── nucleo/
│   │       ├── auditoria/
│   │       │   ...
│   │       ├── facturas/
│   │       │   ...
│   │       ├── inmuebles/
│   │       │   ...
│   │       ├── pagos/
│   │       │   ...
│   │       ├── proveedores/
│   │       │   ...
│   │       ├── recibos/
│   │       │   ...
│   │       ├── recuperacion/
│   │       │   ...
│   │       ├── usuarios/
│   │       │   ...
│   │       ├── base.html (5.2 KB)
│   │       ├── base_login.html (3.8 KB)
│   │       ├── cambiar_password.html (1.5 KB)
│   │       ├── dashboard.html (9.7 KB)
│   │       ├── login.html (40.2 KB)
│   │       ├── notificaciones.html (2.7 KB)
│   │       └── pdf_reporte_inmuebles.html (4.3 KB)
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── nucleo_tags.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── api.py (3.6 KB)
│   │   ├── auditoria.py (5.7 KB)
│   │   ├── auth.py (6.6 KB)
│   │   ├── facturas.py (4.9 KB)
│   │   ├── inmuebles.py (5.5 KB)
│   │   ├── main.py (6.1 KB)
│   │   ├── pagos.py (1.7 KB)
│   │   ├── proveedores.py (3.5 KB)
│   │   ├── reportes.py (25.5 KB)
│   │   └── usuarios.py (6.4 KB)
│   ├── __init__.py
│   ├── admin.py (7.1 KB)
│   ├── apps.py
│   ├── context_processors.py
│   ├── forms.py (16.7 KB)
│   ├── models.py (20.4 KB)
│   ├── tests.py
│   ├── tests_qa_security.py (3.2 KB)
│   ├── urls.py (7.3 KB)
│   ├── utils.py (17.3 KB)
│   └── views.py.bak (76.7 KB)
├── sac_web/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py (9.0 KB)
│   ├── urls.py
│   └── wsgi.py
├── scripts/
│   ├── generate_pdf.js (2.7 KB)
│   └── setup_roles.py (3.3 KB)
├── static/
│   ├── css/
│   │   └── estilos.css (12.9 KB)
│   ├── img/
│   │   ├── condominio.jpg (84.2 KB)
│   │   ├── dilca.jpeg (22.4 KB)
│   │   ├── edxamir.jpeg (117.5 KB)
│   │   ├── grecia.jpeg (123.8 KB)
│   │   ├── juan carlos.jpeg (96.3 KB)
│   │   ├── ricardo.jpeg (66.2 KB)
│   │   ├── sac.png (17.8 KB)
│   │   ├── starlin.jpeg (73.8 KB)
│   │   └── unexca.png (20.2 KB)
│   └── js/
│       └── busqueda.js (1.6 KB)
├──  .env.example
├── CREDENCIALES.txt (1.0 KB)
├── GUIA_INSTALACION.txt (10.0 KB)
├── GUIA_MIGRACION_OTRA_PC.md (8.7 KB)
├── INFORME_AUDITORIA_QA.md (18.2 KB)
├── INICIAR_SERVIDOR.bat (1.5 KB)
├── Informe QA (18.2 KB)
├── LOGICA_DEL_SISTEMA.md (14.6 KB)
├── MANUAL_USUARIO_SAC_WEB.md (40.5 KB)
├── MANUAL_USUARIO_SAC_WEB_LIMPIO.md (40.1 KB)
├── README.md (3.3 KB)
├── dashboard_function_temp.py (3.6 KB)
├── db.sqlite3 (304.0 KB)
├── export_functions_temp.py (10.8 KB)
├── iniciar_servidor.sh
├── manage.py
├── package.json
├── requirements.txt
└── temp_dashboard.txt (3.5 KB)
```

## 🛠️ Estado Actual y Capacidades Detectadas
### 📌 Lo que ya funciona y está integrado:
- [x] Formularios interactivos para entrada, captura y validación de datos.
- [x] Capa de base de datos y persistencia (detectado archivo de base de datos o de configuración).
- [x] Funcionalidad integrada para exportación de datos en formatos XLSX/CSV/PDF.
- [x] Suite de pruebas automatizadas configurada.
- [x] Capa de autenticación de usuarios y seguridad.
- [x] Capa de servicios API y endpoints de backend estructurados.
- [x] Interfaz de inicio de sesión y validación de usuarios.

## ⚠️ Diagnóstico de Errores, Bugs y Seguridad (CRÍTICO)
Se han detectado automáticamente problemas que debes priorizar antes de continuar:

### ❌ Errores de Integridad y Sintaxis:
- ❌ **Sintaxis Rota en Python**: Archivo `export_functions_temp.py` en la línea 63 (Error: *unindent does not match any outer indentation level*)

### 🚀 Próximos pasos y tareas pendientes:
- [ ] No se detectaron marcas `TODO` pendientes. Listo para definir nuevas metas.

---
*Generado e inspeccionado de forma 100% autónoma por el **Project Context Agent** de Antigravity.*

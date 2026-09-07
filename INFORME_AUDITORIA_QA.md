# INFORME DE AUDITORÍA QA — SAC WEB
## Sistema de Administración de Condominio Web

---

| Campo | Detalle |
|-------|---------|
| **Proyecto** | SAC WEB — Sistema de Administración de Condominio |
| **Framework** | Django 6.0.1 / Python |
| **Base de Datos** | SQLite 3 |
| **Fecha de Auditoría** | Octubre 2026 |
| **Versión del Documento** | 1.0 |

---

## 📋 RESUMEN EJECUTIVO

El sistema SAC WEB es una aplicación Django para la administración de condominios que gestiona inmuebles, facturación, pagos, proveedores y auditoría. Tras un análisis exhaustivo del código fuente, se identificaron **27 hallazgos** distribuidos en 4 niveles de severidad:

| Severidad | Cantidad | Descripción |
|-----------|----------|-------------|
| 🔴 **CRÍTICO** | 6 | Vulnerabilidades que comprometen la seguridad del sistema |
| 🟠 **ALTO** | 8 | Problemas que afectan la integridad o robustez del sistema |
| 🟡 **MEDIO** | 8 | Deficiencias de calidad o buenas prácticas |
| 🔵 **BAJO** | 5 | Mejoras menores o cosméticas |

**Veredicto General:** El sistema es funcional para un entorno de desarrollo académico, pero **NO está listo para producción** sin resolver los hallazgos críticos y altos.

---

## 🔴 HALLAZGOS CRÍTICOS

### C-01: SECRET_KEY con valor por defecto en código fuente
**Archivo:** `sac_web/settings.py` (línea 24)
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'dummy-secret-key-for-dev')
```
**Riesgo:** Si no se configura la variable de entorno `SECRET_KEY`, el sistema utiliza la clave `dummy-secret-key-for-dev`, lo que permite a un atacante falsificar sesiones, crear tokens CSRF válidos y comprometer toda la criptografía del sistema.

**Recomendación:** Eliminar el valor por defecto y hacer que la aplicación falle si no está configurada:
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY debe estar configurada en las variables de entorno")
```

---

### C-02: DEBUG=True por defecto en producción
**Archivo:** `sac_web/settings.py` (línea 27)
```python
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
```
**Riesgo:** Si la variable `DEBUG` no se configura explícitamente, el sistema queda en modo debug, exponiendo stack traces completos, variables de entorno y configuración sensible.

**Recomendación:** Cambiar el valor por defecto a `False`:
```python
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
```

---

### C-03: Respuesta de seguridad almacenada en texto plano
**Archivo:** `nucleo/models.py` (línea 683-687)
```python
respuesta_seguridad = models.CharField(
    max_length=200,
    verbose_name='Respuesta',
    help_text='Respuesta para recuperar contraseña'
)
```
**Riesgo:** La respuesta de seguridad se almacena sin hash ni cifrado. Si un atacante obtiene acceso a la base de datos, puede leer directamente las respuestas y restablecer contraseñas de cualquier cuenta.

**Recomendación:** Almacenar un hash de la respuesta usando `make_password()` de Django:
```python
from django.contrib.auth.hashers import make_password, check_password
# Al guardar: respuesta_seguridad = make_password(respuesta.strip().lower())
# Al verificar: check_password(respuesta.strip().lower(), user.perfil.respuesta_seguridad)
```

---

### C-04: Recuperación de contraseña sin protección contra fuerza bruta
**Archivo:** `nucleo/views.py` (líneas 127-188)
**Riesgo:** El flujo de recuperación de contraseña (3 pasos) no tiene límite de intentos, rate limiting, CAPTCHA ni expiración de sesión. Un atacante puede intentar respuestas indefinidamente.

**Recomendación:**
- Implementar `django-ratelimit` o un decorator personalizado
- Limitar a 3-5 intentos por sesión
- Agregar CAPTCHA después de intentos fallidos
- Establecer expiración de la sesión de recuperación (ej: 10 minutos)

---

### C-05: Eliminación de registros sin verificación de método HTTP
**Archivos:** `nucleo/views.py` (eliminar_inmueble, eliminar_proveedor, eliminar_gasto, etc.)
**Riesgo:** Las vistas de eliminación no verifican que el método sea POST. Son vulnerables a ataques CSRF via GET (un enlace malicioso puede eliminar datos).

**Recomendación:** Proteger todas las vistas de eliminación verificando `request.method == 'POST'` y mostrando una página de confirmación para GET.

---

### C-06: Falta de validación de contraseña en recuperación
**Archivo:** `nucleo/views.py` (líneas 165-188)
```python
user.set_password(password_nueva)
user.save()
```
**Riesgo:** Al restablecer la contraseña mediante preguntas de seguridad, no se aplican los validadores de contraseña configurados en `AUTH_PASSWORD_VALIDATORS` (longitud mínima, similitud, contraseñas comunes, etc.).

**Recomendación:** Usar `validate_password` o `SetPasswordForm` de Django.

---

## 🟠 HALLAZGOS ALTOS

### A-01: Ausencia de headers de seguridad HTTP
**Archivo:** `sac_web/settings.py`
**Problema:** No están configurados: `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`.

**Recomendación:** Agregar configuración de seguridad para producción:
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
```

---

### A-02: Subida de archivos sin validación de tipo MIME en servidor
**Archivo:** `nucleo/models.py` (línea 382-388)
**Problema:** La validación `accept='image/*,application/pdf'` es solo del lado del cliente. No hay validación del tipo MIME real del archivo en el servidor.

**Recomendación:** Implementar validación del lado del servidor verificando el contenido real del archivo.

---

### A-03: Datos personales expuestos en el código fuente frontend
**Archivo:** `nucleo/templates/nucleo/login.html` (líneas 810-903)
**Problema:** Emails, teléfonos y perfiles de LinkedIn de los miembros del equipo codificados directamente en JavaScript, accesibles públicamente en el código fuente del navegador.

**Recomendación:** Extraer esta información a una fuente de datos o eliminar los datos de contacto del código frontend.

---

### A-04: ALLOWED_HOSTS vacío
**Archivo:** `sac_web/settings.py` (línea 31)
**Problema:** En producción, `ALLOWED_HOSTS` vacío con `DEBUG=False` rechazará todas las peticiones. Con `DEBUG=True`, permite cualquier host (vulnerabilidad de Host header poisoning).

**Recomendación:** Configurar explícitamente desde variable de entorno.

---

### A-05: Problema N+1 en consultas del dashboard
**Archivo:** `nucleo/views.py` (líneas 254-272)
**Problema:** Se ejecutan consultas N+1 anidadas. Para 20 inmuebles y 12 facturas, se generan ~240+ consultas a la base de datos en cada carga del dashboard.

**Recomendación:** Usar `select_related`/`prefetch_related` y optimizar con agregaciones a nivel de base de datos.

---

### A-06: vista_logout acepta solicitudes GET
**Archivo:** `nucleo/views.py` (líneas 74-87)
**Problema:** La vista de logout no verifica el método HTTP, permitiendo que un atacante cierre la sesión de un usuario mediante un enlace GET (CSRF de logout).

**Recomendación:** Proteger con verificación de método POST.

---

### A-07: actualizar_tasa_dolar sin control de permisos
**Archivo:** `nucleo/views.py` (líneas 310-347)
**Problema:** Cualquier usuario autenticado puede actualizar la tasa de cambio del dólar, afectando todos los cálculos financieros. No tiene `@permission_required`.

**Recomendación:** Agregar `@permission_required('nucleo.change_datoscondominio', raise_exception=True)`.

---

### A-08: es_administrador permite acceso a is_staff
**Archivo:** `nucleo/views.py` (líneas 17-18)
**Problema:** `is_staff` en Django significa acceso al panel de administración, no necesariamente que sea administrador del condominio. Puede otorgar permisos excesivos.

**Recomendación:** Usar un campo personalizado o grupos de permisos para distinguir roles.

---

## 🟡 HALLAZGOS MEDIOS

### M-01: Decorador @login_required duplicado
**Archivo:** `nucleo/views.py` (líneas 195-196)
```python
@login_required
@login_required  # ← Duplicado
def vista_dashboard(request):
```
**Recomendación:** Eliminar la línea duplicada.

---

### M-02: Clase Meta duplicada en CrearUsuarioForm
**Archivo:** `nucleo/forms.py` (líneas 355-358)
```python
class Meta:
    model = User
class Meta:  # ← Duplicado
    model = User
    fields = [...]
```
**Recomendación:** Eliminar la primera definición de `Meta`.

---

### M-03: Importación faltante de User en vistas de recuperación
**Archivo:** `nucleo/views.py` (líneas 132, 149, 177)
**Problema:** Se usa `User` sin importación explícita. Puede causar `NameError` en tiempo de ejecución.

**Recomendación:** Agregar `from django.contrib.auth.models import User` al inicio del archivo.

---

### M-04: Comentarios de código residual
**Archivo:** `nucleo/views.py` (líneas 14, 20-23)
**Problema:** Comentarios como `# ... (utils imports remain same)` que parecen ser de un proceso de refactorización.

**Recomendación:** Limpiar estos comentarios residuales.

---

### M-05: Sin paginación en listados
**Archivos:** `nucleo/views.py` (lista_inmuebles, lista_proveedores, lista_facturas, lista_pagos)
**Problema:** Ningún listado implementa paginación. Con muchos registros, las consultas y el renderizado se vuelven lentos.

**Recomendación:** Implementar `Paginator` de Django con 25 registros por página.

---

### M-06: Lógica de conversión de moneda duplicada
**Archivos:** `nucleo/views.py` (múltiples funciones), `nucleo/utils.py`
**Problema:** La lógica de conversión USD→BS se repite en al menos 8 lugares diferentes. Ya existe `convertir_a_bs()` en `utils.py` pero no se usa consistentemente.

**Recomendación:** Centralizar usando la función `convertir_a_bs()` existente.

---

### M-07: Sin tests unitarios
**Archivo:** `nucleo/tests.py`
**Problema:** El archivo de tests está vacío. No hay pruebas para la lógica de cálculo financiero, flujos de autenticación, permisos ni conversión de moneda.

**Recomendación:** Implementar tests mínimos para la lógica crítica: `calcular_deuda_inmueble()`, `validar_alicuotas()`, `convertir_a_bs()`, flujos de login/logout y permisos de vistas CRUD.

---

### M-08: DatosCondominio sin restricción de singleton
**Archivo:** `nucleo/models.py` (clase DatosCondominio)
**Problema:** El modelo está diseñado para tener un solo registro, pero no hay restricción que impida crear múltiples registros.

**Recomendación:** Agregar validación en el método `save()` del modelo.

---

## 🔵 HALLAZGOS BAJOS

### B-01: SQLite no es adecuado para producción
**Archivo:** `sac_web/settings.py` (líneas 107-112)
**Problema:** SQLite no soporta concurrencia de escritura, no es adecuado para entornos multiusuario en producción.
**Recomendación:** Migrar a PostgreSQL para producción.

---

### B-02: Imports dentro de funciones
**Archivo:** `nucleo/views.py` (múltiples líneas)
**Problema:** Múltiples imports dentro de funciones (datetime, json, openpyxl, etc.) que deberían estar al inicio del módulo según PEP 8.
**Recomendación:** Mover los imports al inicio del archivo, excepto los que evitan importación circular.

---

### B-03: Archivos de imagen con espacios en el nombre
**Directorio:** `static/img/` — El archivo `juan carlos.jpeg` contiene un espacio.
**Recomendación:** Renombrar a `juan_carlos.jpeg` o `juancarlos.jpeg`.

---

### B-04: Falta de logging configurado
**Archivo:** `sac_web/settings.py`
**Problema:** No hay configuración de logging. Los errores se pierden si `DEBUG=False`.
**Recomendación:** Agregar configuración de `LOGGING` en settings.py.

---

### B-05: Falta de archivo .env.example
**Problema:** Se usa `python-dotenv` pero no existe un `.env.example` que documente las variables necesarias.
**Recomendación:** Crear `.env.example` con las variables requeridas.

---

## 📊 EVALUACIÓN POR CATEGORÍA

### 🔒 Seguridad

| Aspecto | Estado | Nota |
|---------|--------|------|
| Autenticación | ✅ Correcto | Usa sistema de auth de Django |
| Autorización | ⚠️ Parcial | Permisos en CRUD, pero no en todas las vistas |
| CSRF | ✅ Correcto | Token CSRF en formularios |
| XSS | ✅ Correcto | Django auto-escapa en templates |
| Inyección SQL | ✅ Correcto | Usa ORM de Django |
| Headers de seguridad | ❌ Ausente | No configurados |
| Gestión de secretos | ❌ Deficiente | SECRET_KEY con default |
| Protección de archivos | ⚠️ Parcial | Validación solo en frontend |

**Puntuación: 5/10**

---

### 🏗️ Estructura y Arquitectura

| Aspecto | Estado | Nota |
|---------|--------|------|
| Patrón MVT | ✅ Correcto | Sigue el patrón Django |
| Separación de responsabilidades | ⚠️ Parcial | Lógica en utils, pero vistas muy pesadas |
| Organización de archivos | ✅ Correcto | Estructura estándar de Django |
| Reutilización de código | ❌ Deficiente | Mucha duplicación |
| Nomenclatura | ✅ Correcto | Nombres descriptivos en español |
| Migraciones | ✅ Correcto | 8 migraciones ordenadas |

**Puntuación: 6/10**

---

### ⚡ Rendimiento

| Aspecto | Estado | Nota |
|---------|--------|------|
| Consultas N+1 | ❌ Crítico | Dashboard con cientos de consultas |
| Paginación | ❌ Ausente | Sin paginación en ningún listado |
| Caché | ❌ Ausente | Sin configuración de caché |
| Índices de BD | ⚠️ Parcial | Solo los que Django crea por defecto |
| Select Related | ❌ Ausente | No se usa en consultas con FK |

**Puntuación: 3/10**

---

### 🧪 Calidad del Código

| Aspecto | Estado | Nota |
|---------|--------|------|
| Tests unitarios | ❌ Ausente | 0% de cobertura |
| Documentación | ✅ Bueno | Docstrings en funciones y modelos |
| PEP 8 | ⚠️ Parcial | Imports dentro de funciones, líneas largas |
| Código muerto | ⚠️ Presente | Decoradores duplicados, comentarios residuales |
| Manejo de errores | ⚠️ Parcial | Excepciones genéricas (`except Exception`) |

**Puntuación: 4/10**

---

### 📐 Modelado de Datos

| Aspecto | Estado | Nota |
|---------|--------|------|
| Normalización | ✅ Correcto | Modelos bien normalizados |
| Relaciones | ✅ Correcto | FK con on_delete apropiado |
| Restricciones | ⚠️ Parcial | unique=True en algunos campos, faltan validaciones |
| Integridad referencial | ✅ Correcto | CASCADE y SET_NULL apropiados |
| Auditoría | ✅ Bueno | Modelo ActividadLog implementado |

**Puntuación: 7/10**

---

## 🗺️ PLAN DE REMEDIACIÓN

### Fase 1 — Crítico (1-2 semanas)
| # | Hallazgo | Acción |
|---|----------|--------|
| 1 | C-01 | Eliminar SECRET_KEY por defecto |
| 2 | C-02 | Cambiar DEBUG default a False |
| 3 | C-03 | Hashear respuestas de seguridad |
| 4 | C-04 | Implementar rate limiting en recuperación |
| 5 | C-05 | Proteger eliminaciones con POST + confirmación |
| 6 | C-06 | Validar contraseñas en recuperación |

### Fase 2 — Alto (2-4 semanas)
| # | Hallazgo | Acción |
|---|----------|--------|
| 7 | A-01 | Configurar headers de seguridad |
| 8 | A-02 | Validar tipo MIME en subida de archivos |
| 9 | A-03 | Eliminar datos personales del código frontend |
| 10 | A-04 | Configurar ALLOWED_HOSTS |
| 11 | A-05 | Optimizar consultas N+1 del dashboard |
| 12 | A-06 | Proteger logout con POST |
| 13 | A-07 | Agregar permisos a actualizar_tasa_dolar |
| 14 | A-08 | Revisar lógica de es_administrador |

### Fase 3 — Medio (4-6 semanas)
| # | Hallazgo | Acción |
|---|----------|--------|
| 15 | M-01 | Eliminar decorador duplicado |
| 16 | M-02 | Corregir Meta duplicado en form |
| 17 | M-03 | Agregar import de User |
| 18 | M-04 | Limpiar comentarios residuales |
| 19 | M-05 | Implementar paginación |
| 20 | M-06 | Centralizar conversión de moneda |
| 21 | M-07 | Implementar tests unitarios |
| 22 | M-08 | Restringir singleton en DatosCondominio |

### Fase 4 — Bajo (6+ semanas)
| # | Hallazgo | Acción |
|---|----------|--------|
| 23 | B-01 | Evaluar migración a PostgreSQL |
| 24 | B-02 | Reorganizar imports |
| 25 | B-03 | Renombrar archivos con espacios |
| 26 | B-04 | Configurar logging |
| 27 | B-05 | Crear .env.example |

---

## ✅ PUNTOS FUERTES DEL PROYECTO

1. **Sistema de auditoría completo** — El modelo `ActividadLog` registra todas las acciones del sistema con usuario, fecha y descripción detallada.
2. **Sistema de notificaciones** — Los usuarios son notificados automáticamente de las actividades relevantes.
3. **Manejo de moneda dual** — Soporte para pagos en Bolívares y Dólares con tasa de cambio configurable.
4. **Cálculo financiero sólido** — La función `calcular_deuda_inmueble()` implementa correctamente el prorrateo por alícuotas, fondo de reserva (10%) y gastos no comunes.
5. **Validación de alícuotas** — El sistema verifica que las alícuotas sumen 100% y advierte al usuario.
6. **Buen uso de permisos Django** — Las vistas CRUD usan `@permission_required` para controlar acceso.
7. **Exportaciones a Excel** — Múltiples reportes exportables con formato profesional.
8. **Documentación interna** — Docstrings completos en modelos, vistas y utilidades.
9. **Token de acceso temporal** — Implementación segura para Puppeteer con expiración de 5 minutos.
10. **Estructura de templates organizada** — Separación lógica por módulos (inmuebles, facturas, pagos, etc.).

---

## 📈 PUNTUACIÓN GLOBAL

| Categoría | Puntuación | Peso | Ponderada |
|-----------|-----------|------|-----------|
| Seguridad | 5/10 | 30% | 1.50 |
| Estructura | 6/10 | 20% | 1.20 |
| Rendimiento | 3/10 | 20% | 0.60 |
| Calidad de Código | 4/10 | 15% | 0.60 |
| Modelado de Datos | 7/10 | 15% | 1.05 |
| **TOTAL** | | **100%** | **4.95/10** |

---

## 🏁 CONCLUSIÓN

El sistema SAC WEB demuestra un buen entendimiento del framework Django y una lógica de negocio sólida para la administración de condominios. Sin embargo, presenta deficiencias significativas en seguridad que deben resolverse antes de cualquier despliegue en producción.

Los 6 hallazgos críticos (SECRET_KEY expuesta, DEBUG activo por defecto, respuestas de seguridad en texto plano, ausencia de rate limiting, eliminaciones sin protección y validación de contraseñas) representan riesgos inaceptables en un entorno real.

Se recomienda seguir el plan de remediación en 4 fases, priorizando los hallazgos críticos y altos antes de considerar cualquier despliegue productivo.

---

*Informe generado automáticamente — Auditoría QA SAC WEB v1.0*
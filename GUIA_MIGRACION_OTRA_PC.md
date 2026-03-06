# 🚀 Guía: Migrar SAC WEB a Otra PC/Laptop

**Última actualización:** Enero 2026

---

## 📋 Resumen Ejecutivo

Esta guía te permite instalar y ejecutar el sistema SAC WEB en cualquier computadora Windows desde cero.

**Tiempo estimado:** 15-20 minutos

---

## 📦 PASO 1: Preparar el Proyecto para Mover

### En tu PC actual:

#### 1.1 Copiar el proyecto completo

**Opción A: A un pendrive**
```powershell
# Copiar todo el proyecto al pendrive (cambiar E: por tu letra de pendrive)
xcopy "d:\Universidad\sac_web" "E:\sac_web" /E /I /H /Y
```

**Opción B: A una carpeta comprimida**
```powershell
# Comprimir el proyecto en un ZIP
Compress-Archive -Path "d:\Universidad\sac_web" -DestinationPath "d:\Universidad\sac_web.zip"
```

**Importante:** La carpeta `venv` NO es necesaria copiarla (se crea nueva en la otra PC).

---

## 💻 PASO 2: Requisitos en la PC Nueva

### 2.1 Programas que DEBES descargar de la web

#### A) Python 3.11.7 (OBLIGATORIO)

**Link de descarga:**
https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe

**Instalación:**
1. Ejecutar el instalador
2. ✅ **IMPORTANTE:** Marcar "Add Python to PATH"
3. ✅ Marcar "Install for all users"
4. Clic en "Install Now"
5. Esperar a que termine
6. Reiniciar CMD/PowerShell

**Verificar instalación:**
```cmd
python --version
```
Debe mostrar: `Python 3.11.7`

---

#### B) GTK+ para Windows (Para que funcionen los PDFs)

**Link de descarga:**
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe

**Instalación:**
1. Ejecutar el instalador
2. Next → Next → Install
3. Esperar a que termine
4. Reiniciar CMD

**¿Por qué es necesario?**
WeasyPrint (la librería que genera PDFs) necesita GTK+ para funcionar en Windows.

---

#### C) Git (OPCIONAL - Solo si usas control de versiones)

**Link de descarga:**
https://git-scm.com/download/win

---

### 2.2 Requisitos por CMD (Librerías Python)

**Estos se instalan DESPUÉS de copiar el proyecto.**

---

## 📂 PASO 3: Copiar el Proyecto a la PC Nueva

### 3.1 Ubicación recomendada

Crea una carpeta en:
```
C:\Proyectos\sac_web
```

O en tu carpeta de usuario:
```
C:\Users\TuNombre\Documentos\sac_web
```

### 3.2 Copiar los archivos

**Si usaste pendrive:**
```cmd
xcopy "E:\sac_web" "C:\Proyectos\sac_web" /E /I /H /Y
```

**Si usaste ZIP:**
1. Copiar el ZIP a la PC nueva
2. Clic derecho → Extraer todo
3. Elegir destino: `C:\Proyectos\`

---

## ⚙️ PASO 4: Configurar el Entorno (Solo Primera Vez)

### 4.1 Abrir PowerShell o CMD

```cmd
# Ir a la carpeta del proyecto
cd C:\Proyectos\sac_web
```

### 4.2 Crear entorno virtual

```cmd
python -m venv venv
```

**Esto crea una carpeta `venv` con un Python aislado para tu proyecto.**

### 4.3 Activar entorno virtual

```cmd
venv\Scripts\activate.bat
```

**Sabrás que está activado cuando veas `(venv)` al inicio de la línea.**

### 4.4 Instalar dependencias (Librerías Python)

```cmd
pip install -r requirements.txt
```

**Esto instala automáticamente:**
- Django 5.1.4
- Pillow 11.0.0
- python-dateutil 2.9.0
- WeasyPrint 63.1
- openpyxl 3.1.5

**Tiempo estimado:** 2-3 minutos

---

## ✅ PASO 5: Verificar que Todo Funcione

### 5.1 Iniciar el servidor

```cmd
python manage.py runserver
```

**Deberías ver:**
```
Starting development server at http://127.0.0.1:8000/
```

### 5.2 Abrir en el navegador

1. Abrir Chrome, Firefox o Edge
2. Ir a: `http://127.0.0.1:8000`
3. Iniciar sesión con tus credenciales

### 5.3 Probar funcionalidades clave

- [ ] Dashboard se carga correctamente
- [ ] Puedes crear una factura
- [ ] Puedes registrar un pago
- [ ] **Generar un PDF de recibo** ← IMPORTANTE
- [ ] Exportar a Excel

---

## 🔧 Solución de Problemas Comunes

### Problema 1: "python: command not found"

**Causa:** Python no está instalado o no está en el PATH

**Solución:**
1. Reinstalar Python
2. ✅ Marcar "Add Python to PATH"
3. Reiniciar CMD

---

### Problema 2: "No module named 'django'"

**Causa:** No se instalaron las dependencias

**Solución:**
```cmd
# Asegurarse de que el entorno virtual esté activado
venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt
```

---

### Problema 3: Error al generar PDF (WinError 2)

**Causa:** GTK+ no está instalado

**Solución:**
1. Descargar GTK+ del link arriba
2. Instalar
3. Reiniciar CMD
4. Reiniciar el servidor

---

### Problema 4: "Port 8000 is already in use"

**Causa:** Ya hay un servidor corriendo en ese puerto

**Solución:**
```cmd
# Usar otro puerto
python manage.py runserver 8080

# Luego ir a: http://127.0.0.1:8080
```

---

### Problema 5: No se ven los estilos CSS

**Causa:** Falta recolectar archivos estáticos

**Solución:**
```cmd
python manage.py collectstatic --noinput
```

---

## 📋 Checklist de Migración Completa

### Antes de empezar:
- [ ] Descargar Python 3.11.7
- [ ] Descargar GTK+ Runtime
- [ ] Copiar proyecto a pendrive o ZIP

### En la PC nueva:
- [ ] Instalar Python (con "Add to PATH")
- [ ] Instalar GTK+
- [ ] Copiar proyecto a ubicación deseada
- [ ] Abrir CMD en la carpeta del proyecto
- [ ] Crear entorno virtual: `python -m venv venv`
- [ ] Activar entorno: `venv\Scripts\activate.bat`
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Iniciar servidor: `python manage.py runserver`
- [ ] Abrir navegador: `http://127.0.0.1:8000`
- [ ] Probar generar PDF

---

## 🚀 Script de Instalación Automatizada

Para facilitar el proceso, puedes crear un archivo `INSTALAR.bat` en la carpeta del proyecto:

```batch
@echo off
echo ========================================
echo   INSTALACION SAC WEB
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado
    echo Descarga Python de: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Crear entorno virtual
echo Creando entorno virtual...
python -m venv venv
echo [OK] Entorno virtual creado
echo.

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt
echo [OK] Dependencias instaladas
echo.

echo ========================================
echo   INSTALACION COMPLETADA
echo ========================================
echo.
echo Para iniciar el servidor ejecuta:
echo   1. venv\Scripts\activate.bat
echo   2. python manage.py runserver
echo.
pause
```

Guarda este código como `INSTALAR.bat` en la carpeta raíz del proyecto. Luego solo ejecutas este archivo en la PC nueva.

---

## 📝 Comandos Rápidos de Referencia

### Activar entorno virtual:
```cmd
venv\Scripts\activate.bat
```

### Desactivar entorno virtual:
```cmd
deactivate
```

### Iniciar servidor:
```cmd
python manage.py runserver
```

### Detener servidor:
```
Ctrl + C
```

### Crear migraciones (si cambias modelos):
```cmd
python manage.py makemigrations
python manage.py migrate
```

### Crear superusuario nuevo:
```cmd
python manage.py createsuperuser
```

---

## 🔗 Links de Descarga Completos

### Python:
- **Windows 64-bit:** https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe
- **Windows 32-bit:** https://www.python.org/ftp/python/3.11.7/python-3.11.7.exe

### GTK+ Runtime:
- **Installer:** https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe

### Git (Opcional):
- **Windows:** https://git-scm.com/download/win

---

## ⚠️ Notas Importantes

1. **NO copies la carpeta `venv` de una PC a otra.** Siempre crea un nuevo entorno virtual.

2. **La base de datos (`db.sqlite3`) SÍ se copia.** Contiene todos tus datos.

3. **Las carpetas `media` y `static` también se copian.** Contienen imágenes y estilos.

4. **Si cambias de PC frecuentemente,** considera usar Git para sincronizar el código.

5. **Para producción,** este método es solo para desarrollo. Para un servidor real se necesita configuración adicional.

---

## 🎯 Resumen en 5 Pasos

1. **Descargar:** Python + GTK+
2. **Copiar:** Proyecto a la PC nueva
3. **Instalar:** `python -m venv venv` → `pip install -r requirements.txt`
4. **Ejecutar:** `python manage.py runserver`
5. **Probar:** Abrir `http://127.0.0.1:8000`

---

**¡Listo! Tu sistema SAC WEB funcionará en la nueva PC.** 🎉

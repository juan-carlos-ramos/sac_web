"""
Vistas del sistema SAC WEB
Sistema de Administración de Condominio
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Sum, Count, Q
from decimal import Decimal

# ... (utils imports remain same)

# Helper para verificar si es superusuario (o admin)
def es_administrador(user):
    return user.is_superuser or user.is_staff

# -----------------------------------------------------------------------------
# AUTENTICACIÓN
# -----------------------------------------------------------------------------
# ... (vista_login, vista_logout remain same)

from nucleo.utils import (
    registrar_actividad,
    notificar_usuarios_sobre_actividad,
    marcar_notificacion_leida,
    obtener_notificaciones_no_leidas,
    calcular_deuda_inmueble,
    validar_alicuotas
)
from nucleo.models import (
    Inmueble, Proveedor, Factura, Gasto, Pago, 
    DatosCondominio, Notificacion
)
from nucleo.forms import (
    InmuebleForm, ProveedorForm, FacturaForm, GastoForm, 
    PagoForm, DatosCondominioForm
)


# =============================================================================
# AUTENTICACIÓN
# =============================================================================

def vista_login(request):
    """Vista de inicio de sesión."""
    if request.user.is_authenticated:
        return redirect('nucleo:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            registrar_actividad(
                usuario=user,
                accion='CREAR',
                modelo='Sesión',
                objeto_id=user.id,
                descripcion=f'Usuario {user.username} inició sesión'
            )
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('nucleo:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'nucleo/login.html')


@login_required
def vista_logout(request):
    """Vista de cierre de sesión."""
    username = request.user.username
    registrar_actividad(
        usuario=request.user,
        accion='BORRAR',
        modelo='Sesión',
        objeto_id=request.user.id,
        descripcion=f'Usuario {username} cerró sesión'
    )
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('nucleo:login')


@login_required
def vista_cambiar_password(request):
    """Vista para cambiar contraseña."""
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirmar = request.POST.get('password_confirmar')
        
        if not request.user.check_password(password_actual):
            messages.error(request, 'La contraseña actual es incorrecta')
            return render(request, 'nucleo/cambiar_password.html')
        
        if password_nueva != password_confirmar:
            messages.error(request, 'Las contraseñas nuevas no coinciden')
            return render(request, 'nucleo/cambiar_password.html')
        
        request.user.set_password(password_nueva)
        request.user.save()
        
        registrar_actividad(
            usuario=request.user,
            accion='EDITAR',
            modelo='Usuario',
            objeto_id=request.user.id,
            descripcion=f'Usuario {request.user.username} cambió su contraseña'
        )
        
        messages.success(request, 'Contraseña cambiada correctamente. Por favor inicia sesión nuevamente.')
        return redirect('nucleo:login')
    
    return render(request, 'nucleo/cambiar_password.html')


# =============================================================================
# RECUPERACIÓN DE CONTRASEÑA (OFFLINE / PREGUNTAS)
# =============================================================================

def vista_recuperar_password(request):
    """Paso 1: Solicitar nombre de usuario."""
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            if hasattr(user, 'perfil'):
                request.session['recup_user_id'] = user.id
                return redirect('nucleo:recuperar_pregunta')
            else:
                messages.error(request, 'Este usuario no tiene configurada una pregunta de seguridad. Contacte al administrador.')
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            
    return render(request, 'nucleo/recuperacion/paso1_usuario.html')

def vista_recuperar_pregunta(request):
    """Paso 2: Mostrar pregunta y validar respuesta."""
    user_id = request.session.get('recup_user_id')
    if not user_id:
        return redirect('nucleo:recuperar_password')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        # Comparación flexible (ignorando mayúsculas/minúsculas y espacios extra)
        if user.perfil.respuesta_seguridad.strip().lower() == respuesta.strip().lower():
            request.session['recup_validado'] = True
            return redirect('nucleo:recuperar_confirmar')
        else:
            messages.error(request, 'Respuesta incorrecta. Intente de nuevo.')
    
    return render(request, 'nucleo/recuperacion/paso2_pregunta.html', {
        'pregunta': user.perfil.pregunta_seguridad,
        'username': user.username
    })

def vista_recuperar_confirmar(request):
    """Paso 3: Establecer nueva contraseña."""
    if not request.session.get('recup_validado') or not request.session.get('recup_user_id'):
        return redirect('nucleo:recuperar_password')
    
    if request.method == 'POST':
        password_nueva = request.POST.get('password_nueva')
        password_confirmar = request.POST.get('password_confirmar')
        
        if password_nueva != password_confirmar:
            messages.error(request, 'Las contraseñas no coinciden.')
        else:
            user = User.objects.get(id=request.session['recup_user_id'])
            user.set_password(password_nueva)
            user.save()
            
            # Limpiar sesión de recuperación
            del request.session['recup_user_id']
            del request.session['recup_validado']
            
            messages.success(request, '¡Contraseña restablecida! Inicia sesión con tu nueva clave.')
            return redirect('nucleo:login')
            
    return render(request, 'nucleo/recuperacion/paso3_confirmar.html')


# =============================================================================
# DASHBOARD
# =============================================================================

@login_required
@login_required
def vista_dashboard(request):
    """Vista principal del sistema con estadísticas."""
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import json
    
    # Estadísticas básicas
    total_inmuebles = Inmueble.objects.count()
    total_facturas = Factura.objects.count()
    
    # Total recaudado (suma de todos los pagos convertidos a BS)
    pagos = Pago.objects.all()
    total_recaudado = Decimal('0.00')
    for pago in pagos:
        if pago.moneda == 'USD' and pago.tasa_cambio:
            total_recaudado += pago.monto_pagado * pago.tasa_cambio
        else:
            total_recaudado += pago.monto_pagado
    
    # Total de gastos
    total_gastos = Gasto.objects.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
    
    # Deuda pendiente
    deuda_pendiente = total_gastos - total_recaudado
    
    # Validar alícuotas
    validacion = validar_alicuotas()
    
    # =========================================================================
    # DATOS PARA GRÁFICOS
    # =========================================================================
    
    # Gráfico 1: Evolución de pagos (últimos 6 meses)
    hoy = datetime.now()
    meses_labels = []
    meses_montos = []
    
    for i in range(5, -1, -1):
        mes = hoy - relativedelta(months=i)
        mes_inicio = mes.replace(day=1)
        if i == 0:
            mes_fin = hoy
        else:
            mes_fin = (mes_inicio + relativedelta(months=1)) - relativedelta(days=1)
        
        # Sumar pagos del mes
        pagos_mes = Pago.objects.filter(fecha_pago__range=[mes_inicio, mes_fin])
        total_mes = Decimal('0.00')
        for pago in pagos_mes:
            if pago.moneda == 'USD' and pago.tasa_cambio:
                total_mes += pago.monto_pagado * pago.tasa_cambio
            else:
                total_mes += pago.monto_pagado
        
        meses_labels.append(mes.strftime('%b %Y'))
        meses_montos.append(float(total_mes))
    
    # Gráfico 2: Deuda por inmueble (top 10)
    inmuebles = Inmueble.objects.all()
    deudas_data = []
    for inmueble in inmuebles:
        # Calcular deuda total del inmueble sumando deudas de todas sus facturas
        deuda_total = Decimal('0.00')
        facturas = Factura.objects.all()
        for factura in facturas:
            resultado = calcular_deuda_inmueble(inmueble, factura)
            deuda_total += resultado['saldo']
        
        if deuda_total > 0:
            deudas_data.append({
                'nombre': str(inmueble),
                'deuda': float(deuda_total)
            })
    
    # Ordenar por deuda descendente y tomar top 10
    deudas_data = sorted(deudas_data, key=lambda x: x['deuda'], reverse=True)[:10]
    
    # Gráfico 3: Distribución de gastos por categoría
    gastos_por_categoria = Gasto.objects.values('categoria').annotate(
        total=Sum('monto')
    ).order_by('-total')
    
    gastos_data = [
        {
            'categoria': g.get('get_categoria_display', g['categoria']),
            'total': float(g['total'])
        }
        for g in gastos_por_categoria
    ]
    
    # Obtener tasa de cambio
    datos_condominio = DatosCondominio.objects.first()
    tasa_actual = datos_condominio.tasa_cambio_dolar if datos_condominio else Decimal('1.0000')

    context = {
        # Estadísticas básicas
        'total_inmuebles': total_inmuebles,
        'total_facturas': total_facturas,
        'total_recaudado': total_recaudado,
        'deuda_pendiente': deuda_pendiente,
        'validacion_alicuotas': validacion,
        'tasa_cambio_dolar': tasa_actual,
        
        # Datos para gráficos (convertidos a JSON para JavaScript)
        'chart_pagos_labels': json.dumps(meses_labels),
        'chart_pagos_data': json.dumps(meses_montos),
        'chart_deudas_data': json.dumps(deudas_data),
        'chart_gastos_data': json.dumps(gastos_data),
    }
    
    return render(request, 'nucleo/dashboard.html', context)


@login_required
def actualizar_tasa_dolar(request):
    """Actualiza la tasa de cambio del día."""
    if request.method == 'POST':
        nueva_tasa = request.POST.get('tasa_cambio')
        try:
            nueva_tasa = Decimal(nueva_tasa)
            if nueva_tasa <= 0:
                raise ValueError("La tasa debe ser mayor a 0")
                
            datos = DatosCondominio.objects.first()
            if not datos:
                # Si no existe, crearlo
                datos = DatosCondominio.objects.create(
                    nombre_condominio="Mi Condominio",
                    rif="J-00000000-0",
                    direccion="Dirección",
                    datos_bancarios="Banco",
                    contacto_admin="Admin",
                    tasa_cambio_dolar=nueva_tasa
                )
            else:
                datos.tasa_cambio_dolar = nueva_tasa
                datos.save()
            
            registrar_actividad(
                usuario=request.user,
                accion='EDITAR',
                modelo='DatosCondominio',
                objeto_id=datos.id,
                descripcion=f'Actualizó Tasa BCV a {nueva_tasa}'
            )
            messages.success(request, f'Tasa actualizada correctamente a: {nueva_tasa}')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar tasa: {str(e)}')
            
    return redirect('nucleo:dashboard')


# =============================================================================
# CRUD INMUEBLES
# =============================================================================

@login_required
def lista_inmuebles(request):
    """Lista todos los inmuebles con opción de búsqueda."""
    query = request.GET.get('q')
    inmuebles = Inmueble.objects.all().order_by('numero_apto')
    
    if query:
        inmuebles = inmuebles.filter(
            Q(numero_apto__icontains=query) |
            Q(propietario__icontains=query) |
            Q(documento_identidad__icontains=query)
        )

    validacion = validar_alicuotas()
    
    return render(request, 'nucleo/inmuebles/lista.html', {
        'inmuebles': inmuebles,
        'validacion': validacion,
        'query': query,  # Para mantener el texto en el input
    })


@login_required
@permission_required('nucleo.add_inmueble', raise_exception=True)
def crear_inmueble(request):
    """Crea un nuevo inmueble."""
    if request.method == 'POST':
        form = InmuebleForm(request.POST)
        if form.is_valid():
            inmueble = form.save()
            
            # Registrar actividad
            actividad = registrar_actividad(
                usuario=request.user,
                accion='CREAR',
                modelo='Inmueble',
                objeto_id=inmueble.id,
                descripcion=f'Creado inmueble {inmueble.numero_apto}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, f'Inmueble {inmueble.numero_apto} creado correctamente')
            return redirect('nucleo:lista_inmuebles')
    else:
        form = InmuebleForm()
    
    return render(request, 'nucleo/inmuebles/form.html', {
        'form': form,
        'titulo': 'Crear Inmueble',
    })


@login_required
@permission_required('nucleo.change_inmueble', raise_exception=True)
def editar_inmueble(request, inmueble_id):
    """Edita un inmueble existente."""
    inmueble = get_object_or_404(Inmueble, id=inmueble_id)
    
    if request.method == 'POST':
        form = InmuebleForm(request.POST, instance=inmueble)
        if form.is_valid():
            inmueble = form.save()
            
            # Registrar actividad
            actividad = registrar_actividad(
                usuario=request.user,
                accion='EDITAR',
                modelo='Inmueble',
                objeto_id=inmueble.id,
                descripcion=f'Editado inmueble {inmueble.numero_apto}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, f'Inmueble {inmueble.numero_apto} actualizado correctamente')
            return redirect('nucleo:lista_inmuebles')
    else:
        form = InmuebleForm(instance=inmueble)
    
    return render(request, 'nucleo/inmuebles/form.html', {
        'form': form,
        'titulo': f'Editar Inmueble {inmueble.numero_apto}',
        'inmueble': inmueble,
    })


@login_required
@permission_required('nucleo.delete_inmueble', raise_exception=True)
def eliminar_inmueble(request, inmueble_id):
    """Elimina un inmueble."""
    inmueble = get_object_or_404(Inmueble, id=inmueble_id)
    numero_apto = inmueble.numero_apto
    
    # Registrar actividad antes de eliminar
    actividad = registrar_actividad(
        usuario=request.user,
        accion='BORRAR',
        modelo='Inmueble',
        objeto_id=inmueble.id,
        descripcion=f'Eliminado inmueble {numero_apto}'
    )
    notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
    
    inmueble.delete()
    messages.success(request, f'Inmueble {numero_apto} eliminado correctamente')
    return redirect('nucleo:lista_inmuebles')


@login_required
@permission_required('nucleo.change_inmueble', raise_exception=True)
def calcular_alicuotas_automatico(request):
    """Calcula y aplica alícuotas igualitarias a todos los inmuebles."""
    if request.method == 'POST':
        inmuebles = Inmueble.objects.all()
        total_inmuebles = inmuebles.count()
        
        if total_inmuebles == 0:
            messages.warning(request, 'No hay inmuebles registrados para calcular alícuotas')
            return redirect('nucleo:lista_inmuebles')
        
        # Calcular alícuota igualitaria
        alicuota_base = Decimal('1') / Decimal(total_inmuebles)
        
        # Aplicar a todos los inmuebles
        for i, inmueble in enumerate(inmuebles):
            # El último inmueble recibe el residuo para que sume exactamente 1
            if i == total_inmuebles - 1:
                suma_anterior = alicuota_base * (total_inmuebles - 1)
                inmueble.alicuota = Decimal('1') - suma_anterior
            else:
                inmueble.alicuota = alicuota_base
            inmueble.save()
        
        # Registrar actividad
        actividad = registrar_actividad(
            usuario=request.user,
            accion='EDITAR',
            modelo='Inmueble',
            objeto_id=inmuebles.first().id,
            descripcion=f'Calculadas alícuotas automáticas para {total_inmuebles} inmuebles ({float(alicuota_base):.4f} cada uno)'
        )
        notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
        
        messages.success(request, f'Alícuotas calculadas automáticamente para {total_inmuebles} inmuebles')
        return redirect('nucleo:lista_inmuebles')
    
    return redirect('nucleo:lista_inmuebles')


# =============================================================================
# CRUD PROVEEDORES
# =============================================================================

@login_required
def lista_proveedores(request):
    """Lista todos los proveedores."""
    proveedores = Proveedor.objects.all().order_by('nombre')
    return render(request, 'nucleo/proveedores/lista.html', {
        'proveedores': proveedores
    })


@login_required
@permission_required('nucleo.add_proveedor', raise_exception=True)
def crear_proveedor(request):
    """Crea un nuevo proveedor."""
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            
            actividad = registrar_actividad(
                usuario=request.user,
                accion='CREAR',
                modelo='Proveedor',
                objeto_id=proveedor.id,
                descripcion=f'Creado proveedor {proveedor.nombre}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, f'Proveedor {proveedor.nombre} creado correctamente')
            return redirect('nucleo:lista_proveedores')
    else:
        form = ProveedorForm()
    
    return render(request, 'nucleo/proveedores/form.html', {
        'form': form,
        'titulo': 'Crear Proveedor',
    })


@login_required
@permission_required('nucleo.change_proveedor', raise_exception=True)
def editar_proveedor(request, proveedor_id):
    """Edita un proveedor existente."""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save()
            
            actividad = registrar_actividad(
                usuario=request.user,
                accion='EDITAR',
                modelo='Proveedor',
                objeto_id=proveedor.id,
                descripcion=f'Editado proveedor {proveedor.nombre}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, f'Proveedor {proveedor.nombre} actualizado correctamente')
            return redirect('nucleo:lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    
    return render(request, 'nucleo/proveedores/form.html', {
        'form': form,
        'titulo': f'Editar Proveedor {proveedor.nombre}',
        'proveedor': proveedor,
    })


@login_required
@permission_required('nucleo.delete_proveedor', raise_exception=True)
def eliminar_proveedor(request, proveedor_id):
    """Elimina un proveedor."""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    nombre = proveedor.nombre
    
    actividad = registrar_actividad(
        usuario=request.user,
        accion='BORRAR',
        modelo='Proveedor',
        objeto_id=proveedor.id,
        descripcion=f'Eliminado proveedor {nombre}'
    )
    notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
    
    proveedor.delete()
    messages.success(request, f'Proveedor {nombre} eliminado correctamente')
    return redirect('nucleo:lista_proveedores')


# =============================================================================
# CRUD FACTURAS Y GASTOS
# =============================================================================

@login_required
def lista_facturas(request):
    """Lista todas las facturas."""
    facturas = Factura.objects.all().order_by('-periodo')
    return render(request, 'nucleo/facturas/lista.html', {
        'facturas': facturas
    })


@login_required
@permission_required('nucleo.add_factura', raise_exception=True)
def crear_factura(request):
    """Crea una nueva factura."""
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            factura = form.save()
            
            actividad = registrar_actividad(
                usuario=request.user,
                accion='CREAR',
                modelo='Factura',
                objeto_id=factura.id,
                descripcion=f'Creada factura {factura.periodo}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, f'Factura {factura.periodo} creada correctamente')
            return redirect('nucleo:detalle_factura', factura_id=factura.id)
    else:
        form = FacturaForm()
    
    return render(request, 'nucleo/facturas/form.html', {
        'form': form,
        'titulo': 'Crear Factura',
    })


@login_required
def detalle_factura(request, factura_id):
    """Muestra el detalle de una factura con sus gastos."""
    from datetime import date
    
    factura = get_object_or_404(Factura, id=factura_id)
    gastos = Gasto.objects.filter(factura=factura)
    
    # Calcular totales
    total_gastos_comunes = gastos.filter(es_gasto_no_comun=False).aggregate(
        total=Sum('monto'))['total'] or Decimal('0.00')
    total_gastos_no_comunes = gastos.filter(es_gasto_no_comun=True).aggregate(
        total=Sum('monto'))['total'] or Decimal('0.00')
    total_general = total_gastos_comunes + total_gastos_no_comunes
    
    # Obtener inmuebles para la sección de recibos
    # Filtrar por fecha_ingreso: solo mostrar inmuebles que existían en el período de la factura
    # Formato esperado del periodo: "YYYY-MM" (ej: "2026-01")
    try:
        año, mes = factura.periodo.split('-')
        # Crear fecha del último día del mes de la factura
        if int(mes) == 12:
            fecha_limite = date(int(año) + 1, 1, 1)
        else:
            fecha_limite = date(int(año), int(mes) + 1, 1)
        
        # Filtrar inmuebles: sin fecha_ingreso (existían desde siempre) o con fecha_ingreso antes del fin del mes
        from django.db.models import Q
        inmuebles = Inmueble.objects.filter(
            Q(fecha_ingreso__isnull=True) | Q(fecha_ingreso__lt=fecha_limite)
        ).order_by('numero_apto')
    except (ValueError, AttributeError):
        # Si el formato del periodo no es válido, mostrar todos
        inmuebles = Inmueble.objects.all().order_by('numero_apto')
    
    return render(request, 'nucleo/facturas/detalle.html', {
        'factura': factura,
        'gastos': gastos,
        'total_gastos_comunes': total_gastos_comunes,
        'total_gastos_no_comunes': total_gastos_no_comunes,
        'total_general': total_general,
        'inmuebles': inmuebles,
    })


@login_required
def api_solvencia_factura(request, factura_id):
    """API que retorna la solvencia de todos los inmuebles para una factura (JSON)."""
    from datetime import date
    from django.db.models import Q
    
    factura = get_object_or_404(Factura, id=factura_id)
    
    # Obtener tasa del día
    datos_condominio = DatosCondominio.objects.first()
    tasa_actual = datos_condominio.tasa_cambio_dolar if datos_condominio else Decimal('1.0000')
    
    # Filtrar inmuebles por fecha_ingreso
    try:
        año, mes = factura.periodo.split('-')
        if int(mes) == 12:
            fecha_limite = date(int(año) + 1, 1, 1)
        else:
            fecha_limite = date(int(año), int(mes) + 1, 1)
        
        inmuebles = Inmueble.objects.filter(
            Q(fecha_ingreso__isnull=True) | Q(fecha_ingreso__lt=fecha_limite)
        ).order_by('numero_apto')
    except (ValueError, AttributeError):
        inmuebles = Inmueble.objects.all().order_by('numero_apto')
    
    data = []
    
    for inmueble in inmuebles:
        resultado = calcular_deuda_inmueble(inmueble, factura)
        deuda = resultado['saldo']
        deuda_usd = float(deuda / tasa_actual) if tasa_actual else 0
        
        data.append({
            'apto': inmueble.numero_apto,
            'propietario': inmueble.propietario or '-',
            'total_a_pagar': round(float(resultado['total_a_pagar']), 2),
            'total_pagado': round(float(resultado['total_pagado']), 2),
            'deuda': round(float(deuda), 2),
            'deuda_usd': round(deuda_usd, 2),
            'es_solvente': deuda <= 0
        })
    
    return JsonResponse({
        'success': True,
        'factura': factura.periodo,
        'tasa': float(tasa_actual),
        'inmuebles': data
    })


@login_required
def exportar_solvencia_excel(request, factura_id):
    """Exporta el reporte de solvencia de una factura a Excel."""
    factura = get_object_or_404(Factura, id=factura_id)
    
    # Obtener tasa del día
    datos_condominio = DatosCondominio.objects.first()
    tasa_actual = datos_condominio.tasa_cambio_dolar if datos_condominio else Decimal('1.0000')
    
    # Crear Excel
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Solvencia {factura.periodo}"
    
    # Estilos
    header_fill = PatternFill(start_color="2C5F8D", end_color="2C5F8D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    # Encabezados
    headers = ['Apto', 'Propietario', 'Total a Pagar (Bs)', 'Pagado (Bs)', 'Deuda (Bs)', 'Ref Deuda ($)', 'Estado']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        
    # Datos
    inmuebles = Inmueble.objects.all().order_by('numero_apto')
    
    for row, inmueble in enumerate(inmuebles, 2):
        resultado = calcular_deuda_inmueble(inmueble, factura)
        deuda = resultado['saldo']
        deuda_usd = deuda / tasa_actual if tasa_actual else 0
        estado = 'SOLVENTE' if deuda <= 0 else 'DEUDOR'
        
        ws.cell(row=row, column=1, value=inmueble.numero_apto)
        ws.cell(row=row, column=2, value=inmueble.propietario)
        ws.cell(row=row, column=3, value=round(float(resultado['total_a_pagar']), 2))
        ws.cell(row=row, column=4, value=round(float(resultado['total_pagado']), 2))
        ws.cell(row=row, column=5, value=round(float(deuda), 2))
        ws.cell(row=row, column=6, value=round(float(deuda_usd), 2))
        
        cell_estado = ws.cell(row=row, column=7, value=estado)
        
        # Color condicional para estado
        if estado == 'SOLVENTE':
            cell_estado.font = Font(color="008000", bold=True)
        else:
            cell_estado.font = Font(color="FF0000", bold=True)
            
    # Ajustar anchos
    ws.column_dimensions['A'].width = 10
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 15
    
    # Respuesta
    from django.http import HttpResponse
    from datetime import datetime
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'solvencia_{factura.periodo}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


@login_required
def exportar_recibos_factura(request, factura_id):
    """Exporta resumen de todos los recibos de una factura a Excel."""
    from datetime import date
    from django.db.models import Q
    
    factura = get_object_or_404(Factura, id=factura_id)
    
    # Obtener tasa del día
    datos_condominio = DatosCondominio.objects.first()
    tasa_actual = datos_condominio.tasa_cambio_dolar if datos_condominio else Decimal('1.0000')
    
    # Crear Excel
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Recibos {factura.periodo}"
    
    # Estilos
    header_fill = PatternFill(start_color="2C5F8D", end_color="2C5F8D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    # Encabezados
    headers = ['Apto', 'Propietario', 'Alícuota', 'G. Comunes (Bs)', 'G. No Comunes (Bs)', 
               'Total a Pagar (Bs)', 'Total Pagado (Bs)', 'Deuda (Bs)', 'Ref. Deuda ($)', 'Estado']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        
    # Filtrar inmuebles por fecha_ingreso
    try:
        año, mes = factura.periodo.split('-')
        if int(mes) == 12:
            fecha_limite = date(int(año) + 1, 1, 1)
        else:
            fecha_limite = date(int(año), int(mes) + 1, 1)
        
        inmuebles = Inmueble.objects.filter(
            Q(fecha_ingreso__isnull=True) | Q(fecha_ingreso__lt=fecha_limite)
        ).order_by('numero_apto')
    except (ValueError, AttributeError):
        inmuebles = Inmueble.objects.all().order_by('numero_apto')
    
    for row, inmueble in enumerate(inmuebles, 2):
        resultado = calcular_deuda_inmueble(inmueble, factura)
        deuda = resultado['saldo']
        deuda_usd = deuda / tasa_actual if tasa_actual else 0
        estado = 'SOLVENTE' if deuda <= 0 else 'DEUDOR'
        
        ws.cell(row=row, column=1, value=inmueble.numero_apto)
        ws.cell(row=row, column=2, value=inmueble.propietario or 'Sin asignar')
        ws.cell(row=row, column=3, value=round(float(inmueble.alicuota or 0), 4))
        ws.cell(row=row, column=4, value=round(float(resultado.get('gasto_comun', 0)), 2))
        ws.cell(row=row, column=5, value=round(float(resultado.get('gasto_no_comun', 0)), 2))
        ws.cell(row=row, column=6, value=round(float(resultado['total_a_pagar']), 2))
        ws.cell(row=row, column=7, value=round(float(resultado['total_pagado']), 2))
        ws.cell(row=row, column=8, value=round(float(deuda), 2))
        ws.cell(row=row, column=9, value=round(float(deuda_usd), 2))
        
        cell_estado = ws.cell(row=row, column=10, value=estado)
        if estado == 'SOLVENTE':
            cell_estado.font = Font(color="008000", bold=True)
        else:
            cell_estado.font = Font(color="FF0000", bold=True)
            
    # Ajustar anchos
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 18
    ws.column_dimensions['F'].width = 18
    ws.column_dimensions['G'].width = 18
    ws.column_dimensions['H'].width = 15
    ws.column_dimensions['I'].width = 15
    ws.column_dimensions['J'].width = 12
    
    # Respuesta
    from django.http import HttpResponse
    from datetime import datetime
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'recibos_{factura.periodo}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


@login_required
def exportar_recibos_todos(request):
    """Exporta resumen de todos los recibos de TODAS las facturas a Excel."""
    from datetime import datetime, date
    from django.db.models import Q
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    
    datos_condominio = DatosCondominio.objects.first()
    tasa_actual = datos_condominio.tasa_cambio_dolar if datos_condominio else Decimal('1.0000')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Recibos Todas Facturas"
    
    header_fill = PatternFill(start_color="2C5F8D", end_color="2C5F8D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    headers = ['Factura', 'Apto', 'Propietario', 'Alícuota', 'Total a Pagar (Bs)', 
               'Total Pagado (Bs)', 'Deuda (Bs)', 'Ref. Deuda ($)', 'Estado']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    row_num = 2
    for factura in Factura.objects.all().order_by('-periodo'):
        try:
            año, mes = factura.periodo.split('-')
            if int(mes) == 12:
                fecha_limite = date(int(año) + 1, 1, 1)
            else:
                fecha_limite = date(int(año), int(mes) + 1, 1)
            inmuebles = Inmueble.objects.filter(
                Q(fecha_ingreso__isnull=True) | Q(fecha_ingreso__lt=fecha_limite)
            ).order_by('numero_apto')
        except (ValueError, AttributeError):
            inmuebles = Inmueble.objects.all().order_by('numero_apto')
        
        for inmueble in inmuebles:
            resultado = calcular_deuda_inmueble(inmueble, factura)
            deuda = resultado['saldo']
            deuda_usd = deuda / tasa_actual if tasa_actual else 0
            estado = 'SOLVENTE' if deuda <= 0 else 'DEUDOR'
            
            ws.cell(row=row_num, column=1, value=factura.periodo)
            ws.cell(row=row_num, column=2, value=inmueble.numero_apto)
            ws.cell(row=row_num, column=3, value=inmueble.propietario or 'Sin asignar')
            ws.cell(row=row_num, column=4, value=round(float(inmueble.alicuota or 0), 4))
            ws.cell(row=row_num, column=5, value=round(float(resultado['total_a_pagar']), 2))
            ws.cell(row=row_num, column=6, value=round(float(resultado['total_pagado']), 2))
            ws.cell(row=row_num, column=7, value=round(float(deuda), 2))
            ws.cell(row=row_num, column=8, value=round(float(deuda_usd), 2))
            cell_estado = ws.cell(row=row_num, column=9, value=estado)
            cell_estado.font = Font(color="008000" if estado == 'SOLVENTE' else "FF0000", bold=True)
            row_num += 1
    
    for col, width in [('A', 12), ('B', 12), ('C', 25), ('D', 12), ('E', 18), ('F', 18), ('G', 15), ('H', 15), ('I', 12)]:
        ws.column_dimensions[col].width = width
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="recibos_todas_facturas_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    wb.save(response)
    return response


@login_required
def exportar_solvencia_todos(request):
    """Exporta la solvencia de TODAS las facturas a Excel."""
    from datetime import datetime, date
    from django.db.models import Q
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    
    datos_condominio = DatosCondominio.objects.first()
    tasa_actual = datos_condominio.tasa_cambio_dolar if datos_condominio else Decimal('1.0000')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Solvencia Todas Facturas"
    
    header_fill = PatternFill(start_color="2C5F8D", end_color="2C5F8D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    headers = ['Factura', 'Apto', 'Propietario', 'A Pagar (Bs)', 'Pagado (Bs)', 'Deuda (Bs)', 'Ref. $ (USD)', 'Estado']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    row_num = 2
    for factura in Factura.objects.all().order_by('-periodo'):
        try:
            año, mes = factura.periodo.split('-')
            if int(mes) == 12:
                fecha_limite = date(int(año) + 1, 1, 1)
            else:
                fecha_limite = date(int(año), int(mes) + 1, 1)
            inmuebles = Inmueble.objects.filter(
                Q(fecha_ingreso__isnull=True) | Q(fecha_ingreso__lt=fecha_limite)
            ).order_by('numero_apto')
        except (ValueError, AttributeError):
            inmuebles = Inmueble.objects.all().order_by('numero_apto')
        
        for inmueble in inmuebles:
            resultado = calcular_deuda_inmueble(inmueble, factura)
            deuda = resultado['saldo']
            deuda_usd = deuda / tasa_actual if tasa_actual else 0
            estado = 'SOLVENTE' if deuda <= 0 else 'DEUDOR'
            
            ws.cell(row=row_num, column=1, value=factura.periodo)
            ws.cell(row=row_num, column=2, value=inmueble.numero_apto)
            ws.cell(row=row_num, column=3, value=inmueble.propietario or 'Sin asignar')
            ws.cell(row=row_num, column=4, value=round(float(resultado['total_a_pagar']), 2))
            ws.cell(row=row_num, column=5, value=round(float(resultado['total_pagado']), 2))
            ws.cell(row=row_num, column=6, value=round(float(deuda), 2))
            ws.cell(row=row_num, column=7, value=round(float(deuda_usd), 2))
            cell_estado = ws.cell(row=row_num, column=8, value=estado)
            cell_estado.font = Font(color="008000" if estado == 'SOLVENTE' else "FF0000", bold=True)
            row_num += 1
    
    for col, width in [('A', 12), ('B', 12), ('C', 25), ('D', 15), ('E', 15), ('F', 15), ('G', 15), ('H', 12)]:
        ws.column_dimensions[col].width = width
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="solvencia_todas_facturas_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    wb.save(response)
    return response


@login_required
@permission_required('nucleo.add_gasto', raise_exception=True)
def agregar_gasto(request, factura_id):
    """Agrega un gasto a una factura."""
    factura = get_object_or_404(Factura, id=factura_id)
    
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.factura = factura
            gasto.save()
            
            actividad = registrar_actividad(
                usuario=request.user,
                accion='CREAR',
                modelo='Gasto',
                objeto_id=gasto.id,
                descripcion=f'Agregado gasto "{gasto.descripcion}" a factura {factura.periodo}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, 'Gasto agregado correctamente')
            return redirect('nucleo:detalle_factura', factura_id=factura.id)
    else:
        form = GastoForm()
    
    return render(request, 'nucleo/facturas/agregar_gasto.html', {
        'form': form,
        'factura': factura,
    })


@login_required
@permission_required('nucleo.delete_gasto', raise_exception=True)
def eliminar_gasto(request, gasto_id):
    """Elimina un gasto."""
    gasto = get_object_or_404(Gasto, id=gasto_id)
    factura_id = gasto.factura.id
    descripcion = gasto.descripcion
    
    actividad = registrar_actividad(
        usuario=request.user,
        accion='BORRAR',
        modelo='Gasto',
        objeto_id=gasto.id,
        descripcion=f'Eliminado gasto "{descripcion}"'
    )
    notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
    
    gasto.delete()
    messages.success(request, 'Gasto eliminado correctamente')
    return redirect('nucleo:detalle_factura', factura_id=factura_id)


# =============================================================================
# REGISTRO DE PAGOS
# =============================================================================

@login_required
def lista_pagos(request):
    """Lista todos los pagos."""
    pagos = Pago.objects.all().order_by('-fecha_pago')
    return render(request, 'nucleo/pagos/lista.html', {
        'pagos': pagos
    })


@login_required
@permission_required('nucleo.add_pago', raise_exception=True)
def registrar_pago(request):
    """Registra un nuevo pago."""
    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save()
            
            actividad = registrar_actividad(
                usuario=request.user,
                accion='CREAR',
                modelo='Pago',
                objeto_id=pago.id,
                descripcion=f'Registrado pago de {pago.inmueble} para factura {pago.factura.periodo}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, 'Pago registrado correctamente')
            return redirect('nucleo:lista_pagos')
    else:
        form = PagoForm()
    
    # Obtener tasa BCV para auto-fill (formateada a 2 decimales como en dashboard)
    datos_condominio = DatosCondominio.objects.first()
    if datos_condominio:
        tasa_bcv = f"{datos_condominio.tasa_cambio_dolar:.2f}"
    else:
        tasa_bcv = "0"
    
    return render(request, 'nucleo/pagos/form.html', {
        'form': form,
        'titulo': 'Registrar Pagos',
        'tasa_bcv': tasa_bcv,
    })


# =============================================================================
# API ENDPOINTS (AJAX)
# =============================================================================

@login_required
def api_obtener_deuda(request):
    """
    API que devuelve la deuda pendiente de un inmueble para una factura dada.
    Retorna JSON: {'deuda': 123.45, 'moneda': 'Bs'}
    """
    factura_id = request.GET.get('factura_id')
    inmueble_id = request.GET.get('inmueble_id')
    
    if not factura_id or not inmueble_id:
        return JsonResponse({'error': 'Parámetros faltantes'}, status=400)
    
    try:
        factura = Factura.objects.get(id=factura_id)
        inmueble = Inmueble.objects.get(id=inmueble_id)
        
        # Usar la utilidad existente para calcular deuda
        resultado = calcular_deuda_inmueble(inmueble, factura)
        
        # El resultado incluye 'saldo' (deuda pendiente)
        deuda = resultado.get('saldo', Decimal('0.00'))
        
        # Obtener tasa del día
        datos = DatosCondominio.objects.first()
        tasa = datos.tasa_cambio_dolar if datos else Decimal('1.0000')
        deuda_usd = deuda / tasa if tasa > 0 else 0
        
        return JsonResponse({
            'success': True,
            'deuda': float(deuda),
            'deuda_formateada': f"{deuda:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
            'deuda_usd': float(deuda_usd),
            'deuda_usd_formateada': f"{deuda_usd:,.2f}",
            'tasa': float(tasa)
        })
        
    except (Factura.DoesNotExist, Inmueble.DoesNotExist):
        return JsonResponse({'error': 'No encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# =============================================================================
# RECIBO POR INMUEBLE
# =============================================================================

def recibo_inmueble(request, factura_id, inmueble_id):
    """
    Muestra el recibo de un inmueble para una factura.
    
    Permite acceso de dos formas:
    1. Usuario autenticado (@login_required)
    2. Token temporal válido (para Puppeteer)
    """
    from nucleo.models import TokenAccesoTemporal
    
    # Verificar autenticación
    autenticado = False
    
    # Opción 1: Usuario logeado
    if request.user.is_authenticated:
        autenticado = True
    
    # Opción 2: Token válido
    token_param = request.GET.get('token')
    if token_param and not autenticado:
        try:
            token = TokenAccesoTemporal.objects.get(token=token_param)
            if token.es_valido() and token.vista_destino == 'recibo_inmueble':
                # Verificar que los parámetros coincidan
                if (token.parametros.get('factura_id') == factura_id and 
                    token.parametros.get('inmueble_id') == inmueble_id):
                    # Token válido: marcar como usado
                    token.usado = True
                    token.save()
                    autenticado = True
        except TokenAccesoTemporal.DoesNotExist:
            pass
    
    # Si no está autenticado de ninguna forma, redirigir a login
    if not autenticado:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
    
    # Usuario autenticado o token válido: mostrar recibo
    factura = get_object_or_404(Factura, id=factura_id)
    inmueble = get_object_or_404(Inmueble, id=inmueble_id)
    
    # Calcular deuda usando la función de utils
    resultado = calcular_deuda_inmueble(inmueble, factura)
    
    # Obtener datos del condominio
    datos_condominio = DatosCondominio.objects.first()
    tasa_cambio = datos_condominio.tasa_cambio_dolar if datos_condominio else None
    
    return render(request, 'nucleo/recibos/recibo.html', {
        'factura': factura,
        'inmueble': inmueble,
        'resultado': resultado,
        'datos_condominio': datos_condominio,
        'tasa_cambio': tasa_cambio,
    })


# =============================================================================
# NOTIFICACIONES
# =============================================================================

@login_required
def vista_notificaciones(request):
    """Vista para listar todas las notificaciones del usuario."""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-fecha_creacion')
    
    return render(request, 'nucleo/notificaciones.html', {
        'notificaciones': notificaciones
    })


@login_required
def marcar_notificacion_como_leida(request, notificacion_id):
    """Marca una notificación como leída."""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.leida = True
    notificacion.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notificación marcada como leída')
    return redirect('nucleo:notificaciones')


@login_required
def marcar_todas_notificaciones_leidas(request):
    """Marca todas las notificaciones del usuario como leídas."""
    Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).update(leida=True)
    
    messages.success(request, 'Todas las notificaciones marcadas como leídas')
    return redirect('nucleo:notificaciones')


# =============================================================================
# GENERACIÓN DE PDFs SIMPLES (WEASYPRINT)
# =============================================================================
# IMPORTANTE: WeasyPrint se usa SOLO para PDFs administrativos simples
# NO usar para recibos finales ni avisos de cobro del usuario

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import datetime


@login_required
def pdf_reporte_inmuebles(request):
    """
    Genera un PDF simple con el reporte de inmuebles.
    
    Este es un PDF ADMINISTRATIVO INTERNO.
    NO es para el usuario final.
    
    Características:
    - HTML simple sin recursos externos
    - Estilos inline
    - Generación rápida (< 5 segundos)
    """
    
    # Obtener datos
    inmuebles = Inmueble.objects.all().order_by('numero_apto')
    validacion = validar_alicuotas()
    
    # Preparar contexto
    context = {
        'inmuebles': inmuebles,
        'total_inmuebles': inmuebles.count(),
        'suma_alicuotas': validacion['suma_total'],
        'validacion_alicuotas': validacion['es_valida'],
        'inmuebles_con_alicuota': validacion['inmuebles_con_alicuota'],
        'inmuebles_sin_alicuota': len(validacion['inmuebles_sin_alicuota']),
        'fecha_generacion': datetime.now(),
    }
    
    # Renderizar HTML
    # IMPORTANTE: pasar request=request para que funcione correctamente
    html_string = render_to_string('nucleo/pdf_reporte_inmuebles.html', context, request=request)
    
    # Generar PDF con WeasyPrint
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()
    
    # Registrar actividad
    actividad = registrar_actividad(
        usuario=request.user,
        accion='GENERAR',
        modelo='PDF',
        objeto_id=0,
        descripcion='Generado PDF de reporte de inmuebles'
    )
    
    # Retornar PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_inmuebles.pdf"'
    
    return response


# =============================================================================
# GENERACIÓN DE PDFs CON PUPPETEER (MOTOR PRINCIPAL)
# =============================================================================
# Puppeteer es el motor PRINCIPAL para PDFs del usuario final
# Genera PDFs desde la vista HTML existente (sin duplicar código)

import subprocess
import os
import tempfile
import uuid


@login_required
def pdf_recibo_puppeteer(request, factura_id, inmueble_id):
    """
    Genera un PDF del recibo usando Puppeteer.
    
    Este es el MOTOR PRINCIPAL de PDFs para el usuario final.
    
    Flujo:
    1. Genera un token temporal de acceso
    2. Construye la URL del recibo con el token
    3. Ejecuta script Node.js con Puppeteer
    4. Puppeteer usa el token para acceder sin login
    5. Django lee el PDF y lo retorna
    """
    from nucleo.models import TokenAccesoTemporal
    
    # Validar que la factura e inmueble existen
    factura = get_object_or_404(Factura, id=factura_id)
    inmueble = get_object_or_404(Inmueble, id=inmueble_id)
    
    # PASO 1: Crear token temporal de acceso
    token = TokenAccesoTemporal.objects.create(
        usuario=request.user,
        vista_destino='recibo_inmueble',
        parametros={
            'factura_id': factura_id,
            'inmueble_id': inmueble_id
        }
    )
    
    # PASO 2: Construir URL con token
    recibo_path = f'/recibos/factura/{factura_id}/inmueble/{inmueble_id}/?token={token.token}'
    recibo_url = request.build_absolute_uri(recibo_path)
    
    # Crear archivo temporal para el PDF
    temp_dir = tempfile.gettempdir()
    pdf_filename = f'recibo_{inmueble.numero_apto}_{factura.periodo}_{uuid.uuid4().hex[:8]}.pdf'
    pdf_path = os.path.join(temp_dir, pdf_filename)
    
    # Ruta al script de Puppeteer
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'generate_pdf.js')
    
    try:
        # PASO 3: Ejecutar script de Puppeteer con URL que incluye token
        result = subprocess.run(
            ['node', script_path, recibo_url, pdf_path],
            capture_output=True,
            text=True,
            timeout=30  # 30 segundos máximo
        )
        
        # Verificar si hubo error
        if result.returncode != 0:
            messages.error(request, f'Error al generar PDF: {result.stderr}')
            return redirect('nucleo:recibo_inmueble', factura_id=factura_id, inmueble_id=inmueble_id)
        
        # PASO 4: Leer el PDF generado
        with open(pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        
        # Eliminar archivo temporal
        os.remove(pdf_path)
        
        # Registrar actividad
        actividad = registrar_actividad(
            usuario=request.user,
            accion='GENERAR',
            modelo='Recibo',
            objeto_id=inmueble.id,
            descripcion=f'Generado PDF de recibo para {inmueble.numero_apto} - {factura.periodo}'
        )
        
        # PASO 5: Retornar PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="recibo_{inmueble.numero_apto}_{factura.periodo}.pdf"'
        
        return response
        
    except subprocess.TimeoutExpired:
        messages.error(request, 'Timeout al generar PDF. Intente nuevamente.')
        return redirect('nucleo:recibo_inmueble', factura_id=factura_id, inmueble_id=inmueble_id)
        
    except Exception as e:
        messages.error(request, f'Error inesperado: {str(e)}')
        return redirect('nucleo:recibo_inmueble', factura_id=factura_id, inmueble_id=inmueble_id)



# =============================================================================
# VISTAS: Gestión de Usuarios
# =============================================================================

from django.contrib.auth.models import User
from nucleo.forms import CrearUsuarioForm, EditarUsuarioForm, CambiarPasswordUsuarioForm
from django.contrib.auth.decorators import user_passes_test


def es_administrador(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(es_administrador)
def lista_usuarios(request):
    """""""""Lista todos los usuarios del sistema."""""""""
    usuarios = User.objects.all().order_by('username')
    return render(request, 'nucleo/usuarios/lista.html', {
        'usuarios': usuarios,
    })


@login_required
@user_passes_test(es_administrador)
def crear_usuario(request):
    """""""""Crea un nuevo usuario."""""""""
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            
            # Registrar actividad
            actividad = registrar_actividad(
                usuario=request.user,
                accion='CREAR',
                modelo='User',
                objeto_id=usuario.id,
                descripcion=f'Creado usuario {usuario.username}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, f'Usuario {usuario.username} creado correctamente')
            return redirect('nucleo:lista_usuarios')
    else:
        form = CrearUsuarioForm()
    
    return render(request, 'nucleo/usuarios/form.html', {
        'form': form,
        'titulo': 'Crear Usuario',
        'es_creacion': True,
    })


@login_required
@user_passes_test(es_administrador)
def editar_usuario(request, user_id):
    """""""""Edita un usuario existente."""""""""
    usuario = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            # Validar que el usuario no se quite permisos de admin a sí mismo
            if usuario.id == request.user.id:
                if not form.cleaned_data.get('is_staff') and request.user.is_staff:
                    messages.error(request, 'No puedes quitarte permisos de administrador a ti mismo')
                    return redirect('nucleo:editar_usuario', user_id=user_id)
            
            usuario = form.save()
            
            # Registrar actividad
            actividad = registrar_actividad(
                usuario=request.user,
                accion='EDITAR',
                modelo='User',
                objeto_id=usuario.id,
                descripcion=f'Editado usuario {usuario.username}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, f'Usuario {usuario.username} actualizado correctamente')
            return redirect('nucleo:lista_usuarios')
    else:
        form = EditarUsuarioForm(instance=usuario)
    
    return render(request, 'nucleo/usuarios/form.html', {
        'form': form,
        'titulo': f'Editar Usuario: {usuario.username}',
        'es_creacion': False,
        'usuario_editado': usuario,
    })


@login_required
@user_passes_test(es_administrador)
def eliminar_usuario(request, user_id):
    """""""""Elimina un usuario."""""""""
    usuario = get_object_or_404(User, pk=user_id)
    
    # Validar que el usuario no se elimine a sí mismo
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes eliminarte a ti mismo')
        return redirect('nucleo:lista_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        
        # Registrar actividad antes de eliminar
        actividad = registrar_actividad(
            usuario=request.user,
            accion='ELIMINAR',
            modelo='User',
            objeto_id=usuario.id,
            descripcion=f'Eliminado usuario {username}'
        )
        notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
        
        usuario.delete()
        messages.success(request, f'Usuario {username} eliminado correctamente')
        return redirect('nucleo:lista_usuarios')
    
    return render(request, 'nucleo/usuarios/eliminar.html', {
        'usuario_a_eliminar': usuario,
    })


@login_required
@user_passes_test(es_administrador)
def cambiar_password_usuario(request, user_id):
    """""""""Cambia la contraseña de un usuario."""""""""
    usuario = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = CambiarPasswordUsuarioForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            
            # Registrar actividad
            actividad = registrar_actividad(
                usuario=request.user,
                accion='EDITAR',
                modelo='User',
                objeto_id=usuario.id,
                descripcion=f'Cambiada contraseña del usuario {usuario.username}'
            )
            notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
            
            messages.success(request, f'Contraseña de {usuario.username} cambiada correctamente')
            return redirect('nucleo:lista_usuarios')
    else:
        form = CambiarPasswordUsuarioForm(usuario)
    
    return render(request, 'nucleo/usuarios/cambiar_password.html', {
        'form': form,
        'usuario_editado': usuario,
    })


@login_required
@user_passes_test(es_administrador)
def toggle_usuario_activo(request, user_id):
    """""""""Activa o desactiva un usuario."""""""""
    usuario = get_object_or_404(User, pk=user_id)
    
    # Validar que el usuario no se desactive a sí mismo
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes desactivarte a ti mismo')
        return redirect('nucleo:lista_usuarios')
    
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    estado = 'activado' if usuario.is_active else 'desactivado'
    
    # Registrar actividad
    actividad = registrar_actividad(
        usuario=request.user,
        accion='EDITAR',
        modelo='User',
        objeto_id=usuario.id,
        descripcion=f'Usuario {usuario.username} {estado}'
    )
    notificar_usuarios_sobre_actividad(actividad, excluir_usuario=request.user)
    
    messages.success(request, f'Usuario {usuario.username} {estado} correctamente')
    return redirect('nucleo:lista_usuarios')



# =============================================================================
# VISTAS: Sistema de Auditoría
# =============================================================================

from django.db.models import Q
from django.core.paginator import Paginator
from nucleo.models import ActividadLog
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from django.http import HttpResponse
from datetime import datetime


@login_required
@user_passes_test(es_administrador)
def vista_auditoria(request):
    """Panel de auditoría global con filtros."""
    # Obtener todos los logs
    logs = ActividadLog.objects.select_related('usuario').all()
    
    # Filtros
    usuario_id = request.GET.get('usuario')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    modelo = request.GET.get('modelo')
    accion = request.GET.get('accion')
    
    # Aplicar filtros
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)
    
    if fecha_desde:
        logs = logs.filter(fecha_hora__gte=fecha_desde)
    
    if fecha_hasta:
        logs = logs.filter(fecha_hora__lte=fecha_hasta)
    
    if modelo:
        logs = logs.filter(modelo=modelo)
    
    if accion:
        logs = logs.filter(accion=accion)
    
    # Paginación
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)
    
    # Opciones para filtros
    usuarios = User.objects.filter(is_active=True).order_by('username')
    modelos = ActividadLog.objects.values_list('modelo', flat=True).distinct().order_by('modelo')
    acciones = ActividadLog.ACCION_CHOICES
    
    return render(request, 'nucleo/auditoria/panel.html', {
        'logs': logs_page,
        'usuarios': usuarios,
        'modelos': modelos,
        'acciones': acciones,
        'filtros': {
            'usuario': usuario_id,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'modelo': modelo,
            'accion': accion,
        }
    })


@login_required
@user_passes_test(es_administrador)
def exportar_auditoria_excel(request):
    """Exporta los logs de auditoría a Excel."""
    # Aplicar los mismos filtros que en vista_auditoria
    logs = ActividadLog.objects.select_related('usuario').all()
    
    usuario_id = request.GET.get('usuario')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    modelo = request.GET.get('modelo')
    accion = request.GET.get('accion')
    
    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)
    if fecha_desde:
        logs = logs.filter(fecha_hora__gte=fecha_desde)
    if fecha_hasta:
        logs = logs.filter(fecha_hora__lte=fecha_hasta)
    if modelo:
        logs = logs.filter(modelo=modelo)
    if accion:
        logs = logs.filter(accion=accion)
    
    # Crear Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Auditoría"
    
    # Estilos
    header_fill = PatternFill(start_color="2C5F8D", end_color="2C5F8D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    # Encabezados
    headers = ['Fecha/Hora', 'Usuario', 'Acción', 'Modelo', 'Objeto ID', 'Descripción']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    # Datos
    for row, log in enumerate(logs, 2):
        ws.cell(row=row, column=1, value=log.fecha_hora.strftime('%d/%m/%Y %H:%M:%S'))
        ws.cell(row=row, column=2, value=log.usuario.username)
        ws.cell(row=row, column=3, value=log.get_accion_display())
        ws.cell(row=row, column=4, value=log.modelo)
        ws.cell(row=row, column=5, value=log.objeto_id)
        ws.cell(row=row, column=6, value=log.descripcion)
    
    # Ajustar anchos de columna
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 50
    
    # Preparar respuesta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=auditoria_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    wb.save(response)
    return response


@login_required
def historial_inmueble(request, inmueble_id):
    """Muestra el historial de cambios de un inmueble."""
    inmueble = get_object_or_404(Inmueble, pk=inmueble_id)
    logs = ActividadLog.objects.filter(
        modelo='Inmueble',
        objeto_id=inmueble_id
    ).select_related('usuario').order_by('-fecha_hora')
    
    return render(request, 'nucleo/auditoria/historial.html', {
        'objeto': inmueble,
        'tipo': 'Inmueble',
        'logs': logs,
    })


@login_required
def historial_factura(request, factura_id):
    """Muestra el historial de cambios de una factura."""
    factura = get_object_or_404(Factura, pk=factura_id)
    logs = ActividadLog.objects.filter(
        modelo='Factura',
        objeto_id=factura_id
    ).select_related('usuario').order_by('-fecha_hora')
    
    return render(request, 'nucleo/auditoria/historial.html', {
        'objeto': factura,
        'tipo': 'Factura',
        'logs': logs,
    })


@login_required
def historial_pago(request, pago_id):
    """Muestra el historial de cambios de un pago."""
    pago = get_object_or_404(Pago, pk=pago_id)
    logs = ActividadLog.objects.filter(
        modelo='Pago',
        objeto_id=pago_id
    ).select_related('usuario').order_by('-fecha_hora')
    
    return render(request, 'nucleo/auditoria/historial.html', {
        'objeto': pago,
        'tipo': 'Pago',
        'logs': logs,
    })





# =============================================================================
# EXPORTACIONES A EXCEL
# =============================================================================

@login_required
def exportar_inmuebles_excel(request):
    """Exporta la lista de inmuebles a Excel."""
    from datetime import datetime
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inmuebles"
    
    # Estilos
    header_fill = PatternFill(start_color="2C5F8D", end_color="2C5F8D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    center = Alignment(horizontal='center', vertical='center')
    
    # Encabezados
    headers = ['Número', 'Propietario', 'Documento', 'Email', 'Teléfono', 'Alícuota (%)', 'Notas']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center
    
    # Datos
    inmuebles = Inmueble.objects.all().order_by('numero_apto')
    for row, inmueble in enumerate(inmuebles, 2):
        ws.cell(row=row, column=1, value=inmueble.numero_apto)
        ws.cell(row=row, column=2, value=inmueble.propietario or '')
        ws.cell(row=row, column=3, value=inmueble.documento_identidad or '')
        ws.cell(row=row, column=4, value=inmueble.email or '')
        ws.cell(row=row, column=5, value=inmueble.telefono or '')
        ws.cell(row=row, column=6, value=round(float(inmueble.alicuota), 4) * 100)
        ws.cell(row=row, column=7, value=inmueble.notas or '')
    
    # Ajustar anchos
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 30
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 40
    
    # Respuesta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=inmuebles_{datetime.now().strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


@login_required
def exportar_facturas_excel(request):
    """Exporta la lista de facturas a Excel. Acepta parámetro ?periodo=YYYY-MM para filtrar."""
    from datetime import datetime
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    
    # Filtro opcional por periodo
    periodo_filtro = request.GET.get('periodo', None)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Facturas"
    
    header_fill = PatternFill(start_color="2C5F8D", end_color="2C5F8D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    headers = ['Período', 'Monto Total (Bs)', '# Gastos', 'Fecha Creación']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
    
    # Filtrar facturas
    if periodo_filtro:
        facturas = Factura.objects.filter(periodo=periodo_filtro).order_by('-periodo')
        filename_suffix = periodo_filtro
    else:
        facturas = Factura.objects.all().order_by('-periodo')
        filename_suffix = 'todos'
    
    for row, factura in enumerate(facturas, 2):
        # Calcular monto total sumando gastos
        monto_total = factura.gastos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        ws.cell(row=row, column=1, value=factura.periodo)
        ws.cell(row=row, column=2, value=float(monto_total))
        ws.cell(row=row, column=3, value=factura.gastos.count())
        ws.cell(row=row, column=4, value=factura.creada_en.strftime('%d/%m/%Y'))
    
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 18
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=facturas_{filename_suffix}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


@login_required
def exportar_pagos_excel(request):
    """Exporta la lista de pagos a Excel."""
    from datetime import datetime
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pagos"
    
    header_fill = PatternFill(start_color="2C5F8D", end_color="2C5F8D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    headers = ['Fecha', 'Inmueble', 'Factura', 'Monto', 'Moneda', 'Tasa', 'Total Bs', 'Método']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
    
    pagos = Pago.objects.select_related('inmueble', 'factura').all().order_by('-fecha_pago')
    total_recaudado = Decimal('0.00')
    
    for row, pago in enumerate(pagos, 2):
        if pago.moneda == 'USD' and pago.tasa_cambio:
            total_bs = pago.monto_pagado * pago.tasa_cambio
        else:
            total_bs = pago.monto_pagado
        total_recaudado += total_bs
        
        ws.cell(row=row, column=1, value=pago.fecha_pago.strftime('%d/%m/%Y'))
        ws.cell(row=row, column=2, value=str(pago.inmueble))
        ws.cell(row=row, column=3, value=f"{pago.factura.get_mes_display()} {pago.factura.anio}")
        ws.cell(row=row, column=4, value=float(pago.monto_pagado))
        ws.cell(row=row, column=5, value=pago.moneda)
        ws.cell(row=row, column=6, value=float(pago.tasa_cambio) if pago.tasa_cambio else '')
        ws.cell(row=row, column=7, value=float(total_bs))
        ws.cell(row=row, column=8, value=pago.get_metodo_pago_display())
    
    total_row = len(pagos) + 2
    ws.cell(row=total_row, column=6, value='TOTAL RECAUDADO:').font = Font(bold=True)
    ws.cell(row=total_row, column=7, value=float(total_recaudado)).font = Font(bold=True)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=pagos_{datetime.now().strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


@login_required
def exportar_resumen_financiero_excel(request):
    """Exporta un resumen financiero completo."""
    from datetime import datetime
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resumen"
    
    header_fill = PatternFill(start_color="2C5F8D", end_color="2C5F8D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    title_font = Font(bold=True, size=14, color="2C5F8D")
    
    ws['A1'] = 'RESUMEN FINANCIERO - SAC WEB'
    ws['A1'].font = title_font
    ws.merge_cells('A1:B1')
    
    ws['A3'] = 'Concepto'
    ws['B3'] = 'Monto (Bs)'
    ws['A3'].fill = header_fill
    ws['B3'].fill = header_fill
    ws['A3'].font = header_font
    ws['B3'].font = header_font
    
    total_inmuebles = Inmueble.objects.count()
    total_facturas = Factura.objects.count()
    
    pagos = Pago.objects.all()
    total_recaudado = Decimal('0.00')
    for pago in pagos:
        if pago.moneda == 'USD' and pago.tasa_cambio:
            total_recaudado += pago.monto_pagado * pago.tasa_cambio
        else:
            total_recaudado += pago.monto_pagado
    
    total_gastos = Gasto.objects.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
    deuda_pendiente = total_gastos - total_recaudado
    
    ws['A4'] = 'Total Inmuebles'
    ws['B4'] = total_inmuebles
    ws['A5'] = 'Total Facturas'
    ws['B5'] = total_facturas
    ws['A6'] = 'Total Recaudado'
    ws['B6'] = float(total_recaudado)
    ws['A7'] = 'Total Gastos'
    ws['B7'] = float(total_gastos)
    ws['A8'] = 'Deuda Pendiente'
    ws['B8'] = float(deuda_pendiente)
    
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 20
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=resumen_{datetime.now().strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Sum
from decimal import Decimal
from django.http import JsonResponse
from django.contrib import messages
from nucleo.models import Inmueble, Factura, Pago, Gasto, DatosCondominio, Notificacion
from nucleo.utils import (
    validar_alicuotas, 
    calcular_deuda_inmueble, 
    registrar_actividad
)

def es_directiva_o_admin(user):
    """Verifica si el usuario es staff, superusuario o pertenece al grupo Directiva."""
    return user.is_staff or user.is_superuser or user.groups.filter(name='Directiva').exists()


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
        
        # Datos para gráficos (para renderizar de forma segura con json_script)
        'chart_pagos_labels': meses_labels,
        'chart_pagos_data': meses_montos,
        'chart_deudas_data': deudas_data,
        'chart_gastos_data': gastos_data,
    }
    
    return render(request, 'nucleo/dashboard.html', context)


@login_required
@user_passes_test(es_directiva_o_admin)
@require_POST
def actualizar_tasa_dolar(request):
    """Actualiza la tasa de cambio del día."""
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
@require_POST
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
@require_POST
def marcar_todas_notificaciones_leidas(request):
    """Marca todas las notificaciones del usuario como leídas."""
    Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).update(leida=True)
    
    messages.success(request, 'Todas las notificaciones marcadas como leídas')
    return redirect('nucleo:notificaciones')


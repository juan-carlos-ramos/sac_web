from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum, Q
from decimal import Decimal
from nucleo.models import Factura, Gasto, Inmueble, DatosCondominio
from nucleo.forms import FacturaForm, GastoForm
from nucleo.utils import (
    calcular_deuda_inmueble, 
    registrar_actividad, 
    notificar_usuarios_sobre_actividad
)

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
    
    return render(request, 'nucleo/facturas/detalle.html', {
        'factura': factura,
        'gastos': gastos,
        'total_gastos_comunes': total_gastos_comunes,
        'total_gastos_no_comunes': total_gastos_no_comunes,
        'total_general': total_general,
        'inmuebles': inmuebles,
    })


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
@require_POST
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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal
from nucleo.models import Inmueble
from nucleo.forms import InmuebleForm
from nucleo.utils import (
    validar_alicuotas, 
    registrar_actividad, 
    notificar_usuarios_sobre_actividad
)

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
        'query': query,
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
@require_POST
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
@require_POST
def calcular_alicuotas_automatico(request):
    """Calcula y aplica alícuotas igualitarias a todos los inmuebles."""
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

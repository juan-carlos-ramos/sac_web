from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from nucleo.models import Pago, DatosCondominio
from nucleo.forms import PagoForm
from nucleo.utils import registrar_actividad, notificar_usuarios_sobre_actividad

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
    
    # Obtener tasa BCV para auto-fill
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

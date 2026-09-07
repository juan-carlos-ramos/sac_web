from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from nucleo.models import Proveedor
from nucleo.forms import ProveedorForm
from nucleo.utils import registrar_actividad, notificar_usuarios_sobre_actividad

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
@require_POST
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

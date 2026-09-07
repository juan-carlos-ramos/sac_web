from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User
from nucleo.forms import CrearUsuarioForm, EditarUsuarioForm, CambiarPasswordUsuarioForm
from nucleo.utils import registrar_actividad, notificar_usuarios_sobre_actividad

def es_administrador(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(es_administrador)
def lista_usuarios(request):
    """Lista todos los usuarios del sistema."""
    usuarios = User.objects.all().order_by('username')
    return render(request, 'nucleo/usuarios/lista.html', {
        'usuarios': usuarios,
    })


@login_required
@user_passes_test(es_administrador)
def crear_usuario(request):
    """Crea un nuevo usuario."""
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
    """Edita un usuario existente."""
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
    """Elimina un usuario."""
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
    """Cambia la contraseña de un usuario."""
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
@require_POST
def toggle_usuario_activo(request, user_id):
    """Activa o desactiva un usuario."""
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

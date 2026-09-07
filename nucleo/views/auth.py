from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User
from nucleo.utils import registrar_actividad

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
@require_POST
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
        
        try:
            validate_password(password_nueva, request.user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
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
        respuesta = request.POST.get('respuesta', '').strip().lower()
        almacenada = (user.perfil.respuesta_seguridad or '').strip()
        
        # Verificar respuesta (hash o texto plano heredado)
        es_valido = False
        if check_password(respuesta, almacenada):
            es_valido = True
        elif respuesta == almacenada.lower():
            # Respuesta heredada en texto plano: validar y auto-hashear para mayor seguridad
            from django.contrib.auth.hashers import make_password
            user.perfil.respuesta_seguridad = make_password(respuesta)
            user.perfil.save()
            es_valido = True
            
        if es_valido:
            request.session['recup_validado'] = True
            return redirect('nucleo:recuperar_confirmar')
        else:
            messages.error(request, 'Respuesta incorrecta. Intente de nuevo.')
    
    return render(request, 'nucleo/recuperacion/paso2_pregunta.html', {
        'pregunta': user.perfil.pregunta_seguridad,
        'username': user.username
    })

def vista_recuperar_confirmar(request):
    """Paso 3: Establecer nueva contraseña con validación."""
    if not request.session.get('recup_validado') or not request.session.get('recup_user_id'):
        return redirect('nucleo:recuperar_password')
    
    if request.method == 'POST':
        password_nueva = request.POST.get('password_nueva')
        password_confirmar = request.POST.get('password_confirmar')
        
        if password_nueva != password_confirmar:
            messages.error(request, 'Las contraseñas no coinciden.')
        else:
            try:
                user = User.objects.get(id=request.session['recup_user_id'])
                # Validar la robustez de la contraseña antes de guardarla
                validate_password(password_nueva, user)
                
                user.set_password(password_nueva)
                user.save()
                
                # Limpiar sesión de recuperación
                del request.session['recup_user_id']
                del request.session['recup_validado']
                
                messages.success(request, '¡Contraseña restablecida! Inicia sesión con tu nueva clave.')
                return redirect('nucleo:login')
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
            except Exception:
                messages.error(request, 'Ocurrió un error inesperado.')
                
    return render(request, 'nucleo/recuperacion/paso3_confirmar.html')

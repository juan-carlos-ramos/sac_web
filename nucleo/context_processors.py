# nucleo/context_processors.py
# Los procesadores de contexto agregan variables disponibles en TODAS las plantillas.

from nucleo.utils import obtener_notificaciones_no_leidas


def informacion_sistema(request):
    """
    Agrega información global del sistema a todas las plantillas.
    """
    return {
        'nombre_sistema': 'SAC WEB',
        'nombre_completo': 'Sistema de Administración de Condominio',
    }


def notificaciones_usuario(request):
    """
    Agrega las notificaciones no leídas del usuario actual a todas las plantillas.
    Solo si el usuario está autenticado.
    """
    if request.user.is_authenticated:
        notificaciones = obtener_notificaciones_no_leidas(request.user)
        return {
            'notificaciones_no_leidas': notificaciones,
            'cantidad_notificaciones': notificaciones.count(),
        }
    return {
        'notificaciones_no_leidas': [],
        'cantidad_notificaciones': 0,
    }

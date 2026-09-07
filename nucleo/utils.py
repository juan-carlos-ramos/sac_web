"""
Utilidades y lógica de negocio del sistema SAC WEB
Sistema de Administración de Condominio

Este archivo contiene todas las funciones de cálculo financiero
y reglas de negocio del sistema.
"""

from decimal import Decimal
from typing import Dict, List, Optional
from django.db.models import Sum, Q


# =============================================================================
# FUNCIÓN PRINCIPAL: CALCULAR DEUDA POR INMUEBLE
# =============================================================================

def calcular_deuda_inmueble(inmueble, factura) -> Dict:
    """
    Calcula la deuda completa de un inmueble para una factura específica.
    
    Parámetros:
    - inmueble: Objeto Inmueble
    - factura: Objeto Factura
    
    Retorna un diccionario con:
    - gastos_comunes_totales: Suma de todos los gastos comunes
    - gastos_comunes_por_inmueble: Gastos comunes × alícuota
    - gastos_no_comunes: Gastos específicos del inmueble
    - fondo_reserva: 10% sobre gastos comunes prorrateados
    - total_a_pagar: Total que debe pagar el inmueble
    - total_pagado: Total de pagos realizados
    - saldo: Diferencia (positivo = deuda, negativo = saldo a favor)
    - detalle_gastos_comunes: Lista de gastos comunes
    - detalle_gastos_no_comunes: Lista de gastos no comunes
    - detalle_pagos: Lista de pagos realizados
    """
    
    # Importar modelos aquí para evitar importación circular
    from nucleo.models import Gasto, Pago
    
    # =========================================================================
    # A) GASTOS COMUNES
    # =========================================================================
    # Son los gastos que todos los inmuebles comparten según su alícuota.
    # Incluye: ORDINARIO, IMPREVISTO, EXTRAORDINARIO
    # Excluye: gastos no comunes (es_gasto_no_comun=True)
    
    gastos_comunes = Gasto.objects.filter(
        factura=factura,
        es_gasto_no_comun=False
    )
    
    # Sumar el total de gastos comunes
    gastos_comunes_totales = gastos_comunes.aggregate(
        total=Sum('monto')
    )['total'] or Decimal('0.00')
    
    # Aplicar alícuota del inmueble
    # Si el inmueble no tiene alícuota, su parte es 0
    alicuota = inmueble.alicuota or Decimal('0.00')
    gastos_comunes_por_inmueble = gastos_comunes_totales * alicuota
    
    # Detalle de gastos comunes para mostrar
    detalle_gastos_comunes = [
        {
            'descripcion': gasto.descripcion,
            'monto_total': gasto.monto,
            'categoria': gasto.get_categoria_display(),
            'monto_inmueble': gasto.monto * alicuota
        }
        for gasto in gastos_comunes
    ]
    
    # =========================================================================
    # B) GASTOS NO COMUNES
    # =========================================================================
    # Son gastos específicos de UN solo inmueble.
    # NO se prorratean, NO generan fondo de reserva.
    # Se suman directamente al total.
    
    gastos_no_comunes = Gasto.objects.filter(
        factura=factura,
        es_gasto_no_comun=True,
        inmueble_especifico=inmueble
    )
    
    # Sumar gastos no comunes
    gastos_no_comunes_total = gastos_no_comunes.aggregate(
        total=Sum('monto')
    )['total'] or Decimal('0.00')
    
    # Detalle de gastos no comunes
    detalle_gastos_no_comunes = [
        {
            'descripcion': gasto.descripcion,
            'monto': gasto.monto,
            'categoria': gasto.get_categoria_display()
        }
        for gasto in gastos_no_comunes
    ]
    
    # =========================================================================
    # C) FONDO DE RESERVA
    # =========================================================================
    # Se calcula el 10% SOLO sobre los gastos comunes prorrateados.
    # NO se aplica sobre gastos no comunes.
    
    porcentaje_fondo_reserva = Decimal('0.10')  # 10%
    fondo_reserva = gastos_comunes_por_inmueble * porcentaje_fondo_reserva
    
    # =========================================================================
    # D) TOTAL A PAGAR
    # =========================================================================
    # Suma de:
    # - Gastos comunes prorrateados
    # - Fondo de reserva (10% de gastos comunes)
    # - Gastos no comunes (sin prorratear)
    
    total_a_pagar = (
        gastos_comunes_por_inmueble +
        fondo_reserva +
        gastos_no_comunes_total
    )
    
    # =========================================================================
    # E) PAGOS REALIZADOS
    # =========================================================================
    # Obtener todos los pagos del inmueble para esta factura.
    # Convertir pagos en USD a Bs usando la tasa de cambio registrada.
    
    pagos = Pago.objects.filter(
        factura=factura,
        inmueble=inmueble
    )
    
    total_pagado = Decimal('0.00')
    detalle_pagos = []
    
    for pago in pagos:
        # Convertir el pago a Bs
        if pago.moneda == 'USD' and pago.tasa_cambio:
            monto_en_bs = pago.monto_pagado * pago.tasa_cambio
        else:
            monto_en_bs = pago.monto_pagado
        
        total_pagado += monto_en_bs
        
        detalle_pagos.append({
            'fecha': pago.fecha_pago,
            'monto_original': pago.monto_pagado,
            'moneda': pago.get_moneda_display(),
            'tasa_cambio': pago.tasa_cambio,
            'monto_en_bs': monto_en_bs,
            'metodo': pago.get_metodo_pago_display(),
            'referencia': pago.referencia
        })
    
    # =========================================================================
    # F) SALDO
    # =========================================================================
    # Diferencia entre lo que debe pagar y lo que ha pagado.
    # - saldo > 0: tiene deuda
    # - saldo < 0: tiene saldo a favor
    # - saldo = 0: está al día
    
    saldo = total_a_pagar - total_pagado
    
    # =========================================================================
    # RETORNAR RESULTADO COMPLETO
    # =========================================================================
    
    return {
        # Gastos comunes
        'gastos_comunes_totales': gastos_comunes_totales,
        'alicuota': alicuota,
        'gastos_comunes_por_inmueble': gastos_comunes_por_inmueble,
        'detalle_gastos_comunes': detalle_gastos_comunes,
        
        # Gastos no comunes
        'gastos_no_comunes_total': gastos_no_comunes_total,
        'detalle_gastos_no_comunes': detalle_gastos_no_comunes,
        
        # Fondo de reserva
        'porcentaje_fondo_reserva': porcentaje_fondo_reserva,
        'fondo_reserva': fondo_reserva,
        
        # Totales
        'total_a_pagar': total_a_pagar,
        'total_pagado': total_pagado,
        'saldo': saldo,
        'saldo_absoluto': abs(saldo),  # Valor absoluto para mostrar sin signo negativo
        'detalle_pagos': detalle_pagos,
        
        # Estado
        'tiene_deuda': saldo > 0,
        'tiene_saldo_favor': saldo < 0,
        'esta_al_dia': saldo == 0,
    }


# =============================================================================
# VALIDACIÓN DE ALÍCUOTAS
# =============================================================================

def validar_alicuotas() -> Dict:
    """
    Valida que las alícuotas de todos los inmuebles sumen 100%.
    
    Retorna un diccionario con:
    - suma_total: Suma de todas las alícuotas
    - es_valida: True si suma 100% (con margen de error)
    - diferencia: Diferencia con respecto a 100%
    - inmuebles_sin_alicuota: Lista de inmuebles sin alícuota
    - advertencias: Lista de mensajes de advertencia
    """
    
    from nucleo.models import Inmueble
    
    # Obtener todos los inmuebles
    inmuebles = Inmueble.objects.all()
    
    # Inmuebles sin alícuota
    inmuebles_sin_alicuota = inmuebles.filter(
        Q(alicuota__isnull=True) | Q(alicuota=0)
    )
    
    # Sumar todas las alícuotas
    suma_alicuotas = inmuebles.filter(
        alicuota__isnull=False
    ).aggregate(
        total=Sum('alicuota')
    )['total'] or Decimal('0.00')
    
    # Convertir a porcentaje (multiplicar por 100)
    suma_porcentaje = suma_alicuotas * 100
    
    # Diferencia con respecto a 100%
    diferencia = abs(Decimal('100.00') - suma_porcentaje)
    
    # Margen de error aceptable (0.01%)
    margen_error = Decimal('0.01')
    es_valida = diferencia <= margen_error
    
    # Generar advertencias
    advertencias = []
    
    if inmuebles_sin_alicuota.exists():
        advertencias.append(
            f'{inmuebles_sin_alicuota.count()} inmueble(s) sin alícuota asignada'
        )
    
    if not es_valida:
        if suma_porcentaje > 100:
            advertencias.append(
                f'Las alícuotas suman {suma_porcentaje:.2f}% (excede 100%)'
            )
        else:
            advertencias.append(
                f'Las alícuotas suman {suma_porcentaje:.2f}% (falta {diferencia:.2f}%)'
            )
    
    return {
        'suma_total': suma_alicuotas,
        'suma_porcentaje': suma_porcentaje,
        'es_valida': es_valida,
        'diferencia': diferencia,
        'inmuebles_sin_alicuota': list(inmuebles_sin_alicuota.values_list('numero_apto', flat=True)),
        'advertencias': advertencias,
        'total_inmuebles': inmuebles.count(),
        'inmuebles_con_alicuota': inmuebles.filter(alicuota__isnull=False).count(),
    }


# =============================================================================
# CONVERSIÓN DE MONEDA
# =============================================================================

def convertir_a_bs(monto: Decimal, moneda: str, tasa_cambio: Optional[Decimal] = None) -> Decimal:
    """
    Convierte un monto a Bolívares.
    
    Parámetros:
    - monto: Cantidad a convertir
    - moneda: 'BS' o 'USD'
    - tasa_cambio: Tasa de cambio (solo si moneda='USD')
    
    Retorna:
    - Monto en Bolívares
    """
    
    if moneda == 'BS':
        return monto
    elif moneda == 'USD' and tasa_cambio:
        return monto * tasa_cambio
    else:
        # Si no hay tasa de cambio, retornar el monto original
        return monto


def convertir_a_usd(monto_bs: Decimal, tasa_cambio: Decimal) -> Decimal:
    """
    Convierte un monto en Bolívares a Dólares.
    
    Parámetros:
    - monto_bs: Cantidad en Bolívares
    - tasa_cambio: Tasa de cambio actual
    
    Retorna:
    - Monto en Dólares
    """
    
    if tasa_cambio and tasa_cambio > 0:
        return monto_bs / tasa_cambio
    else:
        return Decimal('0.00')


def obtener_tasa_cambio_promedio(factura) -> Optional[Decimal]:
    """
    Obtiene la tasa de cambio promedio de los pagos de una factura.
    Útil para mostrar referencias en USD.
    
    Parámetros:
    - factura: Objeto Factura
    
    Retorna:
    - Tasa de cambio promedio o None
    """
    
    from nucleo.models import Pago
    
    pagos_usd = Pago.objects.filter(
        factura=factura,
        moneda='USD',
        tasa_cambio__isnull=False
    )
    
    if pagos_usd.exists():
        tasa_promedio = pagos_usd.aggregate(
            promedio=Sum('tasa_cambio')
        )['promedio'] / pagos_usd.count()
        return tasa_promedio
    
    return None


# =============================================================================
# RESUMEN DE FACTURA
# =============================================================================

def obtener_resumen_factura(factura) -> Dict:
    """
    Genera un resumen completo de una factura.
    
    Parámetros:
    - factura: Objeto Factura
    
    Retorna un diccionario con:
    - total_gastos_comunes: Suma de gastos comunes
    - total_gastos_no_comunes: Suma de gastos no comunes
    - total_gastos: Total general
    - total_pagos: Total de pagos recibidos
    - saldo_general: Diferencia
    - inmuebles_al_dia: Cantidad de inmuebles sin deuda
    - inmuebles_con_deuda: Cantidad de inmuebles con deuda
    """
    
    from nucleo.models import Gasto, Pago, Inmueble
    
    # Gastos comunes
    total_gastos_comunes = Gasto.objects.filter(
        factura=factura,
        es_gasto_no_comun=False
    ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
    
    # Gastos no comunes
    total_gastos_no_comunes = Gasto.objects.filter(
        factura=factura,
        es_gasto_no_comun=True
    ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
    
    # Total de gastos
    total_gastos = total_gastos_comunes + total_gastos_no_comunes
    
    # Total de pagos (convertidos a BS)
    pagos = Pago.objects.filter(factura=factura)
    total_pagos = Decimal('0.00')
    
    for pago in pagos:
        total_pagos += convertir_a_bs(pago.monto_pagado, pago.moneda, pago.tasa_cambio)
    
    # Saldo general
    saldo_general = total_gastos - total_pagos
    
    # Contar inmuebles al día y con deuda
    inmuebles = Inmueble.objects.all()
    inmuebles_al_dia = 0
    inmuebles_con_deuda = 0
    
    for inmueble in inmuebles:
        resultado = calcular_deuda_inmueble(inmueble, factura)
        if resultado['saldo'] <= 0:
            inmuebles_al_dia += 1
        else:
            inmuebles_con_deuda += 1
    
    return {
        'total_gastos_comunes': total_gastos_comunes,
        'total_gastos_no_comunes': total_gastos_no_comunes,
        'total_gastos': total_gastos,
        'total_pagos': total_pagos,
        'saldo_general': saldo_general,
        'inmuebles_al_dia': inmuebles_al_dia,
        'inmuebles_con_deuda': inmuebles_con_deuda,
        'total_inmuebles': inmuebles.count(),
        'porcentaje_cobranza': (total_pagos / total_gastos * 100) if total_gastos > 0 else Decimal('0.00'),
    }


# =============================================================================
# SISTEMA DE AUDITORÍA
# =============================================================================

def registrar_actividad(usuario, accion, modelo, objeto_id, descripcion):
    """
    Registra una actividad en el sistema de auditoría.
    
    Parámetros:
    - usuario: Objeto User que realiza la acción
    - accion: Tipo de acción ('CREAR', 'EDITAR', 'BORRAR', 'GENERAR')
    - modelo: Nombre del modelo afectado (ej: 'Factura', 'Pago')
    - objeto_id: ID del objeto afectado
    - descripcion: Descripción detallada de la acción
    
    Retorna:
    - Objeto ActividadLog creado
    """
    
    from nucleo.models import ActividadLog
    
    actividad = ActividadLog.objects.create(
        usuario=usuario,
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        descripcion=descripcion
    )
    
    return actividad


def crear_notificacion(usuario, actividad):
    """
    Crea una notificación para un usuario basada en una actividad.
    
    Parámetros:
    - usuario: Objeto User que recibirá la notificación
    - actividad: Objeto ActividadLog que generó la notificación
    
    Retorna:
    - Objeto Notificacion creado
    """
    
    from nucleo.models import Notificacion
    
    notificacion = Notificacion.objects.create(
        usuario=usuario,
        actividad=actividad,
        leida=False
    )
    
    return notificacion


def notificar_usuarios_sobre_actividad(actividad, excluir_usuario=None):
    """
    Crea notificaciones para todos los usuarios sobre una actividad.
    Opcionalmente excluye al usuario que realizó la acción.
    
    Parámetros:
    - actividad: Objeto ActividadLog
    - excluir_usuario: Usuario a excluir (generalmente quien hizo la acción)
    
    Retorna:
    - Lista de notificaciones creadas
    """
    
    from django.contrib.auth.models import User
    from nucleo.models import Notificacion
    
    # Obtener todos los usuarios activos
    usuarios = User.objects.filter(is_active=True)
    
    # Excluir al usuario especificado
    if excluir_usuario:
        usuarios = usuarios.exclude(id=excluir_usuario.id)
    
    # Crear notificaciones
    notificaciones = []
    for usuario in usuarios:
        notificacion = crear_notificacion(usuario, actividad)
        notificaciones.append(notificacion)
    
    return notificaciones


def marcar_notificacion_leida(notificacion_id):
    """
    Marca una notificación como leída.
    
    Parámetros:
    - notificacion_id: ID de la notificación
    
    Retorna:
    - True si se marcó correctamente, False si no existe
    """
    
    from nucleo.models import Notificacion
    
    try:
        notificacion = Notificacion.objects.get(id=notificacion_id)
        notificacion.leida = True
        notificacion.save()
        return True
    except Notificacion.DoesNotExist:
        return False


def obtener_notificaciones_no_leidas(usuario):
    """
    Obtiene todas las notificaciones no leídas de un usuario.
    
    Parámetros:
    - usuario: Objeto User
    
    Retorna:
    - QuerySet de notificaciones no leídas
    """
    
    from nucleo.models import Notificacion
    
    return Notificacion.objects.filter(
        usuario=usuario,
        leida=False
    ).order_by('-fecha_creacion')


def sanitizar_para_excel(valor):
    """
    Sanitiza cadenas de texto para prevenir ataques de Formula Injection (CSV/Excel Injection).
    Si el valor de texto comienza con '=', '+', '-', '@', tabulación o retorno de carro,
    antepone un apóstrofe (') para forzar su interpretación como texto literal.
    """
    if valor is None:
        return ""
    str_val = str(valor)
    if str_val.startswith(('=', '+', '-', '@', '\t', '\r')):
        return f"'{str_val}"
    return str_val


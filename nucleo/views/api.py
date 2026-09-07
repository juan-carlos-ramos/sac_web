import logging
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal
from nucleo.models import Factura, Inmueble, DatosCondominio
from nucleo.utils import calcular_deuda_inmueble

logger = logging.getLogger(__name__)

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
        logger.exception("Error al obtener deuda de inmueble")
        return JsonResponse({'error': 'Error interno al procesar la solicitud'}, status=500)

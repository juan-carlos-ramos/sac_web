from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def formato_moneda(value):
    """
    Formatea un número o decimal al formato europeo/venezolano:
    1.234,56
    
    Uso: {{ valor|formato_moneda }}
    """
    if value is None:
        return "0,00"
    
    try:
        # Convertir a float para formatear
        numero = float(value)
        # Formatear: {:,.2f} genera 1,234.56
        s = "{:,.2f}".format(numero)
        # Reemplazos para cambiar , por . y . por ,
        # 1. Cambiar , por X -> 1X234.56
        # 2. Cambiar . por , -> 1X234,56
        # 3. Cambiar X por . -> 1.234,56
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return value

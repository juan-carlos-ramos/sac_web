"""
Configuración del panel de administración de Django
para el sistema SAC WEB
"""

from django.contrib import admin
from .models import (
    Inmueble,
    Factura,
    Proveedor,
    DatosCondominio,
    Gasto,
    Pago,
    Presupuesto,
    PartidaPresupuestaria,
    ActividadLog,
    Notificacion
)


# =============================================================================
# INMUEBLE
# =============================================================================

@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Inmuebles.
    """
    list_display = ('numero_apto', 'propietario', 'documento_identidad', 'telefono', 'email', 'alicuota')
    search_fields = ('numero_apto', 'propietario', 'documento_identidad', 'email', 'telefono')
    list_filter = ('propietario',)
    ordering = ('numero_apto',)
    fieldsets = (
        ('Información del Inmueble', {
            'fields': ('numero_apto', 'alicuota')
        }),
        ('Información del Propietario', {
            'fields': ('propietario', 'documento_identidad', 'email', 'telefono')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# FACTURA
# =============================================================================

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Facturas.
    """
    list_display = ('periodo', 'creada_en')
    search_fields = ('periodo',)
    ordering = ('-periodo',)
    readonly_fields = ('creada_en',)


# =============================================================================
# PROVEEDOR
# =============================================================================

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Proveedores.
    """
    list_display = ('nombre', 'rif', 'telefono', 'email')
    search_fields = ('nombre', 'rif')
    list_filter = ('nombre',)
    ordering = ('nombre',)


# =============================================================================
# DATOS DEL CONDOMINIO
# =============================================================================

@admin.register(DatosCondominio)
class DatosCondominioAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Datos del Condominio.
    """
    list_display = ('nombre_condominio', 'rif', 'contacto_admin')
    search_fields = ('nombre_condominio', 'rif')


# =============================================================================
# GASTO
# =============================================================================

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Gastos.
    """
    list_display = ('descripcion', 'factura', 'monto', 'categoria', 'es_gasto_no_comun', 'inmueble_especifico')
    search_fields = ('descripcion',)
    list_filter = ('factura', 'categoria', 'es_gasto_no_comun')
    ordering = ('-factura', 'descripcion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('factura', 'descripcion', 'monto', 'categoria')
        }),
        ('Gasto No Común', {
            'fields': ('es_gasto_no_comun', 'inmueble_especifico'),
            'description': 'Marcar si este gasto aplica solo a un inmueble específico'
        }),
    )


# =============================================================================
# PAGO
# =============================================================================

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Pagos.
    """
    list_display = ('inmueble', 'factura', 'fecha_pago', 'monto_pagado', 'moneda', 'metodo_pago', 'referencia')
    search_fields = ('inmueble__numero_apto', 'referencia')
    list_filter = ('factura', 'moneda', 'metodo_pago', 'fecha_pago')
    ordering = ('-fecha_pago',)
    
    fieldsets = (
        ('Información del Pago', {
            'fields': ('factura', 'inmueble', 'fecha_pago')
        }),
        ('Monto', {
            'fields': ('monto_pagado', 'moneda', 'tasa_cambio')
        }),
        ('Detalles de la Transacción', {
            'fields': ('metodo_pago', 'referencia', 'comprobante', 'notas')
        }),
    )


# =============================================================================
# PRESUPUESTO
# =============================================================================

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Presupuestos.
    """
    list_display = ('nombre', 'anio')
    search_fields = ('nombre',)
    list_filter = ('anio',)
    ordering = ('-anio',)


# =============================================================================
# PARTIDA PRESUPUESTARIA
# =============================================================================

@admin.register(PartidaPresupuestaria)
class PartidaPresupuestariaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Partidas Presupuestarias.
    """
    list_display = ('descripcion', 'presupuesto', 'monto_presupuestado')
    search_fields = ('descripcion',)
    list_filter = ('presupuesto',)
    ordering = ('presupuesto', 'descripcion')


# =============================================================================
# ACTIVIDAD LOG (AUDITORÍA)
# =============================================================================

@admin.register(ActividadLog)
class ActividadLogAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Registros de Actividad.
    """
    list_display = ('usuario', 'accion', 'modelo', 'objeto_id', 'fecha_hora')
    search_fields = ('usuario__username', 'modelo', 'descripcion')
    list_filter = ('accion', 'modelo', 'fecha_hora')
    ordering = ('-fecha_hora',)
    readonly_fields = ('usuario', 'accion', 'modelo', 'objeto_id', 'descripcion', 'fecha_hora')
    
    def has_add_permission(self, request):
        # No permitir crear logs manualmente
        return False
    
    def has_delete_permission(self, request, obj=None):
        # No permitir borrar logs
        return False


# =============================================================================
# NOTIFICACIÓN
# =============================================================================

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Notificaciones.
    """
    list_display = ('usuario', 'actividad', 'leida', 'fecha_creacion')
    search_fields = ('usuario__username',)
    list_filter = ('leida', 'fecha_creacion')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion',)

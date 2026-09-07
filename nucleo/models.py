"""
Modelos de datos del sistema SAC WEB
Sistema de Administración de Condominio
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


# =============================================================================
# MODELO: Inmueble
# =============================================================================
# Representa cada apartamento o local del condominio.

class Inmueble(models.Model):
    """
    Apartamento o local dentro del condominio.
    """
    numero_apto = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de apartamento',
        help_text='Identificador único del inmueble (ej: 1A, 2B, PH-1)'
    )
    
    propietario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nombre del propietario',
        help_text='Nombre completo del propietario actual'
    )
    
    documento_identidad = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Documento de Identidad',
        help_text='R.I.F. o C.I. del propietario (ej: V-12345678, J-31215969-3)'
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Correo Electrónico',
        help_text='Email de contacto del propietario'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono de Contacto',
        help_text='Número de teléfono del propietario (ej: 0424-232-43-85)'
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentarios Adicionales',
        help_text='Notas o comentarios sobre el inmueble o propietario'
    )
    
    alicuota = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        blank=True,
        null=True,
        verbose_name='Alícuota',
        help_text='Porcentaje de participación en gastos comunes (ej: 0.05263158)'
    )
    
    fecha_ingreso = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Ingreso',
        help_text='Fecha desde la cual el inmueble participa en las facturas'
    )

    class Meta:
        verbose_name = 'Inmueble'
        verbose_name_plural = 'Inmuebles'
        ordering = ['numero_apto']

    def __str__(self):
        if self.propietario:
            doc = f' ({self.documento_identidad})' if self.documento_identidad else ''
            return f'{self.numero_apto} - {self.propietario}{doc}'
        return self.numero_apto


# =============================================================================
# MODELO: Factura
# =============================================================================
# Representa un período de facturación del condominio (ej: enero 2026).

class Factura(models.Model):
    """
    Período de facturación mensual del condominio.
    """
    periodo = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Período',
        help_text='Formato: YYYY-MM (ej: 2026-01 para enero 2026)'
    )
    
    creada_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
        help_text='Fecha y hora en que se creó la factura'
    )

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-periodo']

    def __str__(self):
        return f'Factura {self.periodo}'


# =============================================================================
# MODELO: Proveedor
# =============================================================================
# Empresas o personas que prestan servicios al condominio.

class Proveedor(models.Model):
    """
    Empresa o persona que presta servicios al condominio.
    """
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre del proveedor o empresa'
    )
    
    rif = models.CharField(
        max_length=20,
        verbose_name='RIF',
        help_text='Registro de Información Fiscal (ej: J-12345678-9)'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono',
        help_text='Número de contacto'
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Correo electrónico',
        help_text='Email de contacto'
    )
    
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección',
        help_text='Dirección física del proveedor'
    )

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.rif})'


# =============================================================================
# MODELO: DatosCondominio
# =============================================================================
# Información general del condominio. Solo debe existir UN registro.

class DatosCondominio(models.Model):
    """
    Datos generales del condominio (solo un registro).
    """
    nombre_condominio = models.CharField(
        max_length=200,
        verbose_name='Nombre del condominio',
        help_text='Nombre oficial del edificio o conjunto residencial'
    )
    
    rif = models.CharField(
        max_length=20,
        verbose_name='RIF del condominio',
        help_text='Registro de Información Fiscal del condominio'
    )
    
    direccion = models.TextField(
        verbose_name='Dirección',
        help_text='Dirección completa del condominio'
    )
    
    datos_bancarios = models.TextField(
        verbose_name='Datos bancarios',
        help_text='Información de la cuenta bancaria para recibir pagos'
    )
    
    contacto_admin = models.CharField(
        max_length=100,
        verbose_name='Contacto del administrador',
        help_text='Nombre y teléfono del administrador'
    )
    
    tasa_cambio_dolar = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1.0000,
        verbose_name='Tasa de cambio del día (BCV)',
        help_text='Valor del dólar para cálculos referenciales'
    )

    class Meta:
        verbose_name = 'Datos del Condominio'
        verbose_name_plural = 'Datos del Condominio'

    def __str__(self):
        return self.nombre_condominio


# =============================================================================
# MODELO: Gasto
# =============================================================================
# Cada gasto registrado en una factura mensual.
# Puede ser ordinario (mensual), imprevisto o extraordinario.
# Puede ser común (todos pagan) o no común (solo un inmueble paga).

class Gasto(models.Model):
    """
    Gasto registrado en una factura mensual.
    """
    # Opciones para el tipo de gasto
    CATEGORIA_CHOICES = [
        ('ORDINARIO', 'Ordinario'),          # Gastos mensuales normales
        ('IMPREVISTO', 'Imprevisto'),        # Gastos inesperados
        ('EXTRAORDINARIO', 'Extraordinario'), # Gastos especiales aprobados
    ]
    
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,  # Si se borra la factura, se borran sus gastos
        related_name='gastos',     # Permite acceder: factura.gastos.all()
        verbose_name='Factura'
    )
    
    descripcion = models.CharField(
        max_length=255,
        verbose_name='Descripción',
        help_text='Descripción del gasto (ej: Servicio de limpieza)'
    )
    
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Monto',
        help_text='Monto total del gasto'
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='ORDINARIO',
        verbose_name='Categoría',
        help_text='Tipo de gasto'
    )
    
    es_gasto_no_comun = models.BooleanField(
        default=False,
        verbose_name='¿Es gasto no común?',
        help_text='Marcar si solo un inmueble debe pagar este gasto'
    )
    
    inmueble_especifico = models.ForeignKey(
        Inmueble,
        on_delete=models.SET_NULL,  # Si se borra el inmueble, el gasto permanece
        blank=True,
        null=True,
        verbose_name='Inmueble específico',
        help_text='Solo aplica si es gasto no común'
    )

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['factura', 'descripcion']

    def __str__(self):
        return f'{self.descripcion} - {self.monto}'


# =============================================================================
# MODELO: Pago
# =============================================================================
# Registro de cada pago realizado por un propietario.
# Incluye el método de pago, referencia y comprobante adjunto.

class Pago(models.Model):
    """
    Pago realizado por un propietario para una factura.
    """
    # Opciones para moneda
    MONEDA_CHOICES = [
        ('BS', 'Bolívares'),
        ('USD', 'Dólares'),
    ]
    
    # Opciones para método de pago
    METODO_PAGO_CHOICES = [
        ('TRANSFERENCIA', 'Transferencia bancaria'),
        ('PAGO_MOVIL', 'Pago móvil'),
        ('EFECTIVO', 'Efectivo'),
        ('CHEQUE', 'Cheque'),
        ('ZELLE', 'Zelle'),
        ('OTRO', 'Otro'),
    ]
    
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        verbose_name='Factura',
        help_text='Factura a la que corresponde el pago'
    )
    
    inmueble = models.ForeignKey(
        Inmueble,
        on_delete=models.CASCADE,
        verbose_name='Inmueble',
        help_text='Apartamento que realiza el pago'
    )
    
    fecha_pago = models.DateField(
        verbose_name='Fecha de pago',
        help_text='Fecha en que se realizó el pago'
    )
    
    monto_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Monto pagado',
        help_text='Cantidad pagada'
    )
    
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='BS',
        verbose_name='Moneda',
        help_text='Moneda del pago'
    )
    
    tasa_cambio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name='Tasa de cambio',
        help_text='Solo si el pago es en USD'
    )
    
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        default='TRANSFERENCIA',
        verbose_name='Método de pago'
    )
    
    referencia = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Número de referencia',
        help_text='Número de referencia de la transacción'
    )
    
    comprobante = models.FileField(
        upload_to='comprobantes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
        verbose_name='Comprobante',
        help_text='Imagen o PDF del comprobante de pago'
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas',
        help_text='Observaciones adicionales'
    )

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f'Pago {self.inmueble} - {self.fecha_pago}'


# =============================================================================
# MODELO: Presupuesto
# =============================================================================
# Presupuesto anual del condominio.

class Presupuesto(models.Model):
    """
    Presupuesto anual del condominio.
    """
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre del presupuesto (ej: Presupuesto 2026)'
    )
    
    anio = models.IntegerField(
        verbose_name='Año',
        help_text='Año del presupuesto'
    )

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-anio']

    def __str__(self):
        return f'{self.nombre} ({self.anio})'


# =============================================================================
# MODELO: PartidaPresupuestaria
# =============================================================================
# Cada línea del presupuesto anual.

class PartidaPresupuestaria(models.Model):
    """
    Línea individual de un presupuesto.
    """
    presupuesto = models.ForeignKey(
        Presupuesto,
        on_delete=models.CASCADE,
        related_name='partidas',  # presupuesto.partidas.all()
        verbose_name='Presupuesto'
    )
    
    descripcion = models.CharField(
        max_length=255,
        verbose_name='Descripción',
        help_text='Descripción de la partida (ej: Mantenimiento ascensores)'
    )
    
    monto_presupuestado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Monto presupuestado',
        help_text='Monto asignado a esta partida'
    )

    class Meta:
        verbose_name = 'Partida Presupuestaria'
        verbose_name_plural = 'Partidas Presupuestarias'
        ordering = ['presupuesto', 'descripcion']

    def __str__(self):
        return f'{self.descripcion} - {self.monto_presupuestado}'


# =============================================================================
# MODELO: ActividadLog (AUDITORÍA)
# =============================================================================
# Registro de todas las acciones realizadas en el sistema.
# Permite saber quién hizo qué y cuándo.

class ActividadLog(models.Model):
    """
    Registro de auditoría de acciones en el sistema.
    """
    # Tipos de acción
    ACCION_CHOICES = [
        ('CREAR', 'Crear'),
        ('EDITAR', 'Editar'),
        ('BORRAR', 'Borrar'),
        ('GENERAR', 'Generar'),
    ]
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        help_text='Usuario que realizó la acción'
    )
    
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        verbose_name='Acción',
        help_text='Tipo de acción realizada'
    )
    
    modelo = models.CharField(
        max_length=50,
        verbose_name='Modelo',
        help_text='Modelo afectado (ej: Factura, Pago)'
    )
    
    objeto_id = models.IntegerField(
        verbose_name='ID del objeto',
        help_text='ID del registro afectado'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción detallada de la acción'
    )
    
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora',
        help_text='Momento en que se realizó la acción'
    )

    class Meta:
        verbose_name = 'Registro de Actividad'
        verbose_name_plural = 'Registros de Actividad'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'{self.usuario} - {self.accion} {self.modelo}'


# =============================================================================
# MODELO: Notificacion
# =============================================================================
# Notificaciones para usuarios del sistema.
# Se vincula a una actividad para dar contexto.

class Notificacion(models.Model):
    """
    Notificación para un usuario del sistema.
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        help_text='Usuario que recibe la notificación'
    )
    
    actividad = models.ForeignKey(
        ActividadLog,
        on_delete=models.CASCADE,
        verbose_name='Actividad',
        help_text='Actividad que generó la notificación'
    )
    
    leida = models.BooleanField(
        default=False,
        verbose_name='Leída',
        help_text='Indica si el usuario ya vio la notificación'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
        help_text='Momento en que se creó la notificación'
    )

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        estado = '🔔' if not self.leida else '✓'
        return f'{estado} {self.usuario} - {self.actividad.accion}'


# =============================================================================
# MODELO: TokenAccesoTemporal
# =============================================================================
# Tokens de un solo uso para permitir que Puppeteer acceda a vistas protegidas

import secrets
from datetime import timedelta
from django.utils import timezone

class TokenAccesoTemporal(models.Model):
    """
    Token temporal de un solo uso para acceso sin autenticación.
    Usado principalmente para que Puppeteer pueda acceder a vistas protegidas.
    """
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Token',
        help_text='Token único generado automáticamente'
    )
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        help_text='Usuario que generó el token'
    )
    
    vista_destino = models.CharField(
        max_length=100,
        verbose_name='Vista destino',
        help_text='Nombre de la vista a la que da acceso'
    )
    
    parametros = models.JSONField(
        default=dict,
        verbose_name='Parámetros',
        help_text='Parámetros necesarios para la vista (factura_id, inmueble_id, etc.)'
    )
    
    usado = models.BooleanField(
        default=False,
        verbose_name='Usado',
        help_text='Indica si el token ya fue utilizado'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    fecha_expiracion = models.DateTimeField(
        verbose_name='Fecha de expiración'
    )
    
    class Meta:
        verbose_name = 'Token de Acceso Temporal'
        verbose_name_plural = 'Tokens de Acceso Temporal'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'Token {self.token[:8]}... para {self.vista_destino}'
    
    def save(self, *args, **kwargs):
        # Generar token si no existe
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        
        # Establecer expiración a 5 minutos si no está definida
        if not self.fecha_expiracion:
            self.fecha_expiracion = timezone.now() + timedelta(minutes=5)
        
        super().save(*args, **kwargs)
    
    def es_valido(self):
        """Verifica si el token es válido (no usado y no expirado)."""
        return not self.usado and timezone.now() < self.fecha_expiracion


# =============================================================================
# MODELO: PerfilUsuario (PREGUNTA DE SEGURIDAD)
# =============================================================================
# Extensión del modelo User para guardar preguntas de recuperación.

class PerfilUsuario(models.Model):
    """
    Perfil extendido del usuario para guardar pregunta de seguridad.
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )
    
    pregunta_seguridad = models.CharField(
        max_length=200,
        verbose_name='Pregunta de Seguridad',
        help_text='Ej: ¿Nombre de tu primera mascota?'
    )
    
    respuesta_seguridad = models.CharField(
        max_length=255,
        verbose_name='Respuesta (Hashed)',
        help_text='Hash de la respuesta para recuperar contraseña'
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f'Perfil de {self.usuario.username}'

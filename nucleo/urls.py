# nucleo/urls.py
# Rutas de la aplicación nucleo

from django.urls import path
from . import views

app_name = 'nucleo'

urlpatterns = [
    # =========================================================================
    # AUTENTICACIÓN
    # =========================================================================
    path('login/', views.vista_login, name='login'),
    path('logout/', views.vista_logout, name='logout'),
    path('cambiar-password/', views.vista_cambiar_password, name='cambiar_password'),
    
    # Recuperación por Preguntas de Seguridad
    path('recuperar-password/', views.vista_recuperar_password, name='recuperar_password'),
    path('recuperar-password/pregunta/', views.vista_recuperar_pregunta, name='recuperar_pregunta'),
    path('recuperar-password/confirmar/', views.vista_recuperar_confirmar, name='recuperar_confirmar'),
    
    # =========================================================================
    # DASHBOARD
    # =========================================================================
    path('', views.vista_dashboard, name='dashboard'),
    path('dashboard/actualizar-tasa/', views.actualizar_tasa_dolar, name='actualizar_tasa_dolar'),
    
    # =========================================================================
    # INMUEBLES
    # =========================================================================
    path('inmuebles/', views.lista_inmuebles, name='lista_inmuebles'),
    path('inmuebles/crear/', views.crear_inmueble, name='crear_inmueble'),
    path('inmuebles/<int:inmueble_id>/editar/', views.editar_inmueble, name='editar_inmueble'),
    path('inmuebles/<int:inmueble_id>/eliminar/', views.eliminar_inmueble, name='eliminar_inmueble'),
    path('inmuebles/calcular-alicuotas/', views.calcular_alicuotas_automatico, name='calcular_alicuotas'),
    
    # =========================================================================
    # PROVEEDORES
    # =========================================================================
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:proveedor_id>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/<int:proveedor_id>/eliminar/', views.eliminar_proveedor, name='eliminar_proveedor'),
    
    # =========================================================================
    # FACTURAS Y GASTOS
    # =========================================================================
    path('facturas/', views.lista_facturas, name='lista_facturas'),
    path('facturas/crear/', views.crear_factura, name='crear_factura'),
    path('facturas/<int:factura_id>/', views.detalle_factura, name='detalle_factura'),
    path('facturas/<int:factura_id>/agregar-gasto/', views.agregar_gasto, name='agregar_gasto'),
    path('facturas/<int:factura_id>/api/solvencia/', views.api_solvencia_factura, name='api_solvencia_factura'),
    path('facturas/<int:factura_id>/exportar-solvencia/', views.exportar_solvencia_excel, name='exportar_solvencia'),
    path('facturas/<int:factura_id>/exportar-recibos/', views.exportar_recibos_factura, name='exportar_recibos_factura'),
    path('facturas/exportar-recibos-todos/', views.exportar_recibos_todos, name='exportar_recibos_todos'),
    path('facturas/exportar-solvencia-todos/', views.exportar_solvencia_todos, name='exportar_solvencia_todos'),
    path('gastos/<int:gasto_id>/eliminar/', views.eliminar_gasto, name='eliminar_gasto'),
    
    # =========================================================================
    # PAGOS
    # =========================================================================
    path('pagos/', views.lista_pagos, name='lista_pagos'),
    path('pagos/registrar/', views.registrar_pago, name='registrar_pago'),
    path('pagos/api/deuda/', views.api_obtener_deuda, name='api_obtener_deuda'),
    
    # =========================================================================
    # RECIBOS
    # =========================================================================
    path('recibos/factura/<int:factura_id>/inmueble/<int:inmueble_id>/', 
         views.recibo_inmueble, name='recibo_inmueble'),
    
    # =========================================================================
    # NOTIFICACIONES
    # =========================================================================
    path('notificaciones/', views.vista_notificaciones, name='notificaciones'),
    path('notificaciones/<int:notificacion_id>/marcar-leida/', 
         views.marcar_notificacion_como_leida, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas-leidas/', 
         views.marcar_todas_notificaciones_leidas, name='marcar_todas_leidas'),
    
    # =========================================================================
    # PDFs ADMINISTRATIVOS (WEASYPRINT)
    # =========================================================================
    path('pdf/inmuebles/', views.pdf_reporte_inmuebles, name='pdf_reporte_inmuebles'),
    
    # =========================================================================
    # PDFs CRÍTICOS (PUPPETEER - MOTOR PRINCIPAL)
    # =========================================================================
    path('pdf/recibo/factura/<int:factura_id>/inmueble/<int:inmueble_id>/', 
         views.pdf_recibo_puppeteer, name='pdf_recibo_puppeteer'),

    # =========================================================================
    # GESTIÓN DE USUARIOS
    # =========================================================================
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/<int:user_id>/cambiar-password/', views.cambiar_password_usuario, name='cambiar_password_usuario'),
    path('usuarios/<int:user_id>/toggle-activo/', views.toggle_usuario_activo, name='toggle_usuario_activo'),

    # =========================================================================
    # AUDITORÍA
    # =========================================================================
    path('auditoria/', views.vista_auditoria, name='vista_auditoria'),
    path('auditoria/exportar/', views.exportar_auditoria_excel, name='exportar_auditoria'),
    path('auditoria/inmueble/<int:inmueble_id>/', views.historial_inmueble, name='historial_inmueble'),
    path('auditoria/factura/<int:factura_id>/', views.historial_factura, name='historial_factura'),
    path('auditoria/pago/<int:pago_id>/', views.historial_pago, name='historial_pago'),

    # =========================================================================
    # EXPORTACIONES A EXCEL
    # =========================================================================
    path('export/inmuebles/', views.exportar_inmuebles_excel, name='exportar_inmuebles'),
    path('export/facturas/', views.exportar_facturas_excel, name='exportar_facturas'),
    path('export/pagos/', views.exportar_pagos_excel, name='exportar_pagos'),
    path('export/resumen/', views.exportar_resumen_financiero_excel, name='exportar_resumen'),
]

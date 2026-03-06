import os
import sys
import django

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_web.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from nucleo.models import Inmueble, Pago, Factura, Gasto, Proveedor

def setup_roles():
    print("Iniciando configuración de roles...")

    # 1. Definir los modelos que vamos a controlar
    models = [Inmueble, Pago, Factura, Gasto, Proveedor]
    
    # 2. Crear Grupo DIRECTIVA (Full Access)
    directiva_group, created = Group.objects.get_or_create(name='Directiva')
    print(f"Grupo 'Directiva' {'creado' if created else 'ya existe'}.")
    
    # Asignar TODOS los permisos de nucleo a Directiva
    params = {'content_type__app_label': 'nucleo'}
    permissions = Permission.objects.filter(**params)
    directiva_group.permissions.set(permissions)
    print(f"  -> Asignados {permissions.count()} permisos a Directiva.")

    # 3. Crear Grupo SECRETARIA (Gestor Comunidad)
    secretaria_group, created = Group.objects.get_or_create(name='Secretaria')
    print(f"Grupo 'Secretaria' {'creado' if created else 'ya existe'}.")
    
    permissions_secretaria = []
    
    # Permiso para EDITAR Inmuebles (change) y VER (view)
    ct_inmueble = ContentType.objects.get_for_model(Inmueble)
    permissions_secretaria.append(Permission.objects.get(content_type=ct_inmueble, codename='change_inmueble'))
    permissions_secretaria.append(Permission.objects.get(content_type=ct_inmueble, codename='view_inmueble'))
    
    # Permiso para VER todo lo demás (read-only)
    read_only_models = [Pago, Factura, Gasto, Proveedor]
    for model in read_only_models:
        ct = ContentType.objects.get_for_model(model)
        model_name = model.__name__.lower()
        try:
            p = Permission.objects.get(content_type=ct, codename=f'view_{model_name}')
            permissions_secretaria.append(p)
        except Permission.DoesNotExist:
            print(f"  [WARN] No se encontró permiso view_{model_name}")

    # Asignar permisos acumulados
    secretaria_group.permissions.set(permissions_secretaria)
    print(f"  -> Asignados {len(permissions_secretaria)} permisos a Secretaria.")


    # 4. Crear Grupo LECTORES (Solo Ver Todo)
    lectores_group, created = Group.objects.get_or_create(name='Lectores')
    print(f"Grupo 'Lectores' {'creado' if created else 'ya existe'}.")
    
    permissions_lectores = []
    all_models = [Inmueble, Pago, Factura, Gasto, Proveedor]
    for model in all_models:
        ct = ContentType.objects.get_for_model(model)
        model_name = model.__name__.lower()
        try:
            p = Permission.objects.get(content_type=ct, codename=f'view_{model_name}')
            permissions_lectores.append(p)
        except Permission.DoesNotExist:
            print(f"  [WARN] No se encontró permiso view_{model_name}")
            
    lectores_group.permissions.set(permissions_lectores)
    print(f"  -> Asignados {len(permissions_lectores)} permisos a Lectores.")

    print("✅ Configuración de roles completada con éxito.")

if __name__ == '__main__':
    setup_roles()

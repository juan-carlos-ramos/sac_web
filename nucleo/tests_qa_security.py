from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from nucleo.models import Inmueble, Proveedor, Factura, Gasto
from django.urls import reverse
from decimal import Decimal

class SecurityQATest(TestCase):
    def setUp(self):
        # Crear superusuario para las pruebas
        self.user = User.objects.create_superuser(username='testadmin', password='password123', email='test@test.com')
        self.client = Client()
        self.client.login(username='testadmin', password='password123')
        
        # Crear objetos de prueba
        self.inmueble = Inmueble.objects.create(numero_apto='QA-101', propietario='QA Propietario', alicuota=Decimal('0.10'))
        self.proveedor = Proveedor.objects.create(nombre='QA Proveedor', rif='J-12345678-9')
        self.factura = Factura.objects.create(periodo='2025-01')
        self.gasto = Gasto.objects.create(factura=self.factura, descripcion='Gasto QA', monto=Decimal('100.00'))
        self.other_user = User.objects.create_user(username='otheruser', password='password123')

    def test_eliminar_inmueble_requires_post(self):
        """Verifica que eliminar_inmueble rechaza GET (405) y solo permite POST."""
        url = reverse('nucleo:eliminar_inmueble', args=[self.inmueble.id])
        # Intentar por GET -> Debe rechazar con 405
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Inmueble.objects.filter(id=self.inmueble.id).exists())
        
        # Intentar por POST -> Debe ejecutar y redirigir
        post_response = self.client.post(url)
        self.assertEqual(post_response.status_code, 302)
        self.assertFalse(Inmueble.objects.filter(id=self.inmueble.id).exists())

    def test_eliminar_proveedor_requires_post(self):
        """Verifica que eliminar_proveedor rechaza GET (405) y solo permite POST."""
        url = reverse('nucleo:eliminar_proveedor', args=[self.proveedor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Proveedor.objects.filter(id=self.proveedor.id).exists())
        
        post_response = self.client.post(url)
        self.assertEqual(post_response.status_code, 302)
        self.assertFalse(Proveedor.objects.filter(id=self.proveedor.id).exists())

    def test_eliminar_gasto_requires_post(self):
        """Verifica que eliminar_gasto rechaza GET (405) y solo permite POST."""
        url = reverse('nucleo:eliminar_gasto', args=[self.gasto.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Gasto.objects.filter(id=self.gasto.id).exists())
        
        post_response = self.client.post(url)
        self.assertEqual(post_response.status_code, 302)
        self.assertFalse(Gasto.objects.filter(id=self.gasto.id).exists())

    def test_toggle_usuario_activo_requires_post(self):
        """Verifica que toggle_usuario_activo rechaza GET (405) y solo permite POST."""
        initial_status = self.other_user.is_active
        url = reverse('nucleo:toggle_usuario_activo', args=[self.other_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.other_user.refresh_from_db()
        self.assertEqual(initial_status, self.other_user.is_active)
        
        post_response = self.client.post(url)
        self.assertEqual(post_response.status_code, 302)
        self.other_user.refresh_from_db()
        self.assertNotEqual(initial_status, self.other_user.is_active)

    def test_calcular_alicuotas_is_protected(self):
        """Verifica que calcular_alicuotas_automatico rechaza GET (405) y requiere POST."""
        url = reverse('nucleo:calcular_alicuotas')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        
        post_response = self.client.post(url)
        self.assertEqual(post_response.status_code, 302)

# tests.py
from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from .services import get_ip_geolocation

class GeolocationTests(TestCase):
    def test_public_ip(self):
        ip = '190.18.134.56'
        data = get_ip_geolocation(ip)
        self.assertIsNotNone(data)
        self.assertIn('country', data)
        self.assertEqual(data['country'], 'AR')

    def test_private_ip(self):
        ip = '192.168.1.1'
        data = get_ip_geolocation(ip)
        self.assertIsNone(data)
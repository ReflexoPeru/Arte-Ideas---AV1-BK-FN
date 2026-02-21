from django.test import TestCase, Client


class AgendaURLsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_demo_html_page_serves(self):
        resp = self.client.get('/api/crm/agenda/demo/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Próximos Eventos', resp.content.decode('utf-8'))

    def test_demo_api_public(self):
        resp = self.client.get('/api/crm/agenda/proximos-eventos-demo/')
        self.assertEqual(resp.status_code, 200)
        import json
        payload = json.loads(resp.content.decode('utf-8'))
        self.assertIn('eventos', payload)

    def test_protected_list_requires_auth(self):
        # Sin autenticación debe responder 401 por configuración de DRF
        resp = self.client.get('/api/crm/agenda/eventos/')
        self.assertIn(resp.status_code, (401, 403))
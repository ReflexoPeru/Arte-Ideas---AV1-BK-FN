"""
Tests para el CRM App - Arte Ideas
Tests para el modelo Client
"""
import json
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.core.models import Tenant
from .models import Client, Contract

User = get_user_model()


class BaseCRMTestCase(APITestCase):
    """Clase base para tests del CRM app"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear tenant de prueba
        self.tenant = Tenant.objects.create(
            name='Estudio de Prueba',
            business_name='Estudio Fotográfico Prueba S.A.C.',
            ruc='12345678901',
            phone='123456789',
            email='prueba@estudio.com',
            address='Av. Prueba 123'
        )
        
        # Crear usuarios de prueba
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            tenant=self.tenant
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='testpass123',
            role='employee',
            tenant=self.tenant
        )


class ClientModelTest(BaseCRMTestCase):
    """Tests para el modelo Client"""
    
    def test_create_client_particular(self):
        """Test crear cliente particular"""
        client = Client.objects.create(
            tenant=self.tenant,
            client_type='particular',
            first_name='Juan',
            last_name='Pérez',
            email='juan@test.com',
            phone='987654321',
            dni='12345678'
        )
        
        self.assertEqual(client.client_type, 'particular')
        self.assertEqual(client.first_name, 'Juan')
        self.assertEqual(client.last_name, 'Pérez')
        self.assertEqual(client.dni, '12345678')
        self.assertEqual(client.email, 'juan@test.com')
    
    def test_create_client_empresa(self):
        """Test crear cliente empresa"""
        client = Client.objects.create(
            tenant=self.tenant,
            client_type='empresa',
            first_name='María',
            last_name='Gómez',
            email='maria@empresa.com',
            phone='987654322',
            dni='87654321',
            company_name='Empresa Test S.A.C.',
            ruc='98765432109'
        )
        
        self.assertEqual(client.client_type, 'empresa')
        self.assertEqual(client.company_name, 'Empresa Test S.A.C.')
        self.assertEqual(client.ruc, '98765432109')
    
    def test_create_client_colegio(self):
        """Test crear cliente colegio"""
        client = Client.objects.create(
            tenant=self.tenant,
            client_type='colegio',
            first_name='Colegio',
            last_name='San José',
            email='colegio@sanjose.edu.pe',
            phone='123456789',
            dni='11111111',
            school_level='secundaria',
            school_grade='3ro',
            school_section='A'
        )
        
        self.assertEqual(client.client_type, 'colegio')
        self.assertEqual(client.school_level, 'secundaria')
        self.assertEqual(client.school_grade, '3ro')
        self.assertEqual(client.school_section, 'A')
    
    def test_client_str_method(self):
        """Test método string del cliente"""
        client = Client.objects.create(
            tenant=self.tenant,
            client_type='particular',
            first_name='Ana',
            last_name='López',
            email='ana@test.com',
            phone='987654323',
            dni='22222222'
        )
        
        expected_str = "Ana López (DNI: 22222222)"
        self.assertEqual(str(client), expected_str)
    
    def test_client_empresa_str_method(self):
        """Test método string del cliente empresa"""
        client = Client.objects.create(
            tenant=self.tenant,
            client_type='empresa',
            first_name='Carlos',
            last_name='Ruiz',
            email='carlos@empresa.com',
            phone='987654324',
            dni='33333333',
            company_name='Empresa Ejemplo S.A.',
            ruc='11223344556'
        )
        
        expected_str = "Carlos Ruiz - Empresa Ejemplo S.A. (RUC: 11223344556)"
        self.assertEqual(str(client), expected_str)
    
    def test_client_validation_dni_format(self):
        """Test validación de formato DNI"""
        # DNI válido
        client = Client(
            tenant=self.tenant,
            client_type='particular',
            first_name='Test',
            last_name='User',
            email='test@test.com',
            phone='123456789',
            dni='12345678'  # 8 dígitos
        )
        
        # No debería lanzar excepción
        client.full_clean()
        client.save()
        
        # DNI inválido (muy corto)
        client_invalid = Client(
            tenant=self.tenant,
            client_type='particular',
            first_name='Test',
            last_name='Invalid',
            email='invalid@test.com',
            phone='123456789',
            dni='123'  # Muy corto
        )
        
        # Debería lanzar excepción al validar
        with self.assertRaises(Exception):
            client_invalid.full_clean()
    
    def test_client_validation_ruc_format(self):
        """Test validación de formato RUC"""
        # RUC válido
        client = Client(
            tenant=self.tenant,
            client_type='empresa',
            first_name='Test',
            last_name='Empresa',
            email='empresa@test.com',
            phone='123456789',
            dni='12345678',
            company_name='Test S.A.C.',
            ruc='12345678901'  # 11 dígitos
        )
        
        # No debería lanzar excepción
        client.full_clean()
        client.save()
        
        # RUC inválido (muy corto)
        client_invalid = Client(
            tenant=self.tenant,
            client_type='empresa',
            first_name='Test',
            last_name='Invalid',
            email='invalid@test.com',
            phone='123456789',
            dni='12345678',
            company_name='Invalid S.A.C.',
            ruc='123'  # Muy corto
        )
        
        # Debería lanzar excepción al validar
        with self.assertRaises(Exception):
            client_invalid.full_clean()
    
    def test_client_validation_required_fields_particular(self):
        """Test validación de campos requeridos para cliente particular"""
        # Cliente particular sin DNI
        client = Client(
            tenant=self.tenant,
            client_type='particular',
            first_name='Test',
            last_name='SinDNI',
            email='sindni@test.com',
            phone='123456789'
            # Falta dni
        )
        
        # Debería lanzar excepción al validar
        with self.assertRaises(Exception):
            client.full_clean()
    
    def test_client_validation_required_fields_empresa(self):
        """Test validación de campos requeridos para cliente empresa"""
        # Cliente empresa sin RUC ni nombre de empresa
        client = Client(
            tenant=self.tenant,
            client_type='empresa',
            first_name='Test',
            last_name='SinEmpresa',
            email='sinempresa@test.com',
            phone='123456789',
            dni='12345678'
            # Falta company_name y ruc
        )
        
        # Debería lanzar excepción al validar
        with self.assertRaises(Exception):
            client.full_clean()
    
    def test_client_validation_required_fields_colegio(self):
        """Test validación de campos requeridos para cliente colegio"""
        # Cliente colegio sin nivel, grado y sección
        client = Client(
            tenant=self.tenant,
            client_type='colegio',
            first_name='Test',
            last_name='SinColegio',
            email='sincolegio@test.com',
            phone='123456789',
            dni='12345678'
            # Falta school_level, school_grade, school_section
        )
        
        # Debería lanzar excepción al validar
        with self.assertRaises(Exception):
            client.full_clean()


class ContractModelTest(BaseCRMTestCase):
    """Tests para el modelo Contract"""
    
    def setUp(self):
        super().setUp()
        self.client = Client.objects.create(
            tenant=self.tenant,
            client_type='empresa',
            first_name='Contract',
            last_name='Test',
            email='contract@test.com',
            phone='123456789',
            dni='12345678',
            company_name='Contract S.A.C.',
            ruc='12345678901'
        )
    
    def test_create_contract(self):
        """Test crear contrato"""
        contract = Contract.objects.create(
            tenant=self.tenant,
            client=self.client,
            contract_number='CONT-001',
            title='Contrato de Servicios Fotográficos',
            description='Contrato para servicios fotográficos anuales',
            start_date='2024-01-01',
            end_date='2024-12-31',
            total_amount=5000.00,
            status='active'
        )
        
        self.assertEqual(contract.contract_number, 'CONT-001')
        self.assertEqual(contract.title, 'Contrato de Servicios Fotográficos')
        self.assertEqual(contract.total_amount, 5000.00)
        self.assertEqual(contract.status, 'active')
    
    def test_contract_str_method(self):
        """Test método string del contrato"""
        contract = Contract.objects.create(
            tenant=self.tenant,
            client=self.client,
            contract_number='CONT-002',
            title='Contrato Test',
            description='Contrato de prueba',
            start_date='2024-01-01',
            end_date='2024-12-31',
            total_amount=1000.00,
            status='pending'
        )
        
        expected_str = "CONT-002 - Contrato Test - S/.1000.00"
        self.assertEqual(str(contract), expected_str)
    
    def test_contract_date_validation(self):
        """Test validación de fechas del contrato"""
        # Contrato con fecha fin anterior a fecha inicio
        contract = Contract(
            tenant=self.tenant,
            client=self.client,
            contract_number='CONT-INVALID',
            title='Contrato Inválido',
            description='Contrato con fechas inválidas',
            start_date='2024-12-31',
            end_date='2024-01-01',  # Fecha fin anterior a inicio
            total_amount=1000.00,
            status='pending'
        )
        
        # Debería lanzar excepción al validar
        with self.assertRaises(Exception):
            contract.full_clean()


class ClientAPITest(BaseCRMTestCase):
    """Tests para la API de clientes"""
    
    def setUp(self):
        super().setUp()
        self.client_api = APIClient()
        self.client_api.force_authenticate(user=self.admin)
        
        # Crear cliente de prueba
        self.test_client = Client.objects.create(
            tenant=self.tenant,
            client_type='particular',
            first_name='Test',
            last_name='API',
            email='testapi@test.com',
            phone='987654321',
            dni='12345678'
        )
        
        self.client_list_url = reverse('crm:client-list')
    
    def test_list_clients(self):
        """Test listar clientes"""
        response = self.client_api.get(self.client_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Test')
    
    def test_create_client_particular(self):
        """Test crear cliente particular via API"""
        client_data = {
            'client_type': 'particular',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juanapi@test.com',
            'phone': '987654321',
            'dni': '12345678'
        }
        
        response = self.client_api.post(
            self.client_list_url,
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Juan')
        self.assertEqual(response.data['last_name'], 'Pérez')
        self.assertEqual(response.data['dni'], '12345678')
    
    def test_create_client_empresa(self):
        """Test crear cliente empresa via API"""
        client_data = {
            'client_type': 'empresa',
            'first_name': 'María',
            'last_name': 'Gómez',
            'email': 'mariaapi@empresa.com',
            'phone': '987654322',
            'dni': '87654321',
            'company_name': 'Empresa API S.A.C.',
            'ruc': '98765432109'
        }
        
        response = self.client_api.post(
            self.client_list_url,
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['company_name'], 'Empresa API S.A.C.')
        self.assertEqual(response.data['ruc'], '98765432109')
    
    def test_create_client_colegio(self):
        """Test crear cliente colegio via API"""
        client_data = {
            'client_type': 'colegio',
            'first_name': 'Colegio',
            'last_name': 'API',
            'email': 'colegioapi@sanjose.edu.pe',
            'phone': '123456789',
            'dni': '11111111',
            'school_level': 'primaria',
            'school_grade': '5to',
            'school_section': 'A'
        }
        
        response = self.client_api.post(
            self.client_list_url,
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['school_level'], 'primaria')
        self.assertEqual(response.data['school_grade'], '5to')
        self.assertEqual(response.data['school_section'], 'A')
    
    def test_create_client_with_invalid_data(self):
        """Test crear cliente con datos inválidos"""
        # Cliente particular sin DNI
        client_data = {
            'client_type': 'particular',
            'first_name': 'Invalid',
            'last_name': 'Client',
            'email': 'invalid@test.com',
            'phone': '123456789'
            # Falta dni
        }
        
        response = self.client_api.post(
            self.client_list_url,
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_client(self):
        """Test actualizar cliente"""
        client_detail_url = reverse('crm:client-detail', kwargs={'pk': self.test_client.id})
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Client',
            'email': 'updated@test.com',
            'phone': '999999999',
            'dni': '12345678'
        }
        
        response = self.client_api.put(
            client_detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['email'], 'updated@test.com')
    
    def test_delete_client(self):
        """Test eliminar cliente"""
        client_detail_url = reverse('crm:client-detail', kwargs={'pk': self.test_client.id})
        
        response = self.client_api.delete(client_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar que fue eliminado
        response = self.client_api.get(client_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_client_permissions_by_role(self):
        """Test permisos según rol de usuario"""
        # Employee debería poder listar y crear clientes
        self.client_api.force_authenticate(user=self.employee)
        
        response = self.client_api.get(self.client_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        client_data = {
            'client_type': 'particular',
            'first_name': 'Employee',
            'last_name': 'Client',
            'email': 'employee@test.com',
            'phone': '123456789',
            'dni': '12345678'
        }
        
        response = self.client_api.post(
            self.client_list_url,
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ContractAPITest(BaseCRMTestCase):
    """Tests para la API de contratos"""
    
    def setUp(self):
        super().setUp()
        self.client_api = APIClient()
        self.client_api.force_authenticate(user=self.admin)
        
        # Crear cliente de prueba
        self.test_client = Client.objects.create(
            tenant=self.tenant,
            client_type='empresa',
            first_name='Contract',
            last_name='Test',
            email='contract@test.com',
            phone='123456789',
            dni='12345678',
            company_name='Contract S.A.C.',
            ruc='12345678901'
        )
        
        # Crear contrato de prueba
        self.test_contract = Contract.objects.create(
            tenant=self.tenant,
            client=self.test_client,
            contract_number='CONT-TEST',
            title='Contrato de Prueba',
            description='Descripción del contrato de prueba',
            start_date='2024-01-01',
            end_date='2024-12-31',
            total_amount=1000.00,
            status='active'
        )
        
        self.contract_list_url = reverse('crm:contract-list')
    
    def test_list_contracts(self):
        """Test listar contratos"""
        response = self.client_api.get(self.contract_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['contract_number'], 'CONT-TEST')
    
    def test_create_contract(self):
        """Test crear contrato via API"""
        contract_data = {
            'client': self.test_client.id,
            'contract_number': 'CONT-API',
            'title': 'Contrato API',
            'description': 'Contrato creado via API',
            'start_date': '2024-02-01',
            'end_date': '2024-12-31',
            'total_amount': 2500.00,
            'status': 'pending'
        }
        
        response = self.client_api.post(
            self.contract_list_url,
            data=json.dumps(contract_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['contract_number'], 'CONT-API')
        self.assertEqual(response.data['total_amount'], 2500.00)
    
    def test_create_contract_with_invalid_dates(self):
        """Test crear contrato con fechas inválidas"""
        contract_data = {
            'client': self.test_client.id,
            'contract_number': 'CONT-INVALID',
            'title': 'Contrato Inválido',
            'description': 'Contrato con fechas inválidas',
            'start_date': '2024-12-31',
            'end_date': '2024-01-01',  # Fecha fin anterior a inicio
            'total_amount': 1000.00,
            'status': 'pending'
        }
        
        response = self.client_api.post(
            self.contract_list_url,
            data=json.dumps(contract_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_contract(self):
        """Test actualizar contrato"""
        contract_detail_url = reverse('crm:contract-detail', kwargs={'pk': self.test_contract.id})
        
        update_data = {
            'client': self.test_client.id,
            'contract_number': 'CONT-UPDATED',
            'title': 'Contrato Actualizado',
            'description': 'Descripción actualizada',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'total_amount': 1500.00,
            'status': 'active'
        }
        
        response = self.client_api.put(
            contract_detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contract_number'], 'CONT-UPDATED')
        self.assertEqual(response.data['total_amount'], 1500.00)


class ClientSearchTest(BaseCRMTestCase):
    """Tests para búsqueda y filtrado de clientes"""
    
    def setUp(self):
        super().setUp()
        self.client_api = APIClient()
        self.client_api.force_authenticate(user=self.admin)
        
        # Crear varios clientes de prueba
        Client.objects.create(
            tenant=self.tenant,
            client_type='particular',
            first_name='Juan',
            last_name='Pérez',
            email='juan@test.com',
            phone='987654321',
            dni='12345678'
        )
        
        Client.objects.create(
            tenant=self.tenant,
            client_type='empresa',
            first_name='María',
            last_name='Gómez',
            email='maria@empresa.com',
            phone='987654322',
            dni='87654321',
            company_name='Empresa Test S.A.C.',
            ruc='98765432109'
        )
        
        Client.objects.create(
            tenant=self.tenant,
            client_type='colegio',
            first_name='Colegio',
            last_name='San José',
            email='colegio@sanjose.edu.pe',
            phone='123456789',
            dni='11111111',
            school_level='primaria',
            school_grade='5to',
            school_section='A'
        )
        
        self.client_list_url = reverse('crm:client-list')
    
    def test_search_clients_by_name(self):
        """Test búsqueda de clientes por nombre"""
        response = self.client_api.get(self.client_list_url, {'search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Juan')
    
    def test_filter_clients_by_type(self):
        """Test filtrado de clientes por tipo"""
        response = self.client_api.get(self.client_list_url, {'client_type': 'particular'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['client_type'], 'particular')
        
        response = self.client_api.get(self.client_list_url, {'client_type': 'empresa'})
        self.assertEqual(response.data['results'][0]['client_type'], 'empresa')
        
        response = self.client_api.get(self.client_list_url, {'client_type': 'colegio'})
        self.assertEqual(response.data['results'][0]['client_type'], 'colegio')
    
    def test_filter_clients_by_school_level(self):
        """Test filtrado de clientes colegio por nivel"""
        response = self.client_api.get(self.client_list_url, {
            'client_type': 'colegio',
            'school_level': 'primaria'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['school_level'], 'primaria')
    
    def test_search_clients_by_email(self):
        """Test búsqueda de clientes por email"""
        response = self.client_api.get(self.client_list_url, {'search': 'maria@empresa.com'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], 'maria@empresa.com')
    
    def test_search_clients_by_phone(self):
        """Test búsqueda de clientes por teléfono"""
        response = self.client_api.get(self.client_list_url, {'search': '987654321'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['phone'], '987654321')
    
    def test_search_clients_by_dni(self):
        """Test búsqueda de clientes por DNI"""
        response = self.client_api.get(self.client_list_url, {'search': '12345678'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['dni'], '12345678')
    
    def test_search_clients_by_company_name(self):
        """Test búsqueda de clientes empresa por nombre de empresa"""
        response = self.client_api.get(self.client_list_url, {'search': 'Empresa Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['company_name'], 'Empresa Test S.A.C.')


class ClientIntegrationTest(BaseCRMTestCase):
    """Tests de integración para el flujo completo de gestión de clientes"""
    
    def setUp(self):
        super().setUp()
        self.client_api = APIClient()
        self.client_api.force_authenticate(user=self.admin)
        
        self.client_list_url = reverse('crm:client-list')
        self.contract_list_url = reverse('crm:contract-list')
    
    def test_complete_client_workflow(self):
        """Test flujo completo de creación y gestión de cliente"""
        # 1. Crear cliente
        client_data = {
            'client_type': 'empresa',
            'first_name': 'Integración',
            'last_name': 'Test',
            'email': 'integracion@test.com',
            'phone': '987654321',
            'dni': '12345678',
            'company_name': 'Integración S.A.C.',
            'ruc': '12345678901'
        }
        
        response = self.client_api.post(
            self.client_list_url,
            data=json.dumps(client_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        client_id = response.data['id']
        
        # 2. Verificar que el cliente fue creado
        client_detail_url = reverse('crm:client-detail', kwargs={'pk': client_id})
        response = self.client_api.get(client_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Integración S.A.C.')
        
        # 3. Crear contrato para el cliente
        contract_data = {
            'client': client_id,
            'contract_number': 'CONT-INTEGRACION',
            'title': 'Contrato de Integración',
            'description': 'Contrato creado en el test de integración',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'total_amount': 5000.00,
            'status': 'active'
        }
        
        response = self.client_api.post(
            self.contract_list_url,
            data=json.dumps(contract_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        contract_id = response.data['id']
        
        # 4. Verificar que el contrato fue creado
        contract_detail_url = reverse('crm:contract-detail', kwargs={'pk': contract_id})
        response = self.client_api.get(contract_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_amount'], 5000.00)
        
        # 5. Actualizar cliente
        update_data = {
            'client_type': 'empresa',
            'first_name': 'Integración',
            'last_name': 'Actualizada',
            'email': 'actualizada@test.com',
            'phone': '999999999',
            'dni': '12345678',
            'company_name': 'Integración Actualizada S.A.C.',
            'ruc': '12345678901'
        }
        
        response = self.client_api.put(
            client_detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['last_name'], 'Actualizada')
        self.assertEqual(response.data['email'], 'actualizada@test.com')
        
        # 6. Buscar cliente por nombre
        response = self.client_api.get(self.client_list_url, {'search': 'Integración'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Integración')
        
        # 7. Filtrar clientes por tipo
        response = self.client_api.get(self.client_list_url, {'client_type': 'empresa'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        # 8. Eliminar contrato
        response = self.client_api.delete(contract_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 9. Eliminar cliente
        response = self.client_api.delete(client_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 10. Verificar que fueron eliminados
        response = self.client_api.get(client_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client_api.get(contract_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
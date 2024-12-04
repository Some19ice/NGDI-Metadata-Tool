# pylint: disable=C0115, E1101, C0114, C0303, C0301, W0613, C0116, W0611

from datetime import datetime
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Metadata, IdentificationInfo

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="test@example.com",
            name="Test User",
            password="testpass123",
            role="USER",
            organization="Test Org"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.role, "USER")

    def test_metadata_creation(self):
        metadata = Metadata.objects.create(
            status="DRAFT",
            user=self.user,
            metadata_linkage="http://example.com",
            metadata_standard="ISO 19115"
        )
        self.assertEqual(metadata.status, "DRAFT")
        self.assertEqual(metadata.user, self.user)

class APITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            name="Test User",
            password="testpass123",
            role="USER",
            organization="Test Org"
        )
        self.client.force_authenticate(user=self.user)

    def test_metadata_crud(self):
        # Test Create
        create_data = {
            'status': 'DRAFT',
            'metadata_standard': 'ISO 19115',
            'metadata_linkage': 'http://example.com',
            'identification': {
                'title': 'Test Dataset',
                'abstract': 'Test abstract description',
                'spatial_rep_type': 'VECTOR',
                'production_date': timezone.now().isoformat(),
                'geographic_bounding_box': {
                    'north': 90.0,
                    'south': -90.0,
                    'east': 180.0,
                    'west': -180.0
                }
            },
            'distribution': {
                'name': 'Test Distribution',
                'address': 'Test Address',
                'distributor_email': 'test@example.com'
            },
            'lineage': {
                'statement': 'Test Lineage Statement',
                'hierarchy_level': 1
            },
            'reference_system': {
                'identifier': 'EPSG:4326',
                'code': 'WGS 84'
            },
            'contact': {
                'name': 'Test Contact',
                'organization': 'Test Org',
                'email': 'contact@example.com',
                'role': 'maintainer'
            },
            'quality': {
                'completeness_report': 'Test Quality Report'
            }
        }
        response = self.client.post('/api/metadata/', create_data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        metadata_id = response.data['id']

        # Test Read
        response = self.client.get(f'/api/metadata/{metadata_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'DRAFT')
        self.assertEqual(response.data['identification']['title'], 'Test Dataset')

        # Test Update (using PATCH instead of PUT)
        update_data = {
            'identification': {
                'title': 'Updated Dataset',
                'abstract': 'Updated abstract description'
            },
            'distribution': {
                'name': 'Updated Distribution'
            }
        }
        response = self.client.patch(f'/api/metadata/{metadata_id}/', update_data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print("Update response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['identification']['title'], 'Updated Dataset')
        self.assertEqual(response.data['distribution']['name'], 'Updated Distribution')

        # Test Delete
        response = self.client.delete(f'/api/metadata/{metadata_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_metadata_filters(self):
        # Create test metadata records
        Metadata.objects.create(
            status="DRAFT",
            user=self.user,
            created_at=timezone.now() - timezone.timedelta(days=10)
        )
        Metadata.objects.create(
            status="PUBLISHED",
            user=self.user,
            created_at=timezone.now()
        )

        # Test status filter
        response = self.client.get('/api/metadata/?status=DRAFT')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test date range filter
        start_date = (timezone.now() - timezone.timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        response = self.client.get(
            f'/api/metadata/?start_date={start_date}&end_date={end_date}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class UserAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            name="Admin User",
            password="adminpass123",
            role="ADMIN",
            organization="Test Org"
        )
        self.regular_user = User.objects.create_user(
            email="user@example.com",
            name="Regular User",
            password="userpass123",
            role="USER",
            organization="Test Org"
        )

    def test_user_list_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should see all users

    def test_user_list_regular(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only see themselves

    def test_user_create(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'newpass123',
            'role': 'USER',
            'organization': 'Test Org'
        }
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

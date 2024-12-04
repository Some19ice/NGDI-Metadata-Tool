# pylint: disable=C0115, E1101, C0114, C0303, C0301, W0613, C0116, W0611

from datetime import datetime
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status


from .models import (
    User, Metadata, IdentificationInfo, PointOfContact,
    ResourceConstraints, Distribution, ResourceLineage,
    ReferenceSystem, MetadataContact, DataQuality,
    TemporalExtent
)

from .serializers import MetadataSerializer

class ModelTests(TestCase):
    def setUp(self):
        # Create base user
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

    def test_identification_info_creation(self):
        metadata = Metadata.objects.create(
            status="DRAFT",
            user=self.user
        )
        identification = IdentificationInfo.objects.create(
            title="Test Dataset",
            production_date=timezone.now(),
            abstract="Test abstract",
            spatial_rep_type="VECTOR",
            metadata=metadata,
            geographic_bounding_box={
                'north': 90.0,
                'south': -90.0,
                'east': 180.0,
                'west': -180.0
            }
        )
        self.assertEqual(identification.title, "Test Dataset")
        self.assertEqual(identification.spatial_rep_type, "VECTOR")

class APITests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create(
            email="test@example.com",
            name="Test User",
            password="testpass123",
            role="USER",
            organization="Test Org"
        )
        self.client.force_authenticate(user=self.user)

        # Create test metadata
        self.metadata = Metadata.objects.create(
            status="DRAFT",
            user=self.user
        )

    def test_user_list(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_metadata_list(self):
        url = reverse('metadata-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_metadata_create(self):
        url = reverse('metadata-list')
        data = {
            'status': 'DRAFT',
            'metadata_linkage': 'http://example.com',
            'metadata_standard': 'ISO 19115',
            'identification': {
                'title': 'Test Dataset',
                'production_date': datetime.now().isoformat(),
                'abstract': 'Test abstract',
                'spatial_rep_type': 'VECTOR',
                'geographic_bounding_box': {
                    'north': 90.0,
                    'south': -90.0,
                    'east': 180.0,
                    'west': -180.0
                }
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_metadata_publish(self):
        url = reverse('metadata-publish', kwargs={'pk': self.metadata.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.metadata.refresh_from_db()
        self.assertEqual(self.metadata.status, 'PUBLISHED')

class SerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="test@example.com",
            name="Test User",
            password="testpass123",
            role="USER",
            organization="Test Org"
        )

    def test_metadata_serializer_validation(self):
        
        
        # Test invalid data
        invalid_data = {
            'status': 'INVALID_STATUS',
        }
        serializer = MetadataSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

        # Test valid data
        valid_data = {
            'status': 'DRAFT',
            'metadata_linkage': 'http://example.com',
            'metadata_standard': 'ISO 19115'
        }
        serializer = MetadataSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

class ViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="test@example.com",
            name="Test User",
            password="testpass123",
            role="ADMIN",
            organization="Test Org"
        )
        self.client.force_authenticate(user=self.user)

    def test_metadata_filters(self):
        # Get current time
        now = timezone.now()
        ten_days_ago = now - timezone.timedelta(days=10)
        
        # Create test metadata with different dates
        Metadata.objects.create(
            status="DRAFT",
            user=self.user,
            created_at=ten_days_ago
        )
        Metadata.objects.create(
            status="PUBLISHED",
            user=self.user,
            created_at=now
        )

        # Test status filter
        url = reverse('metadata-list') + '?status=DRAFT'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test date range filter
        start_date = (now - timezone.timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')
        url = reverse('metadata-list') + f'?start_date={start_date}&end_date={end_date}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only get the recent metadata

    def test_bulk_operations(self):
        # Test bulk create
        url = reverse('metadata-bulk-create')
        data = [
            {
                'status': 'DRAFT',
                'metadata_standard': 'ISO 19115'
            },
            {
                'status': 'DRAFT',
                'metadata_standard': 'ISO 19115-2'
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)

        # Get created metadata IDs
        metadata_ids = [item['id'] for item in response.data]

        # Test individual updates instead of bulk update
        for metadata_id in metadata_ids:
            url = reverse('metadata-detail', kwargs={'pk': metadata_id})
            update_data = {
                'status': 'PUBLISHED'
            }
            response = self.client.patch(url, update_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['status'], 'PUBLISHED')

        # Test bulk delete
        url = reverse('metadata-bulk-delete')
        delete_data = {'ids': metadata_ids}
        response = self.client.post(url, delete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 2)

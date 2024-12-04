# pylint: disable=C0115, E1101, C0114, W0613

from datetime import datetime, timedelta
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import (
    User, Metadata, IdentificationInfo, PointOfContact,
    ResourceConstraints, Distribution, ResourceLineage,
    ReferenceSystem, MetadataContact, DataQuality,
    TemporalExtent
)
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database population...')

        try:
            with transaction.atomic():
                # Create users
                users = self._create_users()
                
                # Create metadata records
                self._create_metadata_records(users)

            self.stdout.write(self.style.SUCCESS('Successfully populated database'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error populating database: {str(e)}'))

    def _create_users(self):
        users = []
        organizations = ['NASA', 'ESA', 'JAXA', 'ISRO', 'CNSA']

        # Create admin user
        admin = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='admin123',
            organization='Admin Org',
            role='ADMIN'
        )
        users.append(admin)

        # Create regular users
        for i in range(5):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                name=f'Test User {i}',
                password='password123',
                role='USER',
                organization=random.choice(organizations)
            )
            users.append(user)

        return users

    def _create_metadata_records(self, users):
        statuses = ['DRAFT', 'PUBLISHED', 'ARCHIVED']
        spatial_types = ['VECTOR', 'RASTER']

        for user in users:
            for i in range(3):  # 3 metadata records per user
                # Create base metadata
                metadata = Metadata.objects.create(
                    status=random.choice(statuses),
                    user=user,
                    metadata_linkage=f'http://example.com/metadata/{user.id}/{i}',
                    metadata_standard='ISO 19115'
                )

                # Create identification info with all required fields
                identification = IdentificationInfo.objects.create(
                    metadata=metadata,
                    title=f'Dataset {i} by {user.name}',
                    production_date=timezone.now() - timedelta(days=random.randint(1, 365)),
                    abstract='This is a detailed abstract describing the dataset, its purpose, and key characteristics.',
                    spatial_rep_type=random.choice(spatial_types),
                    geographic_bounding_box={
                        'north': random.uniform(0, 90),
                        'south': random.uniform(-90, 0),
                        'east': random.uniform(0, 180),
                        'west': random.uniform(-180, 0)
                    },
                    keywords=['sample', 'test', 'data', user.organization.lower()]
                )

                # Create point of contact
                PointOfContact.objects.create(
                    identification_info=identification,
                    name=f'Contact for {user.name}',
                    organization=user.organization,
                    email=f'contact_{user.id}@example.com',
                    phone='+1234567890',
                    address='123 Test Street, Test City',
                    role='maintainer'
                )

                # Create constraints
                ResourceConstraints.objects.create(
                    identification_info=identification,
                    access_constraints='Sample access constraints',
                    use_constraints='Sample use constraints',
                    other_constraints='Additional usage restrictions apply'
                )

                # Create distribution
                Distribution.objects.create(
                    metadata=metadata,
                    name=f'Distribution for {metadata.id}',
                    address='Distribution Center, 456 Data Street',
                    phone_no='+1987654321',
                    weblink='http://example.com/download',
                    format='GeoTIFF',
                    distributor_email=user.email,
                    order_process='Contact distributor via email'
                )

                # Create lineage
                ResourceLineage.objects.create(
                    metadata=metadata,
                    statement='Detailed lineage statement describing data history',
                    hierarchy_level=1,
                    process_software='QGIS 3.22',
                    process_date=timezone.now() - timedelta(days=random.randint(1, 30))
                )

                # Create reference system
                ReferenceSystem.objects.create(
                    metadata=metadata,
                    identifier='EPSG:4326',
                    code='WGS 84'
                )

                # Create metadata contact
                MetadataContact.objects.create(
                    metadata=metadata,
                    name=user.name,
                    organization=user.organization,
                    email=user.email,
                    phone='+1234567890',
                    address='789 Contact Street',
                    role='author',
                    weblink='http://example.com/contact'
                )

                # Create data quality
                DataQuality.objects.create(
                    metadata=metadata,
                    completeness_report='Detailed completeness analysis report',
                    accuracy_report='Comprehensive accuracy assessment',
                    process_description='Data processing methodology',
                    process_date=timezone.now() - timedelta(days=random.randint(1, 15))
                )

                # Create temporal extent
                TemporalExtent.objects.create(
                    identification_info=identification,
                    start_date=timezone.now() - timedelta(days=365),
                    end_date=timezone.now(),
                    frequency='monthly'
                )
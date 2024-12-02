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
        roles = ['ADMIN', 'USER']
        organizations = ['NASA', 'ESA', 'JAXA', 'ISRO', 'CNSA']

        # Create admin user
        admin = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='admin123',
            organization='Admin Org'
        )
        users.append(admin)

        # Create regular users
        for i in range(5):
            user = User.objects.create_user(
                email=f'user{i}@example.com',
                name=f'Test User {i}',
                password='password123',
                role=random.choice(roles),
                organization=random.choice(organizations)
            )
            users.append(user)

        return users

    def _create_metadata_records(self, users):
        statuses = ['DRAFT', 'PUBLISHED', 'ARCHIVED']
        spatial_types = ['VECTOR', 'RASTER']

        for user in users:
            for _ in range(3):  # 3 metadata records per user
                # Create metadata
                metadata = Metadata.objects.create(
                    status=random.choice(statuses),
                    user=user,
                    metadata_linkage=f'http://example.com/metadata/{user.id}',
                    metadata_standard='ISO 19115'
                )

                # Create identification info
                identification = IdentificationInfo.objects.create(
                    metadata=metadata,
                    title=f'Dataset by {user.name}',
                    production_date=timezone.now() - timedelta(days=random.randint(1, 365)),
                    abstract='Sample dataset for testing purposes',
                    spatial_rep_type=random.choice(spatial_types),
                    geographic_bounding_box={
                        'north': random.uniform(0, 90),
                        'south': random.uniform(-90, 0),
                        'east': random.uniform(0, 180),
                        'west': random.uniform(-180, 0)
                    }
                )

                # Create point of contact
                PointOfContact.objects.create(
                    identification_info=identification,
                    name=f'Contact for {user.name}',
                    organization=user.organization,
                    email=f'contact_{user.id}@example.com',
                    phone='+1234567890',
                    role='CUSTODIAN'
                )

                # Create constraints
                ResourceConstraints.objects.create(
                    identification_info=identification,
                    access_constraints='Sample access constraints',
                    use_constraints='Sample use constraints'
                )

                # Create distribution
                Distribution.objects.create(
                    metadata=metadata,
                    name=f'Distribution for {metadata.id}',
                    format='GeoTIFF',
                    distributor_email=user.email
                )

                # Create lineage
                ResourceLineage.objects.create(
                    metadata=metadata,
                    statement='Sample lineage statement',
                    hierarchy_level=1
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
                    role='AUTHOR'
                )

                # Create data quality
                DataQuality.objects.create(
                    metadata=metadata,
                    completeness_report='Sample completeness report',
                    accuracy_report='Sample accuracy report'
                )

                # Create temporal extent
                TemporalExtent.objects.create(
                    identification_info=identification,
                    start_date=timezone.now() - timedelta(days=365),
                    end_date=timezone.now()
                )
# pylint: disable=C0115, E1101, C0114, C0303, C0301
import uuid
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

# Enums
class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    USER = "USER", "User"


class Status(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PUBLISHED = "PUBLISHED", "Published"
    ARCHIVED = "ARCHIVED", "Archived"


class SpatialRepresentationType(models.TextChoices):
    RASTER = "RASTER", "Raster"
    VECTOR = "VECTOR", "Vector"


class CharacterEncoding(models.TextChoices):
    HTML = "HTML", "HTML"
    CPP = "CPP", "C++"
    PYTHON = "PYTHON", "Python"
    JAVA = "JAVA", "Java"


class Language(models.TextChoices):
    EN = "EN", "English"
    FR = "FR", "French"
    ES = "ES", "Spanish"
    DE = "DE", "German"

# Base abstract model for common fields
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    created_at = models.DateTimeField(default=now, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

# Base contact information model
class BaseContactInfo(BaseModel):
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        help_text="Enter phone number in international format: +1234567890"
    )
    address = models.TextField(null=True, blank=True)
    
    class Meta:
        abstract = True

# Add this class before the User model
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email.split('@')[0])
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)

# User Model
class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        default='user'
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=10, 
        choices=UserRole.choices, 
        default=UserRole.USER
    )
    organization = models.CharField(max_length=255, null=True, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name=_('groups'),
        help_text=_('The groups this user belongs to.'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name=_('user permissions'),
        help_text=_('Specific permissions for this user.'),
    )
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        if not self.username:
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            self.username = username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.email})"

    class Meta:
        indexes = [
            models.Index(fields=['email', 'role'])
        ]

# Metadata Model
class Metadata(BaseModel):
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="metadata")
    metadata_linkage = models.TextField(null=True, blank=True)
    metadata_standard = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Metadata {self.id} - {self.status}"


# Identification Information
class IdentificationInfo(BaseModel):
    title = models.CharField(max_length=255, db_index=True)
    production_date = models.DateTimeField()
    edition_date = models.DateTimeField(null=True, blank=True)
    abstract = models.TextField()
    spatial_rep_type = models.CharField(
        max_length=10, choices=SpatialRepresentationType.choices
    )
    equivalent_scale = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    geographic_bounding_box = models.JSONField(
        default=dict,
        help_text="Format: {'north': float, 'south': float, 'east': float, 'west': float}"
    )
    update_frequency = models.CharField(max_length=255, null=True, blank=True)
    keywords = models.JSONField(default=list, db_index=True)
    keyword_type = models.CharField(max_length=255, null=True, blank=True)
    metadata = models.OneToOneField(
        Metadata, on_delete=models.PROTECT, related_name='identification'
    )

    def clean(self):
        super().clean()
        if isinstance(self.geographic_bounding_box, dict):
            required_keys = {'north', 'south', 'east', 'west'}
            missing_keys = required_keys - set(self.geographic_bounding_box.keys())
            if missing_keys:
                raise ValidationError({
                    'geographic_bounding_box': 'Must contain north, south, east, and west coordinates'
                })

    def __str__(self):
        return str(self.title)

    class Meta:
        indexes = [
            models.Index(fields=['title', 'production_date']),
            models.Index(fields=['spatial_rep_type'])
        ]

# Point of Contact
class PointOfContact(BaseContactInfo):
    role = models.CharField(max_length=255)
    identification_info = models.OneToOneField(
        IdentificationInfo, on_delete=models.CASCADE, related_name='point_of_contact'
    )

    def __str__(self):
        return f"{self.name} - {self.role}"


# Resource Constraints
class ResourceConstraints(BaseModel):
    access_constraints = models.TextField(null=True, blank=True)
    use_constraints = models.TextField(null=True, blank=True)
    other_constraints = models.TextField(null=True, blank=True)
    identification_info = models.OneToOneField(
        IdentificationInfo, 
        on_delete=models.CASCADE, 
        related_name='constraints'
    )

    def __str__(self):
        return f"Constraints for {getattr(self.identification_info, 'title', 'Unknown')}"


# Distribution Information
class Distribution(BaseModel):
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    phone_no = models.CharField(max_length=20, null=True, blank=True)
    weblink = models.URLField(null=True, blank=True)
    format = models.CharField(max_length=255, null=True, blank=True)
    distributor_email = models.EmailField(null=True, blank=True)
    order_process = models.TextField(null=True, blank=True)
    metadata = models.OneToOneField(
        Metadata, 
        on_delete=models.CASCADE,
        related_name='distribution'
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        indexes = [
            models.Index(fields=['name', 'format'])
        ]

# Resource Lineage
class ResourceLineage(BaseModel):
    statement = models.TextField()
    hierarchy_level = models.PositiveIntegerField()
    process_software = models.CharField(max_length=255, null=True, blank=True)
    process_date = models.DateTimeField(null=True, blank=True)
    metadata = models.OneToOneField(
        Metadata, 
        on_delete=models.CASCADE,
        related_name='lineage'
    )

    def __str__(self):
        return f"Lineage {self.hierarchy_level} - {getattr(self.metadata, 'id', 'Unknown')}"

    class Meta:
        indexes = [
            models.Index(fields=['hierarchy_level', 'process_date'])
        ]

# Reference System
class ReferenceSystem(BaseModel):
    identifier = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=255)
    metadata = models.OneToOneField(
        Metadata, 
        on_delete=models.CASCADE,
        related_name='reference_system'
    )

    def __str__(self):
        return f"{self.identifier} - {self.code}"


# Metadata Contact
class MetadataContact(BaseContactInfo):
    role = models.CharField(max_length=255)
    weblink = models.URLField(null=True, blank=True)
    metadata = models.OneToOneField(
        Metadata, 
        on_delete=models.CASCADE,
        related_name='contact'
    )

    def __str__(self):
        return f"{self.name} - {self.role}"


# Data Quality Information
class DataQuality(BaseModel):
    completeness_report = models.TextField(null=True, blank=True)
    accuracy_report = models.TextField(null=True, blank=True)
    process_description = models.TextField(null=True, blank=True)
    process_date = models.DateTimeField(null=True, blank=True)
    metadata = models.OneToOneField(
        Metadata, 
        on_delete=models.CASCADE,
        related_name='quality'
    )

    def __str__(self):
        return f"Quality Report for {getattr(self.metadata, 'id', 'Unknown')}"


# Temporal Extent
class TemporalExtent(BaseModel):
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(null=True, blank=True)
    frequency = models.CharField(max_length=255, null=True, blank=True)
    identification_info = models.OneToOneField(
        IdentificationInfo, 
        on_delete=models.CASCADE,
        related_name='temporal_extent'
    )

    class Meta:
        indexes = [
            models.Index(fields=['start_date', 'end_date'])
        ]

    def __str__(self):
        return f"Temporal Extent {self.start_date} to {self.end_date or 'ongoing'}"

# pylint: disable=C0115, E1101, C0114, C0303, C0301
from datetime import datetime
from rest_framework import serializers
from .models import (
    User, Metadata, IdentificationInfo, PointOfContact,
    ResourceConstraints, Distribution, ResourceLineage,
    ReferenceSystem, MetadataContact, DataQuality,
    TemporalExtent
)

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'name', 
            'role', 
            'organization',
            'username',
            'is_active',
            'date_joined',
            'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': True}  # Since it's auto-generated
        }

    def create(self, validated_data):
        """Create and return a new user."""
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """Update and return an existing user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class TemporalExtentSerializer(serializers.ModelSerializer):
    """Serializer for TemporalExtent model."""
    class Meta:
        model = TemporalExtent
        fields = ['id', 'start_date', 'end_date']
        read_only_fields = ['id']

class PointOfContactSerializer(serializers.ModelSerializer):
    """Serializer for PointOfContact model."""
    class Meta:
        model = PointOfContact
        fields = ['id', 'name', 'organization', 'email', 'phone', 'address', 'role']
        read_only_fields = ['id']

class ResourceConstraintsSerializer(serializers.ModelSerializer):
    """Serializer for ResourceConstraints model."""
    class Meta:
        model = ResourceConstraints
        fields = ['id', 'access_constraints', 'use_constraints', 'other_constraints']
        read_only_fields = ['id']

class IdentificationInfoSerializer(serializers.ModelSerializer):
    """Serializer for IdentificationInfo model."""
    point_of_contact = PointOfContactSerializer(required=False)
    constraints = ResourceConstraintsSerializer(required=False)
    temporal_extent = TemporalExtentSerializer(required=False)

    class Meta:
        model = IdentificationInfo
        fields = [
            'id',
            'title',
            'production_date',
            'edition_date',
            'abstract',
            'spatial_rep_type',
            'equivalent_scale',
            'geographic_bounding_box',
            'update_frequency',
            'keywords',
            'keyword_type',
            'point_of_contact',
            'constraints',
            'temporal_extent'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create IdentificationInfo with nested relationships."""
        point_of_contact_data = validated_data.pop('point_of_contact', None)
        constraints_data = validated_data.pop('constraints', None)
        temporal_extent_data = validated_data.pop('temporal_extent', None)
        
        identification_info = IdentificationInfo.objects.create(**validated_data)
        
        if point_of_contact_data:
            PointOfContact.objects.create(identification_info=identification_info, **point_of_contact_data)
        if constraints_data:
            ResourceConstraints.objects.create(identification_info=identification_info, **constraints_data)
        if temporal_extent_data:
            TemporalExtent.objects.create(identification_info=identification_info, **temporal_extent_data)
        
        return identification_info

    def update(self, instance, validated_data):
        """Update IdentificationInfo with nested relationships."""
        point_of_contact_data = validated_data.pop('point_of_contact', None)
        constraints_data = validated_data.pop('constraints', None)
        temporal_extent_data = validated_data.pop('temporal_extent', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if point_of_contact_data:
            PointOfContact.objects.update_or_create(
                identification_info=instance,
                defaults=point_of_contact_data
            )
        if constraints_data:
            ResourceConstraints.objects.update_or_create(
                identification_info=instance,
                defaults=constraints_data
            )
        if temporal_extent_data:
            TemporalExtent.objects.update_or_create(
                identification_info=instance,
                defaults=temporal_extent_data
            )
        
        return instance

    def validate_title(self, value):
        """Validate title field."""
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        return value

    def validate_abstract(self, value):
        """Validate abstract field."""
        if value and len(value) < 10:
            raise serializers.ValidationError("Abstract must be at least 10 characters long")
        return value

    def validate_topic_category(self, value):
        """Validate topic category field."""
        allowed_categories = ['farming', 'biota', 'boundaries', 'climatologyMeteorologyAtmosphere', 
                            'economy', 'elevation', 'environment', 'geoscientificInformation',
                            'health', 'imageryBaseMapsEarthCover', 'intelligenceMilitary',
                            'inlandWaters', 'location', 'oceans', 'planningCadastre',
                            'society', 'structure', 'transportation', 'utilitiesCommunication']
        if value and value not in allowed_categories:
            raise serializers.ValidationError(f"Topic category must be one of: {', '.join(allowed_categories)}")
        return value

    def validate_status(self, value):
        """Validate status field."""
        allowed_statuses = ['completed', 'historicalArchive', 'obsolete', 
                          'onGoing', 'planned', 'required', 'underDevelopment']
        if value and value not in allowed_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return value

    def validate_scale(self, value):
        """Validate scale field."""
        if value and value <= 0:
            raise serializers.ValidationError("Scale must be a positive number")
        return value

class DistributionSerializer(serializers.ModelSerializer):
    """Serializer for Distribution model."""
    class Meta:
        model = Distribution
        fields = [
            'id',
            'name',
            'address',
            'phone_no',
            'weblink',
            'format',
            'distributor_email',
            'order_process'
        ]
        read_only_fields = ['id']

class ResourceLineageSerializer(serializers.ModelSerializer):
    """Serializer for ResourceLineage model."""
    class Meta:
        model = ResourceLineage
        fields = [
            'id',
            'statement',
            'hierarchy_level',
            'process_software',
            'process_date'
        ]
        read_only_fields = ['id']

class ReferenceSystemSerializer(serializers.ModelSerializer):
    """Serializer for ReferenceSystem model."""
    class Meta:
        model = ReferenceSystem
        fields = ['id', 'identifier', 'code']
        read_only_fields = ['id']

class MetadataContactSerializer(serializers.ModelSerializer):
    """Serializer for MetadataContact model."""
    class Meta:
        model = MetadataContact
        fields = [
            'id',
            'name',
            'organization',
            'email',
            'phone',
            'address',
            'role',
            'weblink'
        ]
        read_only_fields = ['id']

class DataQualitySerializer(serializers.ModelSerializer):
    """Serializer for DataQuality model."""
    class Meta:
        model = DataQuality
        fields = [
            'id',
            'completeness_report',
            'accuracy_report',
            'process_description',
            'process_date'
        ]
        read_only_fields = ['id']

class MetadataSerializer(serializers.ModelSerializer):
    """Serializer for Metadata model."""
    identification = IdentificationInfoSerializer()
    distribution = DistributionSerializer()
    lineage = ResourceLineageSerializer()
    reference_system = ReferenceSystemSerializer()
    contact = MetadataContactSerializer()
    quality = DataQualitySerializer()

    class Meta:
        model = Metadata
        fields = '__all__'
        read_only_fields = ('user',)

    def create(self, validated_data):
        # Extract nested data
        identification_data = validated_data.pop('identification', None)
        distribution_data = validated_data.pop('distribution', None)
        lineage_data = validated_data.pop('lineage', None)
        reference_system_data = validated_data.pop('reference_system', None)
        contact_data = validated_data.pop('contact', None)
        quality_data = validated_data.pop('quality', None)

        # Create main metadata instance
        metadata = Metadata.objects.create(**validated_data)

        # Create related objects if data provided
        if identification_data:
            IdentificationInfo.objects.create(metadata=metadata, **identification_data)
        if distribution_data:
            Distribution.objects.create(metadata=metadata, **distribution_data)
        if lineage_data:
            ResourceLineage.objects.create(metadata=metadata, **lineage_data)
        if reference_system_data:
            ReferenceSystem.objects.create(metadata=metadata, **reference_system_data)
        if contact_data:
            MetadataContact.objects.create(metadata=metadata, **contact_data)
        if quality_data:
            DataQuality.objects.create(metadata=metadata, **quality_data)

        return metadata

    def update(self, instance, validated_data):
        """Update Metadata with nested relationships."""
        identification_data = validated_data.pop('identification', None)
        distribution_data = validated_data.pop('distribution', None)
        lineage_data = validated_data.pop('lineage', None)
        reference_system_data = validated_data.pop('reference_system', None)
        contact_data = validated_data.pop('contact', None)
        quality_data = validated_data.pop('quality', None)
        
        # Update main metadata instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update nested objects only if data is provided
        if identification_data and instance.identification:
            for attr, value in identification_data.items():
                setattr(instance.identification, attr, value)
            instance.identification.save()
            
        if distribution_data and instance.distribution:
            for attr, value in distribution_data.items():
                setattr(instance.distribution, attr, value)
            instance.distribution.save()
            
        if lineage_data and instance.lineage:
            for attr, value in lineage_data.items():
                setattr(instance.lineage, attr, value)
            instance.lineage.save()
            
        if reference_system_data and instance.reference_system:
            for attr, value in reference_system_data.items():
                setattr(instance.reference_system, attr, value)
            instance.reference_system.save()
            
        if contact_data and instance.contact:
            for attr, value in contact_data.items():
                setattr(instance.contact, attr, value)
            instance.contact.save()
            
        if quality_data and instance.quality:
            for attr, value in quality_data.items():
                setattr(instance.quality, attr, value)
            instance.quality.save()
        
        return instance

    def validate_file_identifier(self, value):
        """Validate file identifier field."""
        if not value:
            raise serializers.ValidationError("File identifier is required")
        if Metadata.objects.filter(file_identifier=value).exists():
            raise serializers.ValidationError("This file identifier already exists")
        return value

    def validate_language(self, value):
        """Validate language field."""
        allowed_languages = ['en', 'fr', 'es']  # example list
        if value.lower() not in allowed_languages:
            raise serializers.ValidationError(f"Language must be one of: {', '.join(allowed_languages)}")
        return value.lower()

    def validate_metadata_standard_name(self, value):
        """Validate metadata standard name field."""
        if not value:
            raise serializers.ValidationError("Metadata standard name is required")
        return value

    def validate_metadata_standard_version(self, value):
        """Validate metadata standard version field."""
        if not value:
            raise serializers.ValidationError("Metadata standard version is required")
        return value

    def validate_date_stamp(self, value):
        """Validate date stamp field."""
        if value > datetime.now().date():
            raise serializers.ValidationError("Date stamp cannot be in the future")
        return value

    def validate_character_set(self, value):
        """Validate character set field."""
        allowed_charsets = ['utf8', 'utf16', 'ascii', 'iso-8859-1']
        if value and value.lower() not in allowed_charsets:
            raise serializers.ValidationError(f"Character set must be one of: {', '.join(allowed_charsets)}")
        return value.lower()

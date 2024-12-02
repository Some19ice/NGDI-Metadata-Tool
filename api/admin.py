# pylint: disable=C0114, C0115

from django.contrib import admin
from .models import (
    User, Metadata, IdentificationInfo, PointOfContact,
    ResourceConstraints, Distribution, ResourceLineage,
    ReferenceSystem, MetadataContact, DataQuality,
    TemporalExtent
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'organization', 'role']
    ordering = ['email']
    readonly_fields = []

@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'user', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)

@admin.register(IdentificationInfo)
class IdentificationInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'production_date', 'spatial_rep_type', 'metadata')
    list_filter = ('spatial_rep_type', 'production_date')
    search_fields = ('title', 'abstract')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('metadata',)

@admin.register(PointOfContact)
class PointOfContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'email', 'role')
    list_filter = ('organization', 'role')
    search_fields = ('name', 'email', 'organization')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ResourceConstraints)
class ResourceConstraintsAdmin(admin.ModelAdmin):
    list_display = ('id', 'identification_info', 'created_at')
    search_fields = ('access_constraints', 'use_constraints')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('identification_info',)

@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ('name', 'format', 'distributor_email', 'metadata')
    list_filter = ('format',)
    search_fields = ('name', 'distributor_email')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('metadata',)

@admin.register(ResourceLineage)
class ResourceLineageAdmin(admin.ModelAdmin):
    list_display = ('hierarchy_level', 'process_software', 'process_date', 'metadata')
    list_filter = ('hierarchy_level', 'process_date')
    search_fields = ('statement', 'process_software')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('metadata',)

@admin.register(ReferenceSystem)
class ReferenceSystemAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'code', 'metadata')
    search_fields = ('identifier', 'code')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('metadata',)

@admin.register(MetadataContact)
class MetadataContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'email', 'role')
    list_filter = ('organization', 'role')
    search_fields = ('name', 'email', 'organization')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('metadata',)

@admin.register(DataQuality)
class DataQualityAdmin(admin.ModelAdmin):
    list_display = ('id', 'process_date', 'metadata')
    list_filter = ('process_date',)
    search_fields = ('completeness_report', 'accuracy_report')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('metadata',)

@admin.register(TemporalExtent)
class TemporalExtentAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'frequency', 'identification_info')
    list_filter = ('start_date', 'end_date')
    search_fields = ('frequency',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('identification_info',)

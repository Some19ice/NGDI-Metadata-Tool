# pylint: disable=C0115, E1101, C0114, C0303, C0301, W0613

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from .models import (
    User, Metadata, IdentificationInfo, PointOfContact,
    ResourceConstraints, Distribution, ResourceLineage,
    ReferenceSystem, MetadataContact, DataQuality,
    TemporalExtent
)
from .serializers import (
    UserSerializer, MetadataSerializer, IdentificationInfoSerializer,
    PointOfContactSerializer, ResourceConstraintsSerializer,
    DistributionSerializer, ResourceLineageSerializer,
    ReferenceSystemSerializer, MetadataContactSerializer,
    DataQualitySerializer, TemporalExtentSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing User instances.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        if user.role == 'ADMIN':
            return User.objects.all()
        return User.objects.filter(id=user.id)

class MetadataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Metadata instances.
    """
    queryset = Metadata.objects.select_related(
        'user',
        'identification',
        'identification__point_of_contact',
        'identification__constraints',
        'identification__temporal_extent',
        'distribution',
        'lineage',
        'reference_system',
        'contact',
        'quality'
    ).all()
    serializer_class = MetadataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Optimize queryset with select_related"""
        queryset = Metadata.objects.select_related(
            'user',
            'identification',
            'identification__point_of_contact',
            'identification__constraints',
            'identification__temporal_extent',
            'distribution',
            'lineage',
            'reference_system',
            'contact',
            'quality'
        )

        # Add filters based on query parameters
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Add date range filter if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        # Filter based on user permissions
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if user.role != 'ADMIN':
            queryset = queryset.filter(user=user)

        return queryset

    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Bulk create metadata records
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        
        # Create the metadata objects and attach the current user
        metadata_objects = []
        for item in serializer.validated_data:
            metadata = Metadata.objects.create(user=request.user, **item)
            metadata_objects.append(metadata)
        
        # Serialize the created objects for response
        response_serializer = self.get_serializer(metadata_objects, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        """Perform bulk create with user assignment"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Optimized bulk update metadata records"""
        from django.db import transaction
        
        ids = [item['id'] for item in request.data]
        instances = self.get_queryset().filter(id__in=ids)
        
        serializer = self.get_serializer(
            instances,
            data=request.data,
            many=True,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            self.perform_bulk_update(serializer)
            
        return Response(serializer.data)

    def perform_bulk_update(self, serializer):
        """Perform bulk update"""
        serializer.save()

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete metadata records"""
        ids = request.data.get('ids', [])
        deleted_count = self.get_queryset().filter(id__in=ids).delete()[0]
        return Response({'deleted_count': deleted_count})

    def perform_create(self, serializer):
        """Associate the current user with the metadata"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish metadata record"""
        metadata = self.get_object()
        if metadata.status == 'DRAFT':
            metadata.status = 'PUBLISHED'
            metadata.save()
            return Response({'status': 'metadata published'})
        return Response({'error': 'Can only publish draft metadata'},
                      status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive metadata record"""
        metadata = self.get_object()
        if metadata.status == 'PUBLISHED':
            metadata.status = 'ARCHIVED'
            metadata.save()
            return Response({'status': 'metadata archived'})
        return Response({'error': 'Can only archive published metadata'},
                      status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class IdentificationInfoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing IdentificationInfo instances.
    """
    queryset = IdentificationInfo.objects.select_related(
        'metadata',
        'metadata__user',
        'point_of_contact',
        'constraints'
    ).all()
    serializer_class = IdentificationInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter based on user's metadata access"""
        user = self.request.user
        if not user.is_authenticated:
            return IdentificationInfo.objects.none()
        if user.role == 'ADMIN':
            return self.queryset
        return self.queryset.filter(metadata__user=user)

class PointOfContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing PointOfContact instances.
    """
    queryset = PointOfContact.objects.select_related(
        'identification_info',
        'identification_info__metadata',
        'identification_info__metadata__user'
    ).all()
    serializer_class = PointOfContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return PointOfContact.objects.none()
        if user.role == 'ADMIN':
            return self.queryset
        return self.queryset.filter(identification_info__metadata__user=user)

class ResourceConstraintsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing ResourceConstraints instances.
    """
    queryset = ResourceConstraints.objects.select_related(
        'identification_info',
        'identification_info__metadata',
        'identification_info__metadata__user'
    ).all()
    serializer_class = ResourceConstraintsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ResourceConstraints.objects.none()
        if user.role == 'ADMIN':
            return self.queryset
        return self.queryset.filter(identification_info__metadata__user=user)

class DistributionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Distribution instances.
    """
    queryset = Distribution.objects.select_related(
        'metadata',
        'metadata__user'
    ).all()
    serializer_class = DistributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Distribution.objects.none()
        if user.role == 'ADMIN':
            return self.queryset
        return self.queryset.filter(metadata__user=user)

class ResourceLineageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing ResourceLineage instances.
    """
    queryset = ResourceLineage.objects.select_related(
        'metadata',
        'metadata__user'
    ).all()
    serializer_class = ResourceLineageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ResourceLineage.objects.none()
        if user.role == 'ADMIN':
            return self.queryset
        return self.queryset.filter(metadata__user=user)

class ReferenceSystemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing ReferenceSystem instances.
    """
    queryset = ReferenceSystem.objects.select_related(
        'metadata',
        'metadata__user'
    ).all()
    serializer_class = ReferenceSystemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ReferenceSystem.objects.none()
        if user.role == 'ADMIN':
            return self.queryset
        return self.queryset.filter(metadata__user=user)

class MetadataContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing MetadataContact instances.
    """
    queryset = MetadataContact.objects.select_related(
        'metadata',
        'metadata__user'
    ).all()
    serializer_class = MetadataContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return MetadataContact.objects.none()
        if user.role == 'ADMIN':
            return self.queryset
        return self.queryset.filter(metadata__user=user)

class DataQualityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing DataQuality instances.
    """
    queryset = DataQuality.objects.select_related(
        'metadata',
        'metadata__user'
    ).all()
    serializer_class = DataQualitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return DataQuality.objects.none()
        if user.role == 'ADMIN':
            return self.queryset
        return self.queryset.filter(metadata__user=user)

class TemporalExtentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing TemporalExtent instances.
    """
    queryset = TemporalExtent.objects.select_related(
        'identification_info',
        'identification_info__metadata',
        'identification_info__metadata__user'
    ).all()
    serializer_class = TemporalExtentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return TemporalExtent.objects.none()
        if user.role == 'ADMIN':
            return self.queryset
        return self.queryset.filter(identification_info__metadata__user=user)

# pylint: disable=C0114

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from . import views

# Create schema view for Swagger documentation
schema_view = get_schema_view(
    openapi.Info(
        title="NGDI Metadata API",
        default_version='v1',
        description="API for managing NGDI metadata records",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@nasrda.gov.ng"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'metadata', views.MetadataViewSet)
router.register(r'identification', views.IdentificationInfoViewSet)
router.register(r'contacts', views.PointOfContactViewSet)
router.register(r'constraints', views.ResourceConstraintsViewSet)
router.register(r'distributions', views.DistributionViewSet)
router.register(r'lineages', views.ResourceLineageViewSet)
router.register(r'reference-systems', views.ReferenceSystemViewSet)
router.register(r'metadata-contacts', views.MetadataContactViewSet)
router.register(r'quality', views.DataQualityViewSet)
router.register(r'temporal-extents', views.TemporalExtentViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    # Add login URLs for the browsable API
    path('auth/', include('rest_framework.urls')),
    path('token-auth/', obtain_auth_token, name='api_token_auth'),
    # Swagger documentation URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] 
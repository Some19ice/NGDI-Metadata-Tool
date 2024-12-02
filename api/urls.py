# pylint: disable=C0114

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views



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
] 
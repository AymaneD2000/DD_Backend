from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceQuoteViewSet, InstallationViewSet, MaintenanceContractViewSet

router = DefaultRouter()
router.register(r'quotes', ServiceQuoteViewSet)
router.register(r'installations', InstallationViewSet)
router.register(r'maintenance', MaintenanceContractViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

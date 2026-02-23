from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, SaleItemViewSet

router = DefaultRouter()
router.register(r'sales', SaleViewSet)
router.register(r'sale-items', SaleItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

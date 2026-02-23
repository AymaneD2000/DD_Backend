from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet, 
    ProductViewSet, 
    StockItemViewSet, 
    StockMovementViewSet,
    CategoryViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'products', ProductViewSet)
router.register(r'stock-items', StockItemViewSet)
router.register(r'movements', StockMovementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

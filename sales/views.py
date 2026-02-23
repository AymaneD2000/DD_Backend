from rest_framework import viewsets, permissions
from .models import Sale, SaleItem
from .serializers import SaleSerializer, SaleItemSerializer

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().order_by('-transaction_date')
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class SaleItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerializer
    permission_classes = [permissions.IsAuthenticated]

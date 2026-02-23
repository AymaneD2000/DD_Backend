from rest_framework import viewsets, permissions
from django.db.models import Sum, Q, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from .models import Client
from .serializers import ClientSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.annotate(
        total_revenue=Coalesce(
            Sum('sales__total_amount', filter=Q(sales__status='COMPLETED'), output_field=DecimalField()), 
            Decimal('0.00'),
            output_field=DecimalField()
        )
    )
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

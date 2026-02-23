from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ServiceQuote, Installation, MaintenanceContract
from .serializers import ServiceQuoteSerializer, InstallationSerializer, MaintenanceContractSerializer

class ServiceQuoteViewSet(viewsets.ModelViewSet):
    queryset = ServiceQuote.objects.all().order_by('-created_at')
    serializer_class = ServiceQuoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def convert_to_installation(self, request, pk=None):
        quote = self.get_object()
        if quote.status != 'ACCEPTED':
             return Response({'error': 'Quote must be accepted first'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Logic to create installation from quote could go here
        # For now, we assume frontend handles creation via InstallationViewSet
        return Response({'status': 'Ready to schedule installation'})

class InstallationViewSet(viewsets.ModelViewSet):
    queryset = Installation.objects.all().order_by('-scheduled_date')
    serializer_class = InstallationSerializer
    permission_classes = [permissions.IsAuthenticated]

class MaintenanceContractViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceContract.objects.all()
    serializer_class = MaintenanceContractSerializer
    permission_classes = [permissions.IsAuthenticated]

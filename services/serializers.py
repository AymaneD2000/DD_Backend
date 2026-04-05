from rest_framework import serializers
from .models import ServiceQuote, Installation, MaintenanceContract, Service

class ServiceQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceQuote
        fields = '__all__'

class InstallationSerializer(serializers.ModelSerializer):
    technicians_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Installation
        fields = '__all__'

    def get_technicians_details(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.technicians.all(), many=True).data

class MaintenanceContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceContract
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Client
        fields = '__all__'

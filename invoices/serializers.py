from rest_framework import serializers
from .models import Invoice, InvoiceItem

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    client_details = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = '__all__'

    def get_client_details(self, obj):
        return {'name': obj.client.name}

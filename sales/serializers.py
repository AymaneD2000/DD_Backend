from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from .models import Sale, SaleItem
from stock.models import Product, StockItem, Warehouse, StockMovement

class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['unit_price', 'total_price']

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    
    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ['transaction_date', 'total_amount', 'tax_amount', 'discount_amount', 'invoice_number']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Calculate totals
        total_amount = 0
        
        with transaction.atomic():
            sale = Sale.objects.create(**validated_data)
            warehouse = sale.warehouse
            
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                # Use current selling price
                unit_price = product.selling_price
                
                # Check stock availability
                stock_item = StockItem.objects.filter(warehouse=warehouse, product=product).first()
                if not stock_item or stock_item.quantity < quantity:
                    raise serializers.ValidationError(f"Insufficient stock for {product.name} in {warehouse.name}")
                
                # Deduct stock
                stock_item.quantity -= quantity
                stock_item.save()
                
                # Create SaleItem
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=unit_price * quantity
                )
                
                # Log movement
                StockMovement.objects.create(
                    product=product,
                    warehouse=warehouse,
                    quantity=quantity,
                    movement_type='OUT',
                    reference=f'Sale #{sale.id}',
                    notes=f'Sold to {sale.client.name if sale.client else "Unknown"}'
                )

                total_amount += unit_price * quantity
            
            # Update sale total
            sale.total_amount = total_amount
            # Simple tax calculation (e.g., 20% - make configurable later)
            sale.tax_amount = total_amount * Decimal('0.20')
            sale.save()
            
            return sale

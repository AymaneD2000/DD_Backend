from rest_framework import serializers
from .models import Warehouse, Product, StockItem, StockMovement, Category

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class StockItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    warehouse_details = WarehouseSerializer(source='warehouse', read_only=True)

    class Meta:
        model = StockItem
        fields = '__all__'

class StockMovementSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    warehouse_details = WarehouseSerializer(source='warehouse', read_only=True)

    class Meta:
        model = StockMovement
        fields = '__all__'

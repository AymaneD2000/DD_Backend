from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Warehouse, Product, StockItem, StockMovement, Category
from .serializers import (
    WarehouseSerializer, 
    ProductSerializer, 
    StockItemSerializer, 
    StockMovementSerializer,
    CategorySerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

class StockItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = StockItem.objects.all()
        warehouse_id = self.request.query_params.get('warehouse', None)
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        return queryset

class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.all().order_by('-created_at')
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def operation(self, request):
        """
        Handle stock operations: IN (Purchase), OUT (Sale/Loss), TRANSFER
        """
        data = request.data
        movement_type = data.get('movement_type')
        product_id = data.get('product')
        warehouse_id = data.get('warehouse')
        quantity = int(data.get('quantity', 0))
        notes = data.get('notes', '')
        reference = data.get('reference', '')

        if not all([movement_type, product_id, warehouse_id, quantity]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                warehouse = Warehouse.objects.get(id=warehouse_id)
                product = Product.objects.get(id=product_id)
                
                stock_item, created = StockItem.objects.get_or_create(
                    warehouse=warehouse, 
                    product=product,
                    defaults={'quantity': 0}
                )

                if movement_type == 'IN':
                    stock_item.quantity += quantity
                elif movement_type == 'OUT':
                    if stock_item.quantity < quantity:
                        return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
                    stock_item.quantity -= quantity
                
                stock_item.save()

                # Log movement
                StockMovement.objects.create(
                    product=product,
                    warehouse=warehouse,
                    quantity=quantity,
                    movement_type=movement_type,
                    reference=reference,
                    notes=notes
                )

                return Response({'status': 'success', 'new_quantity': stock_item.quantity})

        except Warehouse.DoesNotExist:
            return Response({'error': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        """
        Handle stock transfers between warehouses
        """
        data = request.data
        product_id = data.get('product')
        source_warehouse_id = data.get('source_warehouse')
        target_warehouse_id = data.get('target_warehouse')
        quantity = int(data.get('quantity', 0))
        notes = data.get('notes', '')

        if not all([product_id, source_warehouse_id, target_warehouse_id, quantity]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                source_wh = Warehouse.objects.get(id=source_warehouse_id)
                target_wh = Warehouse.objects.get(id=target_warehouse_id)
                product = Product.objects.get(id=product_id)

                # Decrease source stock
                source_item = StockItem.objects.get(warehouse=source_wh, product=product)
                if source_item.quantity < quantity:
                    return Response({'error': 'Insufficient stock in source warehouse'}, status=status.HTTP_400_BAD_REQUEST)
                
                source_item.quantity -= quantity
                source_item.save()

                # Increase target stock
                target_item, created = StockItem.objects.get_or_create(
                    warehouse=target_wh,
                    product=product,
                    defaults={'quantity': 0}
                )
                target_item.quantity += quantity
                target_item.save()

                # Log movements
                StockMovement.objects.create(
                    product=product,
                    warehouse=source_wh,
                    quantity=quantity,
                    movement_type='OUT',
                    reference=f'Transfer to {target_wh.name}',
                    notes=notes
                )
                StockMovement.objects.create(
                    product=product,
                    warehouse=target_wh,
                    quantity=quantity,
                    movement_type='IN',
                    reference=f'Transfer from {source_wh.name}',
                    notes=notes
                )

                return Response({'status': 'success'})

        except Warehouse.DoesNotExist:
            return Response({'error': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except StockItem.DoesNotExist:
             return Response({'error': 'Product not found in source warehouse'}, status=status.HTTP_404_NOT_FOUND)

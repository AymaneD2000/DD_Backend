from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer
from sales.models import Sale

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-issue_date')
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_from_sale(self, request):
        sale_id = request.data.get('sale_id')
        if not sale_id:
             return Response({'error': 'Sale ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sale = Sale.objects.get(id=sale_id)
            if hasattr(sale, 'invoices') and sale.invoices.exists():
                return Response({'error': 'Invoice already exists for this sale'}, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                invoice = Invoice.objects.create(
                    invoice_number=f"INV-{sale.id}", # Simple format
                    client=sale.client,
                    sale=sale,
                    issue_date=sale.transaction_date.date(),
                    due_date=sale.transaction_date.date(), # Immediate due for now
                    total_amount=sale.total_amount,
                    tax_amount=sale.tax_amount,
                    status='PAID' if sale.payment_status == 'PAID' else 'DRAFT'
                )

                for item in sale.items.all():
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=item.product,
                        description=item.product.name if item.product else "Unknown Product",
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        total_price=item.total_price
                    )
                
                # Update Sale with invoice reference
                sale.invoice_number = invoice.invoice_number
                sale.save()
                
                serializer = self.get_serializer(invoice)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Sale.DoesNotExist:
             return Response({'error': 'Sale not found'}, status=status.HTTP_404_NOT_FOUND)

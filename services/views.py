from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone
from invoices.models import Invoice, InvoiceItem
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Installation, MaintenanceContract, Service, ServiceQuote
from .serializers import (
    InstallationSerializer,
    MaintenanceContractSerializer,
    ServiceQuoteSerializer,
    ServiceSerializer,
)


class ServiceQuoteViewSet(viewsets.ModelViewSet):
    queryset = ServiceQuote.objects.all().order_by("-created_at")
    serializer_class = ServiceQuoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def convert_to_installation(self, request, pk=None):
        quote = self.get_object()
        if quote.status != "ACCEPTED":
            return Response(
                {"error": "Quote must be accepted first"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"status": "Ready to schedule installation"})


class InstallationViewSet(viewsets.ModelViewSet):
    queryset = Installation.objects.all().order_by("-scheduled_date")
    serializer_class = InstallationSerializer
    permission_classes = [permissions.IsAuthenticated]


class MaintenanceContractViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceContract.objects.all()
    serializer_class = MaintenanceContractSerializer
    permission_classes = [permissions.IsAuthenticated]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by("-created_at")
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def generate_invoice(self, request, pk=None):
        service = self.get_object()

        if not service.client:
            return Response(
                {"error": "Service must be linked to a client before invoicing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = request.data or {}

        try:
            quantity = int(payload.get("quantity", 1))
            if quantity <= 0:
                raise ValueError("quantity must be positive")
        except (TypeError, ValueError):
            return Response(
                {"error": "quantity must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            unit_price = Decimal(str(payload.get("unit_price", service.price)))
            tax_amount = Decimal(str(payload.get("tax_amount", "0")))
        except (InvalidOperation, TypeError, ValueError):
            return Response(
                {"error": "unit_price and tax_amount must be valid decimal values"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if unit_price < 0 or tax_amount < 0:
            return Response(
                {"error": "unit_price and tax_amount cannot be negative"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subtotal = unit_price * quantity
        total_amount = subtotal + tax_amount

        issue_date = payload.get("issue_date") or timezone.now().date()
        due_date = payload.get("due_date") or issue_date
        status_value = payload.get("status", "DRAFT")
        notes = payload.get("notes", "")

        description = payload.get("description") or service.name

        base_invoice_number = (
            f"SRV-{service.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        )
        invoice_number = base_invoice_number
        counter = 1
        while Invoice.objects.filter(invoice_number=invoice_number).exists():
            counter += 1
            invoice_number = f"{base_invoice_number}-{counter}"

        with transaction.atomic():
            invoice = Invoice.objects.create(
                invoice_number=invoice_number,
                client=service.client,
                issue_date=issue_date,
                due_date=due_date,
                total_amount=total_amount,
                tax_amount=tax_amount,
                status=status_value,
                notes=(
                    f"{notes}\nGenerated from service #{service.id}: {service.name}"
                ).strip(),
            )

            InvoiceItem.objects.create(
                invoice=invoice,
                product=None,
                description=description,
                quantity=quantity,
                unit_price=unit_price,
                total_price=subtotal,
            )

        from invoices.serializers import InvoiceSerializer

        serializer = InvoiceSerializer(invoice, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

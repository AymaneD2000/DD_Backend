from django.db import models
from django.conf import settings

class ServiceQuote(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    )

    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='quotes')
    installation_type = models.CharField(max_length=200)
    description = models.TextField()
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    material_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    valid_until = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quote for {self.client} - {self.installation_type}"

class Installation(models.Model):
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    quote = models.OneToOneField(ServiceQuote, on_delete=models.SET_NULL, null=True, blank=True, related_name='installation')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='installations')
    technicians = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='installations')
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    address = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Installation for {self.client} on {self.scheduled_date}"

class MaintenanceContract(models.Model):
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='maintenance_contracts')
    equipment_type = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=100)
    installation_date = models.DateField()
    warranty_expiry = models.DateField(blank=True, null=True)
    next_maintenance_date = models.DateField()
    frequency_months = models.IntegerField(default=12)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Maintenance: {self.equipment_type} ({self.serial_number})"

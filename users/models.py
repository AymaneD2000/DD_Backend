from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('WAREHOUSE_STAFF', 'Warehouse Staff'),
        ('TECHNICIAN', 'Technician'),
        ('SALES_STAFF', 'Sales Staff'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ADMIN')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    warehouse = models.ForeignKey('stock.Warehouse', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

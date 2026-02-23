from django.db import models

class Client(models.Model):
    CLIENT_TYPE_CHOICES = (
        ('INDIVIDUAL', 'Individual'),
        ('BUSINESS', 'Business'),
    )

    name = models.CharField(max_length=200)  # Name or Company Name
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES, default='INDIVIDUAL')
    contact_person = models.CharField(max_length=100, blank=True, null=True)  # For businesses
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)  # SIRET/TVA
    preferred_warehouse = models.ForeignKey('stock.Warehouse', on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

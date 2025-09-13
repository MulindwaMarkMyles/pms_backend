from django.db import models
from django.contrib.auth.models import User
from core.models import Apartment

class TenantType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tenant_type = models.ForeignKey(TenantType, on_delete=models.SET_NULL, null=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True)
    lease_start = models.DateField(null=True)
    lease_end = models.DateField(null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
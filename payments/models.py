from django.db import models
from tenants.models import Tenant

class PaymentStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name + '-' + str(self.id)

class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.ForeignKey(PaymentStatus, on_delete=models.SET_NULL, null=True)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_for_month = models.IntegerField(help_text="Month number (1-12)", null=True, blank=True)
    payment_for_year = models.IntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    payment_type = models.CharField(max_length=100, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    receipt_file = models.FileField(upload_to='payment_receipts/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment by {self.tenant.user.username} - {self.amount}"

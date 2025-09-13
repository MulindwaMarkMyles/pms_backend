from django.db import models
from tenants.models import Tenant

class ComplaintStatus(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Complaint Categories"

    def __str__(self):
        return self.name

class Complaint(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    status = models.ForeignKey(ComplaintStatus, on_delete=models.SET_NULL, null=True)
    feedback = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='complaint_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint by {self.tenant.user.username}"
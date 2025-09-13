from django.contrib import admin
from .models import Payment, PaymentStatus

admin.site.register(Payment)
admin.site.register(PaymentStatus)
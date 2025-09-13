from django.contrib import admin
from .models import Tenant, TenantType

admin.site.register(Tenant)
admin.site.register(TenantType)
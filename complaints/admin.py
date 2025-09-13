from django.contrib import admin
from .models import Complaint, ComplaintStatus, ComplaintCategory

admin.site.register(Complaint)
admin.site.register(ComplaintStatus)
admin.site.register(ComplaintCategory)
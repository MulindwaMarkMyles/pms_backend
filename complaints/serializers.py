from rest_framework import serializers
from .models import Complaint, ComplaintStatus, ComplaintCategory

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'

class ComplaintStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintStatus
        fields = '__all__'

class ComplaintCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintCategory
        fields = '__all__'
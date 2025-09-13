from rest_framework import serializers
from .models import Payment, PaymentStatus

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentStatus
        fields = '__all__'
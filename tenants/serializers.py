from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tenant, TenantType
from core.models import UserProfile

class TenantSerializer(serializers.ModelSerializer):
    user = serializers.DictField(write_only=True)
    user_details = serializers.SerializerMethodField(read_only=True)
    tenant_type_details = serializers.SerializerMethodField(read_only=True)
    apartment_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Tenant
        fields = '__all__'
    
    def get_user_details(self, obj):
        """Return user details for read operations"""
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name
            }
        return None
    
    def get_tenant_type_details(self, obj):
        """Return tenant type details"""
        if obj.tenant_type:
            return {
                'id': obj.tenant_type.id,
                'name': obj.tenant_type.name,
                'description': obj.tenant_type.description
            }
        return None
    
    def get_apartment_details(self, obj):
        """Return apartment details with block and estate info"""
        if obj.apartment:
            return {
                'id': obj.apartment.id,
                'number': obj.apartment.number,
                'size': str(obj.apartment.size) if obj.apartment.size else None,
                'rent_amount': str(obj.apartment.rent_amount) if obj.apartment.rent_amount else None,
                'number_of_rooms': obj.apartment.number_of_rooms,
                'block': {
                    'id': obj.apartment.block.id,
                    'name': obj.apartment.block.name,
                    'estate': {
                        'id': obj.apartment.block.estate.id,
                        'name': obj.apartment.block.estate.name,
                        'address': obj.apartment.block.estate.address
                    }
                }
            }
        return None
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        # Create User
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        # Create UserProfile with tenant role
        UserProfile.objects.create(
            user=user,
            phone_number=validated_data.get('phone_number', ''),
            address='',  # Can be updated later
            role='tenant'
        )
        
        # Create Tenant
        tenant = Tenant.objects.create(user=user, **validated_data)
        return tenant

class TenantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantType
        fields = '__all__'
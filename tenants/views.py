from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Tenant, TenantType
from .serializers import TenantSerializer, TenantTypeSerializer
from core.models import Apartment

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Tenant.objects.all()
        apartment_id = self.request.query_params.get('apartment_id')
        tenant_type_id = self.request.query_params.get('tenant_type_id')
        
        if apartment_id:
            queryset = queryset.filter(apartment_id=apartment_id)
        if tenant_type_id:
            queryset = queryset.filter(tenant_type_id=tenant_type_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create tenant with user and profile"""
        try:
            data = request.data
            user_data = data.get('user', {})
            
            # Validate required user fields
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    return Response({
                        'error': f'User {field} is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if username or email already exists
            if User.objects.filter(username=user_data['username']).exists():
                return Response({
                    'error': 'Username already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=user_data['email']).exists():
                return Response({
                    'error': 'Email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if apartment is available
            apartment_id = data.get('apartment')
            if apartment_id:
                apartment = Apartment.objects.filter(id=apartment_id).first()
                if not apartment:
                    return Response({
                        'error': 'Apartment not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Check if apartment already has a tenant
                if Tenant.objects.filter(apartment=apartment).exists():
                    return Response({
                        'error': 'Apartment is already occupied'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Use serializer to create tenant (which will create user and profile)
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                tenant = serializer.save()
                
                return Response({
                    'message': 'Tenant created successfully',
                    'tenant': {
                        'id': tenant.id,
                        'user': {
                            'id': tenant.user.id,
                            'username': tenant.user.username,
                            'email': tenant.user.email,
                            'first_name': tenant.user.first_name,
                            'last_name': tenant.user.last_name
                        },
                        'tenant_type': tenant.tenant_type.id if tenant.tenant_type else None,
                        'apartment': tenant.apartment.id if tenant.apartment else None,
                        'lease_start': tenant.lease_start,
                        'lease_end': tenant.lease_end,
                        'phone_number': tenant.phone_number,
                        'emergency_contact': tenant.emergency_contact
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': 'An error occurred while creating the tenant',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update tenant with proper user handling"""
        print("=== TENANT UPDATE DEBUG ===")
        print(f"Request data: {request.data}")
        print(f"Content type: {request.content_type}")
        
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            data = request.data.copy()
            
            print(f"Original data: {data}")
            
            # Handle user data separately - DO NOT pass to serializer
            user_data = data.pop('user', None)
            print(f"Extracted user_data: {user_data}")
            print(f"Data after popping user: {data}")
            
            if user_data:
                user = instance.user
                print(f"Updating user: {user.username}")
                
                # Update user fields
                for field, value in user_data.items():
                    if field == 'password':
                        user.set_password(value)
                    elif hasattr(user, field):
                        setattr(user, field, value)
                        print(f"Updated user.{field} = {value}")
                
                user.save()
                print("User saved successfully")
            
            # Handle apartment change
            apartment_id = data.get('apartment')
            if apartment_id and str(apartment_id) != str(instance.apartment.id):
                apartment = Apartment.objects.filter(id=apartment_id).first()
                if not apartment:
                    return Response({
                        'error': 'Apartment not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Check if new apartment is available
                if Tenant.objects.filter(apartment=apartment).exclude(id=instance.id).exists():
                    return Response({
                        'error': 'Apartment is already occupied'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"Final data for serializer: {data}")
            
            # Update tenant fields (without user data)
            serializer = self.get_serializer(instance, data=data, partial=partial)
            if serializer.is_valid():
                print("Serializer is valid, saving...")
                tenant = serializer.save()
                print("Tenant saved successfully")
                return Response(self.get_serializer(tenant).data)
            else:
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"Exception in tenant update: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while updating the tenant',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def by_estate(self, request):
        """Get tenants filtered by estate"""
        estate_id = request.query_params.get('estate_id')
        if estate_id:
            tenants = Tenant.objects.filter(apartment__block__estate_id=estate_id)
            serializer = self.get_serializer(tenants, many=True)
            return Response(serializer.data)
        return Response({'error': 'estate_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def expiry_dashboard(self, request):
        """Get tenancy expiry dashboard for property owner"""
        current_date = timezone.now().date()
        
        # Tenants expiring in the next 30 days
        expiring_soon_date = current_date + timedelta(days=30)
        expiring_soon = Tenant.objects.filter(
            lease_end__gte=current_date,
            lease_end__lte=expiring_soon_date
        ).select_related('user', 'apartment', 'apartment__block', 'apartment__block__estate')
        
        # Tenants with expired leases
        expired_leases = Tenant.objects.filter(
            lease_end__lt=current_date
        ).select_related('user', 'apartment', 'apartment__block', 'apartment__block__estate')
        
        # Count tenants expiring this month
        this_month_start = current_date.replace(day=1)
        next_month_start = (this_month_start + timedelta(days=32)).replace(day=1)
        expiring_this_month = Tenant.objects.filter(
            lease_end__gte=this_month_start,
            lease_end__lt=next_month_start
        ).count()
        
        # Count tenants expiring next month
        next_month_end = (next_month_start + timedelta(days=32)).replace(day=1)
        expiring_next_month = Tenant.objects.filter(
            lease_end__gte=next_month_start,
            lease_end__lt=next_month_end
        ).count()
        
        # Calculate renewal rate (simplified - tenants with lease_end > current_date)
        total_active_tenants = Tenant.objects.filter(lease_end__gte=current_date).count()
        renewed_tenants = Tenant.objects.filter(
            lease_end__gte=current_date + timedelta(days=365)  # Extended beyond 1 year
        ).count()
        
        renewal_rate = (renewed_tenants / total_active_tenants * 100) if total_active_tenants > 0 else 0
        
        expiring_soon_data = [
            {
                'tenant_id': tenant.id,
                'tenant_name': f"{tenant.user.first_name} {tenant.user.last_name}",
                'apartment': tenant.apartment.number if tenant.apartment else None,
                'lease_end': tenant.lease_end,
                'days_until_expiry': (tenant.lease_end - current_date).days,
                'estate': tenant.apartment.block.estate.name if tenant.apartment else None,
                'block': tenant.apartment.block.name if tenant.apartment else None
            } for tenant in expiring_soon
        ]
        
        expired_data = [
            {
                'tenant_id': tenant.id,
                'tenant_name': f"{tenant.user.first_name} {tenant.user.last_name}",
                'apartment': tenant.apartment.number if tenant.apartment else None,
                'lease_end': tenant.lease_end,
                'days_overdue': (current_date - tenant.lease_end).days,
                'estate': tenant.apartment.block.estate.name if tenant.apartment else None,
                'block': tenant.apartment.block.name if tenant.apartment else None
            } for tenant in expired_leases
        ]
        
        return Response({
            'expiring_soon': expiring_soon_data,
            'expired_leases': expired_data,
            'expiring_this_month': expiring_this_month,
            'expiring_next_month': expiring_next_month,
            'expired_total': len(expired_data),
            'renewal_rate': renewal_rate
        })
    
    @action(detail=False, methods=['get'])
    def expiring(self, request):
        """Get tenants expiring in a specific date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        expiring_tenants = Tenant.objects.filter(
            lease_end__gte=start_date,
            lease_end__lte=end_date
        ).select_related('user', 'apartment', 'apartment__block', 'apartment__block__estate')
        
        expiring_data = [
            {
                'tenant_id': tenant.id,
                'tenant_name': f"{tenant.user.first_name} {tenant.user.last_name}",
                'apartment': tenant.apartment.number if tenant.apartment else None,
                'lease_end': tenant.lease_end,
                'estate': tenant.apartment.block.estate.name if tenant.apartment else None,
                'block': tenant.apartment.block.name if tenant.apartment else None
            } for tenant in expiring_tenants
        ]
        
        return Response({
            'period': f'{start_date} to {end_date}',
            'expiring_tenants': expiring_data,
            'count': len(expiring_data)
        })

class TenantTypeViewSet(viewsets.ModelViewSet):
    queryset = TenantType.objects.all()
    serializer_class = TenantTypeSerializer
    permission_classes = [IsAuthenticated]
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, Avg, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta
from .models import Estate, Block, Apartment, Amenity, Furnishing
from .serializers import EstateSerializer, BlockSerializer, ApartmentSerializer, AmenitySerializer, FurnishingSerializer
from tenants.models import Tenant
from complaints.models import Complaint
from decimal import Decimal

class EstateViewSet(viewsets.ModelViewSet):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer
    permission_classes = [IsAuthenticated]

class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Block.objects.all()
        estate_id = self.request.query_params.get('estate_id')
        if estate_id:
            queryset = queryset.filter(estate_id=estate_id)
        return queryset

class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Apartment.objects.all()
        block_id = self.request.query_params.get('block_id')
        available_only = self.request.query_params.get('available_only')
        
        if block_id:
            queryset = queryset.filter(block_id=block_id)
        if available_only == 'true':
            queryset = queryset.filter(tenant__isnull=True)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Override create to provide better error handling and debugging"""
        print("=== APARTMENT CREATE DEBUG ===")
        print(f"Request data: {request.data}")
        print(f"Content type: {request.content_type}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            print(f"Serializer initial data: {serializer.initial_data}")
            
            if serializer.is_valid():
                print("Serializer is valid, creating apartment...")
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                print(f"Created apartment: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                # Return detailed validation errors
                print(f"Serializer validation errors: {serializer.errors}")
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception in apartment creation: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while creating the apartment',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Override update to provide better error handling and debugging"""
        print("=== APARTMENT UPDATE DEBUG ===")
        print(f"Request data: {request.data}")
        print(f"Content type: {request.content_type}")
        
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            print(f"Serializer initial data: {serializer.initial_data}")
            
            if serializer.is_valid():
                print("Serializer is valid, updating apartment...")
                self.perform_update(serializer)
                print(f"Updated apartment: {serializer.data}")
                return Response(serializer.data)
            else:
                # Return detailed validation errors
                print(f"Serializer validation errors: {serializer.errors}")
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception in apartment update: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while updating the apartment',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available apartments for tenant assignment with smart filtering"""
        # Get query parameters for smart filtering
        min_rooms = request.query_params.get('min_rooms')
        max_rooms = request.query_params.get('max_rooms')
        min_rent = request.query_params.get('min_rent')
        max_rent = request.query_params.get('max_rent')
        min_size = request.query_params.get('min_size')
        max_size = request.query_params.get('max_size')
        estate_id = request.query_params.get('estate_id')
        block_id = request.query_params.get('block_id')
        amenity_ids = request.query_params.getlist('amenities')  # Can pass multiple
        furnishing_ids = request.query_params.getlist('furnishings')  # Can pass multiple
        
        print(f"=== AVAILABLE APARTMENTS FILTER DEBUG ===")
        print(f"Filters: rooms({min_rooms}-{max_rooms}), rent({min_rent}-{max_rent}), size({min_size}-{max_size})")
        print(f"Location: estate_id={estate_id}, block_id={block_id}")
        print(f"Amenities: {amenity_ids}, Furnishings: {furnishing_ids}")
        
        # Base query - apartments without tenants
        available_apartments = Apartment.objects.filter(tenant__isnull=True).select_related(
            'block', 'block__estate'
        ).prefetch_related('amenities', 'furnishings')
        
        # Apply smart filters
        if min_rooms:
            available_apartments = available_apartments.filter(number_of_rooms__gte=int(min_rooms))
        if max_rooms:
            available_apartments = available_apartments.filter(number_of_rooms__lte=int(max_rooms))
        if min_rent:
            available_apartments = available_apartments.filter(rent_amount__gte=float(min_rent))
        if max_rent:
            available_apartments = available_apartments.filter(rent_amount__lte=float(max_rent))
        if min_size:
            available_apartments = available_apartments.filter(size__gte=float(min_size))
        if max_size:
            available_apartments = available_apartments.filter(size__lte=float(max_size))
        if estate_id:
            available_apartments = available_apartments.filter(block__estate_id=estate_id)
        if block_id:
            available_apartments = available_apartments.filter(block_id=block_id)
        if amenity_ids:
            available_apartments = available_apartments.filter(amenities__id__in=amenity_ids).distinct()
        if furnishing_ids:
            available_apartments = available_apartments.filter(furnishings__id__in=furnishing_ids).distinct()
        
        print(f"Found {available_apartments.count()} available apartments after filtering")
        
        # Build comprehensive response data
        apartments_data = []
        for apartment in available_apartments:
            # Calculate apartment score for smart recommendations
            apartment_score = self._calculate_apartment_score(apartment)
            
            # Get apartment amenities and furnishings
            amenities_list = [
                {
                    'id': amenity.id,
                    'name': amenity.name,
                    'description': amenity.description
                } for amenity in apartment.amenities.all()
            ]
            
            furnishings_list = [
                {
                    'id': furnishing.id,
                    'name': furnishing.name,
                    'description': furnishing.description
                } for furnishing in apartment.furnishings.all()
            ]
            
            # Calculate derived metrics
            rent_per_room = float(apartment.rent_amount) / apartment.number_of_rooms if apartment.rent_amount and apartment.number_of_rooms else 0
            rent_per_sqm = float(apartment.rent_amount) / float(apartment.size) if apartment.rent_amount and apartment.size else 0
            
            apartment_data = {
                'id': apartment.id,
                'number': apartment.number,
                'block': {
                    'id': apartment.block.id,
                    'name': apartment.block.name,
                    'description': apartment.block.description,
                    'estate': {
                        'id': apartment.block.estate.id,
                        'name': apartment.block.estate.name,
                        'address': apartment.block.estate.address,
                        'description': apartment.block.estate.description
                    }
                },
                'rent_amount': str(apartment.rent_amount) if apartment.rent_amount else None,
                'number_of_rooms': apartment.number_of_rooms,
                'size': str(apartment.size) if apartment.size else None,
                'color': apartment.color,
                'description': apartment.description,
                'amenities': amenities_list,
                'furnishings': furnishings_list,
                'created_at': apartment.created_at,
                
                # Smart allocation metrics
                'allocation_score': apartment_score,
                'rent_per_room': round(rent_per_room, 2) if rent_per_room else 0,
                'rent_per_sqm': round(rent_per_sqm, 2) if rent_per_sqm else 0,
                'is_furnished': len(furnishings_list) > 0,
                'amenities_count': len(amenities_list),
                'furnishings_count': len(furnishings_list),
                
                # Room categorization for smart matching
                'room_category': self._categorize_by_rooms(apartment.number_of_rooms),
                'size_category': self._categorize_by_size(apartment.size),
                'rent_category': self._categorize_by_rent(apartment.rent_amount),
                
                # Full address for display
                'full_address': f"{apartment.block.estate.name} - {apartment.block.name} - {apartment.number}",
                'location_hierarchy': {
                    'estate': apartment.block.estate.name,
                    'block': apartment.block.name,
                    'apartment': apartment.number
                }
            }
            apartments_data.append(apartment_data)
        
        # Sort by allocation score (highest first) for smart recommendations
        apartments_data.sort(key=lambda x: x['allocation_score'], reverse=True)
        
        # Generate summary statistics
        summary = self._generate_availability_summary(apartments_data)

        print({
            'total_available': len(apartments_data),
            'apartments': apartments_data,
            'summary': summary,
            'filters_applied': {
                'min_rooms': min_rooms,
                'max_rooms': max_rooms,
                'min_rent': min_rent,
                'max_rent': max_rent,
                'min_size': min_size,
                'max_size': max_size,
                'estate_id': estate_id,
                'block_id': block_id,
                'amenities': amenity_ids,
                'furnishings': furnishing_ids
            }
        })
        
        return Response({
            'total_available': len(apartments_data),
            'apartments': apartments_data,
            'summary': summary,
            'filters_applied': {
                'min_rooms': min_rooms,
                'max_rooms': max_rooms,
                'min_rent': min_rent,
                'max_rent': max_rent,
                'min_size': min_size,
                'max_size': max_size,
                'estate_id': estate_id,
                'block_id': block_id,
                'amenities': amenity_ids,
                'furnishings': furnishing_ids
            }
        })
    
    def _calculate_apartment_score(self, apartment):
        """Calculate a score for apartment recommendation based on various factors"""
        score = 0
        
        # Room score (more rooms = higher score, but diminishing returns)
        if apartment.number_of_rooms:
            score += min(apartment.number_of_rooms * 10, 50)  # Cap at 50 points
        
        # Size score
        if apartment.size:
            if apartment.size >= 100:  # Large apartments
                score += 30
            elif apartment.size >= 50:  # Medium apartments
                score += 20
            else:  # Small apartments
                score += 10
        
        # Amenities score
        amenities_count = apartment.amenities.count()
        score += min(amenities_count * 5, 25)  # Cap at 25 points
        
        # Furnishings score
        furnishings_count = apartment.furnishings.count()
        score += min(furnishings_count * 3, 15)  # Cap at 15 points
        
        # Rent efficiency score (lower rent per room = higher score)
        if apartment.rent_amount and apartment.number_of_rooms:
            rent_per_room = float(apartment.rent_amount) / apartment.number_of_rooms
            if rent_per_room < 5000:  # Very affordable
                score += 20
            elif rent_per_room < 10000:  # Affordable
                score += 15
            elif rent_per_room < 15000:  # Moderate
                score += 10
            else:  # Expensive
                score += 5
        
        return score
    
    def _categorize_by_rooms(self, rooms):
        """Categorize apartment by number of rooms"""
        if not rooms:
            return 'unknown'
        elif rooms == 1:
            return 'studio'
        elif rooms == 2:
            return '1-bedroom'
        elif rooms == 3:
            return '2-bedroom'
        elif rooms == 4:
            return '3-bedroom'
        elif rooms >= 5:
            return 'large-family'
        else:
            return 'other'
    
    def _categorize_by_size(self, size):
        """Categorize apartment by size"""
        if not size:
            return 'unknown'
        elif size < 30:
            return 'small'
        elif size < 60:
            return 'medium'
        elif size < 100:
            return 'large'
        else:
            return 'extra-large'
    
    def _categorize_by_rent(self, rent):
        """Categorize apartment by rent amount"""
        if not rent:
            return 'unknown'
        elif rent < 10000:
            return 'budget'
        elif rent < 20000:
            return 'affordable'
        elif rent < 35000:
            return 'moderate'
        elif rent < 50000:
            return 'premium'
        else:
            return 'luxury'
    
    def _generate_availability_summary(self, apartments_data):
        """Generate summary statistics for available apartments"""
        if not apartments_data:
            return {}
        
        # Count by categories
        room_categories = {}
        size_categories = {}
        rent_categories = {}
        estates = {}
        
        total_rent = 0
        total_size = 0
        rent_count = 0
        size_count = 0
        
        for apt in apartments_data:
            # Room categories
            room_cat = apt['room_category']
            room_categories[room_cat] = room_categories.get(room_cat, 0) + 1
            
            # Size categories
            size_cat = apt['size_category']
            size_categories[size_cat] = size_categories.get(size_cat, 0) + 1
            
            # Rent categories
            rent_cat = apt['rent_category']
            rent_categories[rent_cat] = rent_categories.get(rent_cat, 0) + 1
            
            # Estates
            estate_name = apt['block']['estate']['name']
            estates[estate_name] = estates.get(estate_name, 0) + 1
            
            # Calculate averages
            if apt['rent_amount']:
                total_rent += float(apt['rent_amount'])
                rent_count += 1
            
            if apt['size']:
                total_size += float(apt['size'])
                size_count += 1
        
        return {
            'by_room_category': room_categories,
            'by_size_category': size_categories,
            'by_rent_category': rent_categories,
            'by_estate': estates,
            'average_rent': round(total_rent / rent_count, 2) if rent_count > 0 else 0,
            'average_size': round(total_size / size_count, 2) if size_count > 0 else 0,
            'furnished_count': sum(1 for apt in apartments_data if apt['is_furnished']),
            'unfurnished_count': sum(1 for apt in apartments_data if not apt['is_furnished'])
        }
    
class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticated]

class FurnishingViewSet(viewsets.ModelViewSet):
    queryset = Furnishing.objects.all()
    serializer_class = FurnishingSerializer
    permission_classes = [IsAuthenticated]

class OwnerDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for Owner Dashboard APIs providing comprehensive property management insights
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='occupancy-status')
    def occupancy_status(self, request):
        """Get occupancy status across all estates"""
        estate_id = request.query_params.get('estate_id')
        
        # Base queryset
        estates_queryset = Estate.objects.all()
        if estate_id:
            estates_queryset = estates_queryset.filter(id=estate_id)
        
        estates_data = []
        total_apartments = 0
        total_occupied = 0
        
        for estate in estates_queryset:
            # Get blocks for this estate
            blocks_data = []
            estate_apartments = 0
            estate_occupied = 0
            
            for block in Block.objects.filter(estate=estate):
                # Count apartments and occupied ones for this block
                block_apartments = Apartment.objects.filter(block=block).count()
                block_occupied = Apartment.objects.filter(block=block, tenant__isnull=False).count()

                blocks_data.append({
                    'block_id': block.id,
                    'block_name': block.name,
                    'total_apartments': block_apartments,
                    'occupied_apartments': block_occupied,
                    'vacant_apartments': block_apartments - block_occupied,
                    'occupancy_rate': round((block_occupied / block_apartments * 100) if block_apartments > 0 else 0, 2)
                })
                
                estate_apartments += block_apartments
                estate_occupied += block_occupied
            
            estates_data.append({
                'estate_id': estate.id,
                'estate_name': estate.name,
                'total_apartments': estate_apartments,
                'occupied_apartments': estate_occupied,
                'vacant_apartments': estate_apartments - estate_occupied,
                'occupancy_rate': round((estate_occupied / estate_apartments * 100) if estate_apartments > 0 else 0, 2),
                'blocks': blocks_data
            })
            
            total_apartments += estate_apartments
            total_occupied += estate_occupied
        
        return Response({
            'total_estates': estates_queryset.count(),
            'total_apartments': total_apartments,
            'occupied_apartments': total_occupied,
            'vacant_apartments': total_apartments - total_occupied,
            'occupancy_rate': round((total_occupied / total_apartments * 100) if total_apartments > 0 else 0, 2),
            'estates': estates_data
        })
    
    @action(detail=False, methods=['get'], url_path='payment-dashboard-summary')
    def payment_dashboard_summary(self, request):
        """Get payment dashboard summary"""
        try:
            from payments.models import Payment
            
            # Get current month payments
            current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate payment statistics
            payments_queryset = Payment.objects.filter(created_at__gte=current_month)
            
            paid_payments = payments_queryset.filter(status__name='PAID').count()
            pending_payments = payments_queryset.filter(status__name='PENDING').count()
            overdue_payments = payments_queryset.filter(
                status__name='PENDING', 
                due_date__lt=timezone.now().date()
            ).count()
            
            total_collected = payments_queryset.filter(status__name='PAID').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            total_expected = payments_queryset.aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            payment_rate = round((paid_payments / (paid_payments + pending_payments) * 100) if (paid_payments + pending_payments) > 0 else 0, 2)

            print({
                'monthly_revenue': float(total_collected),
                'payment_rate': payment_rate,
                'paid_payments': paid_payments,
                'pending_payments': pending_payments,
                'overdue_payments': overdue_payments,
                'total_expected': float(total_expected),
                'total_collected': float(total_collected)
            })
            
            return Response({
                'monthly_revenue': float(total_collected),
                'payment_rate': payment_rate,
                'paid_payments': paid_payments,
                'pending_payments': pending_payments,
                'overdue_payments': overdue_payments,
                'total_expected': float(total_expected),
                'total_collected': float(total_collected)
            })
            
        except ImportError:
            # Fallback if payments app not available
            return Response({
                'monthly_revenue': 0,
                'payment_rate': 0,
                'paid_payments': 0,
                'pending_payments': 0,
                'overdue_payments': 0,
                'total_expected': 0,
                'total_collected': 0
            })
    
    @action(detail=False, methods=['get'], url_path='estate-payment-status')
    def estate_payment_status(self, request):
        """Get payment status by estate"""
        try:
            from payments.models import Payment
            
            estates_data = []
            current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            for estate in Estate.objects.all():
                # Get all apartments in this estate
                apartments = Apartment.objects.filter(block__estate=estate)
                total_apartments = apartments.count()
                occupied_apartments = apartments.filter(tenant__isnull=False).count()
                
                # Get payments for this estate's tenants
                estate_payments = Payment.objects.filter(
                    tenant__apartment__block__estate=estate,
                    created_at__gte=current_month
                )
                
                total_expected = estate_payments.aggregate(total=Sum('amount'))['total'] or 0
                collected = estate_payments.filter(status__name='PAID').aggregate(total=Sum('amount'))['total'] or 0
                
                overdue_count = estate_payments.filter(
                    status__name='PENDING',
                    due_date__lt=timezone.now().date()
                ).count()
                
                pending_count = estate_payments.filter(status__name='PENDING').count()
                
                collection_rate = round((float(collected) / float(total_expected) * 100) if total_expected > 0 else 0, 2)
                
                estates_data.append({
                    'estate_id': estate.id,
                    'estate_name': estate.name,
                    'total_apartments': total_apartments,
                    'occupied_apartments': occupied_apartments,
                    'total_rent_expected': float(total_expected),
                    'rent_collected': float(collected),
                    'collection_rate': collection_rate,
                    'overdue_count': overdue_count,
                    'pending_count': pending_count
                })
            
            return Response(estates_data)
            
        except ImportError:
            # Fallback data if payments app not available
            estates_data = []
            for estate in Estate.objects.all():
                apartments = Apartment.objects.filter(block__estate=estate)
                estates_data.append({
                    'estate_id': estate.id,
                    'estate_name': estate.name,
                    'total_apartments': apartments.count(),
                    'occupied_apartments': apartments.filter(tenant__isnull=False).count(),
                    'total_rent_expected': 0,
                    'rent_collected': 0,
                    'collection_rate': 0,
                    'overdue_count': 0,
                    'pending_count': 0
                })
            return Response(estates_data)
    
    @action(detail=False, methods=['get'], url_path='complaint-analytics')
    def complaint_analytics(self, request):
        """Get complaint analytics"""
        try:
            current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get all complaints
            complaints_queryset = Complaint.objects.all()
            total_complaints = complaints_queryset.count()
            
            # Status counts - use proper foreign key filtering
            open_complaints = complaints_queryset.filter(status__name='OPEN').count()
            in_progress_complaints = complaints_queryset.filter(status__name='IN_PROGRESS').count()
            resolved_complaints = complaints_queryset.filter(status__name='RESOLVED').count()
            closed_complaints = complaints_queryset.filter(status__name='CLOSED').count()
            
            # This month complaints
            complaints_this_month = complaints_queryset.filter(
                created_at__gte=current_month
            ).count()
            
            # Category breakdown using foreign key relationship
            complaints_by_category = complaints_queryset.values('category__name').annotate(
                count=Count('id')
            ).order_by('-count')
            category_dict = {item['category__name']: item['count'] for item in complaints_by_category if item['category__name']}
            
            # Calculate average resolution time (mock data for now)
            avg_resolution_time = 3.5  # This would require tracking resolution dates
            
            return Response({
                'total_complaints': total_complaints,
                'open_complaints': open_complaints,
                'in_progress_complaints': in_progress_complaints,
                'resolved_complaints': resolved_complaints,
                'closed_complaints': closed_complaints,
                'avg_resolution_time': avg_resolution_time,
                'complaints_this_month': complaints_this_month,
                'complaints_by_category': category_dict
            })
            
        except ImportError:
            # Fallback if complaints app not available
            return Response({
                'total_complaints': 0,
                'open_complaints': 0,
                'in_progress_complaints': 0,
                'resolved_complaints': 0,
                'closed_complaints': 0,
                'avg_resolution_time': 0,
                'complaints_this_month': 0,
                'complaints_by_category': {}
            })
    
    @action(detail=False, methods=['get'], url_path='tenancy-expiry-dashboard')
    def tenancy_expiry_dashboard(self, request):
        """Get tenancy expiry dashboard data"""
        try:
            current_date = timezone.now().date()
            next_month = current_date + timedelta(days=30)
            this_month_end = current_date + timedelta(days=30)
            
            # Get tenants with lease end dates - use correct field names
            tenants_queryset = Tenant.objects.filter(lease_end__isnull=False)
            
            # Expiring this month
            expiring_this_month = tenants_queryset.filter(
                lease_end__lte=this_month_end,
                lease_end__gte=current_date
            ).count()
            
            # Expiring next month
            expiring_next_month = tenants_queryset.filter(
                lease_end__gt=this_month_end,
                lease_end__lte=next_month
            ).count()
            
            # Get detailed expiring soon list
            expiring_soon = []
            for tenant in tenants_queryset.filter(
                lease_end__lte=next_month,
                lease_end__gte=current_date
            )[:10]:  # Limit to 10 for performance
                days_until = (tenant.lease_end - current_date).days
                expiring_soon.append({
                    'tenant_id': tenant.id,
                    'tenant_name': f"{tenant.user.first_name} {tenant.user.last_name}",
                    'apartment': tenant.apartment.number if tenant.apartment else 'N/A',
                    'estate': tenant.apartment.block.estate.name if tenant.apartment else 'N/A',
                    'lease_end': tenant.lease_end.isoformat(),
                    'days_until_expiry': days_until,
                    'renewal_status': 'pending'  # This would come from a renewal tracking system
                })
            
            # Mock renewal and vacation data
            renewal_rate = 75  # This would be calculated from historical data
            renewed_this_month = 6  # This would come from renewal tracking
            vacated_this_month = 2  # This would come from move-out tracking
            
            return Response({
                'expiring_this_month': expiring_this_month,
                'expiring_next_month': expiring_next_month,
                'renewal_rate': renewal_rate,
                'expiring_soon': expiring_soon,
                'renewed_this_month': renewed_this_month,
                'vacated_this_month': vacated_this_month
            })
            
        except ImportError:
            # Fallback if tenants app not available
            return Response({
                'expiring_this_month': 0,
                'expiring_next_month': 0,
                'renewal_rate': 0,
                'expiring_soon': [],
                'renewed_this_month': 0,
                'vacated_this_month': 0
            })
    
    @action(detail=False, methods=['get'], url_path='payment-alerts')
    def payment_alerts(self, request):
        """Get payment alerts for overdue and upcoming payments"""
        try:
            from payments.models import Payment
            
            current_date = timezone.now().date()
            upcoming_threshold = current_date + timedelta(days=7)
            
            # Overdue payments - use proper foreign key filtering
            overdue_payments = Payment.objects.filter(
                status__name='PENDING',
                due_date__lt=current_date
            ).select_related('tenant', 'tenant__apartment', 'tenant__apartment__block', 'tenant__apartment__block__estate')
            
            overdue_alerts = []
            for payment in overdue_payments[:20]:  # Limit for performance
                days_overdue = (current_date - payment.due_date).days
                overdue_alerts.append({
                    'tenant_id': payment.tenant.id,
                    'tenant_name': f"{payment.tenant.user.first_name} {payment.tenant.user.last_name}",
                    'apartment': payment.tenant.apartment.number if payment.tenant.apartment else 'N/A',
                    'estate': payment.tenant.apartment.block.estate.name if payment.tenant.apartment else 'N/A',
                    'amount': float(payment.amount),
                    'due_date': payment.due_date.isoformat(),
                    'days_overdue': days_overdue,
                    'payment_method': getattr(payment, 'payment_method', 'Not specified')
                })
            
            # Upcoming payments
            upcoming_payments = Payment.objects.filter(
                status__name='PENDING',
                due_date__gte=current_date,
                due_date__lte=upcoming_threshold
            ).select_related('tenant', 'tenant__apartment', 'tenant__apartment__block', 'tenant__apartment__block__estate')
            
            upcoming_alerts = []
            for payment in upcoming_payments[:20]:  # Limit for performance
                days_until = (payment.due_date - current_date).days
                upcoming_alerts.append({
                    'tenant_id': payment.tenant.id,
                    'tenant_name': f"{payment.tenant.user.first_name} {payment.tenant.user.last_name}",
                    'apartment': payment.tenant.apartment.number if payment.tenant.apartment else 'N/A',
                    'estate': payment.tenant.apartment.block.estate.name if payment.tenant.apartment else 'N/A',
                    'amount': float(payment.amount),
                    'due_date': payment.due_date.isoformat(),
                    'days_until_due': days_until
                })
            
            # Recent payments (last 10)
            recent_payments = Payment.objects.filter(
                status__name='PAID'
            ).select_related('tenant', 'tenant__apartment', 'tenant__apartment__block', 'tenant__apartment__block__estate').order_by('-paid_at')[:10]
            
            recent_payments_list = []
            for payment in recent_payments:
                recent_payments_list.append({
                    'tenant_id': payment.tenant.id,
                    'tenant_name': f"{payment.tenant.user.first_name} {payment.tenant.user.last_name}",
                    'apartment': payment.tenant.apartment.number if payment.tenant.apartment else 'N/A',
                    'estate': payment.tenant.apartment.block.estate.name if payment.tenant.apartment else 'N/A',
                    'amount': float(payment.amount),
                    'paid_at': payment.paid_at.isoformat()
                })
            
            return Response({
                'overdue_alerts': overdue_alerts,
                'upcoming_alerts': upcoming_alerts,
                'recent_payments': recent_payments_list
            })
            
        except ImportError:
            # Fallback if payments app not available
            return Response({
                'overdue_alerts': [],
                'upcoming_alerts': [],
                'recent_payments': []
            })
    
    @action(detail=False, methods=['get'], url_path='payment-report')
    def payment_report(self, request):
        """Get detailed payment report for a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'Missing required parameters',
                'detail': 'Both start_date and end_date are required in YYYY-MM-DD format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            from payments.models import Payment
            
            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start > end:
                return Response({
                    'error': 'Invalid date range',
                    'detail': 'End date must be after start date',
                    'code': 'INVALID_DATE_RANGE'
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            # Get payments in date range
            payments_queryset = Payment.objects.filter(
                created_at__date__gte=start,
                created_at__date__lte=end
            )
            
            total_payments = payments_queryset.count()
            total_amount = payments_queryset.aggregate(total=Sum('amount'))['total'] or 0
            paid_amount = payments_queryset.filter(status__name='PAID').aggregate(total=Sum('amount'))['total'] or 0
            pending_amount = payments_queryset.filter(status__name='PENDING').aggregate(total=Sum('amount'))['total'] or 0
            overdue_amount = payments_queryset.filter(
                status__name='PENDING', 
                due_date__lt=timezone.now().date()
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            collection_rate = round((float(paid_amount) / float(total_amount) * 100) if total_amount > 0 else 0, 2)
            
            # Estate breakdown
            estates_data = []
            for estate in Estate.objects.all():
                estate_payments = payments_queryset.filter(tenant__apartment__block__estate=estate)
                estate_total = estate_payments.aggregate(total=Sum('amount'))['total'] or 0
                estate_paid = estate_payments.filter(status__name='PAID').aggregate(total=Sum('amount'))['total'] or 0
                estate_pending = estate_payments.filter(status__name='PENDING').aggregate(total=Sum('amount'))['total'] or 0
                estate_overdue = estate_payments.filter(
                    status__name='PENDING',
                    due_date__lt=timezone.now().date()
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                if estate_total > 0:  # Only include estates with payments
                    estates_data.append({
                        'estate_id': estate.id,
                        'estate_name': estate.name,
                        'payments': estate_payments.count(),
                        'total_amount': float(estate_total),
                        'paid_amount': float(estate_paid),
                        'pending_amount': float(estate_pending),
                        'overdue_amount': float(estate_overdue),
                        'collection_rate': round((float(estate_paid) / float(estate_total) * 100) if estate_total > 0 else 0, 2)
                    })
            
            # Payment methods breakdown
            payment_methods = payments_queryset.values('payment_method').annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            ).order_by('-total_amount')
            
            methods_data = [
                {
                    'method': method['payment_method'] or 'Not Specified',
                    'count': method['count'],
                    'total_amount': float(method['total_amount'] or 0)
                } for method in payment_methods
            ]
            
            # Monthly breakdown
            monthly_data = []
            current = start.replace(day=1)
            while current <= end:
                month_end = (current.replace(month=current.month + 1) if current.month < 12 
                           else current.replace(year=current.year + 1, month=1)) - timedelta(days=1)
                
                month_payments = payments_queryset.filter(
                    created_at__date__gte=current,
                    created_at__date__lte=min(month_end, end)
                )
                
                month_total = month_payments.aggregate(total=Sum('amount'))['total'] or 0
                month_paid = month_payments.filter(status__name='PAID').aggregate(total=Sum('amount'))['total'] or 0
                
                monthly_data.append({
                    'month': current.strftime('%Y-%m'),
                    'total_payments': month_payments.count(),
                    'total_amount': float(month_total),
                    'collection_rate': round((float(month_paid) / float(month_total) * 100) if month_total > 0 else 0, 2)
                })
                
                current = month_end + timedelta(days=1)
            
            return Response({
                'total_payments': total_payments,
                'total_amount': float(total_amount),
                'paid_amount': float(paid_amount),
                'pending_amount': float(pending_amount),
                'overdue_amount': float(overdue_amount),
                'collection_rate': collection_rate,
                'estates': estates_data,
                'payment_methods': methods_data,
                'monthly_breakdown': monthly_data
            })
            
        except ImportError:
            return Response({
                'total_payments': 0,
                'total_amount': 0,
                'paid_amount': 0,
                'pending_amount': 0,
                'overdue_amount': 0,
                'collection_rate': 0,
                'estates': [],
                'payment_methods': [],
                'monthly_breakdown': []
            })
        except ValueError as e:
            return Response({
                'error': 'Invalid date format',
                'detail': 'Dates must be in YYYY-MM-DD format'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='occupancy-report')
    def occupancy_report(self, request):
        """Get detailed occupancy report for a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'Missing required parameters',
                'detail': 'Both start_date and end_date are required in YYYY-MM-DD format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start > end:
                return Response({
                    'error': 'Invalid date range',
                    'detail': 'End date must be after start date'
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            # Generate occupancy trends (daily snapshots)
            occupancy_trends = []
            current = start
            while current <= end:
                # Get tenancies active on this date - use correct field names
                active_tenancies = Tenant.objects.filter(
                    lease_start__lte=current,
                    lease_end__gte=current
                ).count()
                
                total_apartments = Apartment.objects.count()
                
                occupancy_trends.append({
                    'date': current.isoformat(),
                    'total_apartments': total_apartments,
                    'occupied': active_tenancies,
                    'vacant': total_apartments - active_tenancies,
                    'occupancy_rate': round((active_tenancies / total_apartments * 100) if total_apartments > 0 else 0, 2)
                })
                
                current += timedelta(days=7)  # Weekly snapshots for performance
            
            # Estate breakdown
            estate_breakdown = []
            for estate in Estate.objects.all():
                estate_apartments = Apartment.objects.filter(block__estate=estate)
                total_units = estate_apartments.count()
                
                if total_units > 0:
                    # Calculate metrics for the period
                    current_occupied = estate_apartments.filter(tenant__isnull=False).count()
                    
                    # Use correct field names for tenant dates
                    move_ins = Tenant.objects.filter(
                        apartment__block__estate=estate,
                        lease_start__gte=start,
                        lease_start__lte=end
                    ).count()
                    
                    move_outs = Tenant.objects.filter(
                        apartment__block__estate=estate,
                        lease_end__gte=start,
                        lease_end__lte=end,
                        lease_end__lt=timezone.now().date()
                    ).count()
                    
                    avg_occupancy = round((current_occupied / total_units * 100), 2)
                    turnover_rate = round(((move_ins + move_outs) / total_units * 100), 2)
                    
                    estate_breakdown.append({
                        'estate_id': estate.id,
                        'estate_name': estate.name,
                        'avg_occupancy': avg_occupancy,
                        'peak_occupancy': min(avg_occupancy + 10, 100),  # Mock peak
                        'lowest_occupancy': max(avg_occupancy - 10, 0),  # Mock lowest
                        'total_apartments': total_units,
                        'move_ins': move_ins,
                        'move_outs': move_outs,
                        'turnover_rate': turnover_rate
                    })
            
            # Summary calculations
            total_apartments = Apartment.objects.count()
            occupied_apartments = Apartment.objects.filter(tenant__isnull=False).count();
            
            summary = {
                'average_occupancy': round((occupied_apartments / total_apartments * 100) if total_apartments > 0 else 0, 2),
                'peak_occupancy': 92,  # Mock data
                'lowest_occupancy': 62,  # Mock data
                'total_apartments': total_apartments,
                'occupied_apartments': occupied_apartments,
                'vacant_apartments': total_apartments - occupied_apartments
            }
            
            return Response({
                'occupancy_trends': occupancy_trends,
                'estate_breakdown': estate_breakdown,
                'summary': summary
            })
            
        except ValueError as e:
            return Response({
                'error': 'Invalid date format',
                'detail': 'Dates must be in YYYY-MM-DD format'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='complaint-report')
    def complaint_report(self, request):
        """Get detailed complaint report for a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'Missing required parameters',
                'detail': 'Both start_date and end_date are required in YYYY-MM-DD format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start > end:
                return Response({
                    'error': 'Invalid date range',
                    'detail': 'End date must be after start date'
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            # Get complaints in date range
            complaints_queryset = Complaint.objects.filter(
                created_at__date__gte=start,
                created_at__date__lte=end
            )
            
            total_complaints = complaints_queryset.count()
            open_complaints = complaints_queryset.filter(status__name='OPEN').count()
            in_progress_complaints = complaints_queryset.filter(status__name='IN_PROGRESS').count()
            resolved_complaints = complaints_queryset.filter(status__name='RESOLVED').count()
            closed_complaints = complaints_queryset.filter(status__name='CLOSED').count()
            
            # Category breakdown using foreign key relationship
            categories_data = []
            categories = complaints_queryset.values('category__id', 'category__name').annotate(
                count=Count('id'),
                resolved_count=Count(Case(When(status__name='RESOLVED', then=1)))
            ).order_by('-count')
            
            for category in categories:
                if category['category__name']:  # Only include non-null categories
                    cat_id = category['category__id']
                    cat_name = category['category__name']
                    cat_count = category['count']
                    cat_resolved = category['resolved_count']
                    
                    categories_data.append({
                        'category_id': cat_id,
                        'category': cat_name,
                        'count': cat_count,
                        'resolved': cat_resolved,
                        'resolution_rate': round((cat_resolved / cat_count * 100) if cat_count > 0 else 0, 2),
                        'avg_resolution_time': 2.8  # Mock data
                    })
            
            # Estate breakdown
            estates_data = []
            for estate in Estate.objects.all():
                estate_complaints = complaints_queryset.filter(tenant__apartment__block__estate=estate)
                estate_total = estate_complaints.count()
                estate_resolved = estate_complaints.filter(status__name='RESOLVED').count()
                
                if estate_total > 0:
                    estates_data.append({
                        'estate_id': estate.id,
                        'estate_name': estate.name,
                        'total_complaints': estate_total,
                        'resolved_complaints': estate_resolved,
                        'resolution_rate': round((estate_resolved / estate_total * 100) if estate_total > 0 else 0, 2),
                        'avg_resolution_time': 2.5  # Mock data
                    })
            
            # Monthly breakdown
            monthly_data = []
            current = start.replace(day=1)
            while current <= end:
                month_end = (current.replace(month=current.month + 1) if current.month < 12 
                           else current.replace(year=current.year + 1, month=1)) - timedelta(days=1)
                
                month_complaints = complaints_queryset.filter(
                    created_at__date__gte=current,
                    created_at__date__lte=min(month_end, end)
                )
                
                month_resolved = month_complaints.filter(status__name='RESOLVED').count()
                
                monthly_data.append({
                    'month': current.strftime('%Y-%m'),
                    'new_complaints': month_complaints.count(),
                    'resolved_complaints': month_resolved,
                    'avg_resolution_time': 3.1  # Mock data
                })
                
                current = month_end + timedelta(days=1)
            
            return Response({
                'total_complaints': total_complaints,
                'open_complaints': open_complaints,
                'in_progress_complaints': in_progress_complaints,
                'resolved_complaints': resolved_complaints,
                'closed_complaints': closed_complaints,
                'avg_resolution_time': 3.2,  # Mock data
                'complaint_categories': categories_data,
                'estates': estates_data,
                'monthly_breakdown': monthly_data
            })
            
        except ImportError:
            return Response({
                'total_complaints': 0,
                'open_complaints': 0,
                'in_progress_complaints': 0,
                'resolved_complaints': 0,
                'closed_complaints': 0,
                'avg_resolution_time': 0,
                'complaint_categories': [],
                'estates': [],
                'monthly_breakdown': []
            })
        except ValueError as e:
            return Response({
                'error': 'Invalid date format',
                'detail': 'Dates must be in YYYY-MM-DD format'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='complaint-trends')
    def complaint_trends(self, request):
        """Get complaint trends for the specified period"""
        days = int(request.query_params.get('days', 30))
        
        try:
            start_date = timezone.now().date() - timedelta(days=days)
            end_date = timezone.now().date()
            
            complaints_queryset = Complaint.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
            
            new_complaints = complaints_queryset.count()
            resolved_complaints = complaints_queryset.filter(status__name='RESOLVED').count()
            
            # Mock escalated complaints (would need proper escalation tracking)
            escalated_complaints = 0
            
            resolution_rate = round((resolved_complaints / new_complaints * 100) if new_complaints > 0 else 0, 2)
            
            # Daily trends
            daily_trends = []
            current = start_date
            while current <= end_date:
                daily_complaints = complaints_queryset.filter(created_at__date=current)
                daily_resolved = daily_complaints.filter(status__name='RESOLVED').count()
                daily_escalated = 0  # Mock data
                
                daily_trends.append({
                    'date': current.isoformat(),
                    'new': daily_complaints.count(),
                    'resolved': daily_resolved,
                    'escalated': daily_escalated
                })
                
                current += timedelta(days=1)
            
            # Category trends (mock data for now)
            category_trends = [
                {'category': 'Maintenance', 'trend': 'increasing', 'change_percent': 15},
                {'category': 'Noise', 'trend': 'decreasing', 'change_percent': -8},
                {'category': 'Security', 'trend': 'stable', 'change_percent': 2}
            ]
            
            return Response({
                'new_complaints': new_complaints,
                'resolved_complaints': resolved_complaints,
                'escalated_complaints': escalated_complaints,
                'avg_resolution_time': 3.5,  # Mock data
                'resolution_rate': resolution_rate,
                'satisfaction_score': 4.2,  # Mock data
                'daily_trends': daily_trends,
                'category_trends': category_trends
            })
            
        except ImportError:
            return Response({
                'new_complaints': 0,
                'resolved_complaints': 0,
                'escalated_complaints': 0,
                'avg_resolution_time': 0,
                'resolution_rate': 0,
                'satisfaction_score': 0,
                'daily_trends': [],
                'category_trends': []
            })

    @action(detail=False, methods=['get'], url_path='tenants-expiring')
    def tenants_expiring(self, request):
        """Get tenants with leases expiring in the date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'Missing required parameters',
                'detail': 'Both start_date and end_date are required in YYYY-MM-DD format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start > end:
                return Response({
                    'error': 'Invalid date range',
                    'detail': 'End date must be after start date'
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            # Get tenants with lease end dates in range - use correct field names
            tenants_queryset = Tenant.objects.filter(
                lease_end__gte=start,
                lease_end__lte=end
            ).select_related('apartment', 'apartment__block', 'apartment__block__estate', 'user')
            
            tenants_data = []
            current_date = timezone.now().date()
            
            for tenant in tenants_queryset:
                days_until = (tenant.lease_end - current_date).days
                
                # Determine renewal status
                if days_until < 0:
                    renewal_status = 'expired'
                elif days_until <= 30:
                    renewal_status = 'pending'
                else:
                    renewal_status = 'upcoming'
                
                tenants_data.append({
                    'tenant_id': tenant.id,
                    'tenant_name': f"{tenant.user.first_name} {tenant.user.last_name}",
                    'apartment': tenant.apartment.number if tenant.apartment else 'N/A',
                    'apartment_id': tenant.apartment.id if tenant.apartment else None,
                    'estate': tenant.apartment.block.estate.name if tenant.apartment else 'N/A',
                    'estate_id': tenant.apartment.block.estate.id if tenant.apartment else None,
                    'lease_start': tenant.lease_start.isoformat() if tenant.lease_start else None,
                    'lease_end': tenant.lease_end.isoformat(),
                    'days_until_expiry': days_until,
                    'renewal_status': renewal_status,
                    'contact_phone': getattr(tenant, 'phone_number', 'Not provided'),
                    'contact_email': tenant.user.email if tenant.user else 'Not provided',
                    'rent_amount': float(tenant.apartment.rent_amount) if tenant.apartment and tenant.apartment.rent_amount else 0,
                    'deposit_amount': float(getattr(tenant, 'deposit_amount', 0)),
                    'is_renewed': False,  # This would come from renewal tracking
                    'renewal_date': None  # This would come from renewal tracking
                })
            
            return Response(tenants_data)
            
        except ImportError:
            return Response([])
        except ValueError as e:
            return Response({
                'error': 'Invalid date format',
                'detail': 'Dates must be in YYYY-MM-DD format'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='export-report')
    def export_report(self, request):
        """Generate and export reports in various formats"""
        report_type = request.data.get('report_type')
        format_type = request.data.get('format', 'excel')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not all([report_type, start_date, end_date]):
            return Response({
                'error': 'Missing required fields',
                'detail': 'report_type, start_date, and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mock export functionality (would integrate with actual file generation)
        import uuid
        file_id = str(uuid.uuid4())
        
        # Simulate file generation based on report type
        filenames = {
            'payments': f'payment_report_{start_date}_{end_date}.{format_type}',
            'occupancy': f'occupancy_report_{start_date}_{end_date}.{format_type}',
            'complaints': f'complaint_report_{start_date}_{end_date}.{format_type}',
            'tenancy': f'tenancy_report_{start_date}_{end_date}.{format_type}'
        }
        
        filename = filenames.get(report_type, f'report_{start_date}_{end_date}.{format_type}')
        
        return Response({
            'download_url': f'https://api.example.com/downloads/report_{file_id}.{format_type}',
            'expires_at': (timezone.now() + timedelta(hours=24)).isoformat(),
            'file_size': 2048576,  # Mock file size
            'filename': filename
        })
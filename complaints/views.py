from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Complaint, ComplaintStatus, ComplaintCategory
from .serializers import ComplaintSerializer, ComplaintStatusSerializer, ComplaintCategorySerializer
from tenants.models import Tenant
from core.models import Estate, Block

class ComplaintStatusViewSet(viewsets.ModelViewSet):
    queryset = ComplaintStatus.objects.all()
    serializer_class = ComplaintStatusSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """Override list to add debug information"""
        print("=== COMPLAINT STATUS LIST DEBUG ===")
        print(f"Request user: {request.user}")
        print(f"Request method: {request.method}")
        print(f"Request path: {request.path}")
        print(f"Query params: {request.query_params}")
        
        try:
            queryset = self.get_queryset()
            print(f"Queryset count: {queryset.count()}")
            print(f"Queryset values: {list(queryset.values())}")
            
            serializer = self.get_serializer(queryset, many=True)
            print(f"Serialized data: {serializer.data}")
            
            return Response(serializer.data)
        except Exception as e:
            print(f"Exception in ComplaintStatusViewSet.list: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while fetching complaint statuses',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add debug information"""
        print("=== COMPLAINT STATUS RETRIEVE DEBUG ===")
        print(f"Request user: {request.user}")
        print(f"PK: {kwargs.get('pk')}")
        
        try:
            instance = self.get_object()
            print(f"Retrieved instance: {instance}")
            print(f"Instance ID: {instance.id}")
            print(f"Instance name: {instance.name}")
            
            serializer = self.get_serializer(instance)
            print(f"Serialized data: {serializer.data}")
            
            return Response(serializer.data)
        except Exception as e:
            print(f"Exception in ComplaintStatusViewSet.retrieve: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while fetching complaint status',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Override create to add debug information"""
        print("=== COMPLAINT STATUS CREATE DEBUG ===")
        print(f"Request data: {request.data}")
        print(f"Request user: {request.user}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            print(f"Serializer initial data: {serializer.initial_data}")
            
            if serializer.is_valid():
                print("Serializer is valid, creating complaint status...")
                self.perform_create(serializer)
                print(f"Created complaint status: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(f"Serializer validation errors: {serializer.errors}")
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Exception in ComplaintStatusViewSet.create: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while creating complaint status',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        """Override get_queryset to add debug information"""
        print("=== COMPLAINT STATUS GET_QUERYSET DEBUG ===")
        queryset = ComplaintStatus.objects.all()
        print(f"Base queryset: {queryset}")
        print(f"Base queryset count: {queryset.count()}")
        
        # Log all complaint statuses in database
        for status_obj in queryset:
            print(f"Status ID: {status_obj.id}, Name: {status_obj.name}")
        
        return queryset

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Complaint.objects.all()
        status_id = self.request.query_params.get('status_id')
        tenant_id = self.request.query_params.get('tenant_id')
        
        if status_id:
            queryset = queryset.filter(status_id=status_id)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_complaints(self, request):
        """Get complaints for the logged-in tenant with comprehensive data"""
        print("=== MY COMPLAINTS DEBUG ===")
        print(f"Request user: {request.user}")
        
        try:
            tenant = Tenant.objects.get(user=request.user)
            print(f"Found tenant: {tenant}")
            print(f"Tenant ID: {tenant.id}")
            print(f"Tenant apartment: {tenant.apartment}")
            
            # Get complaints with related data for better performance
            complaints = Complaint.objects.filter(tenant=tenant).select_related(
                'status', 'category', 'tenant__user', 'tenant__apartment'
            ).order_by('-created_at')
            
            print(f"Found {complaints.count()} complaints for tenant")
            
            # Build comprehensive response data
            complaints_data = []
            for complaint in complaints:
                # Get status information
                status_info = {
                    'id': complaint.status.id if complaint.status else None,
                    'name': complaint.status.name if complaint.status else 'Unknown'
                }
                
                # Get category information
                category_info = {
                    'id': complaint.category.id if complaint.category else None,
                    'name': complaint.category.name if complaint.category else 'Uncategorized',
                    'description': complaint.category.description if complaint.category else ''
                }
                
                # Get tenant apartment information
                apartment_info = {}
                if complaint.tenant.apartment:
                    apartment_info = {
                        'number': complaint.tenant.apartment.number,
                        'block': complaint.tenant.apartment.block.name if complaint.tenant.apartment.block else 'Unknown Block',
                        'estate': complaint.tenant.apartment.block.estate.name if complaint.tenant.apartment.block else 'Unknown Estate'
                    }
                else:
                    apartment_info = {
                        'number': 'N/A',
                        'block': 'N/A', 
                        'estate': 'N/A'
                    }
                
                # Calculate days since complaint was created
                days_since_created = (timezone.now().date() - complaint.created_at.date()).days
                
                # Determine complaint urgency based on age and status
                urgency = 'low'
                if complaint.status and complaint.status.name.lower() in ['open', 'pending']:
                    if days_since_created > 7:
                        urgency = 'high'
                    elif days_since_created > 3:
                        urgency = 'medium'
                
                complaint_data = {
                    'id': complaint.id,
                    'title': complaint.title or 'No Title',
                    'description': complaint.description,
                    'status': status_info,
                    'category': category_info,
                    'feedback': complaint.feedback or '',
                    'attachment': complaint.attachment.url if complaint.attachment else None,
                    'created_at': complaint.created_at.isoformat(),
                    'updated_at': complaint.updated_at.isoformat(),
                    'apartment': apartment_info,
                    'tenant_name': f"{complaint.tenant.user.first_name} {complaint.tenant.user.last_name}",
                    'days_since_created': days_since_created,
                    'urgency': urgency,
                    'has_feedback': bool(complaint.feedback),
                    'is_resolved': complaint.status.name.lower() in ['resolved', 'closed'] if complaint.status else False,
                    'can_be_updated': complaint.status.name.lower() in ['open', 'pending', 'in progress'] if complaint.status else True
                }
                
                complaints_data.append(complaint_data)
                
            # Generate summary statistics
            summary = {
                'total_complaints': len(complaints_data),
                'open': len([c for c in complaints_data if c['status']['name'].lower() in ['open', 'pending']]),
                'resolved': len([c for c in complaints_data if c['is_resolved']]),
                'complaints_with_feedback': len([c for c in complaints_data if c['has_feedback']]),
                'urgent_complaints': len([c for c in complaints_data if c['urgency'] == 'high']),
                'average_days_open': sum(c['days_since_created'] for c in complaints_data if not c['is_resolved']) / max(len([c for c in complaints_data if not c['is_resolved']]), 1)
            }
            
            print(f"Complaints data summary: {summary}")
            print(f"Sample complaint data: {complaints_data[0] if complaints_data else 'No complaints'}")
            
            return Response({
                'complaints': complaints_data,
                'summary': summary,
                'tenant_info': {
                    'id': tenant.id,
                    'name': f"{tenant.user.first_name} {tenant.user.last_name}",
                    'apartment': apartment_info,
                    'phone': getattr(tenant, 'phone_number', 'Not provided'),
                    'email': tenant.user.email
                }
            })
            
        except Tenant.DoesNotExist:
            print(f"Tenant not found for user: {request.user}")
            return Response({
                'error': 'Tenant profile not found',
                'detail': 'No tenant profile is associated with your account'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Exception in my_complaints: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while fetching complaints',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update complaint status and provide feedback"""
        print("=== COMPLAINT UPDATE STATUS DEBUG ===")
        print(f"Request data: {request.data}")
        print(f"Complaint PK: {pk}")
        print(f"Request user: {request.user}")
        
        try:
            complaint = self.get_object()
            print(f"Retrieved complaint: {complaint}")
            print(f"Current complaint status: {complaint.status}")
            print(f"Current complaint status ID: {complaint.status.id if complaint.status else None}")
            
            status_id = request.data.get('status_id')
            feedback = request.data.get('feedback', '')
            
            print(f"New status ID: {status_id}")
            print(f"Feedback: {feedback}")
            
            if status_id:
                try:
                    new_status = ComplaintStatus.objects.get(id=status_id)
                    print(f"Found new status: {new_status}")
                    
                    complaint.status = new_status
                    complaint.feedback = feedback
                    complaint.save()
                    
                    print(f"Updated complaint status to: {complaint.status}")
                    print(f"Updated complaint feedback to: {complaint.feedback}")
                    
                    # TODO: Trigger email notification to tenant
                    return Response({
                        'message': 'Status updated successfully',
                        'complaint_id': complaint.id,
                        'new_status': complaint.status.name,
                        'feedback': complaint.feedback
                    })
                except ComplaintStatus.DoesNotExist:
                    print(f"ComplaintStatus with ID {status_id} not found")
                    return Response({
                        'error': f'Complaint status with ID {status_id} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                print("No status_id provided in request")
                return Response({
                    'error': 'status_id required'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"Exception in update_status: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while updating complaint status',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def log_complaint(self, request):
        """Tenant logs a new complaint"""
        print("=== LOG COMPLAINT DEBUG ===")
        print(f"Request data: {request.data}")
        print(f"Request user: {request.user}")
        
        try:
            tenant = Tenant.objects.get(user=request.user)
            print(f"Found tenant: {tenant}")
            
            data = request.data.copy()
            data['tenant'] = tenant.id
            print(f"Modified data with tenant: {data}")
            
            # Set default status to 'Open'
            print("Looking for 'Open' status or creating it...")
            open_status, created = ComplaintStatus.objects.get_or_create(
                name='Open',
                defaults={'name': 'Open'}
            )
            print(f"Open status: {open_status} (created: {created})")
            data['status'] = open_status.id
            print(f"Final data with status: {data}")
            
            serializer = self.get_serializer(data=data)
            print(f"Serializer initial data: {serializer.initial_data}")
            
            if serializer.is_valid():
                print("Serializer is valid, saving complaint...")
                complaint = serializer.save()
                print(f"Created complaint: {complaint}")
                
                # TODO: Send SMS and email alert to property manager
                # TODO: Send confirmation SMS to tenant
                
                return Response({
                    'message': 'Complaint logged successfully. Property manager will respond soon.',
                    'complaint': ComplaintSerializer(complaint).data
                }, status=status.HTTP_201_CREATED)
            else:
                print(f"Serializer validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Tenant.DoesNotExist:
            print(f"Tenant not found for user: {request.user}")
            return Response({'error': 'Tenant profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Exception in log_complaint: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while logging complaint',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def complaint_categories(self, request):
        """Get available complaint categories for tenant"""
        categories = ComplaintCategory.objects.all()
        serializer = ComplaintCategorySerializer(categories, many=True)
        return Response(serializer.data)

    # ...existing manager methods...
    @action(detail=False, methods=['get'])
    def dashboard_analytics(self, request):
        """Get complaint analytics for property owner dashboard"""
        total_complaints = Complaint.objects.count()
        
        # Count by status
        status_counts = Complaint.objects.values('status__name').annotate(
            count=Count('id')
        ).order_by('status__name')
        
        status_dict = {item['status__name'].lower(): item['count'] for item in status_counts}
        
        open_complaints = status_dict.get('open', 0)
        in_progress_complaints = status_dict.get('in progress', 0) + status_dict.get('pending review', 0)
        resolved_complaints = status_dict.get('resolved', 0)
        closed_complaints = status_dict.get('closed', 0)
        
        # Calculate average resolution time (simplified)
        resolved_complaints_list = Complaint.objects.filter(
            status__name__icontains='resolved'
        ).exclude(created_at__isnull=True).exclude(updated_at__isnull=True)
        
        if resolved_complaints_list.exists():
            total_resolution_time = sum(
                (complaint.updated_at - complaint.created_at).days 
                for complaint in resolved_complaints_list
            )
            avg_resolution_time = total_resolution_time / resolved_complaints_list.count()
        else:
            avg_resolution_time = 0
        
        # Estate-wise analytics
        estates = Estate.objects.all()
        estate_data = []
        
        for estate in estates:
            estate_complaints = Complaint.objects.filter(
                tenant__apartment__block__estate=estate
            )
            estate_total = estate_complaints.count()
            
            estate_resolved = estate_complaints.filter(
                status__name__icontains='resolved'
            ).count()
            
            estate_open = estate_complaints.filter(
                status__name__icontains='open'
            ).count()
            
            # Calculate resolution rate
            resolution_rate = (estate_resolved / estate_total * 100) if estate_total > 0 else 0
            
            # Calculate average resolution time for this estate
            estate_resolved_list = estate_complaints.filter(
                status__name__icontains='resolved'
            ).exclude(created_at__isnull=True).exclude(updated_at__isnull=True)
            
            if estate_resolved_list.exists():
                estate_resolution_time = sum(
                    (complaint.updated_at - complaint.created_at).days 
                    for complaint in estate_resolved_list
                ) / estate_resolved_list.count()
            else:
                estate_resolution_time = 0
            
            # Block-wise breakdown
            blocks_data = []
            estate_blocks = Block.objects.filter(estate=estate)
            for block in estate_blocks:
                block_complaints = estate_complaints.filter(
                    tenant__apartment__block=block
                )
                block_total = block_complaints.count()
                block_open = block_complaints.filter(status__name__icontains='open').count()
                block_resolved = block_complaints.filter(status__name__icontains='resolved').count()
                
                blocks_data.append({
                    'block_id': block.id,
                    'block_name': block.name,
                    'complaints': block_total,
                    'open': block_open,
                    'resolved': block_resolved
                })
            
            estate_data.append({
                'estate_id': estate.id,
                'estate_name': estate.name,
                'total_complaints': estate_total,
                'open_complaints': estate_open,
                'resolution_rate': resolution_rate,
                'avg_resolution_days': estate_resolution_time,
                'blocks': blocks_data
            })
        
        return Response({
            'total_complaints': total_complaints,
            'open_complaints': open_complaints,
            'in_progress_complaints': in_progress_complaints,
            'resolved_complaints': resolved_complaints,
            'closed_complaints': closed_complaints,
            'avg_resolution_time': avg_resolution_time,
            'estates': estate_data
        })
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get complaint trends over time"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Get daily complaint counts
        trends = []
        current_date = start_date
        
        while current_date <= timezone.now():
            new_complaints = Complaint.objects.filter(
                created_at__date=current_date.date()
            ).count()
            
            resolved_complaints = Complaint.objects.filter(
                updated_at__date=current_date.date(),
                status__name__icontains='resolved'
            ).count()
            
            trends.append({
                'date': current_date.date(),
                'new': new_complaints,
                'resolved': resolved_complaints
            })
            
            current_date += timedelta(days=1)
        
        # Summary for the period
        total_new = Complaint.objects.filter(created_at__gte=start_date).count()
        total_resolved = Complaint.objects.filter(
            updated_at__gte=start_date,
            status__name__icontains='resolved'
        ).count()
        
        return Response({
            'period': f'Last {days} days',
            'new_complaints': total_new,
            'resolved_complaints': total_resolved,
            'trends': trends
        })
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Generate detailed complaint report"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter complaints by date range
        complaints = Complaint.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        total_complaints = complaints.count()
        resolved_complaints = complaints.filter(status__name__icontains='resolved').count()
        
        # Calculate average resolution time
        resolved_list = complaints.filter(status__name__icontains='resolved')
        if resolved_list.exists():
            total_resolution_time = sum(
                (complaint.updated_at - complaint.created_at).days 
                for complaint in resolved_list
            )
            avg_resolution_time = total_resolution_time / resolved_list.count()
        else:
            avg_resolution_time = 0
        
        # Complaint categories (simplified - you can enhance this)
        complaint_categories = [
            {'category': 'Maintenance', 'count': complaints.filter(description__icontains='maintenance').count()},
            {'category': 'Facilities', 'count': complaints.filter(description__icontains='facility').count()},
            {'category': 'Security', 'count': complaints.filter(description__icontains='security').count()},
            {'category': 'Other', 'count': complaints.exclude(
                description__icontains='maintenance'
            ).exclude(
                description__icontains='facility'
            ).exclude(
                description__icontains='security'
            ).count()}
        ]
        
        # Filter out zero counts
        complaint_categories = [cat for cat in complaint_categories if cat['count'] > 0]
        
        # Calculate resolution rates for categories
        for category in complaint_categories:
            if category['count'] > 0:
                resolved_in_category = resolved_complaints  # Simplified - you can make this more specific
                category['resolution_rate'] = (resolved_in_category / total_complaints * 100) if total_complaints > 0 else 0
            else:
                category['resolution_rate'] = 0
        
        # Estate breakdown
        estates = Estate.objects.all()
        estate_breakdown = []
        
        for estate in estates:
            estate_complaints = complaints.filter(tenant__apartment__block__estate=estate)
            estate_count = estate_complaints.count()
            estate_resolved = estate_complaints.filter(status__name__icontains='resolved').count()
            
            if estate_count > 0:
                estate_breakdown.append({
                    'estate_name': estate.name,
                    'complaints': estate_count,
                    'resolution_rate': (estate_resolved / estate_count * 100)
                })
        
        return Response({
            'period': f'{start_date} to {end_date}',
            'total_complaints': total_complaints,
            'resolved_complaints': resolved_complaints,
            'avg_resolution_time': avg_resolution_time,
            'complaint_categories': complaint_categories,
            'estate_breakdown': estate_breakdown
        })
    
    @action(detail=True, methods=['patch'])
    def close(self, request, pk=None):
        """Close a complaint"""
        complaint = self.get_object()
        closed_status = ComplaintStatus.objects.filter(name__icontains='closed').first()
        if closed_status:
            complaint.status = closed_status
            complaint.save()
            # TODO: Trigger email notification to tenant
            return Response({'message': 'Complaint closed successfully'})
        return Response({'error': 'Closed status not found'}, status=status.HTTP_400_BAD_REQUEST)

class ComplaintCategoryViewSet(viewsets.ModelViewSet):
    queryset = ComplaintCategory.objects.all()
    serializer_class = ComplaintCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """Override list to add debug information"""
        print("=== COMPLAINT CATEGORY LIST DEBUG ===")
        print(f"Request user: {request.user}")
        print(f"Request method: {request.method}")
        print(f"Request path: {request.path}")
        print(f"Query params: {request.query_params}")
        
        try:
            queryset = self.get_queryset()
            print(f"Queryset count: {queryset.count()}")
            print(f"Queryset values: {list(queryset.values())}")
            
            serializer = self.get_serializer(queryset, many=True)
            print(f"Serialized data: {serializer.data}")
            
            return Response(serializer.data)
        except Exception as e:
            print(f"Exception in ComplaintCategoryViewSet.list: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while fetching complaint categories',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        """Override get_queryset to add debug information"""
        print("=== COMPLAINT CATEGORY GET_QUERYSET DEBUG ===")
        queryset = ComplaintCategory.objects.all()
        print(f"Base queryset: {queryset}")
        print(f"Base queryset count: {queryset.count()}")
        
        # Log all complaint categories in database
        for category in queryset:
            print(f"Category ID: {category.id}, Name: {category.name}")
        
        return queryset
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Payment, PaymentStatus
from .serializers import PaymentSerializer, PaymentStatusSerializer
from tenants.models import Tenant
from core.models import Estate, Block, Apartment

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Payment.objects.all()
        status_id = self.request.query_params.get('status_id')
        tenant_id = self.request.query_params.get('tenant_id')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        payment_type = self.request.query_params.get('payment_type')
        
        if status_id:
            queryset = queryset.filter(status_id=status_id)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        if month and year:
            queryset = queryset.filter(payment_for_month=month, payment_for_year=year)
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create payment with proper validation"""
        try:
            data = request.data.copy()
            print(f"=== PAYMENT CREATE DEBUG ===")
            print(f"Original request data: {data}")
            print(f"Content type: {request.content_type}")
            
            # Handle months_paid - if provided, use the first month for payment_for_month
            months_paid = data.get('months_paid', [])
            if months_paid and not data.get('payment_for_month'):
                data['payment_for_month'] = months_paid[0]
                print(f"Set payment_for_month to first month in months_paid: {months_paid[0]}")
            
            print(f"Data after processing months_paid: {data}")
            
            # Validate required fields
            required_fields = ['tenant', 'amount', 'due_date', 'payment_for_month', 'payment_for_year']
            missing_fields = []
            for field in required_fields:
                if not data.get(field):
                    missing_fields.append(field)
                    print(f"Missing required field: {field}")
            
            if missing_fields:
                return Response({
                    'error': f'Required fields are missing: {", ".join(missing_fields)}',
                    'missing_fields': missing_fields,
                    'provided_data': list(data.keys())
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"All required fields present: {required_fields}")
            
            # Validate tenant exists
            tenant_id = data.get('tenant')
            print(f"Validating tenant ID: {tenant_id}")
            try:
                tenant = Tenant.objects.get(id=tenant_id)
                print(f"Tenant found: {tenant.user.username} - {tenant.user.first_name} {tenant.user.last_name}")
            except Tenant.DoesNotExist:
                print(f"Tenant with ID {tenant_id} not found")
                return Response({
                    'error': 'Tenant not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validate amount is positive
            try:
                amount = float(data.get('amount'))
                print(f"Amount validation: {amount}")
                if amount <= 0:
                    print(f"Amount is not positive: {amount}")
                    return Response({
                        'error': 'Amount must be greater than 0'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError) as e:
                print(f"Amount format error: {e}")
                return Response({
                    'error': 'Invalid amount format'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate status if provided
            if data.get('status'):
                status_id = data.get('status')
                print(f"Validating status ID: {status_id}")
                try:
                    payment_status = PaymentStatus.objects.get(id=status_id)
                    print(f"Status found: {payment_status.name}")
                except PaymentStatus.DoesNotExist:
                    print(f"Status with ID {status_id} not found")
                    return Response({
                        'error': 'Payment status not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # Set default status if not provided
                pending_status, created = PaymentStatus.objects.get_or_create(
                    name='Pending',
                    defaults={'name': 'Pending'}
                )
                data['status'] = pending_status.id
                print(f"Set default status: {pending_status.name} (ID: {pending_status.id})")
            
            # Check for duplicate payment (same tenant, month, year)
            month = data.get('payment_for_month')
            year = data.get('payment_for_year')
            print(f"Checking for duplicate payment: Tenant {tenant_id}, Month {month}, Year {year}")
            
            existing_payment = Payment.objects.filter(
                tenant=tenant,
                payment_for_month=month,
                payment_for_year=year
            ).first()
            
            if existing_payment:
                print(f"Duplicate payment found: ID {existing_payment.id}")
                return Response({
                    'error': f'Payment for {month}/{year} already exists for this tenant',
                    'existing_payment_id': existing_payment.id
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"No duplicate payment found - proceeding with creation")
            print(f"Final data for serializer: {data}")
            
            # Use serializer to create payment
            serializer = self.get_serializer(data=data)
            print(f"Serializer created with data")
            
            if serializer.is_valid():
                print(f"Serializer is valid - saving payment")
                payment = serializer.save()
                print(f"Payment created successfully with ID: {payment.id}")
                
                return Response({
                    'message': 'Payment created successfully',
                    'payment': PaymentSerializer(payment).data,
                    'months_paid': months_paid
                }, status=status.HTTP_201_CREATED)
            else:
                print(f"Serializer validation failed!")
                print(f"Serializer errors: {serializer.errors}")
                print(f"Serializer error details:")
                for field, errors in serializer.errors.items():
                    print(f"  {field}: {errors}")
                
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors,
                    'provided_data': data
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"Exception in payment create: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while creating the payment',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests with proper validation"""
        try:
            instance = self.get_object()
            data = request.data.copy()

            print(data)
            
            print(f"=== PAYMENT PATCH DEBUG ===")
            print(f"Payment ID: {instance.id}")
            print(f"Request data: {data}")
            
            # Validate tenant if provided
            if 'tenant' in data:
                tenant_id = data.get('tenant')
                try:
                    tenant = Tenant.objects.get(id=tenant_id)
                except Tenant.DoesNotExist:
                    return Response({
                        'error': 'Tenant not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Validate amount if provided
            if 'amount' in data:
                try:
                    amount = float(data.get('amount'))
                    if amount <= 0:
                        return Response({
                            'error': 'Amount must be greater than 0'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except (ValueError, TypeError):
                    return Response({
                        'error': 'Invalid amount format'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate status if provided
            if 'status' in data:
                status_id = data.get('status')
                try:
                    payment_status = PaymentStatus.objects.get(id=status_id)
                    # If status is being changed to 'Paid', set paid_at timestamp
                    if payment_status.name.lower() == 'paid' and not instance.paid_at:
                        data['paid_at'] = timezone.now()
                except PaymentStatus.DoesNotExist:
                    return Response({
                        'error': 'Payment status not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Check for duplicate payment if month/year is being changed
            if 'payment_for_month' in data or 'payment_for_year' in data:
                month = data.get('payment_for_month', instance.payment_for_month)
                year = data.get('payment_for_year', instance.payment_for_year)
                tenant = data.get('tenant', instance.tenant.id)
                
                existing_payment = Payment.objects.filter(
                    tenant_id=tenant,
                    payment_for_month=month,
                    payment_for_year=year
                ).exclude(id=instance.id).first()
                
                if existing_payment:
                    return Response({
                        'error': f'Payment for {month}/{year} already exists for this tenant',
                        'existing_payment_id': existing_payment.id
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Use serializer to update payment
            serializer = self.get_serializer(instance, data=data, partial=True)
            if serializer.is_valid():
                payment = serializer.save()
                
                # Log status change if applicable
                if 'status' in data:
                    print(f"Payment status updated to: {payment.status.name}")
                
                return Response({
                    'message': 'Payment updated successfully',
                    'payment': PaymentSerializer(payment).data
                }, status=status.HTTP_200_OK)
            else:
                print(f"Serializer errors: {serializer.errors}")
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"Exception in payment partial_update: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while updating the payment',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Get payments for the logged-in tenant"""
        try:
            tenant = Tenant.objects.get(user=request.user)
            print(tenant)
            payments = Payment.objects.filter(tenant=tenant).order_by('-created_at')
            serializer = self.get_serializer(payments, many=True)
            return Response(serializer.data)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def my_rent_alerts(self, request):
        """Get rent due alerts for the logged-in tenant"""
        try:
            tenant = Tenant.objects.get(user=request.user)
            today = timezone.now().date()
            
            # Get payments due in next 7 days
            upcoming_due = Payment.objects.filter(
                tenant=tenant,
                status__name__in=['Pending', 'Overdue'],
                due_date__lte=today + timedelta(days=7),
                due_date__gte=today
            ).order_by('due_date')
            
            # Get overdue payments
            overdue = Payment.objects.filter(
                tenant=tenant,
                status__name='Overdue',
                due_date__lt=today
            ).order_by('due_date')
            
            return Response({
                'upcoming_due': PaymentSerializer(upcoming_due, many=True).data,
                'overdue': PaymentSerializer(overdue, many=True).data,
                'total_upcoming': upcoming_due.count(),
                'total_overdue': overdue.count()
            })
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def log_payment(self, request):
        """Tenant logs their payment with receipt"""
        try:
            tenant = Tenant.objects.get(user=request.user)
            data = request.data.copy()
            data['tenant'] = tenant.id
            
            # Get or create 'Processing' status for tenant-logged payments
            processing_status, created = PaymentStatus.objects.get_or_create(
                name='Processing',
                defaults={'name': 'Processing'}
            )
            data['status'] = processing_status.id
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                payment = serializer.save()
                
                # TODO: Send notification to property manager about new payment log
                # TODO: Send SMS alert to property manager
                
                return Response({
                    'message': 'Payment logged successfully. Property manager will verify and update status.',
                    'payment': PaymentSerializer(payment).data
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def payment_receipt_status(self, request):
        """Get payment acknowledgement status for tenant"""
        try:
            tenant = Tenant.objects.get(user=request.user)
            
            # Get recent payments with their acknowledgement status
            recent_payments = Payment.objects.filter(
                tenant=tenant
            ).order_by('-created_at')
            
            payment_data = []
            for payment in recent_payments:
                payment_data.append({
                    'id': payment.id,
                    'amount': str(payment.amount),
                    'due_date': payment.due_date,
                    'paid_at': payment.paid_at,
                    'payment_for_month': payment.payment_for_month,
                    'payment_for_year': payment.payment_for_year,
                    'status': payment.status.name if payment.status else 'Unknown',
                    'payment_method': payment.payment_method,
                    'reference_number': payment.reference_number,
                    'receipt_file': payment.receipt_file.url if payment.receipt_file else None,
                    'acknowledgement_status': 'Acknowledged' if payment.status and payment.status.name == 'Paid' else 'Pending'
                })
            
            print({
                'payments': payment_data,
                'total_paid': recent_payments.filter(status__name='Paid').count(),
                'total_pending': recent_payments.filter(status__name__in=['Pending', 'Processing']).count()
            })
            return Response({
                'payments': payment_data,
                'total_paid': recent_payments.filter(status__name='Paid').count(),
                'total_pending': recent_payments.filter(status__name__in=['Pending', 'Processing']).count()
            })
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # ...existing manager methods...
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get payment dashboard summary for property owner"""
        current_date = timezone.now().date()
        
        # Get payment statistics
        total_payments = Payment.objects.count()
        paid_payments = Payment.objects.filter(status__name__icontains='paid').count()
        pending_payments = Payment.objects.filter(status__name__icontains='pending').count()
        overdue_payments = Payment.objects.filter(
            status__name__icontains='pending',
            due_date__lt=current_date
        ).count()
        
        # Monthly revenue
        current_month = current_date.month
        current_year = current_date.year
        monthly_revenue = Payment.objects.filter(
            status__name__icontains='paid',
            payment_for_month=current_month,
            payment_for_year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'total_payments': total_payments,
            'paid_payments': paid_payments,
            'pending_payments': pending_payments,
            'overdue_payments': overdue_payments,
            'monthly_revenue': monthly_revenue,
            'payment_rate': (paid_payments / total_payments * 100) if total_payments > 0 else 0
        })
    
    @action(detail=False, methods=['get'])
    def estate_payment_status(self, request):
        """Get payment status per estate"""
        estates = Estate.objects.all()
        estate_data = []
        
        for estate in estates:
            # Get all apartments in this estate
            estate_apartments = Apartment.objects.filter(block__estate=estate)
            total_apartments = estate_apartments.count()
            
            # Get tenants in this estate
            estate_tenants = Tenant.objects.filter(apartment__block__estate=estate)
            
            # Calculate payment statistics
            total_rent_expected = sum(
                tenant.apartment.rent_amount or 0 
                for tenant in estate_tenants 
                if tenant.apartment and tenant.apartment.rent_amount
            )
            
            # Get paid payments for current month
            current_month = timezone.now().month
            current_year = timezone.now().year
            paid_amount = Payment.objects.filter(
                tenant__apartment__block__estate=estate,
                status__name__icontains='paid',
                payment_for_month=current_month,
                payment_for_year=current_year
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Get overdue tenants
            overdue_tenants = []
            for tenant in estate_tenants:
                overdue_payments = Payment.objects.filter(
                    tenant=tenant,
                    status__name__icontains='pending',
                    due_date__lt=timezone.now().date()
                ).count()
                if overdue_payments > 0:
                    overdue_tenants.append({
                        'tenant_id': tenant.id,
                        'tenant_name': f"{tenant.user.first_name} {tenant.user.last_name}",
                        'apartment': tenant.apartment.number if tenant.apartment else None,
                        'overdue_months': overdue_payments
                    })
            
            estate_data.append({
                'estate_id': estate.id,
                'estate_name': estate.name,
                'total_apartments': total_apartments,
                'occupied_apartments': estate_tenants.count(),
                'total_rent_expected': total_rent_expected,
                'rent_collected': paid_amount,
                'collection_rate': (paid_amount / total_rent_expected * 100) if total_rent_expected > 0 else 0,
                'overdue_tenants': overdue_tenants,
                'overdue_count': len(overdue_tenants)
            })
        
        return Response(estate_data)
    
    @action(detail=False, methods=['get'])
    def payment_alerts(self, request):
        """Get payment alerts for property owner"""
        current_date = timezone.now().date()
        
        # Overdue payments (more than 30 days)
        overdue_30_days = Payment.objects.filter(
            status__name__icontains='pending',
            due_date__lt=current_date - timedelta(days=30)
        ).select_related('tenant', 'tenant__user', 'tenant__apartment')
        
        # Upcoming due payments (next 7 days)
        upcoming_due = Payment.objects.filter(
            status__name__icontains='pending',
            due_date__gte=current_date,
            due_date__lte=current_date + timedelta(days=7)
        ).select_related('tenant', 'tenant__user', 'tenant__apartment')
        
        # Recently paid payments (last 7 days)
        recently_paid = Payment.objects.filter(
            status__name__icontains='paid',
            paid_at__gte=timezone.now() - timedelta(days=7)
        ).select_related('tenant', 'tenant__user', 'tenant__apartment')
        
        alerts = {
            'overdue_alerts': [
                {
                    'payment_id': payment.id,
                    'tenant_name': f"{payment.tenant.user.first_name} {payment.tenant.user.last_name}",
                    'apartment': payment.tenant.apartment.number if payment.tenant.apartment else None,
                    'amount': str(payment.amount),
                    'due_date': payment.due_date,
                    'days_overdue': (current_date - payment.due_date).days,
                    'estate': payment.tenant.apartment.block.estate.name if payment.tenant.apartment else None
                } for payment in overdue_30_days
            ],
            'upcoming_alerts': [
                {
                    'payment_id': payment.id,
                    'tenant_name': f"{payment.tenant.user.first_name} {payment.tenant.user.last_name}",
                    'apartment': payment.tenant.apartment.number if payment.tenant.apartment else None,
                    'amount': str(payment.amount),
                    'due_date': payment.due_date,
                    'days_until_due': (payment.due_date - current_date).days,
                    'estate': payment.tenant.apartment.block.estate.name if payment.tenant.apartment else None
                } for payment in upcoming_due
            ],
            'recent_payments': [
                {
                    'payment_id': payment.id,
                    'tenant_name': f"{payment.tenant.user.first_name} {payment.tenant.user.last_name}",
                    'apartment': payment.tenant.apartment.number if payment.tenant.apartment else None,
                    'amount': str(payment.amount),
                    'paid_at': payment.paid_at,
                    'estate': payment.tenant.apartment.block.estate.name if payment.tenant.apartment else None
                } for payment in recently_paid
            ]
        }
        
        return Response(alerts)
    
    @action(detail=True, methods=['patch'])
    def update_payment_status(self, request, pk=None):
        """Update payment status for a specific payment"""
        try:
            print(f"=== PAYMENT STATUS UPDATE DEBUG START ===")
            print(f"HTTP Method: {request.method}")
            print(f"Content-Type: {request.content_type}")
            print(f"Raw request data: {request.data}")
            print(f"Request user: {request.user}")
            print(f"Payment PK from URL: {pk}")
            
            # Get the payment object
            try:
                payment = self.get_object()
                print(f"Payment found - ID: {payment.id}")
                print(f"Current payment status: {payment.status.name if payment.status else 'No status'}")
                print(f"Current payment method: {payment.payment_method}")
                print(f"Current reference number: {payment.reference_number}")
                print(f"Payment tenant: {payment.tenant.user.username}")
                print(f"Payment amount: {payment.amount}")
            except Exception as e:
                print(f"Error getting payment object: {str(e)}")
                return Response({
                    'error': 'Payment not found',
                    'details': str(e)
                }, status=status.HTTP_404_NOT_FOUND)
            
            data = request.data.copy()
            print(f"Copied request data: {data}")
            
            status_id = data.get('status_id')
            months_paid = data.get('months_paid', [])
            payment_method = data.get('payment_method')
            reference_number = data.get('reference_number')
            notes = data.get('notes')
            
            print(f"Extracted status_id: {status_id} (type: {type(status_id)})")
            print(f"Extracted months_paid: {months_paid}")
            print(f"Extracted payment_method: {payment_method}")
            print(f"Extracted reference_number: {reference_number}")
            print(f"Extracted notes: {notes}")
            
            if not status_id:
                print(f"ERROR: status_id is missing or falsy")
                return Response({
                    'error': 'status_id is required',
                    'received_data': data,
                    'status_id_value': status_id
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate status exists
            print(f"Looking for PaymentStatus with ID: {status_id}")
            try:
                payment_status = PaymentStatus.objects.get(id=status_id)
                print(f"PaymentStatus found: ID={payment_status.id}, Name='{payment_status.name}'")
            except PaymentStatus.DoesNotExist:
                print(f"ERROR: PaymentStatus with ID {status_id} does not exist")
                # List all available statuses for debugging
                all_statuses = PaymentStatus.objects.all()
                print(f"Available PaymentStatus objects:")
                for s in all_statuses:
                    print(f"  ID: {s.id}, Name: '{s.name}'")
                return Response({
                    'error': 'Payment status not found',
                    'status_id': status_id,
                    'available_statuses': [{'id': s.id, 'name': s.name} for s in all_statuses]
                }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                print(f"ERROR: Exception while getting PaymentStatus: {str(e)}")
                return Response({
                    'error': 'Error retrieving payment status',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Store old values for comparison
            old_status = payment.status.name if payment.status else 'None'
            old_status_id = payment.status.id if payment.status else None
            old_payment_method = payment.payment_method
            old_reference_number = payment.reference_number
            old_notes = payment.notes
            
            print(f"Old status: '{old_status}' (ID: {old_status_id})")
            print(f"New status: '{payment_status.name}' (ID: {payment_status.id})")
            print(f"Old payment method: '{old_payment_method}'")
            print(f"New payment method: '{payment_method}'")
            print(f"Old reference number: '{old_reference_number}'")
            print(f"New reference number: '{reference_number}'")
            
            try:
                # Update payment status
                print(f"Updating payment status from '{old_status}' to '{payment_status.name}'")
                payment.status = payment_status
                
                # Update payment method if provided
                if payment_method:
                    print(f"Updating payment method from '{old_payment_method}' to '{payment_method}'")
                    payment.payment_method = payment_method
                
                # Update reference number if provided
                if reference_number:
                    print(f"Updating reference number from '{old_reference_number}' to '{reference_number}'")
                    payment.reference_number = reference_number
                
                # Update notes if provided
                if notes:
                    print(f"Updating notes from '{old_notes}' to '{notes}'")
                    payment.notes = notes
                
                # Set paid_at timestamp if status is 'Paid'
                if payment_status.name.lower() in ['paid', 'completed']:
                    if not payment.paid_at:
                        payment.paid_at = timezone.now()
                        print(f"Set paid_at timestamp: {payment.paid_at}")
                    else:
                        print(f"paid_at already set: {payment.paid_at}")
                else:
                    print(f"Status '{payment_status.name}' does not require paid_at timestamp")
                
                # Save the payment
                print(f"Saving payment object...")
                payment.save()
                print(f"Payment saved successfully")
                
                # Verify the save worked
                payment.refresh_from_db()
                print(f"After save - Payment status: {payment.status.name if payment.status else 'None'}")
                print(f"After save - Payment method: {payment.payment_method}")
                print(f"After save - Reference number: {payment.reference_number}")
                print(f"After save - Notes: {payment.notes}")
                print(f"After save - Payment paid_at: {payment.paid_at}")
                
            except Exception as e:
                print(f"ERROR: Exception during payment save: {str(e)}")
                import traceback
                print(f"Save traceback: {traceback.format_exc()}")
                return Response({
                    'error': 'Failed to save payment',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            print(f"Payment status update completed successfully")
            
            # TODO: Trigger notifications to tenant and property owner
            # TODO: Send SMS notifications
            
            response_data = {
                'message': 'Payment updated successfully',
                'payment': {
                    'id': payment.id,
                    'status': payment_status.name,
                    'payment_method': payment.payment_method,
                    'reference_number': payment.reference_number,
                    'notes': payment.notes,
                    'paid_at': payment.paid_at,
                    'amount': str(payment.amount),
                    'tenant_name': f"{payment.tenant.user.first_name} {payment.tenant.user.last_name}",
                    'apartment': payment.tenant.apartment.number if payment.tenant.apartment else None
                },
                'months_paid': months_paid,
                'old_status': old_status,
                'new_status': payment_status.name,
                'updated_fields': {
                    'status': old_status != payment_status.name,
                    'payment_method': payment_method and old_payment_method != payment_method,
                    'reference_number': reference_number and old_reference_number != reference_number,
                    'notes': notes and old_notes != notes
                }
            }
            
            print(f"Returning response: {response_data}")
            print(f"=== PAYMENT STATUS UPDATE DEBUG END ===")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"CRITICAL ERROR in update_payment_status: {str(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return Response({
                'error': 'An error occurred while updating payment status',
                'details': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def pending_payments(self, request):
        """Get all pending payments"""
        pending_status = PaymentStatus.objects.filter(name__icontains='pending').first()
        if pending_status:
            pending_payments = Payment.objects.filter(status=pending_status)
            serializer = self.get_serializer(pending_payments, many=True)
            return Response(serializer.data)
        return Response({'error': 'Pending status not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def overdue_payments(self, request):
        """Get all overdue payments"""
        overdue_payments = Payment.objects.filter(
            due_date__lt=timezone.now().date(),
            status__name__icontains='pending'
        )
        serializer = self.get_serializer(overdue_payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def report(self, request):
        """Generate detailed payment report"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({
                'error': 'start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter payments by date range
        payments = Payment.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        total_payments = payments.count()
        total_amount = payments.aggregate(sum=Sum('amount'))['sum'] or 0
        paid_amount = payments.filter(status__name__icontains='paid').aggregate(sum=Sum('amount'))['sum'] or 0
        pending_amount = payments.filter(status__name__icontains='pending').aggregate(sum=Sum('amount'))['sum'] or 0
        overdue_amount = payments.filter(
            status__name__icontains='pending',
            due_date__lt=timezone.now().date()
        ).aggregate(sum=Sum('amount'))['sum'] or 0
        
        # Estate breakdown
        estates = Estate.objects.all()
        estate_breakdown = []
        
        for estate in estates:
            estate_payments = payments.filter(tenant__apartment__block__estate=estate)
            estate_count = estate_payments.count()
            estate_total = estate_payments.aggregate(sum=Sum('amount'))['sum'] or 0
            estate_paid = estate_payments.filter(status__name__icontains='paid').aggregate(sum=Sum('amount'))['sum'] or 0
            
            if estate_count > 0:
                estate_breakdown.append({
                    'estate_name': estate.name,
                    'payments': estate_count,
                    'total_amount': str(estate_total),
                    'paid_amount': str(estate_paid),
                    'collection_rate': (estate_paid / estate_total * 100) if estate_total > 0 else 0
                })
        
        return Response({
            'period': f'{start_date} to {end_date}',
            'total_payments': total_payments,
            'total_amount': str(total_amount),
            'paid_amount': str(paid_amount),
            'pending_amount': str(pending_amount),
            'overdue_amount': str(overdue_amount),
            'estates': estate_breakdown
        })

class PaymentStatusViewSet(viewsets.ModelViewSet):
    queryset = PaymentStatus.objects.all()
    serializer_class = PaymentStatusSerializer
    permission_classes = [IsAuthenticated]

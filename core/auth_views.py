from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken
import json

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user account and create user profile
    """
    try:
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        phone_number = data.get('phone_number', '')
        address = data.get('address', '')
        role = data.get('role', 'tenant')  # Default to tenant role
        
        # Validate required fields
        if not username or not email or not password:
            return Response({
                'error': 'Username, email, and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate role
        valid_roles = ['owner', 'manager', 'tenant']
        if role not in valid_roles:
            return Response({
                'error': f'Role must be one of: {", ".join(valid_roles)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create user profile
        user_profile = UserProfile.objects.create(
            user=user,
            phone_number=phone_number,
            address=address,
            role=role
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'message': 'User and profile created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'profile': {
                'phone_number': user_profile.phone_number,
                'address': user_profile.address,
                'role': user_profile.role
            },
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'An error occurred while creating the user',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    profile = UserProfile.objects.filter(user=user).first()
    if not profile:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)


    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': profile.phone_number,
        'address': profile.address,
        'role': profile.role,
        'created_at': profile.created_at
    }, status=status.HTTP_200_OK)
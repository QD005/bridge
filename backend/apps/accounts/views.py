from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    # Only authenticated admins can create users
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.user.role not in ['SUPER_ADMIN', 'AGENCY_ADMIN']:
        return Response({'detail': 'Only Super Admin or Agency Admin can create users.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = RegisterSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'agency': user.agency.name if user.agency else None,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(
        request=request,
        email=serializer.validated_data['email'],
        password=serializer.validated_data['password']
    )

    if not user:
        return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_active:
        return Response({'detail': 'Account is disabled.'}, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'agency': {
                'id': user.agency.id,
                'name': user.agency.name,
                'code': user.agency.code
            } if user.agency else None,
        }
    })

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    serializer = UserSerializer(user, data=request.data, partial=(request.method == 'PATCH'))
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    user = request.user

    if user.role == 'SUPER_ADMIN':
        users = User.objects.all().select_related('agency')
    elif user.role == 'AGENCY_ADMIN' and user.agency:
        users = User.objects.filter(agency=user.agency).select_related('agency')
    else:
        return Response({'detail': 'Not authorized to list users.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    try:
        target_user = User.objects.select_related('agency').get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    # Authorization checks
    if user.role == 'AGENCY_ADMIN':
        if target_user.agency != user.agency:
            return Response({'detail': 'Not authorized to manage this user.'}, status=status.HTTP_403_FORBIDDEN)
    elif user.role != 'SUPER_ADMIN':
        if target_user.id != user.id:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = UserSerializer(target_user)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        # Non-admins cannot change role, agency, or status
        if user.role not in ['SUPER_ADMIN', 'AGENCY_ADMIN']:
            restricted = ['role', 'agency_id', 'is_active', 'is_staff']
            for field in restricted:
                request.data.pop(field, None)

        serializer = UserSerializer(target_user, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if user.role not in ['SUPER_ADMIN', 'AGENCY_ADMIN']:
            return Response({'detail': 'Not authorized to delete users.'}, status=status.HTTP_403_FORBIDDEN)
        target_user.delete()
        return Response({'detail': 'User deleted.'}, status=status.HTTP_204_NO_CONTENT)
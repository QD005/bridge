from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
import requests
import time

from .models import Agency
from .serializers import AgencySerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def agency_list_create(request):
    user = request.user

    if request.method == 'GET':
        # Super Admin sees all agencies
        if user.role == 'SUPER_ADMIN':
            agencies = Agency.objects.all().select_related('created_by')
        else:
            # Others see ACTIVE agencies + their own agency regardless of status
            q_filter = Q(status='ACTIVE')
            if user.agency_id:
                q_filter |= Q(id=user.agency_id)
            agencies = Agency.objects.filter(q_filter).select_related('created_by')

        serializer = AgencySerializer(agencies, many=True)
        return Response(serializer.data)

    # POST — Only Super Admin can create agencies
    if user.role != 'SUPER_ADMIN':
        return Response(
            {'detail': 'Only Super Admin can create agencies.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = AgencySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def agency_detail(request, pk):
    agency = get_object_or_404(Agency.objects.select_related('created_by'), pk=pk)
    user = request.user

    # Who can modify?
    can_modify = (
        user.role == 'SUPER_ADMIN' or
        (user.role == 'AGENCY_ADMIN' and user.agency == agency)
    )

    # Who can view?
    can_view = (
        user.role == 'SUPER_ADMIN' or
        agency.status == 'ACTIVE' or
        user.agency == agency
    )

    if request.method == 'GET':
        if not can_view:
            return Response(
                {'detail': 'Not authorized to view this agency.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = AgencySerializer(agency)
        return Response(serializer.data)

    # All other methods require modify permission
    if not can_modify:
        return Response(
            {'detail': 'Not authorized to modify this agency.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method in ['PUT', 'PATCH']:
        # Agency Admin cannot change status (only Super Admin can)
        if user.role == 'AGENCY_ADMIN' and 'status' in request.data:
            request.data.pop('status')

        serializer = AgencySerializer(agency, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        # Only Super Admin can delete
        if user.role != 'SUPER_ADMIN':
            return Response(
                {'detail': 'Only Super Admin can delete agencies.'},
                status=status.HTTP_403_FORBIDDEN
            )
        agency.delete()
        return Response({'detail': 'Agency deleted.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def agency_disable(request, pk):
    agency = get_object_or_404(Agency, pk=pk)
    user = request.user

    if user.role != 'SUPER_ADMIN':
        return Response(
            {'detail': 'Only Super Admin can disable agencies.'},
            status=status.HTTP_403_FORBIDDEN
        )

    agency.status = 'SUSPENDED'
    agency.save()
    return Response({
        'detail': f'Agency {agency.name} has been suspended.',
        'agency': AgencySerializer(agency).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agency_test_connectivity(request, pk):
    agency = get_object_or_404(Agency, pk=pk)
    user = request.user

    # Only Super Admin or the agency's own members can test
    if user.role != 'SUPER_ADMIN' and user.agency != agency:
        return Response(
            {'detail': 'Not authorized to test this agency.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if not agency.base_url:
        return Response(
            {'detail': 'This agency has no base URL configured.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        start = time.time()
        response = requests.head(
            agency.base_url,
            timeout=10,
            allow_redirects=True,
            headers={'User-Agent': 'GovBridge-HealthCheck/1.0'}
        )
        elapsed_ms = round((time.time() - start) * 1000, 2)

        health_status = 'ONLINE' if response.status_code < 400 else 'DEGRADED'

        return Response({
            'agency': agency.name,
            'code': agency.code,
            'base_url': agency.base_url,
            'status_code': response.status_code,
            'response_time_ms': elapsed_ms,
            'health_status': health_status
        })

    except requests.exceptions.Timeout:
        return Response({
            'agency': agency.name,
            'code': agency.code,
            'base_url': agency.base_url,
            'error': 'Connection timed out after 10 seconds',
            'health_status': 'OFFLINE'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    except requests.exceptions.RequestException as e:
        return Response({
            'agency': agency.name,
            'code': agency.code,
            'base_url': agency.base_url,
            'error': str(e),
            'health_status': 'OFFLINE'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
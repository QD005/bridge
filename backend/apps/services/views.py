import requests
import time
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import ServiceEndpoint, ServiceField
from .serializers import (
    ServiceEndpointSerializer, ServiceEndpointListSerializer,
    ServiceFieldSerializer, ServiceSchemaSerializer,
    ServicePreviewSerializer, ServiceExecuteSerializer
)
from .permissions import CanManageService


def get_service_queryset(user):
    """Return services the user is allowed to see"""
    if user.role == 'SUPER_ADMIN':
        return ServiceEndpoint.objects.all().select_related('agency')
    elif user.role in ['AGENCY_ADMIN', 'DEVELOPER', 'OPERATIONS_OFFICER']:
        q = Q(status='ACTIVE')
        if user.agency_id:
            q |= Q(agency=user.agency)
        return ServiceEndpoint.objects.filter(q).select_related('agency')
    else:
        return ServiceEndpoint.objects.filter(status='ACTIVE').select_related('agency')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def service_list_create(request):
    user = request.user

    if request.method == 'GET':
        queryset = get_service_queryset(user)
        agency_id = request.query_params.get('agency')
        status_filter = request.query_params.get('status')
        method = request.query_params.get('method')
        search = request.query_params.get('search')

        if agency_id:
            queryset = queryset.filter(agency_id=agency_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if method:
            queryset = queryset.filter(http_method=method.upper())
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        serializer = ServiceEndpointListSerializer(queryset, many=True)
        return Response(serializer.data)

    # POST — create service
    if user.role not in ['SUPER_ADMIN', 'AGENCY_ADMIN', 'DEVELOPER']:
        return Response(
            {'detail': 'You do not have permission to create services.'},
            status=status.HTTP_403_FORBIDDEN
        )

    data = request.data.copy()
    if user.role != 'SUPER_ADMIN':
        data['agency_id'] = user.agency_id

    serializer = ServiceEndpointSerializer(data=data)
    if serializer.is_valid():
        serializer.save(created_by=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, CanManageService])
def service_detail(request, pk):
    service = get_object_or_404(ServiceEndpoint.objects.select_related('agency').prefetch_related('service_fields'), pk=pk)
    user = request.user

    if request.method == 'GET':
        if user.role == 'SUPER_ADMIN' or (service.status == 'ACTIVE') or (user.agency == service.agency):
            serializer = ServiceEndpointSerializer(service)
            return Response(serializer.data)
        return Response({'detail': 'Not authorized to view this service.'}, status=status.HTTP_403_FORBIDDEN)

    can_modify = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == service.agency)
    )
    if not can_modify:
        return Response(
            {'detail': 'Not authorized to modify this service.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method in ['PUT', 'PATCH']:
        data = request.data.copy()
        if user.role != 'SUPER_ADMIN':
            data.pop('agency_id', None)

        serializer = ServiceEndpointSerializer(service, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        service.delete()
        return Response({'detail': 'Service deleted.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def service_schema(request, pk):
    """
    GET /api/services/{id}/schema/
    Returns the auto-generated API contract for frontend dynamic forms.
    """
    service = get_object_or_404(ServiceEndpoint.objects.prefetch_related('service_fields'), pk=pk)
    user = request.user

    # Permission check
    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if service.status != 'ACTIVE' and user.agency != service.agency:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    fields = service.get_fields()

    # Transform to frontend-friendly format
    frontend_fields = []
    for f in fields:
        frontend_fields.append({
            'name': f.get('name'),
            'label': f.get('label') or f.get('name').replace('_', ' ').title(),
            'type': f.get('field_type', 'text'),
            'required': f.get('required', False),
            'location': f.get('location', 'query'),
            'placeholder': f.get('placeholder', ''),
            'help_text': f.get('help_text', ''),
            'default_value': f.get('default_value', ''),
            'validation_regex': f.get('validation_regex', ''),
            'min_length': f.get('min_length'),
            'max_length': f.get('max_length'),
            'options': f.get('options', []),
            'order': f.get('order', 0),
            'is_sensitive': f.get('is_sensitive', False),
        })

    return Response({
        'service_id': service.id,
        'service_name': service.name,
        'description': service.description,
        'http_method': service.http_method,
        'endpoint_url': service.get_full_url(),
        'agency': {
            'id': service.agency.id,
            'name': service.agency.name,
            'code': service.agency.code,
        } if service.agency else None,
        'fields': frontend_fields,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def service_preview(request, pk):
    """
    POST /api/services/{id}/preview/
    Body: {"raw_values": {"nin": "CM1234567890AB", "tin": "1000123456"}}
    Returns a human-readable preview of how the request will be built.
    """
    service = get_object_or_404(ServiceEndpoint, pk=pk)
    user = request.user

    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if service.status != 'ACTIVE' and user.agency != service.agency:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = ServicePreviewSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    raw_values = serializer.validated_data['raw_values']

    # Validate required fields
    fields = service.get_fields()
    errors = {}
    for f in fields:
        if f.get('required') and not raw_values.get(f['name']):
            errors[f['name']] = f"This field is required."

    if errors:
        return Response({'detail': 'Validation failed.', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    preview = service.preview_request(raw_values)

    return Response({
        'service': service.name,
        'preview': preview,
        'raw_values': raw_values,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def service_execute(request, pk):
    """
    POST /api/services/{id}/execute/
    Body: {"raw_values": {"nin": "CM1234567890AB"}}
    Backend builds the actual HTTP request from field locations and executes it.
    """
    service = get_object_or_404(ServiceEndpoint, pk=pk)
    user = request.user

    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if service.status != 'ACTIVE' and user.agency != service.agency:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = ServiceExecuteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    raw_values = serializer.validated_data['raw_values']

    # Validate fields
    fields = service.get_fields()
    errors = {}
    import re

    for f in fields:
        fname = f['name']
        value = raw_values.get(fname)

        if f.get('required') and not value:
            errors[fname] = f"Field '{f.get('label', fname)}' is required."
            continue

        if not value:
            continue

        if f.get('validation_regex') and not re.match(f['validation_regex'], str(value)):
            errors[fname] = f"Field '{f.get('label', fname)}' format is invalid."

        if f.get('min_length') and len(str(value)) < f['min_length']:
            errors[fname] = f"Must be at least {f['min_length']} characters."

        if f.get('max_length') and len(str(value)) > f['max_length']:
            errors[fname] = f"Must be at most {f['max_length']} characters."

    if errors:
        return Response({'detail': 'Validation failed.', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    # Build and execute request
    req = service.build_request(raw_values)
    timeout = min(service.timeout_seconds or 30, 60)

    try:
        start = time.time()

        kwargs = {
            'url': req['url'],
            'headers': req['headers'],
            'timeout': timeout,
            'allow_redirects': True,
        }

        if req['query_params']:
            kwargs['params'] = req['query_params']

        if req['body'] and service.http_method in ['POST', 'PUT', 'PATCH']:
            kwargs['json'] = req['body']

        # Apply auth
        agency_auth = service.agency.auth_config or {}
        service_auth = service.authentication_override or {}
        auth_config = {**agency_auth, **service_auth}

        if auth_config.get('username') and auth_config.get('password'):
            kwargs['auth'] = (auth_config['username'], auth_config['password'])

        response = requests.request(service.http_method, **kwargs)
        elapsed_ms = round((time.time() - start) * 1000, 2)

        # Update health status
        if response.status_code < 400:
            service.health_status = 'ONLINE'
        elif response.status_code < 500:
            service.health_status = 'DEGRADED'
        else:
            service.health_status = 'OFFLINE'
        service.save(update_fields=['health_status'])

        try:
            body = response.json()
        except ValueError:
            body = {'raw_text': response.text[:2000]}

        return Response({
            'service': service.name,
            'request_built': {
                'method': req['method'],
                'url': req['url'],
                'headers': {k: '***' if any(x in k.lower() for x in ['key', 'token', 'auth', 'secret']) else v
                           for k, v in req['headers'].items()},
                'query_params': req['query_params'],
                'body': req['body'],
            },
            'response': {
                'status_code': response.status_code,
                'response_time_ms': elapsed_ms,
                'headers': dict(response.headers),
                'body': body,
            },
            'health_status': service.health_status,
        })

    except requests.exceptions.Timeout:
        service.health_status = 'OFFLINE'
        service.save(update_fields=['health_status'])
        return Response({
            'service': service.name,
            'error': f'Request timed out after {timeout} seconds',
            'health_status': 'OFFLINE'
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)

    except requests.exceptions.RequestException as e:
        service.health_status = 'OFFLINE'
        service.save(update_fields=['health_status'])
        return Response({
            'service': service.name,
            'error': str(e),
            'health_status': 'OFFLINE'
        }, status=status.HTTP_502_BAD_GATEWAY)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def service_test(request, pk):
    """
    Legacy test endpoint — now delegates to service_execute for consistency.
    """
    return service_execute(request, pk)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def service_field_create(request, pk):
    """
    POST /api/services/{id}/fields/
    Add a field to a service.
    """
    service = get_object_or_404(ServiceEndpoint, pk=pk)
    user = request.user

    can_modify = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == service.agency)
    )
    if not can_modify:
        return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    data['service'] = service.id

    serializer = ServiceFieldSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def service_field_detail(request, pk, field_pk):
    """
    Update or delete a service field.
    """
    service = get_object_or_404(ServiceEndpoint, pk=pk)
    field = get_object_or_404(ServiceField, pk=field_pk, service=service)
    user = request.user

    can_modify = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == service.agency)
    )
    if not can_modify:
        return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        serializer = ServiceFieldSerializer(field, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        field.delete()
        return Response({'detail': 'Field deleted.'}, status=status.HTTP_204_NO_CONTENT)
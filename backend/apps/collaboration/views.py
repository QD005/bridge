import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from apps.accounts.models import User
from apps.agencies.models import Agency
from .models import Conversation, Message
from .serializers import ConversationSerializer, ConversationDetailSerializer, MessageSerializer


def get_connected_agency_ids(user):
    """Return agency IDs connected to the user's agency via workflows/executions/services."""
    if not user.agency:
        return []
    
    agency_id = user.agency.id
    
    # Agencies that share workflows
    from apps.workflows.models import Workflow
    workflow_agencies = Workflow.objects.filter(
        Q(agency_id=agency_id) | Q(steps__service__agency_id=agency_id)
    ).values_list('agency_id', flat=True).distinct()
    
    # Agencies from executions
    from apps.executions.models import WorkflowExecution
    execution_agencies = WorkflowExecution.objects.filter(
        Q(workflow__agency_id=agency_id) | Q(initiated_by__agency_id=agency_id)
    ).values_list('workflow__agency_id', flat=True).distinct()
    
    connected = set(list(workflow_agencies) + list(execution_agencies))
    connected.discard(agency_id)
    return list(connected)


def get_conversation_queryset(user):
    if user.role in ['SUPER_ADMIN', 'AUDITOR']:
        return Conversation.objects.all()
    
    # User can see conversations they participate in, created, or related to their agency
    q = Q(participants=user) | Q(created_by=user)
    
    if user.agency:
        q |= Q(agency=user.agency)
        q |= Q(workflow__agency=user.agency)
        q |= Q(execution__workflow__agency=user.agency)
        # Also include conversations from connected agencies
        connected = get_connected_agency_ids(user)
        if connected:
            q |= Q(agency_id__in=connected)
            q |= Q(workflow__agency_id__in=connected)
    
    return Conversation.objects.filter(q).distinct()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversation_list_create(request):
    user = request.user

    if request.method == 'GET':
        queryset = get_conversation_queryset(user)
        conversation_type = request.query_params.get('type')
        workflow_id = request.query_params.get('workflow')
        execution_id = request.query_params.get('execution')

        if conversation_type:
            queryset = queryset.filter(conversation_type=conversation_type.upper())
        if workflow_id:
            queryset = queryset.filter(workflow_id=workflow_id)
        if execution_id:
            queryset = queryset.filter(execution_id=execution_id)

        serializer = ConversationSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # POST
    data = request.data.copy()
    data['created_by'] = user.id
    
    # Auto-add creator as participant
    participant_ids = data.get('participant_ids', [])
    if isinstance(participant_ids, str):
        import json
        participant_ids = json.loads(participant_ids)
    if user.id not in participant_ids:
        participant_ids.append(user.id)
    data['participant_ids'] = participant_ids
    
    serializer = ConversationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    user = request.user

    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if not conversation.participants.filter(id=user.id).exists():
            if conversation.created_by != user:
                if conversation.agency and conversation.agency != user.agency:
                    if conversation.workflow and conversation.workflow.agency != user.agency:
                        if conversation.execution and conversation.execution.workflow.agency != user.agency:
                            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = ConversationDetailSerializer(conversation, context={'request': request})
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = ConversationSerializer(conversation, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        conversation.delete()
        return Response({'detail': 'Conversation deleted.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def message_list_create(request, conversation_pk):
    conversation = get_object_or_404(Conversation, pk=conversation_pk)
    user = request.user

    # Permission check
    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if not conversation.participants.filter(id=user.id).exists():
            if conversation.created_by != user:
                return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        messages = conversation.messages.select_related('sender', 'assigned_to').all()
        
        # Mark messages as read for current user
        for msg in messages:
            if user.id not in msg.read_by:
                msg.read_by.append(user.id)
                msg.save(update_fields=['read_by'])
        
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    # POST
    data = request.data.copy()
    data['conversation'] = conversation.id
    serializer = MessageSerializer(data=data)
    if serializer.is_valid():
        serializer.save(sender=user)
        conversation.save(update_fields=['updated_at'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_attachment(request, conversation_pk):
    """Upload a file and return its metadata for attachment to a message."""
    conversation = get_object_or_404(Conversation, pk=conversation_pk)
    user = request.user

    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if not conversation.participants.filter(id=user.id).exists():
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    if 'file' not in request.FILES:
        return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = request.FILES['file']
    
    # Validate file size (max 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        return Response({'detail': 'File size exceeds 10MB limit.'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate unique filename
    ext = os.path.splitext(uploaded_file.name)[1]
    filename = f"chat/{conversation_pk}/{uuid.uuid4()}{ext}"
    
    # Save file
    path = default_storage.save(filename, uploaded_file)
    file_url = default_storage.url(path)

    return Response({
        'name': uploaded_file.name,
        'url': file_url,
        'size': uploaded_file.size,
        'type': uploaded_file.content_type
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eligible_users(request):
    """Return users from connected agencies that the current user can message."""
    user = request.user
    
    if user.role in ['SUPER_ADMIN', 'AUDITOR']:
        users = User.objects.filter(is_active=True).exclude(id=user.id)
    else:
        # Same agency + connected agencies
        agency_ids = [user.agency.id] if user.agency else []
        connected = get_connected_agency_ids(user)
        agency_ids.extend(connected)
        
        users = User.objects.filter(
            agency_id__in=agency_ids,
            is_active=True
        ).exclude(id=user.id)
    
    from apps.accounts.serializers import UserSerializer
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_task_status(request, conversation_pk, message_pk):
    """Update task status on a TASK message."""
    conversation = get_object_or_404(Conversation, pk=conversation_pk)
    message = get_object_or_404(Message, pk=message_pk, conversation=conversation, message_type='TASK')
    user = request.user

    new_status = request.data.get('task_status')
    if new_status not in ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']:
        return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

    # Only assigned user, sender, or admin can update
    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if message.assigned_to != user and message.sender != user:
            return Response({'detail': 'Not authorized to update this task.'}, status=status.HTTP_403_FORBIDDEN)

    message.task_status = new_status
    message.save(update_fields=['task_status'])
    
    serializer = MessageSerializer(message, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def message_pin(request, conversation_pk, message_pk):
    """Toggle pin status on a message (like WhatsApp)."""
    conversation = get_object_or_404(Conversation, pk=conversation_pk)
    message = get_object_or_404(Message, pk=message_pk, conversation=conversation)
    user = request.user

    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if not conversation.participants.filter(id=user.id).exists():
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    # Toggle pin
    message.is_pinned = not message.is_pinned
    message.save(update_fields=['is_pinned'])

    serializer = MessageSerializer(message, context={'request': request})
    return Response(serializer.data)
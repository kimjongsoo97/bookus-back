from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .serializers import MessageSerializer,SendMessageSerializer
from .models import Message
# Create your views here.

## 받은메시지
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def index(request):
    user = request.user
    messages = Message.objects.filter(owner_id=user.id, is_sender=False, delete_status='UNDELETE').order_by('-created_at')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

##보낸 메시지
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def send(request):
    user = request.user
    messages = Message.objects.filter(owner_id=user.id, is_sender=True, delete_status='UNDELETE').order_by('-created_at')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

## 쪽지 보내기
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    serializer = SendMessageSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        message = serializer.save()
        response_serializer=MessageSerializer(message)
        print(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



## 쪽지 상세 보기

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detail_message(request,message_id):
    user = request.user
    message= get_object_or_404(
        Message,
        id=message_id,
        owner=user,
        delete_status='UNDELETE'
    )

    if  message.read_status=='UNREAD':
        message.read_status='READ'
        message.save()
    serializer=MessageSerializer(message)
    return Response(serializer.data,status=status.HTTP_200_OK)

## 쪽지 삭제
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_message(request,message_id):
    user=request.user
    message=get_object_or_404(
        Message,
        id=message_id,
        owner=user,
        delete_status='UNDELETE'
    )
    
    message.delete_status='DELETE'
    message.save()
    
    serializer=MessageSerializer(message)
    return Response(serializer.data,status=status.HTTP_200_OK)
    

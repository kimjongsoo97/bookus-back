from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import CommunitySerializer,CommunityCreateSerializer
from .models import Community
# Create your views here.
@api_view(['GET'])
def index(request):
    community=Community.objects.filter(delete_status='UNDELETE').order_by('-created_at')
    serializer=CommunitySerializer(community,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    serializer=CommunityCreateSerializer(data=request.data,context={'request':request})

    if serializer.is_valid():
        community=serializer.save()
        response_serializer=CommunityCreateSerializer(community)
        return Response(response_serializer.data,status=status.HTTP_200_OK)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def detail_community(request,community_id):
    community=Community.objects.get(id=community_id)
    if community.delete_status=='DELETE':
        return Response({"error":"게시글이 존재하지 않습니다"},status=status.HTTP_404_NOT_FOUND)
    serializer=CommunitySerializer(community)
    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_community(request,community_id):
    user= request.user
    try:
        community = Community.objects.get(id=community_id)
    except Community.DoesNotExist:
        return Response({"error": "해당 게시글이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

    if community.user_id != user.id:
        return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    community.delete_status = 'DELETE'
    community.save()

    return Response({"message": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_community(request, community_id):
    user = request.user
    try:
        community = Community.objects.get(id=community_id)
    except Community.DoesNotExist:
        return Response({"error": "해당 게시글이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

    # 삭제된 상태라면
    if community.delete_status == "DELETE":
        return Response({"error": "삭제된 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)

    # 작성자 체크
    if community.user_id != user.id:
        return Response({"error": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CommunitySerializer(instance=community, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

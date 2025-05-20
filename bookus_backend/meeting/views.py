# meetings/views.py
import requests
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Meeting, Membership
from .serializers import MeetingSerializer, MembershipSerializer
from books.models import Book

@api_view(['GET'])
def index(request):
    # 기본 쿼리셋: 삭제되지 않은 모임, created_at 내림차순 정렬
    queryset = Meeting.objects.filter(delete_status='UNDELETE').order_by('-created_at')
    
    # 쿼리 파라미터에서 정렬 기준 가져오기
    ordering = request.query_params.get('ordering', None)
    
    if ordering == 'created_at':
        # 최신순: created_at 내림차순
        queryset = queryset.order_by('-created_at')
    if ordering == 'meeting_date':
        # 마감순: meeting_date 오름차순, 과거 모임 제거
        queryset = queryset.filter(meeting_date__gte=timezone.now()).order_by('meeting_date')
    
    # 시리얼라이저로 데이터 변환
    serializer = MeetingSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    # 요청 데이터 복사
    data = request.data.copy()
    data['delete_status'] = 'UNDELETE'  # 기본값 설정

    # 시리얼라이저로 데이터 검증 및 저장
    serializer = MeetingSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(creator=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # 유효성 검사 실패 시 에러 반환
    print("Validation errors:", serializer.errors)  # 디버깅 로그
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def detail_meeting(request, meeting_id):
    meeting=Meeting.objects.get(id=meeting_id)
    serializer=MeetingSerializer(meeting)
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def join(request, meeting_id):
    # 회의 조회
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    
    # 이미 참여했는지 확인
    if Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response({"detail": "이미 이 회의에 참여 중입니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 최대 인원 초과 여부 확인
    if meeting.membership_set.count() >= meeting.max_members:
        return Response({"detail": "회의 정원이 가득 찼습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    if meeting.meeting_date < timezone.now():
        return Response({"detail": "지난 모임에는 참여할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    # 새로운 Membership 생성
    membership = Membership.objects.create(
        user=request.user,
        meeting=meeting,
        member_status='MEETING_USER'  # 기본적으로 일반 사용자
    )
    
    # 시리얼라이저로 응답
    serializer = MembershipSerializer(membership, context={'request': request})
    return Response({'success':serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def withdraw(request,meeting_id):
    # 회의 조회
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    
    # 과거 모임인지 확인
    if meeting.meeting_date < timezone.now():
        return Response({"detail": "지난 모임에서는 탈퇴할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 사용자의 Membership 조회
    membership = get_object_or_404(Membership, user=request.user, meeting=meeting)
    
    # 모임장인 경우
    if membership.member_status == 'MEETING_ADMIN':
        # 모임과 관련된 모든 Membership 삭제 후 모임 하드 삭제
        Membership.objects.filter(meeting=meeting).delete()
        meeting.delete()
        return Response({"detail": "모임장이 탈퇴하여 모임이 삭제되었습니다."}, status=status.HTTP_200_OK)
    print(meeting_id)
    print(membership)
    # 일반 사용자인 경우 Membership만 삭제
    membership.delete()
    return Response({"detail": "모임에서 성공적으로 탈퇴되었습니다."}, status=status.HTTP_200_OK)


# 네이버 검색어 API 프록시
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def search_place(request):
    query = request.GET.get('query')
    if not query:
        return Response({'error': 'query 파라미터가 필요합니다.'}, status=400)

    headers = {
        'X-Naver-Client-Id': '',  ## 네이버 클라이언트 id 키
        'X-Naver-Client-Secret': '',  ## 네이버 클라이언트 시크릿 키
    }
    params = {'query': query, 'display': 1}

    try:
        res = requests.get('https://openapi.naver.com/v1/search/local.json', headers=headers, params=params)
        return Response(res.json(), status=res.status_code)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=500)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import Content, DiscussionReply, QuizReply, BookReview, BookReviewCompilation
from .serializers import ContentSerializer, DiscussionReplySerializer, QuizReplySerializer, BookReviewSerializer, BookReviewCompilationSerializer
from meeting.models import Meeting, Membership

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def content_list(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    if not Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response({"detail": "모임 회원만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
    contents = Content.objects.filter(meeting=meeting)
    serializer = ContentSerializer(contents, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def content_detail(request, meeting_id, content_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    if not Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response({"detail": "모임 회원만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
    content = get_object_or_404(Content, id=content_id, meeting=meeting)
    serializer = ContentSerializer(content, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def content_create(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    if not Membership.objects.filter(user=request.user, meeting=meeting, member_status='MEETING_ADMIN').exists():
        return Response({"detail": "모임장만 컨텐츠를 생성할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
    if meeting.meeting_date < timezone.now():
        return Response({"detail": "지난 모임에서는 컨텐츠를 생성할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data.copy()
                # print([data['meeting']])
    data['meeting'] = meeting_id
    data['creator'] = request.user.id
    serializer = ContentSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def content_delete(request, meeting_id, content_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    if not Membership.objects.filter(user=request.user, meeting=meeting, member_status='MEETING_ADMIN').exists():
        return Response({"detail": "모임장만 컨텐츠를 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
    content = get_object_or_404(Content, id=content_id, meeting=meeting)
    content.delete()
    return Response({"detail": "컨텐츠가 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def discussion_reply_create(request, meeting_id, content_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    content = get_object_or_404(Content, id=content_id, meeting=meeting, content_type='DISCUSSION')
    if not Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response({"detail": "모임 회원만 답글을 작성할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
    if meeting.meeting_date < timezone.now():
        return Response({"detail": "지난 모임에서는 답글을 작성할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    data = request.data.copy()
    data['content'] = content_id
    # data['user'] = request.user.id
    serializer = DiscussionReplySerializer(data=data,context={"request":request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quiz_reply_create(request, meeting_id, content_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    content = get_object_or_404(Content, id=content_id, meeting=meeting, content_type='QUIZ')
    if not Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response({"detail": "모임 회원만 답글을 작성할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
    if meeting.meeting_date < timezone.now():
        return Response({"detail": "지난 모임에서는 답글을 작성할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    data = request.data.copy()
    data['content'] = content_id
    # data['user'] = request.user.id
    serializer = QuizReplySerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_review_create(request, meeting_id, content_id):
    print("Request data:", request.data)  # 디버깅: 클라이언트가 보낸 JSON 확인
    print("Content ID from URL:", content_id)  # 디버깅: URL에서 받은 content_id 확인
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    content = get_object_or_404(Content, id=content_id, meeting=meeting, content_type='BOOK_REVIEW')
    print("Content object:", content)  # 디버깅: Content 객체 확인
    if not Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response()
    if meeting.meeting_date < timezone.now():
        return Response({"detail": "지난 모임에서는 독후감을 작성할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    if BookReview.objects.filter(content=content, user=request.user).exists():
        return Response({"detail": "이미 독후감을 작성했습니다."}, status=status.HTTP_400_BAD_REQUEST)
    if content.word_limit and len(request.data.get('body', '')) > content.word_limit:
        return Response({"detail": f"독후감은 {content.word_limit}자를 초과할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    data = request.data.copy()
    data['content'] = content_id  # content_id 설정
    data['user'] = request.user.id
    print("Data to serialize:", data)  # 디버깅: 시리얼라이저에 전달되는 데이터 확인
    serializer = BookReviewSerializer(data=data,context={"request":request})
    if serializer.is_valid():
        print("Validated data:", serializer.validated_data)  # 디버깅: 검증된 데이터 확인
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("Serializer errors:", serializer.errors)  # 디버깅: 시리얼라이저 에러 확인
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def book_review_compilation(request, meeting_id, content_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    content = get_object_or_404(Content, id=content_id, meeting=meeting, content_type='BOOK_REVIEW')
    if not Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response({"detail": "모임 회원만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
    if content.reveal_date and content.reveal_date > timezone.now():
        return Response({"detail": "아직 독후감 합본이 공개되지 않았습니다."}, status=status.HTTP_403_FORBIDDEN)
    compilation = getattr(content, 'compilation', None)
    if not compilation:
        reviews = content.book_reviews.all()
        if not reviews:
            return Response({"detail": "작성된 독후감이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        order = content.order or {}
        sorted_reviews = sorted(reviews, key=lambda r: order.get(str(r.user.id), float('inf')))
        compiled_body = "\n\n".join(f"{r.user.nickname}:\n{r.body}" for r in sorted_reviews)
        compilation = BookReviewCompilation.objects.create(
            content=content,
            compiled_body=compiled_body
        )
    serializer = BookReviewCompilationSerializer(compilation)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def quiz_reply_delete(request, meeting_id, content_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    content = get_object_or_404(Content, id=content_id, meeting=meeting, content_type='QUIZ')

    if not Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response({"detail": "모임 회원만 답글을 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

    if meeting.meeting_date < timezone.now():
        return Response({"detail": "지난 모임의 답글은 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 사용자 자신의 퀴즈 답글만 삭제할 수 있음
    reply = get_object_or_404(QuizReply, content=content, user=request.user)

    reply.delete()
    return Response({"detail": "답글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def book_review_delete(request, meeting_id, content_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    content = get_object_or_404(Content, id=content_id, meeting=meeting, content_type='BOOK')

    if not Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response({"detail": "모임 회원만 리뷰를 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

    if meeting.meeting_date < timezone.now():
        return Response({"detail": "지난 모임의 리뷰는 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    review = get_object_or_404(BookReview, content=content, user=request.user)

    review.delete()
    return Response({"detail": "리뷰가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def discussion_reply_delete(request, meeting_id, content_id):
    meeting = get_object_or_404(Meeting, id=meeting_id, delete_status='UNDELETE')
    content = get_object_or_404(Content, id=content_id, meeting=meeting, content_type='DISCUSSION')

    if not Membership.objects.filter(user=request.user, meeting=meeting).exists():
        return Response({"detail": "모임 회원만 답글을 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

    if meeting.meeting_date < timezone.now():
        return Response({"detail": "지난 모임의 답글은 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    reply = get_object_or_404(DiscussionReply, content=content, user=request.user)

    reply.delete()
    return Response({"detail": "답글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

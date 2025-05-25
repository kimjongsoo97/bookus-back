from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import MemoSerializer
from .models import Memo
from books.models import Book

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def memo_index(request):
    user=request.user
    memo=Memo.objects.filter(user_id=user.id)
    serializer=MemoSerializer(memo,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_memo(request):
    serializer = MemoSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():  
        serializer.save()  # Memo 객체는 여기서 생성됨. user는 serializer에서 자동 할당
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_memo(request,memo_id):
    memo=Memo.objects.get(id=memo_id)
    serializer=MemoSerializer(instance=memo,data=request.data,partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)
    return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detail_memo(request, memo_id):
    user = request.user

    try:
        memo = Memo.objects.get(id=memo_id)
    except Memo.DoesNotExist:
        return Response({"error": "해당 메모는 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

    if memo.user_id != user.id:
        return Response({"error": "해당 메모는 접근이 불가능합니다"}, status=status.HTTP_403_FORBIDDEN)

    serializer = MemoSerializer(memo)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_memo(request, memo_id):
    user = request.user

    try:
        memo = Memo.objects.get(id=memo_id)
    except Memo.DoesNotExist:
        return Response({"error": "해당 메모는 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)

    if memo.user_id != user.id:
        return Response({"error": "해당 메모는 접근이 불가능합니다"}, status=status.HTTP_403_FORBIDDEN)

    memo.delete()
    return Response({"message": "메모가 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_memo_from_audio(request):
    user = request.user
    book_id = request.data.get('book')  # 선택 사항
    audio_file = request.FILES.get('audio')

    if not audio_file:
        return Response({"error": "audio 파일을 첨부해주세요."}, status=400)

    # STT 처리
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ko-KR')
    except sr.UnknownValueError:
        return Response({"error": "음성을 인식할 수 없습니다."}, status=400)
    except sr.RequestError as e:
        return Response({"error": f"STT 서비스 오류: {e}"}, status=500)
    except Exception as e:
        return Response({"error": f"오디오 파일 처리 중 오류: {str(e)}"}, status=500)

    # book 처리 (선택 사항)
    book = None
    if book_id:
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "해당 책이 존재하지 않습니다."}, status=404)

    # 메모 저장
    memo = Memo.objects.create(user=user, book=book, content=text)

    return Response({
        "message": "메모가 성공적으로 저장되었습니다.",
        "content": text
    }, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_memo_from_audio(request, memo_id):
    user = request.user
    audio_file = request.FILES.get('audio')

    if not audio_file:
        return Response({"error": "audio 파일을 첨부해주세요."}, status=400)

    try:
        memo = Memo.objects.get(id=memo_id, user=user)
    except Memo.DoesNotExist:
        return Response({"error": "메모를 찾을 수 없습니다."}, status=404)

    # STT 처리
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ko-KR')
    except sr.UnknownValueError:
        return Response({"error": "음성을 인식할 수 없습니다."}, status=400)
    except sr.RequestError as e:
        return Response({"error": f"STT 서비스 오류: {e}"}, status=500)
    except Exception as e:
        return Response({"error": f"오디오 파일 처리 중 오류: {str(e)}"}, status=500)

    # 기존 메모 내용 업데이트
    memo.content = text
    memo.save()

    return Response({
        "message": "메모가 음성으로 업데이트되었습니다.",
        "content": text
    }, status=200)

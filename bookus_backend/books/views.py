# books/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book
from django.db.models import Q
from .serializers import BookSerializer,FavoriteSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Book,Favorite
from .serializers import BookSerializer
@api_view(['GET'])
def book_list(request):
    category_id = request.GET.get('category')

    if category_id:
        try:
            books = Book.objects.filter(category_id=category_id)
        except ValueError:
            books = Book.objects.none()
    else:
        books = Book.objects.all()

    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def book_random_list(request):
 
    books = Book.objects.all().order_by('?')[:10]

    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def book_detail(request, pk):
    book = get_object_or_404(Book, id=pk)
    serializer = BookSerializer(book, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def book_search(request):
    query = request.query_params.get('q', '')
    books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(content__icontains=query)
        )
    serilalizer=BookSerializer(books,many=True)
    return Response(serilalizer.data)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite(request):
    user = request.user

    # [1] 즐겨찾기 목록 조회
    if request.method == 'GET':
        favorites = Favorite.objects.filter(user=user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    # [2] 즐겨찾기 추가
    elif request.method == 'POST':
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({'detail': 'book_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        book = Book.objects.filter(id=book_id).first()
        if not book:
            return Response({'detail': '책을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        # 이미 찜한 경우 방지
        if Favorite.objects.filter(user=user, book=book).exists():
            return Response({'detail': '이미 찜한 책입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        Favorite.objects.create(user=user, book=book)
        return Response({'detail': '찜 완료'}, status=status.HTTP_201_CREATED)

    # [3] 즐겨찾기 삭제
    elif request.method == 'DELETE':
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({'detail': 'book_id가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        favorite = Favorite.objects.filter(user=user, book__id=book_id).first()
        if favorite:
            favorite.delete()
            return Response({'detail': '찜 해제 완료'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': '찜 기록 없음'}, status=status.HTTP_404_NOT_FOUND)
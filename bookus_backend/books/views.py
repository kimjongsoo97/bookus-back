# books/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def book_list(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    serializer = BookSerializer(book, context={'request': request})
    return Response(serializer.data)
# books/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer

@api_view(['GET'])
def book_list(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def book_detail(request, pk):
    book=Book.objects.get(pk=pk)
    serializer = BookSerializer(book)
    return Response(serializer.data)
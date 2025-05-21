# books/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book
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
def book_detail(request, pk):
    book = get_object_or_404(Book, id=pk)
    serializer = BookSerializer(book, context={'request': request})
    return Response(serializer.data)
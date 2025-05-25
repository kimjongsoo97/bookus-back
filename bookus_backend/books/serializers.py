# books/serializers.py
from rest_framework import serializers
from .models import Book,Favorite

class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'content', 'author', 'img','link', 'best_seller_rank', 'category', 'category_name']

class FavoriteSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'book', 'book_id', 'created_at']
        read_only_fields = ['id', 'user', 'book', 'created_at']
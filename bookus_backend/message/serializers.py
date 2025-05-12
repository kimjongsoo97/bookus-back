from rest_framework import serializers
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

# 조회용
class MessageSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=20)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    content = serializers.CharField()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Message
        fields = ['title', 'sender', 'content', 'created_at', 'status']

# 전송용
class SendMessageSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=20)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    receiver = serializers.SlugRelatedField(slug_field='nickname', queryset=User.objects.all())
    content = serializers.CharField()

    class Meta:
        model = Message
        fields = ['title', 'receiver', 'content']

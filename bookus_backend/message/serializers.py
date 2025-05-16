from rest_framework import serializers
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


# 조회용
class MessageSerializer(serializers.ModelSerializer):
    counterpart_nickname = serializers.CharField(source='counterpart.nickname', read_only=True)
    owner_nickname = serializers.EmailField(source='owner.nickname', read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    counterpart_id = serializers.IntegerField(source='counterpart.id', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'title',
            'owner_nickname',
            'owner_id',
            'content',
            'is_sender',
            'counterpart_nickname',
            'counterpart_id',
            'read_status',
            'delete_status',
            'created_at',
        ]
class SendMessageSerializer(serializers.ModelSerializer):
    receiver = serializers.SlugRelatedField(
        slug_field='nickname',
        queryset=User.objects.all()
    )

    class Meta:
        model = Message
        fields = ['title', 'content', 'receiver']

    def create(self, validated_data):
        sender = self.context['request'].user
        receiver = validated_data['receiver']

        title = validated_data['title']
        content = validated_data['content']

        # 받은 사람 쪽지 생성 (받은함)
        Message.objects.create(
            owner=receiver,
            counterpart=sender,
            is_sender=False,
            title=title,
            content=content,
            read_status='UNREAD',
            delete_status='UNDELETE',
        )

        # 보낸 사람 쪽지 생성 (보낸함)
        return Message.objects.create(
            owner=sender,
            counterpart=receiver,
            is_sender=True,
            title=title,
            content=content,
            read_status='READ',
            delete_status='UNDELETE',
        )
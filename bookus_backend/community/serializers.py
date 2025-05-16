from rest_framework import serializers
from .models import Community
from django.contrib.auth import get_user_model

User=get_user_model()


class CommunitySerializer(serializers.ModelSerializer):
    writer= serializers.CharField(source='user.nickname', read_only=True)
    writer_id=serializers.IntegerField(source='user.id',read_only=True)
    class Meta:
        model=Community
        fields=[
            'id',
            'title',
            'writer',
            'content',
            'writer_id',
            'img',
            'created_at',
            'delete_status',
        ]

class CommunityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ['title', 'content', 'img', 'created_at']
        # 'user'는 context에서 자동 설정하므로 포함하지 않음

    def create(self, validated_data):
        user = self.context['request'].user
        title = validated_data['title']
        content = validated_data['content']
        img = validated_data.get('img')

        community = Community.objects.create(
            user=user,  
            title=title,
            content=content,
            img=img,
            delete_status='UNDELETE',
        )

        return community
    
    

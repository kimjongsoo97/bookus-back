from rest_framework import serializers
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Content, DiscussionReply, QuizReply, BookReview, BookReviewCompilation
from meeting.models import Membership, Meeting

class DiscussionReplySerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    content=serializers.PrimaryKeyRelatedField(queryset=Content.objects.all())
    user=serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = DiscussionReply
        fields = ['id', 'user', 'user_nickname', 'body', 'created_at','content']
        read_only_fields = ['id', 'user', 'user_nickname', 'created_at']

    def create(self,validated_data):
        validated_data['user']=self.context['request'].user
        return super().create(validated_data)
    
class QuizReplySerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    content=serializers.PrimaryKeyRelatedField(queryset=Content.objects.all())
    is_correct = serializers.BooleanField(read_only=True)
    user=serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = QuizReply
        fields = ['id', 'content','user', 'user_nickname', 'body', 'is_correct', 'created_at']
        read_only_fields = ['id', 'user', 'user_nickname', 'is_correct', 'created_at']
        
    def create(self,validated_data):
        validated_data['user']=self.context['request'].user
        return super().create(validated_data)
    
class BookReviewSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    content = serializers.PrimaryKeyRelatedField(queryset=Content.objects.all())  # 추가: content 필드를 명시적으로 처리
    user=serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = BookReview
        fields = ['id', 'content', 'user', 'user_nickname', 'body', 'created_at']
        read_only_fields = ['id', 'user', 'user_nickname', 'created_at']  # 수정: content를 read_only_fields에서 제거

    def create(self,validated_data):
        validated_data['user']=self.context['request'].user
        return super().create(validated_data)

class BookReviewCompilationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReviewCompilation
        fields = ['id', 'compiled_body', 'compiled_at']
        read_only_fields = ['id', 'compiled_body', 'compiled_at']

class ContentSerializer(serializers.ModelSerializer):
    meeting = serializers.PrimaryKeyRelatedField(queryset=Meeting.objects.filter(delete_status='UNDELETE'))
    creator_nickname = serializers.CharField(source='creator.nickname', read_only=True)
    discussion_replies = DiscussionReplySerializer(many=True, read_only=True)
    quiz_replies = QuizReplySerializer(many=True, read_only=True)
    book_reviews = BookReviewSerializer(many=True, read_only=True)
    compilation = BookReviewCompilationSerializer(read_only=True)
    is_revealed = serializers.SerializerMethodField()
    creator=serializers.ReadOnlyField(source='creator.id')
    class Meta:
        model = Content
        fields = [
            'id', 'meeting', 'creator','creator_nickname', 'content_type', 'title', 'body',
            'created_at', 'reveal_date', 'word_limit', 
            'discussion_replies', 'quiz_replies', 'book_reviews', 'compilation', 'is_revealed'
        ]
        read_only_fields = [
            'id', 'creator','creator_nickname', 'created_at',
            'discussion_replies', 'quiz_replies', 'book_reviews', 'compilation', 'is_revealed'
        ]

    def create(self,validated_data):
        validated_data['creator']=self.context['request'].user
        return super().create(validated_data)
    
    def get_is_revealed(self, obj):
        return not obj.reveal_date or obj.reveal_date <= timezone.now()

    def validate(self, data):
        meeting = data.get('meeting')
        if not Membership.objects.filter(user=self.context['request'].user, meeting=meeting, member_status='MEETING_ADMIN').exists():
            raise serializers.ValidationError({"detail": _("모임장만 컨텐츠를 생성할 수 있습니다.")})

        content_type = data.get('content_type', self.instance.content_type if self.instance else None)

        if content_type == 'BOOK_REVIEW':
            if not data.get('word_limit'):
                raise serializers.ValidationError({"word_limit": _("독후감은 글자 수 제한이 필요합니다.")})
            if not data.get('reveal_date'):
                raise serializers.ValidationError({"reveal_date": _("독후감은 공개 날짜가 필요합니다.")})

        if content_type == 'QUIZ' and not data.get('reveal_date'):
            raise serializers.ValidationError({"reveal_date": _("퀴즈는 정답 공개 날짜가 필요합니다.")})

        return data
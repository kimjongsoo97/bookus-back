# meetings/serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Meeting, Membership

class MembershipSerializer(serializers.ModelSerializer):
    """Membership 모델을 직렬화하여 멤버 정보 제공."""
    user_nickname = serializers.CharField(source='user.nickname', read_only=True, default='')
    meeting_name = serializers.CharField(source='meeting.name', read_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'user', 'user_nickname', 'meeting', 'meeting_name', 'member_status', 'joined_at']
        read_only_fields = ['id', 'user', 'user_nickname', 'meeting_name', 'joined_at']

class MeetingSerializer(serializers.ModelSerializer):
    """Meeting 모델을 직렬화하여 모임 정보 제공."""
    book_title = serializers.CharField(source='book.title', read_only=True, allow_null=True)
    creator_nickname = serializers.CharField(source='creator.nickname', read_only=True, default='')
    current_member_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    members = MembershipSerializer(source='membership_set', many=True, read_only=True)
    
    class Meta:
        model = Meeting
        fields = [
            'id', 'name', 'description', 'created_at', 'meeting_date',
            'map_directions', 'meeting_directions', 'max_members',
            'book', 'book_title', 'creator', 'creator_nickname',
            'current_member_count', 'is_owner', 'delete_status', 'members'
        ]
        read_only_fields = ['id', 'created_at', 'creator', 'creator_nickname', 'current_member_count', 'is_owner', 'members']

    def get_current_member_count(self, obj):
        """현재 모임의 멤버 수 반환."""
        return obj.membership_set.count()

    def get_is_owner(self, obj):
        """요청 사용자가 모임 운영자인지 확인."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.membership_set.filter(user=request.user, member_status='MEETING_ADMIN').exists()
        return False

    def validate(self, data):
        """모임 데이터 검증."""
        if data.get('meeting_date') and data['meeting_date'] < timezone.now():
            raise serializers.ValidationError({"meeting_date": _("모임 날짜는 과거일 수 없습니다.")})
        if data.get('delete_status') and data['delete_status'] not in dict(Meeting.STATUS_DELETE_CHOICES):
            raise serializers.ValidationError({"delete_status": _("유효하지 않은 삭제 상태입니다.")})
        return data
    def validate_map_directions(self, value):
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("map_directions은 JSON 객체여야 합니다.")
        
        required_keys = ['title', 'address', 'x', 'y']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"'{key}' 필드가 필요합니다.")
        
        return value
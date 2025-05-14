from rest_framework import serializers
from .models import Memo


class MemoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Memo
        fields=['id','user','book','content','created_at','updated_at']
        read_only_fields=['created_at','updated_at','user']
    
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user 
        return super().create(validated_data)
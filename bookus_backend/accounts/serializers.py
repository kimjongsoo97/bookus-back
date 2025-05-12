from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)
    confirm_password=serializers.CharField(write_only=True)

    
    class Meta:
        model=User
        fields=['email','password','confirm_password','nickname','name','phone_number']

    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Password MissMatched")
        return data
        
    def create(self,validated_data):
        validated_data.pop('confirm_password')
        user=User.objects.create_user(**validated_data)
        return user

class UserUpdateNicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['nickname']    

class UserUpdatePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['password']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token=super().get_token(user)
        token['id']=user.id
        token['email']=user.email
        token['nickname']=user.nickname
        return token
    
    def validate(self,attrs):
        attrs['username']=attrs.get('email')
        return super().validate(attrs)
    

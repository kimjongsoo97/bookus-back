from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer,UserUpdateNicknameSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.
from django.contrib.auth import get_user_model

User=get_user_model()
@api_view(['POST'])
def register_user(request):
    serializer=UserRegisterSerializer(data=request.POST)
    if serializer.is_valid():
        
        serializer.save()
        return Response({'message': '회원가입 성공','user':serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password=request.data.get('password')
    
    user=authenticate(request,username=email,password=password)

    if user is not None:
        refresh=RefreshToken.for_user(user)
        return Response({
            '토큰 발급 성공':str(refresh.access_token),
            # '리프레쉬 토큰':str(refresh),
            'id':user.id,
            '이메일':user.email,
            '닉네임':user.nickname,
        },status=status.HTTP_200_OK)
    return Response({'로그인실패': '아이디 및 비밀번호를 확인해주세요'},status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_email(request):
    email=request.data.get('email')
    if not email:
        return Response({'이메일 없음':'이메일을 입력해주세요'},status=status.HTTP_400_BAD_REQUEST)
    isEamil=User.objects.filter(email=email).exists()
    return Response({'이메일 중복체크 성공': isEamil},status=status.HTTP_200_OK)

@api_view(['POST'])
def check_nickname(request):
    nickname=request.data.get('nickname')
    if not nickname:
        return Response({'NoneNickName':'닉네임을 입력해 주세요'},status=status.HTTP_400_BAD_REQUEST)
    isNickname=User.objects.filter(nickname=nickname).exists()
    return Response({'닉네임 중복체크 성공':isNickname},status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_nickname(request):
    nickname=request.data.get('nickname')
    if not nickname:
        return Response({'NoneNickName':'닉네임을 입력해주세요'},status=status.HTTP_400_BAD_REQUEST)
    isNickname=User.objects.filter(nickname=nickname).exists()
    if isNickname:
        return Response({'duplicate':'이미 존재하는 닉네임입니다'},status=status.HTTP_400_BAD_REQUEST)
    user=request.user
    serializer=UserUpdateNicknameSerializer(user,data={'nickname':nickname},partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'닉네임 변경 성공':serializer.data},status=status.HTTP_200_OK)
    return Response({'요청 에러':'요청 형식이 유효하지 않습니다'},status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
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
    
    serializer=UserRegisterSerializer(data=request.data)
    print(serializer)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': '회원가입 성공','user':serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password=request.data.get('password')
    
    user=authenticate(request,username=email,password=password)
    token = RefreshToken.for_user(user).access_token
    return Response({
        'token': str(token),    
        'user': {
            'id': user.id,
            'email': user.email,
            'nickname': user.nickname,
        }
    })
    # return Response({'로그인실패': '아이디 및 비밀번호를 확인해주세요'},status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_email(request):
    email = request.data.get('email')
    if not email:
        return Response({'message': '이메일을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

    is_used = User.objects.filter(email=email).exists()
    return Response({'available': not is_used}, status=status.HTTP_200_OK)

@api_view(['POST'])
def check_nickname(request):
    nickname=request.data.get('nickname')
    if not nickname:
        return Response({'NoneNickName':'닉네임을 입력해 주세요'},status=status.HTTP_400_BAD_REQUEST)
    is_used=User.objects.filter(nickname=nickname).exists()
    return Response({'available': not is_used},status=status.HTTP_200_OK)

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

@api_view(['POST'])
def kakao_login_view(request):
    kakao_token = request.data.get("access_token")
    if not kakao_token:
        return Response({"error": "카카오 access token이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 사용자 정보 요청
    kakao_user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {kakao_token}"}  # ✅ 오타 수정

    kakao_response = requests.get(kakao_user_info_url, headers=headers)  # ✅ requests.get

    if kakao_response.status_code != 200:
        return Response({"error": "카카오 인증 실패"}, status=400)

    kakao_data = kakao_response.json()
    kakao_id = kakao_data.get("id")
    kakao_account = kakao_data.get("kakao_account", {})

    email = kakao_account.get("email", f"{kakao_id}@kakao.com")
    profile = kakao_account.get("profile", {})
    nickname = profile.get("nickname", f"user_{kakao_id}")
    name = profile.get("nickname", "카카오사용자")
    phone_number = "010-0000-0000"

    # 닉네임 중복 처리
    if User.objects.filter(nickname=nickname).exists():
        nickname += str(User.objects.count())

    # 유저 생성 or 조회
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
    else:
        user = User.objects.create(
            kakao_id=kakao_id,
            email=email,
            nickname=nickname,
            name=name,
            phone_number=phone_number,
        )
        user.set_unusable_password()
        user.save()

    # JWT 토큰 발급
    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    })
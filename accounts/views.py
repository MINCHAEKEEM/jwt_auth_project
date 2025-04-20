from django.contrib.auth import get_user_model
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework import serializers

from .serializers import SignupSerializer, UserResponseSerializer, CustomTokenObtainPairSerializer

User = get_user_model()

# Create your views here.

class SignupView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                response_serializer = UserResponseSerializer(user)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            # 이미 포맷팅된 사용자 정의 에러 확인
            if 'error' in e.detail and 'code' in e.detail['error']:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            
            # 일반 유효성 검사 오류 처리
            try:
                first_error_key = next(iter(e.detail))
                first_error_message = e.detail[first_error_key][0]
                error_data = {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": f"{first_error_key}: {first_error_message}"
                    }
                }
            except (StopIteration, KeyError):
                error_data = {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "입력값이 유효하지 않습니다."
                    }
                }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except AuthenticationFailed:
            return Response({
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "아이디 또는 비밀번호가 올바르지 않습니다."
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        except (InvalidToken, TokenError) as e:
            return Response({
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "토큰이 유효하지 않습니다."
                }
            }, status=status.HTTP_401_UNAUTHORIZED)

class AuthCheckView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user_serializer = UserResponseSerializer(request.user)
        return Response({
            "message": "토큰이 유효합니다.",
            "user": user_serializer.data
        }, status=status.HTTP_200_OK)
    
    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return Response({
                "error": {
                    "code": "TOKEN_NOT_FOUND",
                    "message": "토큰이 없습니다."
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        elif isinstance(exc, InvalidToken) or isinstance(exc, TokenError):
            return Response({
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "토큰이 유효하지 않습니다."
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        return super().handle_exception(exc)
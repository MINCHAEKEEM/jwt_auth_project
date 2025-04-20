from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ['username', 'password', 'nickname']
        extra_kwargs = {
            'nickname' : {'required' : True},
            'username': {'validators': []},  # 기본 유일성 검사 비활성화
            'nickname': {'validators': []}   # 기본 유일성 검사 비활성화
        }
    
    def validate(self, attrs):
        username = attrs.get('username')
        nickname = attrs.get('nickname')
        
        # 사용자 이름 중복 검사
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                "error": {
                    "code": "USER_ALREADY_EXISTS",
                    "message": "이미 가입된 사용자입니다."
                }
            })
        
        # 닉네임 중복 검사
        if User.objects.filter(nickname=nickname).exists():
            raise serializers.ValidationError({
                "error": {
                    "code": "USER_ALREADY_EXISTS",
                    "message": "이미 가입된 사용자입니다."
                }
            })
        
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            nickname=validated_data['nickname'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
        

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'nickname']
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data =  super().validate(attrs)
        
        access_token = data.get('access')
        if access_token:
            return {'token': str(access_token)}
        else:
            raise serializers.ValidationError("액세스 토큰을 생성할 수 없습니다.")
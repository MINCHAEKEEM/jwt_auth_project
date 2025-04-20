# users/urls.py
from django.urls import path
from .views import SignupView, CustomTokenObtainPairView, AuthCheckView
from django.views.generic import RedirectView  # 추가
# from rest_framework_simplejwt.views import TokenRefreshView # 리프레시 토큰 사용 시

urlpatterns = [
    # path('api/users/signup', SignupView.as_view(), name='signup'), # URL 경로에 prefix 추가 가능
    path('', RedirectView.as_view(url='/swagger/', permanent=False), name='index'),  # 루트 URL을 Swagger로 리다이렉트
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), # SimpleJWT의 이름 규칙 또는 직접 지정
    path('auth/', AuthCheckView.as_view(), name='auth_check'),
    # 리프레시 토큰 엔드포인트 (필요 시)
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
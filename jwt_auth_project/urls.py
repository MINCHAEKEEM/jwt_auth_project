"""
URL configuration for jwt_auth_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path # re_path 추가
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Swagger 스키마 뷰 설정
schema_view = get_schema_view(
   openapi.Info(
      title="JWT Auth API", # API 제목
      default_version='v1', # API 버전
      description="JWT 인증 프로젝트 API 문서", # API 설명
      terms_of_service="https://www.google.com/policies/terms/", # 서비스 약관 URL (샘플)
      contact=openapi.Contact(email="contact@example.com"), # 연락처 이메일 (샘플)
      license=openapi.License(name="BSD License"), # 라이선스 정보 (샘플)
   ),
   public=True, # 누구나 접근 가능하도록 설정
   permission_classes=(permissions.AllowAny,), # 권한 클래스 설정
   authentication_classes=(), # 스키마 뷰 자체에는 인증 불필요
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')), # users 앱의 URL 포함 (prefix 없이 루트 경로 사용)

    # Swagger URL 패턴들
    # re_path 사용 이유: format 인자(.json, .yaml)를 선택적으로 받기 위함
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'), # Swagger UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), # Redoc UI
]

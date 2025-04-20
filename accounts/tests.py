# users/tests.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your tests here.
# 이 모듈의 모든 테스트에서 데이터베이스를 사용하도록 표시
pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    """API 클라이언트 인스턴스를 제공하는 Fixture."""
    return APIClient()

@pytest.fixture
def test_user_data():
    """유효한 사용자 데이터를 제공하는 Fixture."""
    return {
        "username": "testuser",
        "password": "StrongPassword123",
        "nickname": "Tester"
    }

@pytest.fixture
def create_test_user(test_user_data):
    """DB에 직접 테스트 사용자를 생성하는 Fixture."""
    user = User.objects.create_user(
        username=test_user_data["username"],
        password=test_user_data["password"],
        nickname=test_user_data["nickname"]
    )
    return user

# --- 회원가입 테스트 ---

def test_signup_success(api_client, test_user_data):
    """성공적인 사용자 회원가입 테스트."""
    url = reverse('signup') # users/urls.py에서 정의한 name 사용
    # 다른 유저 이름과 닉네임을 사용해 중복 회원가입 문제 방지
    new_user_data = {
        "username": "newuser",
        "password": "StrongPassword123",
        "nickname": "Newbie"
    }
    response = api_client.post(url, new_user_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    # DB에 사용자가 생성되었는지 확인
    assert User.objects.filter(username=new_user_data["username"]).exists()
    # 응답 본문 확인
    assert response.data['username'] == new_user_data["username"]
    assert response.data['nickname'] == new_user_data["nickname"]
    # 비밀번호가 응답에 포함되지 않았는지 확인
    assert 'password' not in response.data

def test_signup_user_already_exists(api_client, create_test_user, test_user_data):
    """사용자 이름이 이미 존재할 때 회원가입 실패 테스트."""
    url = reverse('signup')
    # 동일한 사용자 이름으로 다시 회원가입 시도
    signup_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
        "nickname": test_user_data["nickname"]
    }
    response = api_client.post(url, signup_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error']['code'] == "USER_ALREADY_EXISTS"
    assert response.data['error']['message'] == "이미 가입된 사용자입니다."
    # 사용자가 여전히 1명인지 확인 (중복 생성 방지)
    assert User.objects.count() == 1

def test_signup_missing_fields(api_client):
    """필수 필드가 누락되었을 때 회원가입 실패 테스트."""
    url = reverse('signup')
    incomplete_data = {"username": "newuser"} # password와 nickname 누락
    response = api_client.post(url, incomplete_data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error']['code'] == "VALIDATION_ERROR"
    # 어떤 필드가 먼저 검증되는지에 따라 메시지가 달라질 수 있음
    assert "password: 이 필드는 필수 항목입니다." in response.data['error']['message'] or \
           "nickname: 이 필드는 필수 항목입니다." in response.data['error']['message']


# --- 로그인 테스트 ---

def test_login_success(api_client, create_test_user, test_user_data):
    """성공적인 로그인 테스트."""
    url = reverse('token_obtain_pair') # users/urls.py에서 정의한 이름 사용
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = api_client.post(url, login_data, format='json')

    assert response.status_code == status.HTTP_200_OK
    # 응답에 'token' 키가 있는지 확인
    assert 'token' in response.data
    # 토큰이 문자열인지 확인
    assert isinstance(response.data['token'], str)
    # 토큰이 비어있지 않은지 기본적인 확인
    assert len(response.data['token']) > 20

def test_login_invalid_password(api_client, create_test_user, test_user_data):
    """잘못된 비밀번호로 로그인 실패 테스트."""
    url = reverse('token_obtain_pair')
    login_data = {
        "username": test_user_data["username"],
        "password": "WrongPassword" # 잘못된 비밀번호
    }
    response = api_client.post(url, login_data, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['error']['code'] == "INVALID_CREDENTIALS"
    assert response.data['error']['message'] == "아이디 또는 비밀번호가 올바르지 않습니다."

def test_login_user_not_found(api_client, test_user_data):
    """존재하지 않는 사용자로 로그인 실패 테스트."""
    url = reverse('token_obtain_pair')
    login_data = {
        "username": "nonexistentuser", # 존재하지 않는 사용자 이름
        "password": test_user_data["password"]
    }
    response = api_client.post(url, login_data, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # SimpleJWT는 사용자가 없거나 비밀번호가 틀린 경우 모두 AuthenticationFailed 발생시킴
    assert response.data['error']['code'] == "INVALID_CREDENTIALS"
    assert response.data['error']['message'] == "아이디 또는 비밀번호가 올바르지 않습니다."


# --- 인증 확인 테스트 ---

def test_auth_check_success(api_client, create_test_user, test_user_data):
    """유효한 토큰으로 보호된 엔드포인트 접근 성공 테스트."""
    # 1. 로그인하여 토큰 얻기
    login_url = reverse('token_obtain_pair')
    login_data = {"username": test_user_data["username"], "password": test_user_data["password"]}
    login_response = api_client.post(login_url, login_data, format='json')
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.data['token']

    # 2. 얻은 토큰을 사용하여 보호된 엔드포인트 접근
    auth_url = reverse('auth_check')
    # Authorization 헤더 설정 ('Bearer ' 접두사 포함)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    auth_response = api_client.get(auth_url)

    assert auth_response.status_code == status.HTTP_200_OK
    assert auth_response.data['message'] == "토큰이 유효합니다."
    assert auth_response.data['user']['username'] == test_user_data["username"]

    # 다음 테스트를 위해 인증 정보 초기화 (선택 사항)
    api_client.credentials()

def test_auth_check_no_token(api_client):
    """토큰 없이 보호된 엔드포인트 접근 실패 테스트."""
    url = reverse('auth_check')
    # 인증 정보가 설정되지 않았는지 확인
    api_client.credentials()
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['error']['code'] == "TOKEN_NOT_FOUND"
    assert response.data['error']['message'] == "토큰이 없습니다."

def test_auth_check_invalid_token(api_client):
    """유효하지 않은 토큰으로 보호된 엔드포인트 접근 실패 테스트."""
    url = reverse('auth_check')
    invalid_token = "this.is.not.a.valid.token" # 유효하지 않은 형식의 토큰
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {invalid_token}')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['error']['code'] == "INVALID_TOKEN"
    assert response.data['error']['message'] == "토큰이 유효하지 않습니다."
    api_client.credentials() # 인증 정보 초기화

# 참고: 만료된 토큰 테스트는 시간을 모킹(mocking)해야 하므로 복잡성이 증가합니다.
# 여기서는 SimpleJWT의 기본 처리와 커스텀 예외 처리기의 매핑에 의존합니다.
# 만료 메시지를 엄격하게 검증해야 한다면 시간 모킹 라이브러리(예: freezegun)를 사용한 테스트를 추가할 수 있습니다.

# jwt_auth_project/utils/exception_handler.py
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError, AuthenticationFailed
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.exceptions import NotAuthenticated # 토큰 없을 때 발생하는 예외

def custom_exception_handler(exc, context):
    # DRF의 기본 예외 처리기를 먼저 호출하여 표준 에러 응답을 받음
    response = exception_handler(exc, context)

    # DRF 기본 유효성 검사 오류 (SignupView에서 이미 처리된 경우 제외)
    if isinstance(exc, DRFValidationError):
        error_detail = exc.detail
        
        # 사용자 정의 에러 형식인 경우 그대로 사용
        if isinstance(error_detail, dict) and 'error' in error_detail and 'code' in error_detail['error']:
            custom_data = error_detail
            return Response(custom_data, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 첫 번째 오류 메시지를 가져오려고 시도
            first_key = next(iter(error_detail))
            first_message = error_detail[first_key][0]
            error_code = "VALIDATION_ERROR"
            error_message = f"{first_key}: {first_message}"
        except Exception: # 예상치 못한 오류 구조 대비
            error_code = "VALIDATION_ERROR"
            error_message = str(exc.detail) # 오류 내용을 문자열로 변환

        custom_data = {
            "error": {
                "code": error_code,
                "message": error_message
            }
        }
        # DRF의 기본 상태 코드 사용 (보통 400 Bad Request)
        status_code = status.HTTP_400_BAD_REQUEST
        if response:
            status_code = response.status_code
        return Response(custom_data, status=status_code)

    # SimpleJWT의 AuthenticationFailed (잘못된 자격 증명 - 로그인 실패)
    if isinstance(exc, AuthenticationFailed):
        custom_data = {
            "error": {
                "code": "INVALID_CREDENTIALS",
                "message": "아이디 또는 비밀번호가 올바르지 않습니다."
            }
        }
        # AuthenticationFailed는 보통 401 Unauthorized
        return Response(custom_data, status=status.HTTP_401_UNAUTHORIZED)

    # NotAuthenticated (보호된 엔드포인트에 토큰 없이 접근)
    if isinstance(exc, NotAuthenticated):
        custom_data = {
            "error": {
                "code": "TOKEN_NOT_FOUND",
                "message": "토큰이 없습니다."
            }
        }
        return Response(custom_data, status=status.HTTP_401_UNAUTHORIZED)

    # SimpleJWT의 토큰 관련 오류 (만료, 형식 오류 등)
    if isinstance(exc, InvalidToken) or isinstance(exc, TokenError):
        # 만료, 형식 오류 등을 포괄적으로 처리
        error_code = "INVALID_TOKEN"
        error_message = "토큰이 유효하지 않습니다."

        # 예외 상세 정보에서 만료 여부 힌트 확인 (완벽하지 않을 수 있음)
        detail = getattr(exc, 'detail', {})
        if isinstance(detail, dict) and 'code' in detail:
            if detail['code'] == 'token_not_valid':
                # 메시지 내용에서 'expired' 단어 확인 (깨지기 쉬운 방식)
                messages = detail.get('messages', [])
                if any('expired' in msg.get('message', '').lower() for msg in messages):
                    error_code = "TOKEN_EXPIRED"
                    error_message = "토큰이 만료되었습니다."

        custom_data = {
            "error": {
                "code": error_code,
                "message": error_message
            }
        }
        # 유효하지 않은 토큰은 보통 401 Unauthorized
        return Response(custom_data, status=status.HTTP_401_UNAUTHORIZED)


    # 기본 핸들러가 응답을 생성했다면 그대로 반환 (다른 DRF 오류 등)
    if response is not None:
        # 여기서 다른 DRF 기본 오류 형식도 커스터마이징 가능
        pass # 현재는 처리되지 않은 DRF 오류는 기본 형식 유지

    # DRF나 위에서 처리되지 않은 예외는 None 반환 (-> 500 Internal Server Error 발생)
    return response
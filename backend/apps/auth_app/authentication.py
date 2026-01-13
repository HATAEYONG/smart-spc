"""
JWT Authentication for DRF

Django REST Framework용 JWT 인증 클래스
"""

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

from .jwt_auth import JWTManager, TokenBlacklist

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    """
    JWT Authentication for Django REST Framework

    Authorization: Bearer <access_token>
    """

    def authenticate(self, request):
        """
        JWT 토큰으로 사용자 인증
        """
        # Authorization 헤더에서 토큰 추출
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None  # 다른 인증 방식 시도

        token = auth_header[7:]  # 'Bearer ' 제거

        try:
            # 토큰 타입 검증 (access token)
            payload = JWTManager.verify_token_type(token, 'access')

            # 블랙리스트 확인
            if TokenBlacklist.is_blacklisted(token):
                raise AuthenticationFailed('로그아웃된 토큰입니다')

            # 사용자 조회
            user_id = payload['user_id']
            try:
                user = User.objects.get(id=user_id)

                # 사용자 활성 상태 확인
                if not user.is_active:
                    raise AuthenticationFailed('비활성화된 계정입니다')

                # UserProfile 활성 상태 확인
                if hasattr(user, 'spc_profile') and not user.spc_profile.is_active:
                    raise AuthenticationFailed('SPC 계정이 비활성화되었습니다')

                return (user, token)

            except User.DoesNotExist:
                raise AuthenticationFailed('사용자를 찾을 수 없습니다')

        except AuthenticationFailed:
            raise
        except Exception as e:
            raise AuthenticationFailed(f'인증 실패: {str(e)}')

    def authenticate_header(self, request):
        """
        인증 필요 시 응답 헤더에 포함될 값
        """
        return 'Bearer'


class JWTAuthenticationOptional(authentication.BaseAuthentication):
    """
    Optional JWT Authentication

    토큰이 있으면 인증하고, 없으면 익명 사용자로 처리
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]

        try:
            payload = JWTManager.verify_token_type(token, 'access')

            if TokenBlacklist.is_blacklisted(token):
                return None  # 실패 대신 익명 사용자로 처리

            user_id = payload['user_id']
            try:
                user = User.objects.get(id=user_id)

                if not user.is_active:
                    return None

                if hasattr(user, 'spc_profile') and not user.spc_profile.is_active:
                    return None

                return (user, token)

            except User.DoesNotExist:
                return None

        except Exception:
            return None

    def authenticate_header(self, request):
        return 'Bearer'

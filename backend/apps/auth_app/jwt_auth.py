"""
JWT Authentication Configuration and Utilities

JSON Web Token 기반 인증 시스템
- Access Token + Refresh Token
- 토큰 만료 관리
- 블랙리스트 기능
"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class JWTManager:
    """
    JWT 토큰 생성 및 검증 관리자
    """

    # 토큰 만료 시간 (기본값)
    ACCESS_TOKEN_LIFETIME = timedelta(minutes=60)  # 1시간
    REFRESH_TOKEN_LIFETIME = timedelta(days=7)   # 7일

    # 토큰 알고리즘
    ALGORITHM = 'HS256'

    @staticmethod
    def generate_access_token(user_id: int, payload: dict = None) -> str:
        """
        Access Token 생성 (짧은 만료 시간)
        """
        now = datetime.utcnow()

        token_payload = {
            'user_id': user_id,
            'type': 'access',
            'iat': now,
            'exp': now + JWTManager.ACCESS_TOKEN_LIFETIME,
            **(payload or {})
        }

        return jwt.encode(
            token_payload,
            settings.SECRET_KEY,
            algorithm=JWTManager.ALGORITHM
        )

    @staticmethod
    def generate_refresh_token(user_id: int) -> str:
        """
        Refresh Token 생성 (긴 만료 시간)
        """
        now = datetime.utcnow()

        token_payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': now + JWTManager.REFRESH_TOKEN_LIFETIME,
        }

        return jwt.encode(
            token_payload,
            settings.SECRET_KEY,
            algorithm=JWTManager.ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        토큰 디코딩 및 검증
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[JWTManager.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('토큰이 만료되었습니다')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('유효하지 않은 토큰입니다')

    @staticmethod
    def verify_token_type(token: str, expected_type: str) -> dict:
        """
        토큰 타입 검증
        """
        payload = JWTManager.decode_token(token)

        if payload.get('type') != expected_type:
            raise AuthenticationFailed(f'{expected_type} 토큰이 필요합니다')

        return payload

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """
        Refresh Token으로 새 Access Token 발급
        """
        # Refresh Token 검증
        payload = JWTManager.verify_token_type(refresh_token, 'refresh')
        user_id = payload['user_id']

        # 사용자 존재 확인
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('사용자를 찾을 수 없습니다')

        # 새 Access Token 생성
        access_token = JWTManager.generate_access_token(user_id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,  # 기존 refresh_token 재사용 또는 새로 발급
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }


class TokenBlacklist:
    """
    토큰 블랙리스트 관리 (로그아웃된 토큰 처리)
    """

    @staticmethod
    def add_to_blacklist(token: str) -> bool:
        """
        토큰을 블랙리스트에 추가
        """
        from .models import BlacklistedToken

        try:
            payload = JWTManager.decode_token(token)
            jti = payload.get('jti', token)  # JWT ID (있는 경우)

            BlacklistedToken.objects.create(
                token=token,
                jti=jti,
                user_id=payload['user_id'],
                expires_at=datetime.fromtimestamp(payload['exp'])
            )
            return True
        except Exception as e:
            print(f"블랙리스트 추가 실패: {str(e)}")
            return False

    @staticmethod
    def is_blacklisted(token: str) -> bool:
        """
        토큰이 블랙리스트에 있는지 확인
        """
        from .models import BlacklistedToken

        return BlacklistedToken.objects.filter(token=token).exists()


class JWTAuthenticationMiddleware:
    """
    JWT 인증 미들웨어 (선택적 사용)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Authorization 헤더에서 토큰 추출
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # 'Bearer ' 제거

            try:
                # 토큰 검증
                payload = JWTManager.verify_token_type(token, 'access')

                # 블랙리스트 확인
                if TokenBlacklist.is_blacklisted(token):
                    raise AuthenticationFailed('블랙리스트에 있는 토큰입니다')

                # 사용자 정보를 request에 저장
                request.user_id = payload['user_id']
                request.user = User.objects.get(id=payload['user_id'])

            except AuthenticationFailed as e:
                request.user = None
                request.auth_error = str(e)

        return self.get_response(request)

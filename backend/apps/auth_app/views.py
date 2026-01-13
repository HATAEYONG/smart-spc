"""
JWT Authentication Views

JWT 기반 인증 API 엔드포인트
- Login: Access Token + Refresh Token 발급
- Logout: Token 블랙리스트 추가
- Refresh: 새 Access Token 발급
- Verify: Token 유효성 검증
"""

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .jwt_auth import JWTManager, TokenBlacklist
from .serializers import (
    LoginSerializer,
    RefreshSerializer,
    TokenResponseSerializer,
    UserSerializer,
    VerifySerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    로그인 API (JWT Token 발급)
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="로그인하고 Access Token과 Refresh Token을 발급받습니다",
        request_body=LoginSerializer,
        responses={
            200: TokenResponseSerializer,
            401: "인증 실패"
        },
        tags=['Authentication']
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # 사용자 인증
            user = authenticate(username=username, password=password)

            if user is not None:
                if not user.is_active:
                    return Response(
                        {'error': '계정이 비활성화되었습니다'},
                        status=status.HTTP_403_FORBIDDEN
                    )

                # UserProfile 확인
                if hasattr(user, 'spc_profile'):
                    if not user.spc_profile.is_active:
                        return Response(
                            {'error': 'SPC 계정이 비활성화되었습니다'},
                            status=status.HTTP_403_FORBIDDEN
                        )

                # JWT Token 생성
                access_token = JWTManager.generate_access_token(user.id)
                refresh_token = JWTManager.generate_refresh_token(user.id)

                # 마지막 로그인 시간 업데이트
                update_last_login(None, user)

                # AuditLog 생성
                from .models import AuditLog
                AuditLog.objects.create(
                    user=user,
                    action='login',
                    description=f'User {user.username} logged in',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )

                logger.info(f"User {user.username} logged in successfully")

                return Response({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)

            else:
                logger.warning(f"Failed login attempt for username: {username}")
                return Response(
                    {'error': '사용자명 또는 비밀번호가 올바르지 않습니다'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return Response(
            {'error': '요청 데이터가 올바르지 않습니다', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    """
    로그아웃 API (Token 블랙리스트 추가)
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="로그아웃하고 현재 Token을 블랙리스트에 추가합니다",
        request_body=RefreshSerializer,
        responses={
            200: "로그아웃 성공",
            400: "잘못된 요청",
            401: "인증되지 않음"
        },
        tags=['Authentication']
    )
    def post(self, request):
        # Authorization 헤더에서 토큰 추출
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        access_token = None

        if auth_header.startswith('Bearer '):
            access_token = auth_header[7:]

        # Request body에서 refresh_token 추출
        refresh_token = request.data.get('refresh_token')

        if not access_token and not refresh_token:
            return Response(
                {'error': '토큰이 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Access Token 블랙리스트 추가
        if access_token:
            try:
                TokenBlacklist.add_to_blacklist(access_token)
            except Exception as e:
                logger.error(f"Failed to blacklist access token: {str(e)}")

        # Refresh Token 블랙리스트 추가
        if refresh_token:
            try:
                TokenBlacklist.add_to_blacklist(refresh_token)
            except Exception as e:
                logger.error(f"Failed to blacklist refresh token: {str(e)}")

        # AuditLog 생성
        from .models import AuditLog
        try:
            AuditLog.objects.create(
                user=request.user,
                action='logout',
                description=f'User {request.user.username} logged out',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")

        logger.info(f"User {request.user.username} logged out successfully")

        return Response({
            'message': '로그아웃되었습니다'
        }, status=status.HTTP_200_OK)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RefreshView(APIView):
    """
    Access Token 갱신 API
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Refresh Token을 사용하여 새 Access Token을 발급받습니다",
        request_body=RefreshSerializer,
        responses={
            200: TokenResponseSerializer,
            401: "유효하지 않은 Refresh Token"
        },
        tags=['Authentication']
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)

        if serializer.is_valid():
            refresh_token = serializer.validated_data['refresh_token']

            try:
                # 블랙리스트 확인
                if TokenBlacklist.is_blacklisted(refresh_token):
                    return Response(
                        {'error': '블랙리스트에 있는 토큰입니다'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # 새 Access Token 발급
                result = JWTManager.refresh_access_token(refresh_token)

                logger.info(f"Access token refreshed for user {result['user']['id']}")

                return Response(result, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Token refresh failed: {str(e)}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return Response(
            {'error': '요청 데이터가 올바르지 않습니다', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class VerifyView(APIView):
    """
    Token 유효성 검증 API
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Access Token의 유효성을 검증합니다",
        request_body=VerifySerializer,
        responses={
            200: "토큰 유효함",
            401: "유효하지 않은 토큰"
        },
        tags=['Authentication']
    )
    def post(self, request):
        serializer = VerifySerializer(data=request.data)

        if serializer.is_valid():
            token = serializer.validated_data['token']

            try:
                # 토큰 디코딩
                payload = JWTManager.decode_token(token)

                # 블랙리스트 확인
                if TokenBlacklist.is_blacklisted(token):
                    return Response(
                        {'error': '블랙리스트에 있는 토큰입니다'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # 사용자 정보 조회
                user_id = payload['user_id']
                try:
                    user = User.objects.get(id=user_id)
                    user_data = UserSerializer(user).data
                except User.DoesNotExist:
                    return Response(
                        {'error': '사용자를 찾을 수 없습니다'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                return Response({
                    'valid': True,
                    'user': user_data,
                    'payload': payload
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response(
                    {'error': str(e), 'valid': False},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return Response(
            {'error': '요청 데이터가 올바르지 않습니다', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class MeView(APIView):
    """
    현재 사용자 정보 조회 API
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="현재 로그인한 사용자의 정보를 조회합니다",
        responses={
            200: UserSerializer,
            401: "인증되지 않음"
        },
        tags=['Authentication']
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

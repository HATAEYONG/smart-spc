"""
Authentication Serializers
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile"""

    class Meta:
        model = UserProfile
        fields = ['role', 'department', 'phone', 'is_active']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User with profile"""
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_staff", "is_superuser", "profile"]
        read_only_fields = ["id", "is_staff", "is_superuser"]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        default='viewer'
    )
    department = serializers.CharField(required=False, allow_blank=True, max_length=100)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm",
                  "first_name", "last_name", "role", "department", "phone"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        # Extract profile fields
        role = validated_data.pop('role', 'viewer')
        department = validated_data.pop('department', '')
        phone = validated_data.pop('phone', '')

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create user profile
        UserProfile.objects.create(
            user=user,
            role=role,
            department=department,
            phone=phone
        )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm", "first_name", "last_name"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password": "Passwords do not match"})
        return data


# JWT Authentication Serializers

class RefreshSerializer(serializers.Serializer):
    """Refresh Token 요청 Serializer"""
    refresh_token = serializers.CharField(required=True, help_text="Refresh Token")


class TokenResponseSerializer(serializers.Serializer):
    """Token 응답 Serializer"""
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)


class VerifySerializer(serializers.Serializer):
    """Token 검증 요청 Serializer"""
    token = serializers.CharField(required=True, help_text="검증할 Access Token")

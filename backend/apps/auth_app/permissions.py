"""
Custom Permissions for SPC System
"""
from rest_framework import permissions


class IsSPCViewer(permissions.BasePermission):
    """
    Allow read-only access for viewers and above
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'spc_profile'):
            return True  # All authenticated users have at least viewer role

        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsSPCOperator(permissions.BasePermission):
    """
    Allow write access for operators and above
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'spc_profile'):
            profile = request.user.spc_profile
            return profile.is_operator

        return False


class IsQualityEngineer(permissions.BasePermission):
    """
    Allow full access for quality engineers and above
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'spc_profile'):
            profile = request.user.spc_profile
            return profile.is_quality_engineer

        return False


class IsSPCAdmin(permissions.BasePermission):
    """
    Allow admin-only access
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'spc_profile'):
            return request.user.spc_profile.is_admin

        return False

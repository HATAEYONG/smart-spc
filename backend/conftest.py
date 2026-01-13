"""
Pytest configuration and fixtures for the entire test suite
"""
import pytest
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    """Django REST Framework API client"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    """Authenticated API client"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def sample_datetime():
    """Sample datetime for testing"""
    return datetime(2025, 1, 1, 10, 0, 0)


@pytest.fixture
def future_datetime():
    """Future datetime for testing"""
    return datetime(2025, 1, 1, 12, 0, 0)

"""
Custom exception handler for Django REST Framework.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns errors in the format:
    {
        "ok": false,
        "data": None,
        "error": "error message"
    }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the error response format
        custom_response_data = {
            'ok': False,
            'data': None,
            'error': str(exc)
        }

        response.data = custom_response_data
        logger.error(f"API Error: {exc}")

    return response


def api_response(ok=True, data=None, error=None, status_code=status.HTTP_200_OK):
    """
    Helper function to create standardized API responses.
    """
    response_data = {
        'ok': ok,
        'data': data,
        'error': error
    }
    return Response(response_data, status=status_code)

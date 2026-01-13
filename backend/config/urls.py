"""
URL Configuration for online-aps-cps-scheduler with SPC
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="APS + SPC API",
        default_version='v1',
        description="Advanced Planning & Scheduling with Statistical Process Control",
        terms_of_service="https://www.your-website.com/terms/",
        contact=openapi.Contact(email="contact@your-website.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # ✅ SPC API (Statistical Process Control) - 최우선
    path('api/spc/', include('apps.spc.urls')),

    # ERP API
    path('api/erp/', include('apps.erp.urls')),

    # Auth API
    path('api/auth/', include('apps.auth_app.urls')),

    # APS API
    path('api/aps/', include('apps.aps.urls')),
]

# Development: Media & Static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar (optional)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# SPC 앱 URL 통합 가이드

## 📋 개요

SPC 앱의 URL을 메인 Django 프로젝트에 통합하는 방법입니다.

## 🔧 방법 1: 기존 URL 설정에 추가

**파일**: `backend/config/urls.py` (또는 메인 urls.py)

기존 URL 설정 파일에 SPC 앱 URL을 추가합니다:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # 기존 API 엔드포인트들
    path('api/erp/', include('apps.erp.urls')),
    path('api/auth/', include('apps.auth_app.urls')),
    path('api/aps/', include('apps.aps.urls')),

    # ✅ SPC API 추가 (여기 추가!)
    path('api/spc/', include('apps.spc.urls')),
]

# Media files (개발 환경)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

## 🔧 방법 2: 앱 URLs.py가 없는 경우

메인 URL 파일이 없는 경우 새로 생성합니다:

**파일**: `backend/config/urls.py` (새로 생성)

```python
"""
URL Configuration for online-aps-cps-scheduler
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # ERP API
    path('api/erp/', include('apps.erp.urls')),

    # Auth API
    path('api/auth/', include('apps.auth_app.urls')),

    # APS API
    path('api/aps/', include('apps.aps.urls')),

    # ✅ SPC API (품질관리 시스템)
    path('api/spc/', include('apps.spc.urls')),
]

# 개발 환경: Media & Static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Swagger API Documentation (선택사항)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```

## 🔧 방법 3: manage.py에서 설정 확인

**파일**: `backend/manage.py` 확인

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    # 또는
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

settings 모듈 경로를 확인하여 해당 위치에 urls.py를 생성합니다.

## 📡 SPC API 엔드포인트

통합 후 다음 URL로 접근 가능합니다:

### 제품 관리
- `GET/POST /api/spc/products/`
- `GET/PUT/DELETE /api/spc/products/{id}/`
- `GET /api/spc/products/{id}/summary/`

### 검사 계획
- `GET/POST /api/spc/inspection-plans/`
- `GET/PUT/DELETE /api/spc/inspection-plans/{id}/`

### 측정 데이터
- `GET/POST /api/spc/measurements/`
- `GET /api/spc/measurements/chart_data/?product_id={id}&chart_type=XBAR_R`
- `POST /api/spc/measurements/bulk_create/`

### 관리도
- `GET/POST /api/spc/control-charts/`
- `POST /api/spc/control-charts/calculate_limits/`

### 공정능력 분석
- `GET /api/spc/process-capability/`
- `POST /api/spc/process-capability/analyze/`

### Run Rule 위반
- `GET /api/spc/run-rule-violations/`
- `POST /api/spc/run-rule-violations/check/`

### 품질 경고
- `GET /api/spc/alerts/`
- `GET /api/spc/alerts/dashboard/`

### 품질 보고서
- `GET/POST /api/spc/reports/`

## ✅ 통합 확인

다음 명령어로 URL 설정이 올바른지 확인:

```bash
cd backend
python manage.py show_urls
```

또는:

```bash
python manage.py shell
>>> from django.urls import get_resolver
>>> for pattern in get_resolver().url_patterns:
...     print(pattern.pattern)
```

## 🧪 테스트

서버 실행 후 API 접속 확인:

```bash
# 1. 서버 실행
python manage.py runserver 8000

# 2. API 테스트 (별도 터미널)
curl http://localhost:8000/api/spc/products/
curl http://localhost:8000/api/spc/measurements/

# 3. 브라우저 확인
# http://localhost:8000/api/spc/products/
# http://localhost:8000/swagger/  (Swagger가 설정된 경우)
```

## 🚀 Swagger UI 설정 (선택사항)

API 문서 자동 생성을 위해 `drf-yasg`를 설정합니다:

**settings.py**:
```python
INSTALLED_APPS = [
    # ...
    'drf_yasg',
    'rest_framework',
]

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
}
```

그런 다음 http://localhost:8000/swagger/ 에서 모든 API 문서를 확인할 수 있습니다.

---

## 📞 문제 해결

### Q: ModuleNotFoundError: No module named 'config'
**A**: settings 모듈 경로를 확인하세요. `config.settings.dev` 또는 `myproject.settings` 등일 수 있습니다.

### Q: 404 Not Found
**A**:
1. `urlpatterns`에 SPC URL이 추가되었는지 확인
2. `apps.spc.urls` 파일이 존재하는지 확인
3. `python manage.py check`로 설정 확인

### Q: ImportError: cannot import name 'path' from 'django.urls'
**A**: Django 버전 확인. `path`는 Django 2.0+에서 사용 가능합니다.

---

**최종 업데이트**: 2026-01-11

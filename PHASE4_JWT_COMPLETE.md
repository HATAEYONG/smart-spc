# Phase 4: JWT Authentication 완료

## 개요

Phase 4: 아키텍처 현대화 - JWT 인증 시스템 구현 완료

## 구현 완료 기능

### 1. JWT 인증 코어 (`backend/apps/auth_app/jwt_auth.py`)

#### JWTManager 클래스
- **Access Token 발급**: 1시간 유효 (60분)
- **Refresh Token 발급**: 7일 유효
- **토큰 디코딩 및 검증**: HS256 알고리즘 사용
- **Token 갱신**: Refresh Token으로 새 Access Token 발급

```python
# 토큰 만료 시간
ACCESS_TOKEN_LIFETIME = timedelta(minutes=60)
REFRESH_TOKEN_LIFETIME = timedelta(days=7)

# 토큰 생성 예시
access_token = JWTManager.generate_access_token(user_id)
refresh_token = JWTManager.generate_refresh_token(user_id)
```

#### TokenBlacklist 클래스
- **로그아웃된 토큰 관리**: 블랙리스트에 추가하여 재사용 방지
- **토큰 유효성 검증**: 블랙리스트 확인

```python
# 로그아웃 시 토큰 블랙리스트 추가
TokenBlacklist.add_to_blacklist(token)

# 토큰 블랙리스트 확인
is_blacklisted = TokenBlacklist.is_blacklisted(token)
```

#### JWTAuthenticationMiddleware
- Django 미들웨어 형태의 JWT 인증 처리
- Authorization 헤더에서 Bearer 토큰 추출

### 2. BlacklistedToken 모델 (`backend/apps/auth_app/models.py`)

```python
class BlacklistedToken(models.Model):
    token = models.TextField(unique=True)
    jti = models.CharField(max_length=255, unique=True, null=True)  # JWT ID
    user_id = models.IntegerField()
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
```

- **인덱스 최적화**: jti, user_id, expires_at 필드에 인덱스
- **만료 확인**: `is_expired` 프로퍼티

### 3. JWT 인증 API 뷰 (`backend/apps/auth_app/views.py`)

#### LoginView (`POST /api/auth/login/`)
- username/password로 인증
- Access Token + Refresh Token 발급
- UserProfile 활성 상태 확인
- AuditLog 기록

**요청 예시:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**응답 예시:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "profile": {
      "role": "admin",
      "department": "Quality",
      "is_active": true
    }
  }
}
```

#### LogoutView (`POST /api/auth/logout/`)
- Access Token과 Refresh Token을 블랙리스트에 추가
- AuditLog 기록

**요청 예시:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### RefreshView (`POST /api/auth/refresh/`)
- Refresh Token으로 새 Access Token 발급
- 블랙리스트 확인

**요청 예시:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**응답 예시:**
```json
{
  "access_token": "새로운_access_token",
  "refresh_token": "기존_refresh_token",
  "user": {...}
}
```

#### VerifyView (`POST /api/auth/verify/`)
- Access Token 유효성 검증
- 사용자 정보 반환

**요청 예시:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### MeView (`GET /api/auth/me/`)
- 현재 로그인한 사용자 정보 조회
- 인증 필요

### 4. DRF 인증 클래스 (`backend/apps/auth_app/authentication.py`)

#### JWTAuthentication
- Django REST Framework용 JWT 인증 클래스
- Authorization: Bearer <token> 헤더로 인증
- 블랙리스트 확인
- 사용자 활성 상태 확인

#### JWTAuthenticationOptional
- 토큰이 있으면 인증하고, 없으면 익명 사용자로 처리
- 선택적 인증이 필요한 ViewSet에 사용

**사용 예시:**
```python
from rest_framework import viewsets
from apps.auth_app.authentication import JWTAuthentication

class MyViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```

### 5. JWT 시리얼라이저 (`backend/apps/auth_app/serializers.py`)

- **RefreshSerializer**: Refresh Token 요청
- **TokenResponseSerializer**: Token 응답
- **VerifySerializer**: Token 검증 요청

### 6. DRF 설정 업데이트 (`backend/config/settings/dev.py`)

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.auth_app.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Swagger용
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    ...
}
```

### 7. URL 라우팅 (`backend/apps/auth_app/urls.py`)

```
/api/auth/login/       - POST: 로그인 (토큰 발급)
/api/auth/logout/      - POST: 로그아웃 (토큰 블랙리스트)
/api/auth/refresh/     - POST: 토큰 갱신
/api/auth/verify/      - POST: 토큰 검증
/api/auth/me/          - GET: 현재 사용자 정보
```

## 설치된 패키지

```bash
pip install PyJWT==2.10.1
```

## 데이터베이스 마이그레이션

```bash
# 마이그레이션 생성
python manage.py makemigrations auth_app

# 마이그레이션 적용 (PostgreSQL 실행 후)
python manage.py migrate auth_app
```

## 사용 예시

### 1. 로그인 (토큰 발급)

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

### 2. 인증된 요청

```bash
curl -X GET http://localhost:8000/api/spc/products/ \
  -H "Authorization: Bearer <access_token>"
```

### 3. 토큰 갱신

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

### 4. 로그아웃

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

## 프론트엔드 연동 예시

### Axios 인터셉터 설정

```typescript
// src/utils/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// 요청 인터셉터: 토큰 추가
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터: 토큰 갱신
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post('/auth/refresh/', {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', data.access_token);
          error.config.headers.Authorization = `Bearer ${data.access_token}`;
          return axios.request(error.config);
        } catch (refreshError) {
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 로그인 함수

```typescript
// src/services/auth.ts
import api from '../utils/api';

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: any;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/login/', {
    username,
    password,
  });
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
}

export async function logout(): Promise<void> {
  const refreshToken = localStorage.getItem('refresh_token');
  await api.post('/auth/logout/', { refresh_token: refreshToken });
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token');
}
```

## 보안 고려사항

### 1. 토큰 저장
- **Access Token**: 메모리 또는 sessionStorage (짧은 유효기간)
- **Refresh Token**: httpOnly 쿠키 또는 localStorage (보안 강화 필요)

### 2. HTTPS
- 프로덕션에서는 HTTPS 필수 사용
- 토큰 탈취 방지

### 3. 토큰 만료
- Access Token: 1시간 (짧게 설정)
- Refresh Token: 7일

### 4. 블랙리스트 정리
- 주기적으로 만료된 토큰 정리 필요
- Celery task로 자동화 가능

## Swagger API 문서

Swagger UI에서 JWT 인증 테스트:
1. `/swagger/` 접속
2. **Authorize** 버튼 클릭
3. `Bearer <access_token>` 입력
4. 인증이 필요한 엔드포인트 테스트 가능

## 테스트 시나리오

### 1. 정상 로그인 흐름
```
1. POST /api/auth/login/ → 토큰 발급
2. GET /api/auth/me/ → 인증된 사용자 정보 확인
3. POST /api/auth/refresh/ → 새 Access Token 발급
4. POST /api/auth/logout/ → 로그아웃
```

### 2. 만료된 토큰 처리
```
1. Access Token 만료 대기 (60분)
2. 인증된 요청 시도 → 401 Unauthorized
3. POST /api/auth/refresh/ → 새 토큰 발급
4. 재요청 → 성공
```

### 3. 로그아웃된 토큰 처리
```
1. POST /api/auth/logout/ → 토큰 블랙리스트
2. 블랙리스트된 토큰으로 요청 → 401 Unauthorized
```

## 다음 단계: Docker 컨테이너화

Phase 4 다음 작업:
1. **Dockerfile 작성**: Backend, Frontend 각각
2. **docker-compose.yml**: 전체 스택 오케스트레이션
3. **환경 변수 관리**: .env 파일
4. **CI/CD 파이프라인**: GitHub Actions

## 파일 목록

### 생성/수정된 파일
- `backend/apps/auth_app/jwt_auth.py` (JWT 매니저)
- `backend/apps/auth_app/models.py` (BlacklistedToken 모델 추가)
- `backend/apps/auth_app/views.py` (JWT 인증 뷰)
- `backend/apps/auth_app/serializers.py` (JWT 시리얼라이저 추가)
- `backend/apps/auth_app/authentication.py` (DRF 인증 클래스)
- `backend/apps/auth_app/urls.py` (JWT 엔드포인트)
- `backend/config/settings/dev.py` (REST_FRAMEWORK 설정)
- `backend/apps/auth_app/migrations/0002_blacklistedtoken.py` (마이그레이션)

## 참고 자료

- [JWT.io](https://jwt.io/) - JWT 소개
- [PyJWT 문서](https://pyjwt.readthedocs.io/)
- [Django REST Framework Authentication](https://www.django-rest-framework.org/api-guide/authentication/)

---

**완료일시**: 2026-01-11
**상태**: ✅ JWT 인증 시스템 구현 완료

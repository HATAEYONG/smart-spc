# Phase 4: CI/CD 파이프라인 완료

## 개요

Phase 4: 아키텍처 현대화 - CI/CD 파이프라인 구현 완료

GitHub Actions를 활용한 자동화된 CI/CD 파이프라인으로 테스트, 빌드, 배포 자동화

## 구현 완료 기능

### 1. CI (Continuous Integration) - `.github/workflows/ci.yml`

#### 트리거 조건
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

#### 5개 주요 Job

##### 1) Backend Tests Job
- **서비스**: PostgreSQL 15 Alpine, Redis 7 Alpine
- **Python**: 3.11 (pip cache 활용)
- **실행 단계**:
  1. 의존성 설치
  2. Django 시스템 체크 (`manage.py check --deploy`)
  3. 데이터베이스 마이그레이션
  4. pytest 실행 (커버리지 포함)
  5. Codecov 업로드

```yaml
services:
  postgres:
    image: postgres:15-alpine
    env:
      POSTGRES_DB: spc_test_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  redis:
    image: redis:7-alpine
```

##### 2) Frontend Tests Job
- **Node.js**: 18 (npm cache 활용)
- **실행 단계**:
  1. npm ci로 의존성 설치
  2. TypeScript 타입 체크
  3. ESLint 실행
  4. 테스트 실행 (커버리지 포함)
  5. Codecov 업로드

##### 3) Docker Build Test Job
- **의존성**: backend-tests, frontend-tests 성공 후 실행
- **빌드 타겟**:
  - Backend: development, production
  - Frontend: development, production
- **GitHub Actions Cache** 활용 (빌드 속도 향상)

```yaml
- name: Build backend development image
  uses: docker/build-push-action@v4
  with:
    context: ./backend
    file: ./backend/Dockerfile
    target: development
    push: false
    tags: spc-backend:dev
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

##### 4) Code Quality Job
- **도구**: flake8, black, isort, pydocstyle
- **검사 항목**:
  - flake8: 문법 오류, 복잡도, 라인 길이
  - black: 코드 포맷팅
  - isort: import 정렬
  - pydocstyle: 독스트링 스타일

##### 5) Security Scan Job
- **도구**: Trivy (취약점 스캐너)
- **권한**: contents: read, security-events: write
- **기능**:
  - Backend 스캔 (SARIF 형식)
  - Frontend 스캔 (SARIF 형식)
  - GitHub Security 탭에 결과 업로드

```yaml
- name: Run Trivy vulnerability scanner (Backend)
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: './backend'
    format: 'sarif'
    output: 'backend-trivy-results.sarif'
```

### 2. CD (Continuous Deployment) - `.github/workflows/cd.yml`

#### 트리거 조건
```yaml
on:
  push:
    branches: [ main ]
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        type: choice
        options: [staging, production]
```

#### 5개 주요 Job

##### 1) Build and Push Job
- **환경**: GitHub Container Registry (ghcr.io)
- **매트릭스**: backend, frontend
- **기능**:
  - Docker 이미지 빌드 (production 타겟)
  - 태그 생성 (branch, tag, semver, sha)
  - 컨테이너 레지스트리에 푸시

```yaml
tags: |
  type=ref,event=branch
  type=ref,event=pr
  type=semver,pattern={{version}}
  type=semver,pattern={{major}}.{{minor}}
  type=sha,prefix={{branch}}-
```

##### 2) Deploy to Staging Job
- **조건**: main 브랜치 푸시 또는 workflow_dispatch
- **Environment**: staging (https://staging.spc.example.com)
- **배포 단계**:
  1. SSH로 서버 접속
  2. git pull로 최신 코드 가져오기
  3. docker-compose pull로 이미지 가져오기
  4. docker-compose up -d로 컨테이너 시작
  5. 마이그레이션 실행
  6. 정적 파일 수집
  7. 사용하지 않는 Docker 리소스 정리

```bash
cd /opt/spc-scheduler
git pull origin main
docker-compose pull
docker-compose up -d
docker-compose exec -T backend python manage.py migrate --noinput
docker-compose exec -T backend python manage.py collectstatic --noinput
docker system prune -af
```

##### 3) Deploy to Production Job
- **조건**: workflow_dispatch로 production 선택 시
- **Environment**: production (https://spc.example.com)
- **배포 전 백업**:
  - PostgreSQL 덤프
  - Media 파일 압축

```bash
BACKUP_DIR="/backups/spc-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR
docker-compose exec -T db pg_dump -U postgres spc_db > $BACKUP_DIR/db_backup.sql
tar -czf $BACKUP_DIR/media_backup.tar.gz ./backend/media/
```

##### 4) Health Check Job
- **실행 조건**: 배포 성공 후 항상 실행
- **체크 항목**:
  - Backend health (/api/health/)
  - Frontend health (/)
  - Database connection (/api/health/db/)
  - Redis connection (/api/health/redis/)

```bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${{ secrets.STAGING_URL }}/api/health/)
if [ $RESPONSE -eq 200 ]; then
  echo "Backend is healthy"
else
  exit 1
fi
```

##### 5) Rollback Job
- **실행 조건**: health-check 실패 시
- **기능**:
  - 이전 커밋으로 체크아웃
  - 이전 버전으로 재배포
  - Slack 알림

```bash
git checkout ${{ github.event.before }}
docker-compose -f docker-compose.yml --profile production up -d
```

### 3. Slack 알림 통합

#### 알림 시나리오
1. **배포 시작**: Production deployment started!
2. **Health Check 성공**: Deployment health check passed! All systems operational.
3. **Health Check 실패**: Deployment health check failed! Please investigate immediately.
4. **롤백**: Deployment failed and rolled back to previous version!

### 4. GitHub Secrets 설정

#### 필수 Secrets

| Secret | 설명 | 예시 |
|--------|------|------|
| `STAGING_HOST` | 스테이징 서버 호스트 | staging.example.com |
| `STAGING_USER` | 스테이징 SSH 사용자 | deploy |
| `STAGING_SSH_KEY` | 스테이징 SSH 개인키 | -----BEGIN RSA... |
| `PRODUCTION_HOST` | 프로덕션 서버 호스트 | production.example.com |
| `PRODUCTION_USER` | 프로덕션 SSH 사용자 | deploy |
| `PRODUCTION_SSH_KEY` | 프로덕션 SSH 개인키 | -----BEGIN RSA... |
| `STAGING_URL` | 스테이징 URL | https://staging.spc.example.com |
| `SLACK_WEBHOOK` | Slack Webhook URL | https://hooks.slack.com/... |

#### Secrets 설정 방법
1. GitHub Repository → Settings → Secrets and variables → Actions
2. "New repository secret" 클릭
3. Name과 Value 입력 후 "Add secret"

### 5. GitHub Environments

#### Staging Environment
- **Name**: staging
- **URL**: https://staging.spc.example.com
- **Protection Rules**: 없음

#### Production Environment
- **Name**: production
- **URL**: https://spc.example.com
- **Protection Rules**:
  - Required reviewers: 1명 이상
  - Wait timer: 0분
  - Deployment branches: main만 허용

## 사용 방법

### 1. 자동화된 CI 실행

```bash
# main 또는 develop 브랜치에 푸시
git push origin main

# Pull Request 생성
git checkout -b feature/new-feature
git push origin feature/new-feature
# GitHub에서 PR 생성
```

### 2. 수동 배포 (Workflow Dispatch)

#### Staging 배포
1. GitHub Repository → Actions → CD - Continuous Deployment
2. "Run workflow" 클릭
3. Branch: main 선택
4. Environment: staging 선택
5. "Run workflow" 클릭

#### Production 배포
1. GitHub Repository → Actions → CD - Continuous Deployment
2. "Run workflow" 클릭
3. Branch: main 선택
4. Environment: production 선택
5. "Run workflow" 클릭

### 3. 태그 기반 배포

```bash
# 버전 태그 생성 및 푸시
git tag v1.0.0
git push origin v1.0.0

# 자동으로 CD 파이프라인 실행됨
```

### 4. CI 결과 확인

#### Actions 탭에서 확인
1. GitHub Repository → Actions
2. 최근 workflow 실행 현황
3. 각 Job의 로그, 아티팩트 확인

#### Codecov 대시보드
- URL: https://codecov.io/github/[username]/[repo]
- 백엔드/프론트엔드 커버리지 확인

#### Security 탭
- GitHub Repository → Security
- Trivy 스캔 결과 확인
- 취약점별 심각도 확인

## 파이프라인 최적화

### 1. 캐싱 전략

#### Python pip Cache
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'
    cache-dependency-path: backend/requirements.txt
```

#### npm Cache
```yaml
- name: Set up Node.js
  uses: actions/setup-node@v3
  with:
    node-version: '18'
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json
```

#### Docker Layer Cache
```yaml
- name: Build and push
  uses: docker/build-push-action@v4
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### 2. 병렬 실행

```yaml
# backend-tests, frontend-tests, code-quality, security-scan 병렬 실행
# 각 Job이 독립적으로 실행되어 전체 시간 단축
```

### 3. 의존성 관리

```yaml
needs: [backend-tests, frontend-tests]

# docker-build는 backend-tests와 frontend-tests 성공 후 실행
# build-and-push는 docker-build 성공 후 실행
```

## 모니터링 및 알림

### 1. Workflow 상태 배지

#### README.md에 추가
```markdown
![CI](https://github.com/username/spc-scheduler/workflows/CI%20-%20Continuous%20Integration/badge.svg)
![CD](https://github.com/username/spc-scheduler/workflows/CD%20-%20Continuous%20Deployment/badge.svg)
```

### 2. Slack 알림 설정

#### Slack App 생성
1. https://api.slack.com/apps → "Create New App"
2. "Incoming Webhooks" 활성화
3. Webhook URL 복사
4. GitHub Secret `SLACK_WEBHOOK`에 등록

### 3. Health Check 대시보드

#### Uptime Monitoring (선택사항)
- UptimeRobot
- Pingdom
- StatusCake

## 문제 해결

### 1. CI 실패: PostgreSQL 연결 오류
```yaml
# health-cmd 확인
--health-cmd pg_isready
--health-interval 10s
--health-timeout 5s
--health-retries 5
```

### 2. Docker 빌드 실패
```bash
# 로컬에서 빌드 테스트
cd backend
docker build --target production -t test .
```

### 3. 배포 실패: SSH 연결 오류
- SSH 키가 올바른지 확인
- 서버 방화벽에서 GitHub IP 허용
- SSH 키 권한 확인 (chmod 600)

### 4. Health Check 실패
```bash
# 직접 health endpoint 확인
curl https://staging.spc.example.com/api/health/
```

## 모범 사례

### 1. GitFlow 전략
- **main**: 프로덕션 배포 가능
- **develop**: 개발 통합 브랜치
- **feature/***: 기능 개발 브랜치
- **hotfix/***: 긴급 수정 브랜치

### 2. 커밋 메시지 컨벤션
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 리팩토링
test: 테스트 추가
chore: 빌드/설정 변경
```

### 3. Semantic Versioning
- **MAJOR.MINOR.PATCH** (예: 1.2.3)
- MAJOR: 호환되지 않는 변경
- MINOR: 새로운 기능 (호환성 유지)
- PATCH: 버그 수정

### 4. Code Review 프로세스
1. Feature 브랜치에서 개발
2. Pull Request 생성
3. CI 통과 확인
4. Code Review 승인
5. develop 브랜치에 머지
6. main 브랜치로 cherry-pick (필요 시)

## 확장 가능성

### 1. Blue-Green Deployment
```yaml
deploy-blue:
  # Blue 환경 배포

deploy-green:
  # Green 환경 배포

switch-traffic:
  # 트래픽 전환
```

### 2. Canary Deployment
```yaml
deploy-canary:
  # 10% 트래픽을 새 버전으로

monitor-canary:
  # 모니터링

deploy-full:
  # 전체 트래픽 전환
```

### 3. A/B Testing
```yaml
deploy-variant-a:
  # A 버전 배포

deploy-variant-b:
  # B 버전 배포
```

## 보안 강화

### 1. Secrets 관리
- GitHub Secrets 사용 (환경 변수, API 키)
- .gitignore에 .env 파일 추가
- 주기적으로 키 로테이션

### 2. Dependabot 설정
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
```

### 3. Branch Protection
```yaml
# Settings → Branches → Add rule
- Pattern: main
- Require pull request reviews: 1
- Require status checks to pass: CI
- Do not allow bypassing
```

## 파일 목록

### 생성/수정된 파일
- `.github/workflows/ci.yml` (CI 파이프라인)
- `.github/workflows/cd.yml` (CD 파이프라인)

## 참고 자료

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Codecov Documentation](https://docs.codecov.com/)
- [Trivy Scanner](https://aquasecurity.github.io/trivy/)
- [Slack API](https://api.slack.com/)

---

**완료일시**: 2026-01-11
**상태**: ✅ CI/CD 파이프라인 구현 완료

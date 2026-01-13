# AWS Lightsail 배포 가이드

**생성일**: 2026-01-10
**시스템**: Online APS-CPS Scheduler v2.0
**배포 방식**: AWS Lightsail + SQLite

---

## 📦 배포 패키지 구성

### 포함된 파일
```
deployment_package/
├── backend/                 # Django 백엔드
│   ├── apps/               # 앱 모듈
│   ├── config/             # Django 설정
│   ├── requirements.txt    # Python 패키지
│   ├── manage.py           # Django 관리 명령
│   └── db.sqlite3          # 데이터베이스 (마이그레이션 완료)
├── frontend/dist/          # React 빌드 결과물
├── deploy/                 # 배포 스크립트
├── docs/                   # 문서
└── .env.production         # 프로덕션 환경 변수
```

---

## 🚀 1단계: AWS Lightsail 인스턴스 생성

### 1.1 인스턴스 사양
- **OS**: Ubuntu 22.04 LTS
- **플랜**: 최소 2GB RAM 이상 권장
- **스토리지**: 최소 40GB
- **리전**: Seoul (ap-northeast-2) 권장

### 1.2 인스턴스 생성
1. AWS Lightsail 콘솔 접속
2. "Create instance" 클릭
3. Linux/Unix 플랫폼 선택
4. Ubuntu 22.04 LTS 선택
5. 적절한 플랜 선택
6. 인스턴스 이름 입력 (예: aps-cps-scheduler)
7. "Create instance" 클릭

### 1.3 고정 IP 설정
1. 인스턴스 생성 후 "Networking" 탭
2. "Create static IP" 클릭
3. 인스턴스에 연결
4. **고정 IP 주소를 기록** (예: 52.79.123.45)

---

## 🔧 2단계: 서버 초기 설정

### 2.1 SSH 접속
```bash
# SSH 키 다운로드 (Lightsail 콘솔에서)
chmod 400 LightsailDefaultKey-ap-northeast-2.pem

# SSH 접속
ssh -i LightsailDefaultKey-ap-northeast-2.pem ubuntu@YOUR_IP_ADDRESS
```

### 2.2 시스템 업데이트
```bash
sudo apt update && sudo apt upgrade -y
```

### 2.3 필수 패키지 설치
```bash
# Python 및 도구
sudo apt install -y python3.10 python3.10-venv python3-pip

# Nginx 설치
sudo apt install -y nginx

# 기타 도구
sudo apt install -y ufw certbot python3-certbot-nginx
```

---

## 📂 3단계: 파일 업로드

### 3.1 배포 패키지 압축 (Windows에서)
Git Bash 또는 WSL 사용:
```bash
cd /c/Claude
tar -czf aps-deployment.tar.gz online-aps-cps-scheduler/
```

### 3.2 서버로 파일 전송
```bash
# SCP를 사용한 파일 전송
scp -i LightsailDefaultKey-ap-northeast-2.pem aps-deployment.tar.gz ubuntu@YOUR_IP:/home/ubuntu/
```

### 3.3 서버에서 압축 해제
```bash
cd /home/ubuntu
tar -xzf aps-deployment.tar.gz
cd online-aps-cps-scheduler
```

---

## ⚙️ 4단계: 환경 설정

### 4.1 백엔드 환경 변수 설정
```bash
cd /home/ubuntu/online-aps-cps-scheduler/backend

# SECRET_KEY 생성
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# .env 파일 생성 (vi 또는 nano 사용)
nano .env
```

.env 파일 내용:
```env
# Django Settings
SECRET_KEY=생성된_SECRET_KEY_여기에_입력
DEBUG=False
ALLOWED_HOSTS=YOUR_IP_ADDRESS

# CORS
CORS_ALLOWED_ORIGINS=http://YOUR_IP_ADDRESS

# Security
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Static/Media Files
STATIC_ROOT=/var/www/aps/backend/staticfiles
MEDIA_ROOT=/var/www/aps/backend/media
```

### 4.2 Python 가상환경 설정
```bash
cd /home/ubuntu/online-aps-cps-scheduler/backend

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 4.3 Django Static 파일 수집
```bash
source venv/bin/activate

# static 디렉토리 생성
sudo mkdir -p /var/www/aps/backend/staticfiles
sudo mkdir -p /var/www/aps/backend/media
sudo chown -R ubuntu:www-data /var/www/aps/

# static 파일 수집
python manage.py collectstatic --noinput
```

---

## 🌐 5단계: Nginx 설정

### 5.1 Nginx 설정 파일 생성
```bash
sudo nano /etc/nginx/sites-available/aps
```

설정 내용:
```nginx
server {
    listen 80;
    server_name YOUR_IP_ADDRESS;

    client_max_body_size 50M;

    # Frontend (React)
    location / {
        root /home/ubuntu/online-aps-cps-scheduler/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /static/ {
        alias /var/www/aps/backend/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /var/www/aps/backend/media/;
    }
}
```

### 5.2 Nginx 활성화
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/aps /etc/nginx/sites-enabled/

# 기본 사이트 비활성화
sudo rm /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 🔄 6단계: Gunicorn 서비스 설정

### 6.1 Gunicorn 서비스 파일 생성
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

서비스 내용:
```ini
[Unit]
Description=Gunicorn daemon for APS-CPS Scheduler
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/online-aps-cps-scheduler/backend
EnvironmentFile=/home/ubuntu/online-aps-cps-scheduler/backend/.env
ExecStart=/home/ubuntu/online-aps-cps-scheduler/backend/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 6.2 서비스 시작
```bash
# 서비스 재로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start gunicorn

# 부팅 시 자동 시작
sudo systemctl enable gunicorn

# 상태 확인
sudo systemctl status gunicorn
```

---

## 🔒 7단계: 방화벽 설정

### 7.1 UFW 방화벽 설정
```bash
# UFW 활성화
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# 상태 확인
sudo ufw status
```

### 7.2 Lightsail 방화벽 설정
1. Lightsail 콘솔에서 인스턴스 선택
2. "Networking" 탭 클릭
3. "IPv4 Firewall" 섹션:
   - SSH (TCP 22) - 이미 열려있음
   - HTTP (TCP 80) - 추가
   - HTTPS (TCP 443) - 추가

---

## ✅ 8단계: 배포 검증

### 8.1 서비스 상태 확인
```bash
# Gunicorn 상태
sudo systemctl status gunicorn

# Nginx 상태
sudo systemctl status nginx

# 로그 확인
sudo journalctl -u gunicorn -n 50
```

### 8.2 웹 브라우저 테스트
1. **프론트엔드**: http://YOUR_IP_ADDRESS/
2. **API**: http://YOUR_IP_ADDRESS/api/aps/
3. **Admin**: http://YOUR_IP_ADDRESS/admin/

### 8.3 기능 테스트 체크리스트
- [ ] 프론트엔드 로딩
- [ ] AI LLM 메뉴 샘플 데이터 표시
- [ ] API 응답 확인
- [ ] Admin 페이지 접속

---

## 🔐 9단계: SSL 설정 (도메인 연결 후)

도메인을 연결한 후에만 실행:

```bash
# Certbot으로 SSL 인증서 자동 설치
sudo certbot --nginx -d yourdomain.com

# .env 파일 업데이트
nano /home/ubuntu/online-aps-cps-scheduler/backend/.env

# 다음 항목 수정
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Gunicorn 재시작
sudo systemctl restart gunicorn
```

---

## 🔄 10단계: 유지보수

### 코드 업데이트
```bash
# 새 파일 업로드 후
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

### 백업
```bash
# 데이터베이스 백업
cp /home/ubuntu/online-aps-cps-scheduler/backend/db.sqlite3 \
   ~/backups/db.sqlite3.$(date +%Y%m%d)
```

### 로그 확인
```bash
# Nginx 로그
sudo tail -f /var/log/nginx/error.log

# Gunicorn 로그
sudo journalctl -u gunicorn -f
```

---

## 🆘 문제 해결

### 502 Bad Gateway
```bash
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

### Static 파일 오류
```bash
cd /home/ubuntu/online-aps-cps-scheduler/backend
source venv/bin/activate
python manage.py collectstatic --noinput
sudo chown -R ubuntu:www-data /var/www/aps/
```

---

## 📋 배포 완료 체크리스트

- [ ] Lightsail 인스턴스 생성 완료
- [ ] 고정 IP 할당 완료
- [ ] 필수 패키지 설치 완료
- [ ] 파일 업로드 및 압축 해제 완료
- [ ] 환경 변수 설정 완료
- [ ] Python 가상환경 설정 완료
- [ ] Django static 파일 수집 완료
- [ ] Nginx 설정 완료
- [ ] Gunicorn 서비스 시작 완료
- [ ] 방화벽 설정 완료
- [ ] 웹 브라우저 테스트 완료
- [ ] 기능 동작 확인 완료

---

**배포 예상 시간**: 60-90분
**난이도**: 중급

**작성자**: Claude AI Assistant
**작성일**: 2026-01-10

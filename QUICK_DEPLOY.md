# 빠른 배포 가이드 (Quick Deploy)

## 🚀 5분 배포 요약

### 사전 준비 (Windows PC)
1. Git Bash 또는 WSL 설치
2. SSH 클라이언트 준비

### 1단계: 배포 패키지 생성 (5분)
```bash
# Git Bash에서 실행
cd /c/Claude
tar -czf aps-deployment.tar.gz online-aps-cps-scheduler/
```

### 2단계: AWS Lightsail 설정 (10분)
1. Lightsail 콘솔에서 Ubuntu 22.04 인스턴스 생성
2. 고정 IP 할당
3. SSH 키 다운로드
4. 방화벽에서 HTTP(80), HTTPS(443) 포트 열기

### 3단계: 파일 업로드 (5분)
```bash
# YOUR_IP를 실제 IP로 변경
scp -i LightsailDefaultKey.pem aps-deployment.tar.gz ubuntu@YOUR_IP:/home/ubuntu/
```

### 4단계: 서버 설정 및 배포 (30분)
```bash
# SSH 접속
ssh -i LightsailDefaultKey.pem ubuntu@YOUR_IP

# 패키지 설치
sudo apt update && sudo apt install -y python3.10 python3.10-venv python3-pip nginx ufw

# 파일 압축 해제
cd /home/ubuntu
tar -xzf aps-deployment.tar.gz
cd online-aps-cps-scheduler/backend

# SECRET_KEY 생성
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# .env 파일 생성 (위에서 생성한 키 입력)
nano .env
```

.env 내용:
```
SECRET_KEY=생성된키입력
DEBUG=False
ALLOWED_HOSTS=YOUR_IP
CORS_ALLOWED_ORIGINS=http://YOUR_IP
STATIC_ROOT=/var/www/aps/backend/staticfiles
```

계속:
```bash
# Python 설정
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Static 파일 설정
sudo mkdir -p /var/www/aps/backend/staticfiles
sudo chown -R ubuntu:www-data /var/www/aps/
python manage.py collectstatic --noinput

# Gunicorn 서비스 생성
sudo nano /etc/systemd/system/gunicorn.service
```

gunicorn.service 내용:
```ini
[Unit]
Description=Gunicorn
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/online-aps-cps-scheduler/backend
EnvironmentFile=/home/ubuntu/online-aps-cps-scheduler/backend/.env
ExecStart=/home/ubuntu/online-aps-cps-scheduler/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Nginx 설정
sudo nano /etc/nginx/sites-available/aps
```

Nginx 설정:
```nginx
server {
    listen 80;
    server_name YOUR_IP;
    
    location / {
        root /home/ubuntu/online-aps-cps-scheduler/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
    
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
    
    location /static/ {
        alias /var/www/aps/backend/staticfiles/;
    }
}
```

```bash
# 서비스 시작
sudo ln -s /etc/nginx/sites-available/aps /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# 방화벽
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

### 5단계: 접속 테스트
브라우저에서 `http://YOUR_IP` 접속

---

## 완료! 🎉

이제 다음 주소에서 접속 가능합니다:
- **프론트엔드**: http://YOUR_IP/
- **API**: http://YOUR_IP/api/aps/
- **Admin**: http://YOUR_IP/admin/

---

## 문제 발생 시
```bash
# 로그 확인
sudo journalctl -u gunicorn -n 50
sudo tail -f /var/log/nginx/error.log

# 서비스 재시작
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

**예상 소요 시간**: 50-60분
**난이도**: 중급

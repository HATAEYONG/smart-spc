# AWS Lightsail 배포 단계별 가이드

**작성일**: 2026-01-10
**목적**: AWS Lightsail 테스트 배포

---

## ✅ 사전 준비 완료 항목

- [x] 프론트엔드 빌드 완료 (frontend/dist/)
- [x] 백엔드 마이그레이션 완료 (db.sqlite3)
- [x] SECRET_KEY 생성 완료
- [x] 환경 파일 생성 (backend/.env)
- [x] 배포 문서 작성 완료

---

## 📋 Step 1: 로컬 PC에서 배포 패키지 생성

### Windows에서 실행 (Git Bash 필요)

```bash
# Git Bash 열기 (또는 WSL)

# 1. 프로젝트 디렉토리로 이동
cd /c/Claude

# 2. 배포 패키지 압축 (약 2-3분 소요)
tar -czf aps-deployment.tar.gz online-aps-cps-scheduler/

# 3. 파일 크기 확인
ls -lh aps-deployment.tar.gz
```

**예상 크기**: 약 50-100MB

### ⚠️ 주의사항
- `node_modules`와 `venv`는 자동으로 포함됩니다
- 서버에서 다시 설치하므로 문제없습니다
- 압축 시간: 약 2-3분

---

## 📋 Step 2: AWS Lightsail 인스턴스 생성

### 2-1. AWS 콘솔 접속
1. https://lightsail.aws.amazon.com/ 접속
2. AWS 계정으로 로그인

### 2-2. 인스턴스 생성
1. **"Create instance"** 버튼 클릭
2. **인스턴스 위치**: Seoul, Zone A (ap-northeast-2a)
3. **플랫폼 선택**: Linux/Unix
4. **Blueprint 선택**: OS Only → Ubuntu 22.04 LTS
5. **인스턴스 플랜 선택**:
   - **권장**: $10/month (2GB RAM, 1 Core, 60GB SSD)
   - **최소**: $5/month (512MB RAM) - 테스트용
   - **운영**: $20/month (4GB RAM) - 권장

### 2-3. 인스턴스 설정
- **인스턴스 이름**: `aps-scheduler` (또는 원하는 이름)
- **태그**: 선택사항
- **SSH 키**: Lightsail 기본 키 사용

### 2-4. Create instance 클릭
- 생성 시간: 약 2-3분

---

## 📋 Step 3: 고정 IP 할당

### 3-1. 고정 IP 생성
1. 생성된 인스턴스 클릭
2. **Networking** 탭 클릭
3. **"Create static IP"** 클릭
4. 인스턴스 선택 (방금 만든 인스턴스)
5. 이름 입력: `aps-scheduler-ip`
6. **Create** 클릭

### 3-2. IP 주소 기록
```
고정 IP: _____________________ (예: 13.124.xxx.xxx)
```

### 3-3. 방화벽 설정
**Networking** 탭에서 IPv4 Firewall 확인:
- ✅ SSH (TCP 22) - 기본 활성화
- ✅ HTTP (TCP 80) - **추가 필요**
- ✅ HTTPS (TCP 443) - **추가 필요**

**방화벽 규칙 추가**:
1. **"+ Add rule"** 클릭
2. Application: HTTP
3. **Save** 클릭
4. 다시 **"+ Add rule"** 클릭
5. Application: HTTPS
6. **Save** 클릭

---

## 📋 Step 4: SSH 키 다운로드

### 4-1. SSH 키 다운로드
1. Lightsail 메인 페이지에서 **Account** 메뉴
2. **SSH keys** 탭
3. Seoul 리전의 **Default key** 다운로드
4. 파일명: `LightsailDefaultKey-ap-northeast-2.pem`
5. 저장 위치: `C:\Users\사용자명\Downloads\`

### 4-2. 키 파일 권한 설정 (Git Bash에서)
```bash
# 다운로드 폴더로 이동
cd ~/Downloads

# 권한 설정
chmod 400 LightsailDefaultKey-ap-northeast-2.pem
```

---

## 📋 Step 5: 파일 업로드

### 5-1. SCP로 파일 전송 (Git Bash)
```bash
# 압축 파일이 있는 디렉토리로 이동
cd /c/Claude

# 파일 전송 (YOUR_IP를 실제 IP로 변경)
scp -i ~/Downloads/LightsailDefaultKey-ap-northeast-2.pem \
    aps-deployment.tar.gz \
    ubuntu@YOUR_IP:/home/ubuntu/
```

**예시**:
```bash
scp -i ~/Downloads/LightsailDefaultKey-ap-northeast-2.pem \
    aps-deployment.tar.gz \
    ubuntu@13.124.123.45:/home/ubuntu/
```

**전송 시간**: 파일 크기에 따라 3-10분 (인터넷 속도에 따름)

---

## 📋 Step 6: SSH 접속

### 6-1. SSH 접속 (Git Bash)
```bash
ssh -i ~/Downloads/LightsailDefaultKey-ap-northeast-2.pem ubuntu@YOUR_IP
```

### 6-2. 접속 확인
성공 시 다음과 같은 화면:
```
Welcome to Ubuntu 22.04 LTS
...
ubuntu@ip-xxx-xxx-xxx-xxx:~$
```

---

## 📋 Step 7: 서버 초기 설정

### 7-1. 시스템 업데이트
```bash
sudo apt update && sudo apt upgrade -y
```
**소요 시간**: 3-5분

### 7-2. 필수 패키지 설치
```bash
sudo apt install -y python3.10 python3.10-venv python3-pip \
    nginx ufw git
```
**소요 시간**: 2-3분

---

## 📋 Step 8: 애플리케이션 설치

### 8-1. 압축 해제
```bash
cd /home/ubuntu
tar -xzf aps-deployment.tar.gz
cd online-aps-cps-scheduler
```

### 8-2. SECRET_KEY 생성
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
**생성된 키를 복사해두세요!**

### 8-3. .env 파일 생성
```bash
cd backend
nano .env
```

**다음 내용 입력** (YOUR_IP와 SECRET_KEY 변경):
```env
SECRET_KEY=여기에_위에서_생성한_키_붙여넣기
DEBUG=False
ALLOWED_HOSTS=YOUR_IP
CORS_ALLOWED_ORIGINS=http://YOUR_IP
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
STATIC_ROOT=/var/www/aps/backend/staticfiles
MEDIA_ROOT=/var/www/aps/backend/media
```

저장: `Ctrl+O`, Enter, `Ctrl+X`

### 8-4. Python 가상환경 설정
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```
**소요 시간**: 5-10분

### 8-5. Static 파일 수집
```bash
sudo mkdir -p /var/www/aps/backend/staticfiles
sudo mkdir -p /var/www/aps/backend/media
sudo chown -R ubuntu:www-data /var/www/aps/
python manage.py collectstatic --noinput
```

---

## 📋 Step 9: Gunicorn 서비스 설정

### 9-1. 서비스 파일 생성
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

**다음 내용 입력**:
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

저장: `Ctrl+O`, Enter, `Ctrl+X`

### 9-2. 서비스 시작
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

**확인**: "active (running)" 표시되어야 함

---

## 📋 Step 10: Nginx 설정

### 10-1. Nginx 설정 파일 생성
```bash
sudo nano /etc/nginx/sites-available/aps
```

**다음 내용 입력** (YOUR_IP 변경):
```nginx
server {
    listen 80;
    server_name YOUR_IP;

    client_max_body_size 50M;

    location / {
        root /home/ubuntu/online-aps-cps-scheduler/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/aps/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/aps/backend/media/;
    }
}
```

저장: `Ctrl+O`, Enter, `Ctrl+X`

### 10-2. Nginx 활성화
```bash
sudo ln -s /etc/nginx/sites-available/aps /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📋 Step 11: 방화벽 설정

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

---

## 📋 Step 12: 배포 검증

### 12-1. 서비스 상태 확인
```bash
# Gunicorn 상태
sudo systemctl status gunicorn

# Nginx 상태
sudo systemctl status nginx
```

### 12-2. 로그 확인
```bash
# Gunicorn 로그
sudo journalctl -u gunicorn -n 50

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log
```

### 12-3. 브라우저 테스트
1. **프론트엔드**: http://YOUR_IP/
2. **API**: http://YOUR_IP/api/aps/
3. **Admin**: http://YOUR_IP/admin/

---

## 🎯 배포 완료 체크리스트

- [ ] AWS Lightsail 인스턴스 생성
- [ ] 고정 IP 할당
- [ ] 방화벽 설정 (HTTP, HTTPS)
- [ ] SSH 키 다운로드
- [ ] 배포 패키지 업로드
- [ ] 시스템 패키지 설치
- [ ] .env 파일 생성
- [ ] Python 가상환경 설정
- [ ] Static 파일 수집
- [ ] Gunicorn 서비스 시작
- [ ] Nginx 설정 및 시작
- [ ] UFW 방화벽 설정
- [ ] 브라우저 접속 테스트

---

## 🆘 문제 해결

### 502 Bad Gateway
```bash
sudo systemctl restart gunicorn
sudo journalctl -u gunicorn -n 50
```

### Static 파일 404
```bash
cd /home/ubuntu/online-aps-cps-scheduler/backend
source venv/bin/activate
python manage.py collectstatic --noinput
```

### Permission 오류
```bash
sudo chown -R ubuntu:www-data /var/www/aps/
sudo chmod -R 755 /var/www/aps/
```

---

## 📊 예상 소요 시간

- **Step 1-2**: 10분 (패키지 생성, 인스턴스 생성)
- **Step 3-4**: 5분 (IP 할당, SSH 키)
- **Step 5-6**: 10분 (파일 업로드, 접속)
- **Step 7**: 8분 (시스템 업데이트, 패키지 설치)
- **Step 8**: 15분 (앱 설치, Python 설정)
- **Step 9-11**: 10분 (서비스 설정)
- **Step 12**: 5분 (검증)

**총 예상 시간**: 약 60분

---

**다음 단계 준비**: 이 가이드를 열어두고 Step 1부터 차근차근 진행하세요!

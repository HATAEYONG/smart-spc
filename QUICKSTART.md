# 빠른 시작 가이드 (프론트엔드만)

백엔드 없이 프론트엔드만 실행하여 화면을 확인할 수 있습니다.

## 1. Node.js 설치 확인

먼저 Node.js가 설치되어 있는지 확인하세요:

```bash
node --version
npm --version
```

설치되어 있지 않다면 https://nodejs.org 에서 다운로드하세요.

## 2. 프론트엔드 실행

```bash
# 프론트엔드 폴더로 이동
cd frontend

# 의존성 설치 (처음 한 번만)
npm install

# 개발 서버 실행
npm run dev
```

## 3. 브라우저에서 확인

브라우저에서 다음 주소로 접속하세요:
```
http://localhost:3000
```

## 현재 설정

- **Mock Mode**: 현재 Mock 데이터를 사용하도록 설정되어 있습니다
- **백엔드 불필요**: API 서버 없이도 화면을 확인할 수 있습니다
- **실제 데이터 연결**: 백엔드를 실행한 후 `src/config.ts` 파일에서 `useMockApi: false`로 변경하면 됩니다

## 페이지 목록

1. **Dashboard** (/) - KPI 카드와 차트, 최근 결정 내역
2. **Plans** (/plans) - 간트 차트 형태의 생산 계획
3. **Events** (/events) - 이벤트 생성 및 결정 로그
4. **Simulation** (/simulation) - CPS 시뮬레이션 결과
5. **Graph** (/graph) - 의존성 그래프 통계

## 문제 해결

### 포트가 이미 사용 중인 경우

다른 포트를 사용하려면:
```bash
npm run dev -- --port 3001
```

### 의존성 설치 오류

캐시를 삭제하고 다시 설치:
```bash
rm -rf node_modules package-lock.json
npm install
```

## 전체 시스템 실행 (선택사항)

전체 시스템(백엔드 + 워커 + 프론트엔드)을 실행하려면:

1. Docker Desktop 설치
2. 프로젝트 루트에서 실행:
   ```bash
   docker-compose up -d
   ```

자세한 내용은 README.md를 참조하세요.

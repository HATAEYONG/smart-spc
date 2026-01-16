# 다음 단계 및 특별 기능 설계
# Next Steps and Special Features Design

## 📋 목차
1. [다음 단계 로드맵](#다음-단계-로드맵)
2. [특별 기능 설계](#특별-기능-설계)
3. [기술 아키텍처](#기술-아키텍처)
4. [구현 우선순위](#구현-우선순위)

---

## 🎯 다음 단계 로드맵

### Phase 1: Django 백엔드 완성 (2-3주)

#### 1.1 Django 앱 설정 및 마이그레이션
```python
# backend/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 추가할 앱들
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # 커스텀 앱들
    'quality_issues',
    'equipment',
    'tools',
    'work_orders',
    'integration',
    'production',
    'users',
]
```

**실행 순서:**
```bash
cd backend

# 1. 마이그레이션 파일 생성
python manage.py makemigrations

# 2. 각 앱별 마이그레이션
python manage.py makemigrations quality_issues
python manage.py makemigrations equipment
python manage.py makemigrations tools
python manage.py makemigrations work_orders
python manage.py makemigrations integration

# 3. 마이그레이션 적용
python manage.py migrate

# 4. 슈퍼유저 생성
python manage.py createsuperuser

# 5. 서버 실행 테스트
python manage.py runserver
```

#### 1.2 REST API 엔드포인트 구현

**API 구조:**
```
/api/v1/
├── /quality-issues/
│   ├── GET    /api/v1/quality-issues/          # 목록 조회
│   ├── POST   /api/v1/quality-issues/          # 생성
│   ├── GET    /api/v1/quality-issues/{id}/     # 상세 조회
│   ├── PUT    /api/v1/quality-issues/{id}/     # 수정
│   ├── DELETE /api/v1/quality-issues/{id}/     # 삭제
│   ├── GET    /api/v1/quality-issues/{id}/4m/  # 4M 분석 조회
│   └── GET    /api/v1/quality-issues/{id}/steps/ # 8단계 조회
├── /equipment/
│   ├── GET    /api/v1/equipment/               # 설비 목록
│   ├── GET    /api/v1/equipment/{id}/health/   # 건강 점수
│   └── GET    /api/v1/equipment/{id}/repairs/  # 수리 이력
├── /tools/
│   ├── GET    /api/v1/tools/                   # 치공구 목록
│   └── GET    /api/v1/tools/{id}/prediction/   # 수명 예측
├── /work-orders/
│   ├── GET    /api/v1/work-orders/             # 작업지시 목록
│   └── POST   /api/v1/work-orders/{id}/risk/   # 위험도 분석
└── /integration/
    ├── POST   /api/v1/integration/erp/sync/    # ERP 동기화
    └── GET    /api/v1/integration/history/     # 동기화 이력
```

**Serializers 예시:**
```python
# backend/quality_issues/serializers.py

from rest_framework import serializers
from .models import QualityIssue, IssueAnalysis4M, ProblemSolvingStep

class QualityIssueSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)

    class Meta:
        model = QualityIssue
        fields = [
            'id', 'issue_number', 'title', 'description',
            'product_code', 'product_name', 'defect_type',
            'severity', 'status', 'reported_date',
            'reporter', 'reporter_name', 'department',
            'defect_quantity', 'cost_impact', 'responsible_person',
            'target_resolution_date', 'actual_resolution_date',
            'completion_notes', 'created_at', 'updated_at'
        ]

class IssueAnalysis4MSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueAnalysis4M
        fields = ['id', 'category', 'description', 'created_at']

class ProblemSolvingStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemSolvingStep
        fields = [
            'id', 'step_number', 'step_name', 'content',
            'completed', 'completed_at', 'created_at', 'updated_at'
        ]
```

**Views 예시:**
```python
# backend/quality_issues/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import QualityIssue, IssueAnalysis4M, ProblemSolvingStep
from .serializers import (
    QualityIssueSerializer,
    IssueAnalysis4MSerializer,
    ProblemSolvingStepSerializer
)

class QualityIssueViewSet(viewsets.ModelViewSet):
    queryset = QualityIssue.objects.all()
    serializer_class = QualityIssueSerializer

    def get_queryset(self):
        queryset = QualityIssue.objects.all()
        status = self.request.query_params.get('status')
        severity = self.request.query_params.get('severity')

        if status:
            queryset = queryset.filter(status=status)
        if severity:
            queryset = queryset.filter(severity=severity)

        return queryset

    @action(detail=True, methods=['get'])
    def analysis_4m(self, request, pk=None):
        issue = self.get_object()
        analyses = issue.analyses_4m.all()
        serializer = IssueAnalysis4MSerializer(analyses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def solving_steps(self, request, pk=None):
        issue = self.get_object()
        steps = issue.solving_steps.all()
        serializer = ProblemSolvingStepSerializer(steps, many=True)
        return Response(serializer.data)
```

**URL Routing:**
```python
# backend/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from quality_issues.views import QualityIssueViewSet

router = DefaultRouter()
router.register(r'quality-issues', QualityIssueViewSet, basename='quality-issue')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
]
```

#### 1.3 CORS 및 인증 설정

```python
# backend/settings.py

# CORS 설정
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 최상단에 추가
    'django.middleware.common.CommonMiddleware',
    ...
]

# 프론트엔드에서의 접근 허용
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 개발 시 모든 Origin 허용 (프로덕션에서는 제거)
CORS_ALLOW_ALL_ORIGINS = True

# 인증 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

#### 1.4 프론트엔드 API 연동

```typescript
// frontend/src/services/api.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Token ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Quality Issues
  async getQualityIssues(params?: {
    status?: string;
    severity?: string;
  }): Promise<ApiResponse<QualityIssue>> {
    const queryParams = new URLSearchParams(params as any);
    return this.request<ApiResponse<QualityIssue>>(
      `/quality-issues/?${queryParams}`
    );
  }

  async createQualityIssue(data: Partial<QualityIssue>): Promise<QualityIssue> {
    return this.request<QualityIssue>('/quality-issues/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateQualityIssue(
    id: number,
    data: Partial<QualityIssue>
  ): Promise<QualityIssue> {
    return this.request<QualityIssue>(`/quality-issues/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteQualityIssue(id: number): Promise<void> {
    return this.request(`/quality-issues/${id}/`, {
      method: 'DELETE',
    });
  }

  // Equipment
  async getEquipment(): Promise<ApiResponse<Equipment>> {
    return this.request<ApiResponse<Equipment>>('/equipment/');
  }

  async getEquipmentHealth(id: number): Promise<{ health_score: number }> {
    return this.request(`/equipment/${id}/health/`);
  }

  // Work Orders
  async getWorkOrders(): Promise<ApiResponse<WorkOrder>> {
    return this.request<ApiResponse<WorkOrder>>('/work-orders/');
  }

  async analyzeWorkOrderRisk(id: number): Promise<RiskAnalysis> {
    return this.request(`/work-orders/${id}/risk/`, {
      method: 'POST',
    });
  }

  // Integration
  async syncERP(): Promise<SyncResult> {
    return this.request('/integration/erp/sync/', {
      method: 'POST',
    });
  }

  async getSyncHistory(): Promise<ApiResponse<SyncHistory>> {
    return this.request<ApiResponse<SyncHistory>>('/integration/history/');
  }
}

export const apiService = new ApiService(API_BASE_URL);
```

---

## 🚀 특별 기능 설계

### 기능 1: 스마트 알림 및 예측 시스템

#### 개요
AI 기반 실시간 예측 알림 시스템으로, 품질 이슈, 설비 고장, 치공구 교체 시점을 사전에 예측

#### 핵심 기능
1. **실시간 예측 알림**
   - 설비 건강 점수 85점 미만 시 경고
   - 치공구 수명 70% 도달 시 알림
   - 품질 이상 패턴 감지 시 즉시 알림

2. **알림 우선순위 큐**
   ```typescript
   interface NotificationPriority {
     CRITICAL: '설비 고장 임박',      // 즉시 조치
     HIGH: '품질 이상 감지',          // 1시간 이내
     MEDIUM: '치공구 교체 필요',      // 금일 내
     LOW: '예방 보전 예정',           // 주간 내
   }
   ```

3. **다중 채널 알림**
   - 브라우저 푸시 알림
   - 이메일 알림
   - SMS 알림 (선택 사항)
   - Slack/Teams 연동

#### 데이터 모델
```python
# backend/notifications/models.py

class Notification(models.Model):
    class Priority(models.TextChoices):
        CRITICAL = 'CRITICAL', '긴급'
        HIGH = 'HIGH', '높음'
        MEDIUM = 'MEDIUM', '중간'
        LOW = 'LOW', '낮음'

    class Type(models.TextChoices):
        EQUIPMENT = 'EQUIPMENT', '설비'
        QUALITY = 'QUALITY', '품질'
        TOOL = 'TOOL', '치공구'
        MAINTENANCE = 'MAINTENANCE', '보전'

    title = models.CharField(max_length=200, verbose_name='제목')
    message = models.TextField(verbose_name='메시지')
    priority = models.CharField(max_length=20, choices=Priority.choices)
    type = models.CharField(max_length=20, choices=Type.choices)
    related_object_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    action_required = models.BooleanField(default=True)
    action_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    browser_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    slack_notifications = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
```

#### 구현 코드
```typescript
// frontend/src/pages/NotificationsPage.tsx

interface Notification {
  id: number;
  title: string;
  message: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  type: 'EQUIPMENT' | 'QUALITY' | 'TOOL' | 'MAINTENANCE';
  is_read: boolean;
  action_required: boolean;
  action_deadline: string;
  created_at: string;
}

const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<string>('ALL');

  useEffect(() => {
    // 브라우저 푸시 알림 권한 요청
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const handleMarkAsRead = async (id: number) => {
    await apiService.markNotificationAsRead(id);
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, is_read: true } : n)
    );
  };

  const sendBrowserNotification = (notification: Notification) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/icon.png',
        tag: notification.id.toString(),
        requireInteraction: notification.priority === 'CRITICAL',
      });
    }
  };

  return (
    <div className="p-6">
      {/* 알림 목록, 필터, 통계 등 */}
    </div>
  );
};
```

---

### 기능 2: 고급 리포팅 및 대시보드 시스템

#### 개요
사용자 정의 가능한 대시보드와 자동 리포트 생성 시스템

#### 핵심 기능
1. **드래그앤드롭 대시보드**
   - 사용자별 위젯 배치
   - 위젯: OEE 차트, 불량률 추이, 설비 상태, 작업지시 현황
   - 대시보드 템플릿 저장/공유

2. **자동 리포트 생성**
   - PDF/Excel 다운로드
   - 스케줄링 (일일, 주간, 월간)
   - 이메일 자동 발송

3. **리포트 템플릿**
   ```typescript
   interface ReportTemplate {
     name: string;
     sections: ReportSection[];
     schedule: {
       frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
       time: string;
       recipients: string[];
     };
     format: 'PDF' | 'EXCEL' | 'BOTH';
   }
   ```

#### 데이터 모델
```python
# backend/reports/models.py

class Dashboard(models.Model):
    name = models.CharField(max_length=200, verbose_name='대시보드명')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    layout = models.JSONField(verbose_name='레이아웃')  # 위젯 위치 정보
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ReportTemplate(models.Model):
    name = models.CharField(max_length=200, verbose_name='템플릿명')
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.JSONField(verbose_name='리포트 내용')
    schedule_frequency = models.CharField(max_length=20, choices=[
        ('DAILY', '일일'),
        ('WEEKLY', '주간'),
        ('MONTHLY', '월간'),
    ])
    schedule_time = models.TimeField()
    recipients = models.JSONField(default=list)
    format = models.CharField(max_length=10, choices=[
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('BOTH', '둘 다'),
    ])
    is_active = models.BooleanField(default=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)

class GeneratedReport(models.Model):
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=10)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', '대기'),
        ('GENERATING', '생성중'),
        ('COMPLETED', '완료'),
        ('FAILED', '실패'),
    ])
    error_message = models.TextField(blank=True)
```

#### 위젯 라이브러리
```typescript
// frontend/src/components/dashboard/widgets/

interface Widget {
  id: string;
  type: WidgetType;
  title: string;
  size: 'small' | 'medium' | 'large';
  position: { x: number; y: number };
  data: any;
  refreshInterval?: number; // 초
}

type WidgetType =
  | 'oee-chart'           // OEE 실시간 차트
  | 'defect-rate'         // 불량률 추이
  | 'equipment-status'    // 설비 상태 모니터링
  | 'work-orders'         // 작업지시 현황
  | 'quality-issues'      // 품질 이슈 요약
  | 'tool-life'           // 치공구 수명
  | 'production-count'    // 생산 실적
  | 'cost-analysis'       // 품질 코스트 분석
  | 'maintenance-schedule' // 예방 보전 일정
  | 'alert-list';         // 알림 목록

// 위젯 컴포넌트 예시
const OEEChartWidget: React.FC<Widget> = ({ data, refreshInterval = 30 }) => {
  const [oeeData, setOeeData] = useState(data);

  useEffect(() => {
    const interval = setInterval(async () => {
      const fresh = await apiService.getLatestOEE();
      setOeeData(fresh);
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>OEE 실시간 모니터링</CardTitle>
      </CardHeader>
      <CardContent>
        <OEEChart data={oeeData} />
      </CardContent>
    </Card>
  );
};
```

---

### 기능 3: AI 모델 관리 시스템

#### 개요
머신러닝 모델의 학습, 배포, 성능 모니터링을 위한 통합 관리 시스템

#### 핵심 기능
1. **모델 버전 관리**
   - 모델 버전 추적 (v1.0, v1.1, ...)
   - 하이퍼파라미터 기록
   - 학습 데이터셋 정보

2. **모델 성능 모니터링**
   - 예측 정확도 추적
   - Precision, Recall, F1-Score
   - 실제값 vs 예측값 비교 차트

3. **A/B 테스트**
   - 여러 모델 동시 운영
   - 실제 환경에서 성능 비교
   - 자동 최상 모델 선택

#### 데이터 모델
```python
# backend/ml/models.py

class MLModel(models.Model):
    name = models.CharField(max_length=200, verbose_name='모델명')
    version = models.CharField(max_length=20, verbose_name='버전')
    model_type = models.CharField(max_length=50, choices=[
        ('CLASSIFICATION', '분류'),
        ('REGRESSION', '회귀'),
        ('TIMESERIES', '시계열'),
        ('ANOMALY_DETECTION', '이상탐지'),
    ])
    file_path = models.CharField(max_length=500, verbose_name='모델 파일 경로')
    hyperparameters = models.JSONField(default=dict, verbose_name='하이퍼파라미터')
    training_dataset = models.CharField(max_length=200, verbose_name='학습 데이터셋')
    training_date = models.DateTimeField(verbose_name='학습일')
    is_active = models.BooleanField(default=False, verbose_name='활성화')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ModelPerformance(models.Model):
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='performances')
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True)  # Mean Absolute Error
    rmse = models.FloatField(null=True, blank=True)  # Root Mean Squared Error
    test_date = models.DateTimeField(auto_now_add=True)
    test_dataset_size = models.IntegerField()
    notes = models.TextField(blank=True)

class ModelPrediction(models.Model):
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='predictions')
    input_data = models.JSONField(verbose_name='입력 데이터')
    predicted_value = models.FloatField(verbose_name='예측값')
    actual_value = models.FloatField(null=True, blank=True, verbose_name='실제값')
    confidence_score = models.FloatField(verbose_name='신뢰도')
    prediction_time = models.DateTimeField(auto_now_add=True)
    is_correct = models.NullBooleanField(null=True, blank=True)
```

#### API 엔드포인트
```python
# backend/ml/views.py

class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer

    @action(detail=True, methods=['post'])
    def deploy(self, request, pk=None):
        """모델 배포"""
        model = self.get_object()
        # 다른 모델 비활성화
        MLModel.objects.filter(name=model.name).update(is_active=False)
        # 현재 모델 활성화
        model.is_active = True
        model.save()
        return Response({'status': 'deployed'})

    @action(detail=True, methods=['post'])
    def predict(self, request, pk=None):
        """예측 실행"""
        model = self.get_object()
        input_data = request.data.get('input_data')

        # 모델 파일 로드 및 예측
        import joblib
        import numpy as np

        model_file = joblib.load(model.file_path)
        prediction = model_file.predict([input_data])

        # 예측 기록
        ModelPrediction.objects.create(
            model=model,
            input_data=input_data,
            predicted_value=prediction[0],
            confidence_score=0.95
        )

        return Response({'prediction': prediction[0]})

    @action(detail=True, methods=['get'])
    def performance_history(self, request, pk=None):
        """성능 이력 조회"""
        model = self.get_object()
        performances = model.performances.all()[:10]
        serializer = ModelPerformanceSerializer(performances, many=True)
        return Response(serializer.data)
```

#### 프론트엔드 UI
```typescript
// frontend/src/pages/ModelManagementPage.tsx

const ModelManagementPage: React.FC = () => {
  const [models, setModels] = useState<MLModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<MLModel | null>(null);

  return (
    <div className="p-6">
      {/* 모델 목록 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {models.map(model => (
          <Card key={model.id}>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>{model.name} v{model.version}</CardTitle>
                {model.is_active && <Badge>활성</Badge>}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p>유형: {model.model_type}</p>
                <p>정확도: {model.latest_performance?.accuracy || 'N/A'}</p>
                <p>학습일: {model.training_date}</p>
                <Button onClick={() => handleDeploy(model.id)}>
                  배포하기
                </Button>
                <Button onClick={() => handlePredict(model.id)}>
                  테스트 예측
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 성능 차트 */}
      {selectedModel && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>성능 이력</CardTitle>
          </CardHeader>
          <CardContent>
            <ModelPerformanceChart model={selectedModel} />
          </CardContent>
        </Card>
      )}
    </div>
  );
};
```

---

### 기능 4: 모바일 앱 연동

#### 개요
모바일 앱을 통한 현장에서의 실시간 데이터 입력 및 알림 수신

#### 핵심 기능
1. **모바일 웹 앱**
   - 반응형 디자인 (PWA 지원)
   - 오프라인 모드 지원
   - 카메라 스캔 (바코드/QR코드)

2. **현장 작업자 기능**
   - 작업지시 수신 및 완료 보고
   - 불량품 사진 촬영 및 등록
   - 설비 상태 업데이트
   - 푸시 알림 수신

3. **PWA 설정**
```javascript
// frontend/public/sw.js (Service Worker)

const CACHE_NAME = 'spc-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 캐시 있으면 반환, 없으면 네트워크 요청
        return response || fetch(event.request);
      })
  );
});
```

---

### 기능 5: 고급 분석 도구

#### 개요
Six Sigma, 통계 분석, DoE (Design of Experiments) 도구

#### 핵심 기능
1. **통계 공정 능력 분석**
   - Cp, Cpk 계산
   - 정규성 검정 (Shapiro-Wilk)
   - 공정 능력 리포트

2. **DoE (실험계획법)**
   - 완전 요인 설계 (Full Factorial)
   - 일부 요인 설계 (Fractional Factorial)
   - 반응 표면 분석 (RSM)

3. **상관 관계 분석**
   - 히트맵 시각화
   - 산점도 행렬
   - Pearson 상관 계수

#### 데이터 모델
```python
# backend/analytics/models.py

class StatisticalAnalysis(models.Model):
    name = models.CharField(max_length=200)
    analysis_type = models.CharField(max_length=50, choices=[
        ('CAPABILITY', '공정능력'),
        ('CORRELATION', '상관분석'),
        ('REGRESSION', '회귀분석'),
        ('DOE', '실험계획'),
        ('ANOVA', '분산분석'),
    ])
    parameters = models.JSONField()
    results = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProcessCapability(models.Model):
    analysis = models.OneToOneField(StatisticalAnalysis, on_delete=models.CASCADE)
    characteristic = models.CharField(max_length=200, verbose_name='특성치')
    specification_lower = models.FloatField(verbose_name='하한 사양')
    specification_upper = models.FloatField(verbose_name='상한 사양')
    specification_target = models.FloatField(verbose_name='목표치')
    mean = models.FloatField(verbose_name='평균')
    std_dev = models.FloatField(verbose_name='표준편차')
    cp = models.FloatField(verbose_name='Cp')
    cpk = models.FloatField(verbose_name='Cpk')
    sample_size = models.IntegerField()
    data_points = models.JSONField()  # 실제 데이터
```

#### 통계 분석 API
```python
# backend/analytics/views.py

import numpy as np
from scipy import stats

class AnalysisViewSet(viewsets.ViewSet):
    def create_capability_analysis(self, request):
        data = request.data.get('data_points', [])
        lsl = request.data.get('lsl')
        usl = request.data.get('usl')
        target = request.data.get('target')

        mean = np.mean(data)
        std = np.std(data)

        # Cp 계산
        cp = (usl - lsl) / (6 * std)

        # Cpk 계산
        cpu = (usl - mean) / (3 * std)
        cpl = (mean - lsl) / (3 * std)
        cpk = min(cpu, cpl)

        return Response({
            'mean': mean,
            'std_dev': std,
            'cp': cp,
            'cpk': cpk,
            'cpu': cpu,
            'cpl': cpl,
        })

    def create_correlation_analysis(self, request):
        variables = request.data.get('variables', [])

        correlation_matrix = np.corrcoef(variables)

        return Response({
            'correlation_matrix': correlation_matrix.tolist(),
        })
```

---

## 🏗️ 기술 아키텍처

### 시스템 아키텍처 다이어그램
```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    (React + TypeScript)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Pages (20+)                                           │ │
│  │  - Dashboard, Quality, Equipment, Tools, etc.          │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  State Management (Zustand/Redux)                      │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  API Client (axios/fetch)                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓ HTTPS/REST API
┌─────────────────────────────────────────────────────────────┐
│                    Django Backend                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  REST Framework (API Layer)                            │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  Business Logic Layer                                  │ │
│  │  - Quality Issues, Equipment, Tools, etc.              │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  ML/AI Services                                        │ │
│  │  - Prediction, Anomaly Detection, Risk Analysis        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│  PostgreSQL     │ │  Redis      │ │  ML Model Store │
│  (Primary DB)   │ │  (Cache)    │ │  (Joblib/S3)    │
└─────────────────┘ └─────────────┘ └─────────────────┘
```

### 데이터베이스 스키마
```sql
-- 핵심 테이블 관계도
quality_issues (품질 이슈)
├── issue_analysis_4m (4M 분석)
└── problem_solving_steps (8단계 문제해결)

equipment (설비)
├── equipment_parts (부품)
├── equipment_manuals (매뉴얼)
├── equipment_repair_histories (수리이력)
└── preventive_maintenances (예방보전)

tools (치공구)
└── tool_repair_histories (수리이력)

work_orders (작업지시)
└── work_order_tools (작업지시-치공구 연결)

integration_history (연계이력)

notifications (알림)

dashboards (대시보드)

ml_models (ML 모델)
├── model_performances (성능)
└── model_predictions (예측 기록)
```

---

## 📊 구현 우선순위

### 1단계: 백엔드 완성 (1-2주)
- [ ] Django 앱 settings.py 등록
- [ ] 마이그레이션 생성 및 실행
- [ ] REST API 엔드포인트 구현
- [ ] CORS 및 인증 설정
- [ ] API 문서화 (Swagger/OpenAPI)

### 2단계: 프론트엔드-백엔드 연동 (1주)
- [ ] API 서비스 레이어 구현
- [ ] 로그인/인증 구현
- [ ] 모든 페이지 API 연동
- [ ] 로딩/에러 상태 처리
- [ ] 오프라인 모드 지원

### 3단계: 특별 기능 구현 (2-3주)
- [ ] **기능 1: 스마트 알림 시스템** (우선순위 1)
- [ ] **기능 2: 고급 리포팅** (우선순위 2)
- [ ] **기능 3: AI 모델 관리** (우선순위 3)

### 4단계: 테스트 및 배포 (1주)
- [ ] 단위 테스트 (pytest, Jest)
- [ ] 통합 테스트
- [ ] 성능 최적화
- [ ] 배포 자동화 (Docker, CI/CD)

---

## 🎯 성공 지표 (KPI)

### 기술적 지표
- API 응답 시간: < 200ms (p95)
- 페이지 로드 시간: < 2초
- OEE 계산 정확도: > 95%
- 예측 모델 정확도: > 90%

### 비즈니스 지표
- 불량률 감소: 20% 이하
- 설비 다운타임 감소: 30%
- 치공구 교체 비용 절감: 15%
- 품질 이슈 해결 시간 단축: 50%

---

**작성일**: 2025-01-16
**버전**: v1.0
**작성자**: Claude Code

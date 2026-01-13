"""
Celery Configuration for SPC Quality Control System

비동기 작업 처리를 위한 Celery 설정
- 보고서 생성
- 데이터 분석
- 이메일 알림
- 배치 처리
"""

import os
from celery import Celery
from celery.schedules import crontab

# Django settings 모듈 경로
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('spc_quality_control')

# Django 설정 로드
app.config_from_object('django.conf:settings', namespace='CELERY')

# 자동 발견된 작업 (autodiscover)
app.autodiscover_tasks(['apps.spc', 'apps.aps'])

# Celery Beat 스케줄러 설정
app.conf.beat_schedule = {
    # 매일 자정 시간에 일일 보고서 생성
    'generate-daily-report': {
        'task': 'apps.spc.tasks.generate_daily_report',
        'schedule': crontab(hour=6, minute=0),  # 매일 오전 6시
    },

    # 매주 월요일 주간 보고서 생성
    'generate-weekly-report': {
        'task': 'apps.spc.tasks.generate_weekly_report',
        'schedule': crontab(hour=7, minute=0, day_of_week=1),  # 매주 월요일 오전 7시
    },

    # 매월 1일 월간 보고서 생성
    'generate-monthly-report': {
        'task': 'apps.spc.tasks.generate_monthly_report',
        'schedule': crontab(hour=8, minute=0, day_of_month=1),  # 매월 1일 오전 8시
    },

    # 매시간 시계열 분석 실행
    'hourly-timeseries-analysis': {
        'task': 'apps.spc.tasks.run_hourly_timeseries_analysis',
        'schedule': crontab(minute=0),  # 매시간 정각
    },

    # 30분마다 이상 감지 실행
    'detect-anomalies-periodically': {
        'task': 'apps.spc.tasks.detect_anomalies_periodically',
        'schedule': crontab(minute='*/30'),  # 30분마다
    },

    # 매일 자정 시간에 데이터베이스 정리
    'cleanup-old-data': {
        'task': 'apps.spc.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # 매일 새벽 2시
    },
}

# Celery Worker 설정
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    # 결과 백엔드 (Redis)
    result_backend=os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    # 작업 결과 만료 시간 (1일)
    result_expires=3600,
    # 작업 시간 제한 (1시간)
    task_time_limit=3600,
    # 작업 소프트 타임 제한 (55분)
    task_soft_time_limit=3300,
    # 재시도 설정
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # 최대 재시도 횟수
    task_max_retries=3,
    # 재시롱 지연 시간 (초)
    task_default_retry_delay=60,
    # 우선순위 설정
    task_default_priority=5,
    # Workerprefetch_multiplier (메모리 최적화)
    worker_prefetch_multiplier=4,
    # 동시 실행 작업 수
    worker_concurrency=4,
    # 작업 실행 최적화
    worker_max_tasks_per_child=1000,
)

# 라우터 설정 (선택적)
app.conf.task_routes = {
    # 높은 우선순위 작업
    'apps.spc.tasks.send_critical_alert': {
        'queue': 'critical',
        'priority': 10,
    },
    # 일반 우선순위 작업
    'apps.spc.tasks.process_quality_measurement': {
        'queue': 'default',
        'priority': 5,
    },
    # 낮은 우선순위 작업
    'apps.spc.tasks.generate_report': {
        'queue': 'low_priority',
        'priority': 1,
    },
    # 무거운 배치 작업
    'apps.spc.tasks.batch_import_data': {
        'queue': 'heavy',
        'priority': 2,
    },
}

# 성능 최적화를 위한 설정
if os.environ.get('ENVIRONMENT') == 'production':
    app.conf.update(
        # 프로덕션 환경에서는 더 많은 동시성
        worker_concurrency=8,
        worker_prefetch_multiplier=1,
        # Gzip 압축
        worker_compression='gzip',
    )

# 작업 데코레이터
@app.task(bind=True, max_retries=3)
def debug_task(self):
    print(f'Request: {self.request!r}')

@app.task(bind=True)
def add(x, y):
    return x + y


if __name__ == '__main__':
    app.start()

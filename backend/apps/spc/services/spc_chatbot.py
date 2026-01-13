"""
SPC AI Quality Chat Service
SPC 품질 관리 전용 AI 챗봇 서비스
"""
import os
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
import numpy as np

from django.conf import settings
from apps.aps.ai_llm_models import PredictiveModel, AIInsight, KnowledgeBase
from apps.spc.models import (
    Product, QualityMeasurement, ControlChart,
    ProcessCapability, RunRuleViolation, QualityAlert
)


class SPCQualityChatbot:
    """SPC 품질 관리 AI 챗봇"""

    def __init__(self):
        self.context_limit = 10  # 최근 문맑 개수

    def chat(self, user_message: str, product_id: int = None, session_id: str = None) -> Dict[str, Any]:
        """
        AI 챗봇 질의 응답

        Args:
            user_message: 사용자 질문
            product_id: 제품 ID (선택사항)
            session_id: 세션 ID (선택사항)

        Returns:
            응답 결과 (response, context, suggestions)
        """
        # 질문 의도 파악
        intent = self._detect_intent(user_message)

        # 의도별 응답 생성
        if intent == 'capability_analysis':
            return self._handle_capability_query(user_message, product_id)
        elif intent == 'troubleshooting':
            return self._handle_troubleshooting(user_message, product_id)
        elif intent == 'trend_analysis':
            return self._handle_trend_analysis(user_message, product_id)
        elif intent == 'root_cause':
            return self._handle_root_cause_analysis(user_message, product_id)
        elif intent == 'improvement':
            return self._handle_improvement_recommendation(user_message, product_id)
        else:
            return self._handle_general_query(user_message, product_id)

    def _detect_intent(self, message: str) -> str:
        """질문 의도 파악"""
        message_lower = message.lower()

        # 키워드 기반 의도 분류
        keywords = {
            'capability_analysis': ['공정능력', 'cpk', 'cp', '능력', '능력지수', 'ppk', '불량률'],
            'troubleshooting': ['문제', '에러', '불량', '불량률 상승', '개선이 필요', '원인'],
            'trend_analysis': ['트렌드', '추세', '경향', '변화', '증가', '감소'],
            'root_cause': ['원인', '근본 원인', '왜', '이유', '발생'],
            'improvement': ['개선', '최적화', '향상', '해결책', '방안'],
        }

        for intent, words in keywords.items():
            if any(word in message_lower for word in words):
                return intent

        return 'general'

    def _handle_capability_query(self, message: str, product_id: int) -> Dict[str, Any]:
        """공정능력 분석 질의 처리"""
        if not product_id:
            return {
                'response': '제품을 선택해주세요. 제품에 대한 공정능력 분석을 도와드리겠습니다.',
                'context': [],
                'suggestions': ['제품 선택하기', '공정능력 분석 실행하기']
            }

        try:
            # 최신 공정능력 데이터 조회
            capability = ProcessCapability.objects.filter(
                product_id=product_id
            ).order_by('-analyzed_at').first()

            if not capability:
                return {
                    'response': f'해당 제품의 공정능력 분석 데이터가 없습니다. 먼저 공정능력 분석을 실행해주세요.',
                    'context': [],
                    'suggestions': ['공정능력 분석 실행하기']
                }

            product = capability.product
            cpk = capability.cpk
            cp = capability.cp

            # Cpk 등급 평가
            if cpk >= 2.0:
                grade = "우수 (6σ 수준)"
                status = "매우 안정적인 공정 상태입니다."
            elif cpk >= 1.67:
                grade = "양호 (5σ 수준)"
                status = "안정적인 공정 상태입니다."
            elif cpk >= 1.33:
                grade = "보통 (4σ 수준)"
                status = "관리 가능한 수준이나 지속적인 모니터링이 필요합니다."
            elif cpk >= 1.0:
                grade = "미흡 (3σ 수준)"
                status = "공정능력 개선이 필요합니다."
            else:
                grade = "부적합"
                status = "즉시 공정 개선이 필요합니다."

            # AI 인사이트 생성
            insights = self._generate_capability_insights(capability)

            return {
                'response': f'''
## {product.product_name} 공정능력 분석 결과

**공정능력 지수:**
- Cp (잠재 능력): {cp:.3f}
- Cpk (실제 능력): {cpk:.3f}
- 등급: {grade}

**평가:**
{status}

**AI 분석:**
{insights}
                '''.strip(),
                'context': {
                    'product_id': product_id,
                    'cpk': cpk,
                    'cp': cp,
                    'grade': grade
                },
                'suggestions': self._get_capability_suggestions(cpk)
            }

        except Exception as e:
            return {
                'response': f'공정능력 분석 중 오류가 발생했습니다: {str(e)}',
                'context': [],
                'suggestions': []
            }

    def _handle_troubleshooting(self, message: str, product_id: int) -> Dict[str, Any]:
        """문제 해결 질의 처리"""
        if not product_id:
            return {
                'response': '문제가 발생한 제품을 선택해주세요.',
                'context': [],
                'suggestions': ['제품 선택하기', '최근 경고 확인하기']
            }

        try:
            # 최근 품질 경고 조회
            recent_alerts = QualityAlert.objects.filter(
                product_id=product_id,
                created_at__gte=datetime.now() - timedelta(days=7)
            ).order_by('-created_at')[:5]

            # 최근 Run Rule 위반 조회
            recent_violations = RunRuleViolation.objects.filter(
                control_chart__product_id=product_id,
                detected_at__gte=datetime.now() - timedelta(days=7)
            ).order_by('-detected_at')[:5]

            if not recent_alerts and not recent_violations:
                return {
                    'response': '최근 7일간 특별한 문제가 감지되지 않았습니다. 정상적인 공정 운영 상태입니다.',
                    'context': {},
                    'suggestions': ['정기적인 모니터링 유지', '샘플링 주기 준수']
                }

            # 문제 분석 및 해결책 제안
            diagnosis = self._diagnose_quality_issues(recent_alerts, recent_violations)

            return {
                'response': f'''
## 품질 문제 진단 및 해결 방안

{diagnosis}

## 🔧 AI 추천 해결 방안

### 1. 즉시 조치
- 관리 한계 이탈 시: 즉시 공정 중단 및 원인 파악
- 설비 점검: 계측기 보정, 공구 마모 확인

### 2. 근본 원인 분석
- 4M1E (Man, Machine, Material, Method, Environment) 분석 실시
- 작업자 교육 확인
- 원재료 변화 확인

### 3. 예방 조치
- 정기적 예방 보전 실시
- 작업 표준서 (SOP) 업데이트
- 통계적 공정 관리 (SPC) 강화
                '''.strip(),
                'context': {
                    'alert_count': len(recent_alerts),
                    'violation_count': len(recent_violations)
                },
                'suggestions': [
                    '상세 경고 확인',
                    'Run Rule 분석 실행',
                    '공정능력 재분석',
                    '전문가 상담'
                ]
            }

        except Exception as e:
            return {
                'response': f'문제 분석 중 오류가 발생했습니다: {str(e)}',
                'context': [],
                'suggestions': []
            }

    def _handle_trend_analysis(self, message: str, product_id: int) -> Dict[str, Any]:
        """추세 분석 질의 처리"""
        if not product_id:
            return {
                'response': '추세 분석할 제품을 선택해주세요.',
                'context': [],
                'suggestions': ['제품 선택하기']
            }

        try:
            # 최근 30일 데이터 조회
            thirty_days_ago = datetime.now() - timedelta(days=30)
            measurements = QualityMeasurement.objects.filter(
                product_id=product_id,
                measured_at__gte=thirty_days_ago
            ).order_by('measured_at')

            if measurements.count() < 30:
                return {
                    'response': '데이터가 부족하여 추세 분석이 불가능합니다. 최소 30개 이상의 측정 데이터가 필요합니다.',
                    'context': {'data_count': measurements.count()},
                    'suggestions': ['데이터 수집 후 재요청']
                }

            # 추세 분석
            values = list(measurements.values_list('measurement_value', flat=True))
            measurements_array = np.array(values)

            # 기초 통계
            mean = np.mean(measurements_array)
            std = np.std(measurements_array)
            min_val = np.min(measurements_array)
            max_val = np.max(measurements_array)

            # 추세 분석 (단순 회귀)
            x = np.arange(len(measurements_array))
            z = np.polyfit(x, measurements_array, 1)
            p = np.poly1d(z)
            slope = z[0]

            # 추세 판정
            if abs(slope) < 0.0001:
                trend = "안정"
                trend_desc = "공정이 안정적으로 유지되고 있습니다."
            elif slope > 0:
                trend = "상승"
                trend_desc = f"측정값이 상승 추세입니다. (기울기: {slope:.6f})"
                if mean > measurements_array[len(measurements_array)//2]:
                    trend_desc += " 상한선(UCL) 근접 가능성이 있으니 주의가 필요합니다."
            else:
                trend = "하락"
                trend_desc = f"측정값이 하락 추세입니다. (기울기: {slope:.6f})"
                if mean < measurements_array[len(measurements_array)//2]:
                    trend_desc += " 하한선(LCL) 근접 가능성이 있으니 주의가 필요합니다."

            # 변동성 분석
            cv = (std / mean) * 100  # 변동 계수

            return {
                'response': f'''
## 📈 {measurements.first().product.product_name} 추세 분석

### 기초 통계 (최근 30일)
- 평균: {mean:.4f}
- 표준편차: {std:.4f}
- 최소값: {min_val:.4f}
- 최대값: {max_val:.4f}
- 변동 계수(CV): {cv:.2f}%

### 추세 분석
**추세:** {trend}
**설명:** {trend_desc}

### AI 분석
1. **추세 방향:** {'상승 중이면 상한선 근접 주의, 하락 중이면 하한선 근접 주의'}
2. **변동성:** {'변동이 큽니다. 공정 안정화가 필요합니다.' if cv > 5 else '변동이 안정적입니다.'}
3. **예측:** 향후 7일간 평균값은 {mean + slope * 7:.4f} 수준 예상입니다.
                '''.strip(),
                'context': {
                    'trend': trend,
                    'slope': slope,
                    'cv': cv,
                    'data_count': len(values)
                },
                'suggestions': [
                    '관리도 실시간 모니터링',
                    'Run Rule 위반 감시',
                    '정기적 공정능력 재평가'
                ]
            }

        except Exception as e:
            return {
                'response': f'추세 분석 중 오류가 발생했습니다: {str(e)}',
                'context': [],
                'suggestions': []
            }

    def _handle_root_cause_analysis(self, message: str, product_id: int) -> Dict[str, Any]:
        """근본 원인 분석 처리"""
        # 최근 문제 데이터 분석
        recent_alerts = QualityAlert.objects.filter(
            product_id=product_id,
            created_at__gte=datetime.now() - timedelta(days=7)
        ).order_by('-created_at')

        if not recent_alerts.exists():
            return {
                'response': '최근 문제 이력이 없습니다. 정상적인 공정 운영 상태입니다.',
                'context': {},
                'suggestions': ['정기 모니터링 유지']
            }

        # 4M1E 기반 원인 분석
        analysis = self._perform_4m1e_analysis(recent_alerts)

        return {
            'response': f'''
## 🔍 근본 원인 분석 결과

### 문제 개요
최근 {recent_alerts.count()}건의 품질 문제가 발생했습니다.

### 4M1E 원인 분석
{analysis}

### 🎯 추천 조치
1. 인적 요인: 작업자 교육 강화
2. 기계적 요인: 설비 보강 및 예방 보전
3. 재료적 요인: 원재료 품질 관리 강화
4. 방법적 요인: 작업 표준서 개선
5. 환경적 요인: 작업 환경 최적화
            '''.strip(),
            'context': {'alert_count': recent_alerts.count()},
            'suggestions': ['상세 분석 보고서 생성', '전문가 상담', '개선行动计划 수립']
        }

    def _handle_improvement_recommendation(self, message: str, product_id: int) -> Dict[str, Any]:
        """개선 방안 제안"""
        capability = ProcessCapability.objects.filter(
            product_id=product_id
        ).order_by('-analyzed_at').first()

        if not capability:
            return {
                'response': '공정능력 분석 데이터가 없습니다. 먼저 분석을 실행해주세요.',
                'context': {},
                'suggestions': ['공정능력 분석 실행']
            }

        # Cpk 기반 개선 방안
        recommendations = self._generate_improvement_plan(capability)

        return {
            'response': f'''
## 🚀 공정 개선 방안

### 현재 상황
- 현재 Cpk: {capability.cpk:.3f}
- 목표 Cpk: {capability.product.min_cpk_target or 1.33}

### 📋 단계별 개선 계획
{recommendations}

### 📊 예상 효과
- Cpk {capability.cpk:.3f} → {(capability.cpk + 0.5):.3f} (30% 개선 목표)
- 불량률 {self._calculate_ppm(capability.cpk):.0f} PPM → {self._calculate_ppm(capability.cpk + 0.5):.0f} PPM
            '''.strip(),
            'context': {'current_cpk': capability.cpk},
            'suggestions': ['개선 계획 실행', '진행 상태 모니터링', '성과 검증']
        }

    def _handle_general_query(self, message: str, product_id: int) -> Dict[str, Any]:
        """일반 질의 처리"""
        # LLM을 활용한 일반 응답
        response = f'''
## SPC 품질 관리 AI 어시스턴트

안녕하세요! SPC 품질 관리 전용 AI 챗봇입니다.

### 질문할 수 있는 항목
1. **공정능력 분석**: "Cpk가 어때 문제인가요?", "공정능력 평가해주세요"
2. **문제 해결**: "불량률이 상승했어요", "트러블슈팅 도와주세요"
3. **추세 분석**: "최근 추세가 어떻게 되나요?", "데이터 경향을 알려주세요"
4. **원인 분석**: "불량의 원인이 뭘까요?", "왜 문제가 발생했나요?"
5. **개선 방안**: "어떻게 개선하면 좋을까요?", "최적화 방안을 알려주세요"

### 사용 팁
- 제품을 선택 후 질문하면 더 정확한 답변이 가능합니다
- 구체적인 데이터를 포함하면 분석 정확도가 높아집니다
- 주기적으로 모니터링하고 AI 조언을 받으세요!

도움이 필요하시면 말씀해주세요!
        '''.strip()

        return {
            'response': response,
            'context': {},
            'suggestions': []
        }

    def _generate_capability_insights(self, capability: ProcessCapability) -> str:
        """공정능력 AI 인사이트 생성"""
        insights = []

        # Cpk 분석
        if capability.cpk >= 2.0:
            insights.append("✅ 매우 우수한 공정능력입니다. 6시그마 수준을 달성했습니다.")
        elif capability.cpk >= 1.33:
            insights.append("✅ 적정 수준의 공정능력입니다. 4시그마 수준입니다.")
        else:
            insights.append("⚠️ 공정능력이 부족합니다. 개선이 필요합니다.")

        # 정규성 검사
        if not capability.is_normal:
            insights.append("📊 데이터가 정규분포를 따르지 않습니다. 이상치 제거를 고려해주세요.")

        # 중심 위치 분석
        if capability.cpu < capability.cpl:
            insights.append("📈 평균이 상한 규격에 가깝습니다. 상한쪽 이탈에 주의하세요.")
        elif capability.cpl < capability.cpu:
            insights.append("📉 평균이 하한 규격에 가깝습니다. 하한쪽 이탈에 주의하세요.")

        return "\n".join(insights)

    def _get_capability_suggestions(self, cpk: float) -> List[str]:
        """공정능력 개선 제안"""
        if cpk >= 2.0:
            return [
                '현재 상태 유지',
                '정기 모니터링',
                '지속적 개선'
            ]
        elif cpk >= 1.33:
            return [
                '공정 안정화 강화',
                '변동성 저감 활동',
                '샘플링 최적화'
            ]
        else:
            return [
                '즉시 공정 중단 검토',
                '설비 예방 보전 실시',
                '작업 표준서 개정',
                '작업자 재교육'
            ]

    def _diagnose_quality_issues(self, alerts, violations) -> str:
        """품질 문제 진단"""
        diagnosis = []

        if alerts:
            high_priority = alerts.filter(priority__gte=3).count()
            diagnosis.append(f"- 긴급/높음 우선순위 경고: {high_priority}건")

        if violations:
            unresolved = violations.filter(is_resolved=False).count()
            diagnosis.append(f"- 미해결 Run Rule 위반: {unresolved}건")

        # 발생 빈도별 위반 유형
        violation_types = violations.values_list('rule_type').annotate(count=Count('rule_type'))
        most_common = violation_types.order_by('-count').first()

        if most_common:
            diagnosis.append(f"\n**가장 빈번한 위반 유형:**")
            diagnosis.append(f"- {most_common.rule_type}: {most_common.count}회")

        return "\n".join(diagnosis)

    def _perform_4m1e_analysis(self, alerts) -> str:
        """4M1E 원인 분석"""
        analysis = """
**Man (인적 요인)**
- 작업자 숙련도: 작업자 교육 이수 확인 필요
- 작업자 피로도: 교대근무 최적화 검토
- 작업 표준 준수: SOP 준수 여부 모니터링

**Machine (기계적 요인)**
- 설비 노후화: 정기적 설비 보전 실시
- 계측기 정밀도: 校准(교정) 일정 준수
- 공구 마모도: 공구 수명 확인 및 교체

**Material (재료적 요인)**
- 원재료 품질: 입고 검사 강화
- 재료 로트별 관리: FIFO 준수
- 저장 환경: 온습도 관리

**Method (방법적 요인)**
- 작업 순서: 최적 공정 조건 유지
- 표준 작업 시간: 사이클 타임 준수
- 품질 검사 방법: 적정 검사 주기

**Environment (환경적 요인)**
- 온도: 공정 온도 범위 유지
- 습도: 특히 정밀 가공시 중요
- 청결: 작업장 5S 활동
        """
        return analysis

    def _generate_improvement_plan(self, capability) -> str:
        """개선 계획 생성"""
        plan = []

        if capability.cpk < 1.0:
            plan.append("### 🔴 1단계: 즉시 조치 (1개월 이내)")
            plan.append("- 설비 전면 점검 및 보전")
            plan.append("- 작업자 재교육 실시")
            plan.append("- 공정 파라미터 재설정")

        if capability.cpk < 1.33:
            plan.append("### 🟡 2단계: 공정 안정화 (1~3개월)")
            plan.append("- 변동성 저감 활동 전개")
            plan.append("- 샘플링 주기 및 방법 개선")
            plan.append("- 통계적 공정 관리(SPC) 강화")

        plan.append("### 🟢 3단계: 지속적 개선 (3~6개월)")
        plan.append("- 6시그마 도전 목표 설정")
        plan.append("- 고급 통계 기법 도입")
        plan.append("- 품질 경영 전파 (전사원 참여)")

        return "\n".join(plan)

    def _calculate_ppm(self, cpk: float) -> float:
        """Cpk로 PPM 계산"""
        from scipy.stats import norm
        # Cpk를 Z-score로 변환 (편의상 3σ 가정)
        z = cpk * 3
        # 한쪽 불량률 계산
        one_tail = 1 - norm.cdf(z)
        # 양쪽 불량률 (PPM)
        ppm = one_tail * 2 * 1_000_000
        return ppm


# 싱글톤 클래스
class SPCChatbotService:
    """SPC 챗봇 서비스"""

    @staticmethod
    def get_chatbot() -> SPCQualityChatbot:
        """챗봇 인스턴스 반환"""
        return SPCQualityChatbot()

    @staticmethod
    def get_chat_history(session_id: str, limit: int = 10) -> List[Dict]:
        """채팅 기록 조회 (나중에 구현)"""
        # TODO: 채팅 기록을 DB에 저장 후 조회
        return []

    @staticmethod
    def save_chat_message(session_id: str, message: str, is_user: bool):
        """채팅 메시지 저장"""
        # TODO: DB에 저장
        pass

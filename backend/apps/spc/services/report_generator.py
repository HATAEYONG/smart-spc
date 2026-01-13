"""
SPC 품질 보고서 생성 서비스
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
from django.db.models import Avg, StdDev, Count, Q, Max, Min
from django.utils import timezone

from apps.spc.models import (
    Product, QualityMeasurement, ProcessCapability,
    QualityAlert, RunRuleViolation, ControlChart
)


class QualityReportGenerator:
    """품질 보고서 생성기"""

    def generate_daily_report(self, date: datetime) -> Dict[str, Any]:
        """일일 보고서 생성"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        return self._generate_report('DAILY', start_date, end_date)

    def generate_weekly_report(self, date: datetime) -> Dict[str, Any]:
        """주간 보고서 생성"""
        # 해당 주의 월요일 찾기
        start_date = date - timedelta(days=date.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)

        return self._generate_report('WEEKLY', start_date, end_date)

    def generate_monthly_report(self, date: datetime) -> Dict[str, Any]:
        """월간 보고서 생성"""
        start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # 다음 달 1일
        if date.month == 12:
            end_date = date.replace(year=date.year + 1, month=1, day=1)
        else:
            end_date = date.replace(month=date.month + 1, day=1)

        return self._generate_report('MONTHLY', start_date, end_date)

    def generate_custom_report(self, start_date: datetime, end_date: datetime,
                             product_ids: List[int] = None) -> Dict[str, Any]:
        """사용자 정의 보고서 생성"""
        return self._generate_report('CUSTOM', start_date, end_date, product_ids)

    def _generate_report(self, report_type: str, start_date: datetime,
                        end_date: datetime, product_ids: List[int] = None) -> Dict[str, Any]:
        """보고서 공통 생성 로직"""

        # 제품 필터링
        products = Product.objects.filter(is_active=True)
        if product_ids:
            products = products.filter(id__in=product_ids)

        products = list(products)

        # 섹션별 데이터 수집
        summary = self._generate_summary(products, start_date, end_date)
        product_details = self._generate_product_details(products, start_date, end_date)
        alerts_summary = self._generate_alerts_summary(products, start_date, end_date)
        capability_analysis = self._generate_capability_analysis(products, end_date)
        violations_summary = self._generate_violations_summary(products, start_date, end_date)
        recommendations = self._generate_recommendations(products, start_date, end_date)

        return {
            'report_type': report_type,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'formatted': f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
            },
            'generated_at': timezone.now().isoformat(),
            'summary': summary,
            'product_details': product_details,
            'alerts_summary': alerts_summary,
            'capability_analysis': capability_analysis,
            'violations_summary': violations_summary,
            'recommendations': recommendations
        }

    def _generate_summary(self, products: List[Product],
                         start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """요약 통계 생성"""
        total_products = len(products)

        # 전체 측정 데이터
        measurements = QualityMeasurement.objects.filter(
            product__in=products,
            measured_at__gte=start_date,
            measured_at__lt=end_date
        )

        total_measurements = measurements.count()
        out_of_spec = measurements.filter(is_within_spec=False).count()
        out_of_control = measurements.filter(is_within_control=False).count()

        # 전체 경고
        alerts = QualityAlert.objects.filter(
            product__in=products,
            created_at__gte=start_date,
            created_at__lt=end_date
        )

        total_alerts = alerts.count()
        critical_alerts = alerts.filter(priority=4).count()
        resolved_alerts = alerts.filter(status='RESOLVED').count()

        return {
            'total_products': total_products,
            'total_measurements': total_measurements,
            'out_of_spec_count': out_of_spec,
            'out_of_spec_rate': round(out_of_spec / total_measurements * 100, 2) if total_measurements > 0 else 0,
            'out_of_control_count': out_of_control,
            'out_of_control_rate': round(out_of_control / total_measurements * 100, 2) if total_measurements > 0 else 0,
            'total_alerts': total_alerts,
            'critical_alerts': critical_alerts,
            'resolved_alerts': resolved_alerts,
            'resolution_rate': round(resolved_alerts / total_alerts * 100, 2) if total_alerts > 0 else 0
        }

    def _generate_product_details(self, products: List[Product],
                                  start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """제품별 상세 정보 생성"""
        product_details = []

        for product in products:
            measurements = QualityMeasurement.objects.filter(
                product=product,
                measured_at__gte=start_date,
                measured_at__lt=end_date
            )

            if measurements.count() == 0:
                continue

            # 통계 계산
            stats = measurements.aggregate(
                avg_value=Avg('measurement_value'),
                std_dev=StdDev('measurement_value'),
                min_value=Min('measurement_value'),
                max_value=Max('measurement_value'),
                total_count=Count('id'),
                out_of_spec_count=Count('id', filter=Q(is_within_spec=False))
            )

            # 최신 공정능력
            latest_capability = ProcessCapability.objects.filter(
                product=product
            ).order_by('-analyzed_at').first()

            product_details.append({
                'product_id': product.id,
                'product_code': product.product_code,
                'product_name': product.product_name,
                'specifications': {
                    'usl': product.usl,
                    'lsl': product.lsl,
                    'target': product.target_value,
                    'unit': product.unit
                },
                'statistics': {
                    'total_measurements': stats['total_count'],
                    'average': round(stats['avg_value'], 4) if stats['avg_value'] else None,
                    'std_dev': round(stats['std_dev'], 4) if stats['std_dev'] else None,
                    'min_value': round(stats['min_value'], 4) if stats['min_value'] else None,
                    'max_value': round(stats['max_value'], 4) if stats['max_value'] else None,
                    'range': round(stats['max_value'] - stats['min_value'], 4) if stats['max_value'] and stats['min_value'] else None,
                    'out_of_spec_count': stats['out_of_spec_count'],
                    'out_of_spec_rate': round(stats['out_of_spec_count'] / stats['total_count'] * 100, 2) if stats['total_count'] > 0 else 0
                },
                'capability': {
                    'cp': latest_capability.cp if latest_capability else None,
                    'cpk': latest_capability.cpk if latest_capability else None,
                    'pp': latest_capability.pp if latest_capability else None,
                    'ppk': latest_capability.ppk if latest_capability else None,
                    'analyzed_at': latest_capability.analyzed_at.isoformat() if latest_capability else None
                }
            })

        return product_details

    def _generate_alerts_summary(self, products: List[Product],
                                start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """경고 요약 생성"""
        alerts = QualityAlert.objects.filter(
            product__in=products,
            created_at__gte=start_date,
            created_at__lt=end_date
        )

        # 우선순위별 분류
        by_priority = {
            'urgent': alerts.filter(priority=4).count(),
            'high': alerts.filter(priority=3).count(),
            'medium': alerts.filter(priority=2).count(),
            'low': alerts.filter(priority=1).count()
        }

        # 타입별 분류
        by_type = {}
        for alert_type, _ in QualityAlert.ALERT_TYPE_CHOICES:
            by_type[alert_type] = alerts.filter(alert_type=alert_type).count()

        # 상태별 분류
        by_status = {
            'new': alerts.filter(status='NEW').count(),
            'acknowledged': alerts.filter(status='ACKNOWLEDGED').count(),
            'investigating': alerts.filter(status='INVESTIGATING').count(),
            'resolved': alerts.filter(status='RESOLVED').count(),
            'closed': alerts.filter(status='CLOSED').count()
        }

        # 최근 경고 목록
        recent_alerts = []
        for alert in alerts.order_by('-created_at')[:10]:
            recent_alerts.append({
                'id': alert.id,
                'product_code': alert.product.product_code,
                'alert_type': alert.alert_type,
                'priority': alert.priority,
                'status': alert.status,
                'message': alert.message,
                'created_at': alert.created_at.isoformat()
            })

        return {
            'total': alerts.count(),
            'by_priority': by_priority,
            'by_type': by_type,
            'by_status': by_status,
            'recent_alerts': recent_alerts
        }

    def _generate_capability_analysis(self, products: List[Product],
                                     date: datetime) -> Dict[str, Any]:
        """공정능력 분석 생성"""
        capability_data = []

        for product in products:
            latest = ProcessCapability.objects.filter(
                product=product
            ).order_by('-analyzed_at').first()

            if not latest:
                continue

            # Cpk 등급 판정
            cpk = latest.cpk if latest.cpk else 0
            if cpk >= 2.0:
                grade = 'Superior'
                grade_color = '#10B981'  # green
            elif cpk >= 1.67:
                grade = 'Excellent'
                grade_color = '#3B82F6'  # blue
            elif cpk >= 1.33:
                grade = 'Good'
                grade_color = '#6366F1'  # indigo
            elif cpk >= 1.0:
                grade = 'Adequate'
                grade_color = '#F59E0B'  # amber
            else:
                grade = 'Inadequate'
                grade_color = '#EF4444'  # red

            capability_data.append({
                'product_code': product.product_code,
                'product_name': product.product_name,
                'cp': round(latest.cp, 3) if latest.cp else None,
                'cpk': round(latest.cpk, 3) if latest.cpk else None,
                'pp': round(latest.pp, 3) if latest.pp else None,
                'ppk': round(latest.ppk, 3) if latest.ppk else None,
                'grade': grade,
                'grade_color': grade_color,
                'analyzed_at': latest.analyzed_at.isoformat()
            })

        # 등급별 그룹화
        grade_distribution = {}
        for item in capability_data:
            grade = item['grade']
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

        return {
            'total_products_analyzed': len(capability_data),
            'grade_distribution': grade_distribution,
            'products': capability_data
        }

    def _generate_violations_summary(self, products: List[Product],
                                    start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Run Rule 위반 요약 생성"""
        violations = RunRuleViolation.objects.filter(
            control_chart__product__in=products,
            detected_at__gte=start_date,
            detected_at__lt=end_date
        )

        # Rule 타입별 분류
        by_rule = {}
        for i in range(1, 9):
            rule_count = violations.filter(rule_type=f'RULE_{i}').count()
            if rule_count > 0:
                by_rule[f'RULE_{i}'] = rule_count

        # 해결되지 않은 위반
        unresolved = violations.filter(is_resolved=False).count()

        # 최근 위반 목록
        recent_violations = []
        for violation in violations.order_by('-detected_at')[:10]:
            recent_violations.append({
                'id': violation.id,
                'product_code': violation.control_chart.product.product_code,
                'rule_type': violation.rule_type,
                'description': violation.get_rule_type_display(),
                'is_resolved': violation.is_resolved,
                'detected_at': violation.detected_at.isoformat()
            })

        return {
            'total': violations.count(),
            'unresolved': unresolved,
            'by_rule_type': by_rule,
            'recent_violations': recent_violations
        }

    def _generate_recommendations(self, products: List[Product],
                                 start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """개선 권장사항 생성"""
        recommendations = []

        for product in products:
            product_recommendations = []

            # 공정능력 기반 권장사항
            latest_capability = ProcessCapability.objects.filter(
                product=product
            ).order_by('-analyzed_at').first()

            if latest_capability and latest_capability.cpk and latest_capability.cpk < 1.33:
                product_recommendations.append({
                    'type': 'capability',
                    'priority': 'high' if latest_capability.cpk < 1.0 else 'medium',
                    'message': f'Cpk가 {latest_capability.cpk:.2f}로 낮습니다. 공정능력 개선이 필요합니다.',
                    'actions': [
                        '공정 평균을 목표값에 맞추세요',
                        '공정 산포를 줄이세요',
                        '측정 시스템을 점검하세요'
                    ]
                })

            # 불량률 기반 권장사항
            measurements = QualityMeasurement.objects.filter(
                product=product,
                measured_at__gte=start_date,
                measured_at__lt=end_date
            )

            if measurements.count() > 0:
                out_of_spec_rate = measurements.filter(is_within_spec=False).count() / measurements.count() * 100

                if out_of_spec_rate > 1.0:
                    product_recommendations.append({
                        'type': 'defect_rate',
                        'priority': 'urgent' if out_of_spec_rate > 5.0 else 'high',
                        'message': f'불량률이 {out_of_spec_rate:.2f}%입니다. 즉각적인 조치가 필요합니다.',
                        'actions': [
                            '관리 한계를 벗어난 포인트를 조사하세요',
                            '공정 파라미터를 확인하세요',
                            '작업자 교육을 실시하세요'
                        ]
                    })

            # 미해결 경고 기반 권장사항
            unresolved_alerts = QualityAlert.objects.filter(
                product=product,
                created_at__gte=start_date,
                status__in=['NEW', 'ACKNOWLEDGED', 'INVESTIGATING']
            ).count()

            if unresolved_alerts > 5:
                product_recommendations.append({
                    'type': 'alerts',
                    'priority': 'high',
                    'message': f'{unresolved_alerts}개의 미해결 경고가 있습니다.',
                    'actions': [
                        '미해결 경고를 우선순위별로 처리하세요',
                        '반복적인 경고의 근본 원인을 분석하세요',
                        '예방 조치를 계획하세요'
                    ]
                })

            if product_recommendations:
                recommendations.append({
                    'product_code': product.product_code,
                    'product_name': product.product_name,
                    'recommendations': product_recommendations
                })

        return recommendations


class ReportExporter:
    """보고서 내보내기 (PDF, Excel 등)"""

    @staticmethod
    def export_to_markdown(report_data: Dict[str, Any]) -> str:
        """Markdown 형식으로 내보내기"""
        lines = []

        # 헤더
        lines.append(f"# {report_data['report_type']} 품질 보고서")
        lines.append("")
        lines.append(f"**보고서 기간**: {report_data['period']['formatted']}")
        lines.append(f"**생성일시**: {report_data['generated_at']}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 요약
        lines.append("## 1. 요약 통계")
        lines.append("")
        summary = report_data['summary']
        lines.append(f"- **전체 제품**: {summary['total_products']}개")
        lines.append(f"- **전체 측정값**: {summary['total_measurements']}개")
        lines.append(f"- **규격 외률**: {summary['out_of_spec_rate']}% ({summary['out_of_spec_count']}개)")
        lines.append(f"- **관리한계 외율**: {summary['out_of_control_rate']}% ({summary['out_of_control_count']}개)")
        lines.append(f"- **총 경고**: {summary['total_alerts']}개")
        lines.append(f"- **긴급 경고**: {summary['critical_alerts']}개")
        lines.append(f"- **경고 해결률**: {summary['resolution_rate']}%")
        lines.append("")

        # 제품별 상세
        lines.append("## 2. 제품별 상세")
        lines.append("")
        for detail in report_data['product_details']:
            lines.append(f"### {detail['product_name']} ({detail['product_code']})")
            lines.append("")
            lines.append(f"- **측정 개수**: {detail['statistics']['total_measurements']}")
            lines.append(f"- **평균**: {detail['statistics']['average']}")
            lines.append(f"- **표준편차**: {detail['statistics']['std_dev']}")
            lines.append(f"- **불량률**: {detail['statistics']['out_of_spec_rate']}%")

            if detail['capability']['cpk']:
                cpk = detail['capability']['cpk']
                lines.append(f"- **Cpk**: {cpk}")
            lines.append("")

        # 공정능력 분석
        lines.append("## 3. 공정능력 분석")
        lines.append("")
        capability = report_data['capability_analysis']
        lines.append(f"- **분석 제품**: {capability['total_products_analyzed']}개")
        lines.append("")
        lines.append("### 등급별 분포")
        lines.append("")
        for grade, count in capability['grade_distribution'].items():
            lines.append(f"- **{grade}**: {count}개")
        lines.append("")

        # 경고 요약
        lines.append("## 4. 경고 요약")
        lines.append("")
        alerts = report_data['alerts_summary']
        lines.append(f"- **총 경고**: {alerts['total']}개")
        lines.append("")
        for priority, count in alerts['by_priority'].items():
            if count > 0:
                lines.append(f"- **{priority.upper()}**: {count}개")
        lines.append("")

        # 개선 권장사항
        lines.append("## 5. 개선 권장사항")
        lines.append("")
        for rec in report_data['recommendations']:
            lines.append(f"### {rec['product_name']}")
            lines.append("")
            for item in rec['recommendations']:
                lines.append(f"- **{item['message']}**")
                for action in item['actions']:
                    lines.append(f"  - {action}")
            lines.append("")

        return "\n".join(lines)

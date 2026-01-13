from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, StdDev, Count, Min, Max
from .models import (
    Product, InspectionPlan, QualityMeasurement, ControlChart,
    ProcessCapability, RunRuleViolation, QualityAlert, QualityReport
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'product_name', 'get_spec_range', 'target_value', 'measurement_count', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product_code', 'product_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'measurement_count']

    fieldsets = (
        ('기본 정보', {
            'fields': ('product_code', 'product_name', 'description')
        }),
        ('규격 설정', {
            'fields': ('usl', 'lsl', 'target_value', 'unit')
        }),
        ('품질 기준', {
            'fields': ('min_cpk_target', 'max_defect_rate_target')
        }),
        ('통계 정보', {
            'fields': ('measurement_count',),
            'classes': ('collapse',)
        }),
        ('관리', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def get_spec_range(self, obj):
        """규격 범위 표시"""
        return f"{obj.lsl} ~ {obj.usl} {obj.unit}"
    get_spec_range.short_description = '규격 범위'

    def measurement_count(self, obj):
        """측정 데이터 개수"""
        return obj.measurements.count()
    measurement_count.short_description = '측정 건수'


@admin.register(InspectionPlan)
class InspectionPlanAdmin(admin.ModelAdmin):
    list_display = ['plan_name', 'product', 'frequency', 'sample_size', 'subgroup_size', 'is_active']
    list_filter = ['frequency', 'is_active', 'sampling_method']
    search_fields = ['plan_name', 'product__product_code']


@admin.register(QualityMeasurement)
class QualityMeasurementAdmin(admin.ModelAdmin):
    list_display = ['product', 'get_value_with_status', 'subgroup_number', 'sample_number', 'measured_at', 'measured_by']
    list_filter = ['is_within_spec', 'is_within_control', 'measured_at', 'product', 'machine_id']
    search_fields = ['product__product_code', 'measured_by', 'lot_number', 'machine_id']
    date_hierarchy = 'measured_at'
    readonly_fields = ['created_at', 'get_deviation_from_target']

    fieldsets = (
        ('측정 정보', {
            'fields': ('product', 'inspection_plan', 'measurement_value', 'sample_number', 'subgroup_number')
        }),
        ('측정 메타데이터', {
            'fields': ('measured_at', 'measured_by', 'machine_id', 'lot_number', 'work_order_number')
        }),
        ('판정 결과', {
            'fields': ('is_within_spec', 'is_within_control', 'get_deviation_from_target')
        }),
        ('관리 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_value_with_status(self, obj):
        """측정값과 상태 색상 표시"""
        if not obj.is_within_spec:
            color = 'red'
            icon = '✖'
        elif not obj.is_within_control:
            color = 'orange'
            icon = '⚠'
        else:
            color = 'green'
            icon = '✔'

        return format_html(
            '<span style="color: {};">{} {} {}</span>',
            color,
            icon,
            obj.measurement_value,
            obj.product.unit
        )
    get_value_with_status.short_description = '측정값'

    def get_deviation_from_target(self, obj):
        """목표값으로부터 편차"""
        if obj.product.target_value:
            deviation = obj.measurement_value - obj.product.target_value
            return f"{deviation:+.4f} ({obj.product.target_value}) ±{abs(deviation / obj.product.target_value * 100):.2f}%"
        return "목표값 없음"
    get_deviation_from_target.short_description = '목표값 편차'


@admin.register(ControlChart)
class ControlChartAdmin(admin.ModelAdmin):
    list_display = ['product', 'chart_type', 'xbar_ucl', 'xbar_cl', 'xbar_lcl', 'is_active', 'calculated_at']
    list_filter = ['chart_type', 'is_active', 'product']
    search_fields = ['product__product_code']


@admin.register(ProcessCapability)
class ProcessCapabilityAdmin(admin.ModelAdmin):
    list_display = ['product', 'get_cpk_badge', 'cp', 'get_process_rating', 'is_normal', 'analyzed_at']
    list_filter = ['is_normal', 'analyzed_at', 'product']
    search_fields = ['product__product_code']
    date_hierarchy = 'analyzed_at'
    readonly_fields = ['analyzed_at', 'get_process_rating', 'get_capability_assessment']

    fieldsets = (
        ('분석 대상', {
            'fields': ('product', 'control_chart')
        }),
        ('공정능력 지수', {
            'fields': ('cp', 'cpk', 'cpu', 'cpl', 'pp', 'ppk')
        }),
        ('통계 정보', {
            'fields': ('mean', 'std_deviation', 'min_value', 'max_value', 'median')
        }),
        ('정규성 검정', {
            'fields': ('is_normal', 'normality_test', 'normality_p_value')
        }),
        ('샘플 정보', {
            'fields': ('sample_size', 'start_date', 'end_date')
        }),
        ('평가 결과', {
            'fields': ('get_process_rating', 'get_capability_assessment'),
            'classes': ('collapse',)
        }),
        ('분석 정보', {
            'fields': ('analyzed_at', 'analyzed_by'),
            'classes': ('collapse',)
        }),
    )

    def get_cpk_badge(self, obj):
        """Cpk 값에 따른 뱃지 표시"""
        if obj.cpk >= 2.0:
            color = '#10b981'  # green
            label = '우수'
        elif obj.cpk >= 1.67:
            color = '#3b82f6'  # blue
            label = '양호'
        elif obj.cpk >= 1.33:
            color = '#f59e0b'  # yellow
            label = '보통'
        elif obj.cpk >= 1.0:
            color = '#f97316'  # orange
            label = '미흡'
        else:
            color = '#ef4444'  # red
            label = '부적합'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;">{:.2f} ({})</span>',
            color, obj.cpk, label
        )
    get_cpk_badge.short_description = 'Cpk'

    def get_process_rating(self, obj):
        """공정능력 등급"""
        if obj.cpk >= 2.0:
            return "6σ 수준 (우수)"
        elif obj.cpk >= 1.67:
            return "5σ 수준 (양호)"
        elif obj.cpk >= 1.33:
            return "4σ 수준 (보통)"
        elif obj.cpk >= 1.0:
            return "3σ 수준 (미흡)"
        else:
            return "개선 필요 (부적합)"
    get_process_rating.short_description = '공정능력 등급'

    def get_capability_assessment(self, obj):
        """공정능력 종합 평가"""
        html = f"""
        <ul>
            <li>Cp (잠재 능력): <strong>{obj.cp:.3f}</strong></li>
            <li>Cpk (실제 능력): <strong>{obj.cpk:.3f}</strong></li>
            <li>Pp (성능): <strong>{obj.pp:.3f}</strong></li>
            <li>Ppk (실제 성능): <strong>{obj.ppk:.3f}</strong></li>
        </ul>
        """
        if obj.cpk < obj.product.min_cpk_target if obj.product.min_cpk_target else 1.33:
            html += '<p style="color: red;">⚠️ 목표 Cpk 미달! 개선 필요.</p>'
        else:
            html += '<p style="color: green;">✅ 목표 Cpk 달성.</p>'

        return format_html(html)
    get_capability_assessment.short_description = '공정능력 평가'


@admin.register(RunRuleViolation)
class RunRuleViolationAdmin(admin.ModelAdmin):
    list_display = ['get_rule_badge', 'control_chart', 'get_measurement_subgroup', 'severity', 'is_resolved', 'detected_at']
    list_filter = ['rule_type', 'severity', 'is_resolved', 'detected_at']
    search_fields = ['description', 'control_chart__product__product_code']
    date_hierarchy = 'detected_at'
    actions = ['mark_as_resolved', 'mark_as_unresolved']

    def get_measurement_subgroup(self, obj):
        """측정값의 부분군 번호 표시"""
        return obj.measurement.subgroup_number if obj.measurement else '-'
    get_measurement_subgroup.short_description = '부분군'

    def get_rule_badge(self, obj):
        """Rule 타입별 색상 뱃지"""
        colors = {
            'RULE_1': '#ef4444',  # red
            'RULE_2': '#f97316',  # orange
            'RULE_3': '#f59e0b',  # yellow
            'RULE_4': '#84cc16',  # lime
            'RULE_5': '#06b6d4',  # cyan
            'RULE_6': '#3b82f6',  # blue
            'RULE_7': '#8b5cf6',  # purple
            'RULE_8': '#ec4899',  # pink
        }
        color = colors.get(obj.rule_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.rule_type
        )
    get_rule_badge.short_description = 'Rule'

    def mark_as_resolved(self, request, queryset):
        """일괄 해결 처리"""
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f'{updated}개의 위반을 해결 처리했습니다.')
    mark_as_resolved.short_description = '선택 항목 해결 처리'

    def mark_as_unresolved(self, request, queryset):
        """일괄 미해결 처리"""
        updated = queryset.update(is_resolved=False)
        self.message_user(request, f'{updated}개의 위반을 미해결 처리했습니다.')
    mark_as_unresolved.short_description = '선택 항목 미해결 처리'


@admin.register(QualityAlert)
class QualityAlertAdmin(admin.ModelAdmin):
    list_display = ['get_priority_icon', 'title', 'product', 'alert_type', 'status_badge', 'assigned_to', 'created_at']
    list_filter = ['alert_type', 'priority', 'status', 'created_at']
    search_fields = ['title', 'description', 'product__product_code', 'resolution_notes']
    date_hierarchy = 'created_at'
    actions = ['acknowledge_alerts', 'close_alerts']

    fieldsets = (
        ('기본 정보', {
            'fields': ('product', 'measurement', 'violation', 'alert_type', 'title', 'description', 'priority')
        }),
        ('상태 관리', {
            'fields': ('status', 'assigned_to')
        }),
        ('처리 정보', {
            'fields': ('acknowledged_at', 'acknowledged_by', 'resolved_at', 'resolved_by', 'resolution_notes')
        }),
        ('근본 원인 분석', {
            'fields': ('root_cause', 'corrective_action', 'preventive_action'),
            'classes': ('collapse',)
        }),
    )

    def get_priority_icon(self, obj):
        """우선순위 아이콘 표시"""
        priority_labels = {1: 'LOW', 2: 'MEDIUM', 3: 'HIGH', 4: 'CRITICAL'}
        icons = {1: '🟢', 2: '🟡', 3: '🟠', 4: '🔴'}
        label = priority_labels.get(obj.priority, 'UNKNOWN')
        icon = icons.get(obj.priority, '⚪')
        return f"{icon} {label}"
    get_priority_icon.short_description = '우선순위'

    def status_badge(self, obj):
        """상태 뱃지 표시"""
        colors = {
            'NEW': '#ef4444',  # red
            'ACKNOWLEDGED': '#f59e0b',  # yellow
            'INVESTIGATING': '#3b82f6',  # blue
            'RESOLVED': '#10b981',  # green
            'CLOSED': '#6b7280',  # gray
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = '상태'

    def acknowledge_alerts(self, request, queryset):
        """일괄 확인 처리"""
        from django.utils import timezone
        updated = queryset.filter(status='NEW').update(
            status='ACKNOWLEDGED',
            acknowledged_at=timezone.now(),
            acknowledged_by=request.user.username if request.user else 'System'
        )
        self.message_user(request, f'{updated}개의 경고를 확인 처리했습니다.')
    acknowledge_alerts.short_description = '선택 항목 확인'

    def close_alerts(self, request, queryset):
        """일괄 종료 처리"""
        from django.utils import timezone
        updated = queryset.update(
            status='CLOSED',
            resolved_at=timezone.now(),
            resolved_by=request.user.username if request.user else 'System'
        )
        self.message_user(request, f'{updated}개의 경고를 종료 처리했습니다.')
    close_alerts.short_description = '선택 항목 종료'


@admin.register(QualityReport)
class QualityReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'start_date', 'end_date', 'generated_by', 'generated_at']
    list_filter = ['report_type', 'generated_at']
    search_fields = ['title', 'generated_by']
    date_hierarchy = 'generated_at'
    filter_horizontal = ['products']

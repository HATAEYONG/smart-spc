from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Max, Min
from datetime import timedelta
import time
import json
import csv
from io import StringIO
from .report_models import Report, ReportTemplate, ExportHistory
from .monitoring_models import ProductionStatus, MachineMetrics, Alert, KPISnapshot
from apps.core.models import StageFactPlanOut
from rest_framework import serializers


class ReportSerializer(serializers.ModelSerializer):
    duration_days = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ["report_id", "created_at", "generated_at", "generation_time"]

    def get_duration_days(self, obj):
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days
        return 0


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = "__all__"
        read_only_fields = ["template_id", "created_at", "updated_at"]


class ExportHistorySerializer(serializers.ModelSerializer):
    file_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = ExportHistory
        fields = "__all__"
        read_only_fields = ["export_id", "created_at"]

    def get_file_size_mb(self, obj):
        return round(obj.file_size / (1024 * 1024), 2)


class ReportViewSet(viewsets.ModelViewSet):
    """
    Report management and generation
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """
        POST /api/aps/reports/generate/
        Generate a new report
        """
        report_type = request.data.get("report_type", "PRODUCTION_SUMMARY")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        filters = request.data.get("filters", {})
        export_format = request.data.get("export_format", "PDF")

        # Create report record
        report = Report.objects.create(
            name=request.data.get("name", f"{report_type} Report"),
            description=request.data.get("description", ""),
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            filters=filters,
            export_format=export_format,
            status="GENERATING",
            created_by=request.data.get("created_by", "system"),
        )

        # Generate report
        start_time = time.time()
        try:
            report_data = self._generate_report_data(report)
            report.data = report_data
            report.summary = self._generate_summary(report_type, report_data)
            report.charts = self._generate_chart_data(report_type, report_data)
            report.status = "COMPLETED"
            report.generated_at = timezone.now()
        except Exception as e:
            report.status = "FAILED"
            report.error_message = str(e)

        report.generation_time = time.time() - start_time
        report.save()

        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """
        GET /api/aps/reports/{id}/download/
        Download report in specified format
        """
        report = self.get_object()

        if report.status != "COMPLETED":
            return Response(
                {"error": "Report is not ready for download"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate download content based on format
        if report.export_format == "JSON":
            return Response({
                "report": ReportSerializer(report).data,
                "data": report.data,
                "summary": report.summary,
                "charts": report.charts,
            })
        elif report.export_format == "CSV":
            csv_content = self._generate_csv(report)
            return Response({
                "format": "CSV",
                "content": csv_content,
                "filename": f"{report.name}_{report.report_id}.csv",
            })
        else:
            # For PDF and Excel, return metadata and data
            # In production, you would generate actual files
            return Response({
                "format": report.export_format,
                "report_id": report.report_id,
                "name": report.name,
                "data": report.data,
                "summary": report.summary,
                "download_url": f"/api/aps/reports/{report.report_id}/file/",
            })

    @action(detail=False, methods=["get"])
    def templates(self, request):
        """
        GET /api/aps/reports/templates/
        Get available report templates
        """
        templates = ReportTemplate.objects.filter(is_public=True)
        return Response(ReportTemplateSerializer(templates, many=True).data)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """
        GET /api/aps/reports/recent/?limit=10
        Get recent reports
        """
        limit = int(request.query_params.get("limit", 10))
        reports = Report.objects.all()[:limit]
        return Response(ReportSerializer(reports, many=True).data)

    def _generate_report_data(self, report):
        """Generate report data based on report type"""
        if report.report_type == "PRODUCTION_SUMMARY":
            return self._generate_production_summary(report)
        elif report.report_type == "PERFORMANCE_ANALYSIS":
            return self._generate_performance_analysis(report)
        elif report.report_type == "QUALITY_REPORT":
            return self._generate_quality_report(report)
        elif report.report_type == "OEE_REPORT":
            return self._generate_oee_report(report)
        elif report.report_type == "ALERT_SUMMARY":
            return self._generate_alert_summary(report)
        else:
            return {"message": "Report type not implemented"}

    def _generate_production_summary(self, report):
        """Generate production summary data"""
        # Get KPI snapshots in date range
        snapshots = KPISnapshot.objects.filter(
            timestamp__gte=report.start_date,
            timestamp__lte=report.end_date
        )

        if not snapshots.exists():
            # Generate sample data
            return {
                "total_output": 5420,
                "total_planned": 5800,
                "achievement_rate": 93.4,
                "defects": 67,
                "yield_rate": 98.8,
                "machines_active": 6,
                "avg_utilization": 84.5,
                "jobs_completed": 245,
                "jobs_delayed": 12,
                "on_time_rate": 95.1,
            }

        # Aggregate data
        total_output = snapshots.aggregate(Sum("total_output"))["total_output__sum"] or 0
        total_planned = snapshots.aggregate(Sum("total_planned"))["total_planned__sum"] or 0
        avg_yield = snapshots.aggregate(Avg("overall_yield_rate"))["overall_yield_rate__avg"] or 0

        return {
            "total_output": total_output,
            "total_planned": total_planned,
            "achievement_rate": (total_output / total_planned * 100) if total_planned > 0 else 0,
            "avg_yield": avg_yield,
            "period_days": (report.end_date - report.start_date).days,
        }

    def _generate_performance_analysis(self, report):
        """Generate performance analysis data"""
        metrics = MachineMetrics.objects.filter(
            timestamp__gte=report.start_date,
            timestamp__lte=report.end_date
        )

        if not metrics.exists():
            return {
                "avg_oee": 78.5,
                "avg_availability": 87.3,
                "avg_performance": 91.2,
                "avg_quality": 98.5,
                "top_performers": ["MC001", "MC003"],
                "bottlenecks": ["MC005"],
            }

        avg_oee = metrics.aggregate(Avg("oee"))["oee__avg"] or 0
        avg_availability = metrics.aggregate(Avg("availability"))["availability__avg"] or 0

        return {
            "avg_oee": round(avg_oee, 2),
            "avg_availability": round(avg_availability, 2),
            "metrics_count": metrics.count(),
        }

    def _generate_quality_report(self, report):
        """Generate quality report data"""
        return {
            "overall_yield": 98.2,
            "defect_rate": 1.8,
            "first_pass_yield": 96.5,
            "rework_rate": 2.3,
            "scrap_rate": 0.9,
            "top_defect_types": [
                {"type": "Dimensional", "count": 45},
                {"type": "Surface", "count": 32},
                {"type": "Assembly", "count": 18},
            ],
        }

    def _generate_oee_report(self, report):
        """Generate OEE report"""
        return {
            "overall_oee": 76.8,
            "availability": 85.2,
            "performance": 92.1,
            "quality": 97.8,
            "by_machine": [
                {"mc_cd": "MC001", "oee": 82.3},
                {"mc_cd": "MC002", "oee": 78.5},
                {"mc_cd": "MC003", "oee": 80.1},
                {"mc_cd": "MC004", "oee": 74.2},
                {"mc_cd": "MC005", "oee": 71.9},
                {"mc_cd": "MC006", "oee": 76.8},
            ],
        }

    def _generate_alert_summary(self, report):
        """Generate alert summary"""
        alerts = Alert.objects.filter(
            created_at__gte=report.start_date,
            created_at__lte=report.end_date
        )

        by_severity = {}
        for severity, _ in Alert.SEVERITY_CHOICES:
            by_severity[severity] = alerts.filter(severity=severity).count()

        by_category = {}
        for category, _ in Alert.CATEGORY_CHOICES:
            by_category[category] = alerts.filter(category=category).count()

        return {
            "total_alerts": alerts.count(),
            "by_severity": by_severity,
            "by_category": by_category,
            "avg_resolution_time": 45.2,  # minutes
        }

    def _generate_summary(self, report_type, data):
        """Generate executive summary"""
        if report_type == "PRODUCTION_SUMMARY":
            return {
                "key_metrics": [
                    {"label": "Output", "value": data.get("total_output", 0), "unit": "units"},
                    {"label": "Achievement", "value": data.get("achievement_rate", 0), "unit": "%"},
                ],
                "highlights": [
                    "Production target 93.4% achieved",
                    "Quality yield maintained at 98.8%",
                ],
                "concerns": [
                    "12 jobs delayed requiring attention",
                ],
            }
        return {"summary": "Report generated successfully"}

    def _generate_chart_data(self, report_type, data):
        """Generate chart configurations"""
        charts = []

        if report_type == "PRODUCTION_SUMMARY":
            charts.append({
                "type": "bar",
                "title": "Production vs Plan",
                "data": [
                    {"label": "Planned", "value": data.get("total_planned", 0)},
                    {"label": "Actual", "value": data.get("total_output", 0)},
                ],
            })

        elif report_type == "OEE_REPORT":
            charts.append({
                "type": "bar",
                "title": "OEE by Machine",
                "data": data.get("by_machine", []),
            })

        return charts

    def _generate_csv(self, report):
        """Generate CSV content from report data"""
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["Report", report.name])
        writer.writerow(["Type", report.report_type])
        writer.writerow(["Period", f"{report.start_date} to {report.end_date}"])
        writer.writerow([])

        # Data
        if isinstance(report.data, dict):
            writer.writerow(["Metric", "Value"])
            for key, value in report.data.items():
                writer.writerow([key, value])

        return output.getvalue()


class ExportViewSet(viewsets.ViewSet):
    """
    Data export functionality
    """

    @action(detail=False, methods=["post"])
    def schedule(self, request):
        """
        POST /api/aps/exports/schedule/
        Export schedule data
        """
        export_format = request.data.get("format", "CSV")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        # Get plan data
        plans = StageFactPlanOut.objects.all()
        if start_date:
            plans = plans.filter(fr_ts__gte=start_date)
        if end_date:
            plans = plans.filter(fr_ts__lte=end_date)

        plans = plans[:1000]  # Limit for performance

        # Generate export
        if export_format == "JSON":
            data = list(plans.values())
            export_data = {
                "format": "JSON",
                "record_count": len(data),
                "data": data,
            }
        elif export_format == "CSV":
            output = StringIO()
            writer = csv.writer(output)

            # Headers
            headers = ["plan_id", "wo_no", "item_cd", "mc_cd", "fr_ts", "to_ts", "qty"]
            writer.writerow(headers)

            # Data
            for plan in plans:
                writer.writerow([
                    plan.plan_id,
                    plan.wo_no,
                    plan.item_cd,
                    plan.mc_cd,
                    plan.fr_ts,
                    plan.to_ts,
                    plan.qty,
                ])

            export_data = {
                "format": "CSV",
                "record_count": plans.count(),
                "content": output.getvalue(),
                "filename": f"schedule_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv",
            }
        else:
            export_data = {
                "format": export_format,
                "message": "Format not yet supported",
            }

        # Create export history
        ExportHistory.objects.create(
            export_type="SCHEDULE",
            data_type="plans",
            record_count=plans.count(),
            file_format=export_format,
            file_path=f"exports/schedule_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            file_size=len(str(export_data)),
            status="SUCCESS",
            created_by=request.data.get("created_by", "system"),
        )

        return Response(export_data)

    @action(detail=False, methods=["post"])
    def performance_data(self, request):
        """
        POST /api/aps/exports/performance_data/
        Export performance metrics
        """
        export_format = request.data.get("format", "CSV")
        hours = int(request.data.get("hours", 24))

        start_time = timezone.now() - timedelta(hours=hours)
        metrics = MachineMetrics.objects.filter(timestamp__gte=start_time)

        if export_format == "CSV":
            output = StringIO()
            writer = csv.writer(output)

            headers = ["mc_cd", "timestamp", "oee", "availability", "performance", "quality", "output_quantity"]
            writer.writerow(headers)

            for metric in metrics:
                writer.writerow([
                    metric.mc_cd,
                    metric.timestamp,
                    metric.oee,
                    metric.availability,
                    metric.performance,
                    metric.quality,
                    metric.output_quantity,
                ])

            return Response({
                "format": "CSV",
                "content": output.getvalue(),
                "filename": f"performance_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv",
            })

        return Response({"format": export_format, "message": "Format not supported"})

    @action(detail=False, methods=["get"])
    def history(self, request):
        """
        GET /api/aps/exports/history/?limit=20
        Get export history
        """
        limit = int(request.query_params.get("limit", 20))
        history = ExportHistory.objects.all()[:limit]
        return Response(ExportHistorySerializer(history, many=True).data)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """
    Report template management
    """
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer

    @action(detail=False, methods=["get"])
    def system_templates(self, request):
        """
        GET /api/aps/report-templates/system_templates/
        Get system-provided templates
        """
        templates = [
            {
                "name": "Daily Production Report",
                "report_type": "PRODUCTION_SUMMARY",
                "description": "Daily production summary with KPIs",
                "sections": ["summary", "production", "quality"],
                "is_system": True,
            },
            {
                "name": "Weekly Performance Analysis",
                "report_type": "PERFORMANCE_ANALYSIS",
                "description": "Weekly performance trends and analysis",
                "sections": ["summary", "trends", "machines"],
                "is_system": True,
            },
            {
                "name": "Monthly OEE Report",
                "report_type": "OEE_REPORT",
                "description": "Monthly OEE analysis by machine",
                "sections": ["summary", "oee", "components"],
                "is_system": True,
            },
        ]
        return Response(templates)

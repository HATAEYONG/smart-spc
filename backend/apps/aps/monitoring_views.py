from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
from datetime import timedelta
import random
from .monitoring_models import ProductionStatus, MachineMetrics, Alert, KPISnapshot
from rest_framework import serializers


class ProductionStatusSerializer(serializers.ModelSerializer):
    progress_status = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = ProductionStatus
        fields = "__all__"

    def get_progress_status(self, obj):
        if obj.progress_percentage >= 100:
            return "completed"
        elif obj.progress_percentage >= 75:
            return "near_completion"
        elif obj.progress_percentage >= 25:
            return "in_progress"
        else:
            return "started"

    def get_time_remaining(self, obj):
        if obj.estimated_completion:
            remaining = (obj.estimated_completion - timezone.now()).total_seconds() / 60
            return max(0, remaining)
        return None


class MachineMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineMetrics
        fields = "__all__"


class AlertSerializer(serializers.ModelSerializer):
    age_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = "__all__"

    def get_age_minutes(self, obj):
        return (timezone.now() - obj.created_at).total_seconds() / 60


class KPISnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPISnapshot
        fields = "__all__"


class MonitoringViewSet(viewsets.ViewSet):
    """
    Real-time monitoring dashboard endpoints
    """

    @action(detail=False, methods=["get"])
    def realtime_status(self, request):
        """
        GET /api/aps/monitoring/realtime_status/
        Get current production status for all machines
        """
        # Generate or fetch real-time data
        machines = ["MC001", "MC002", "MC003", "MC004", "MC005", "MC006"]

        statuses = []
        for mc in machines:
            # Try to get existing status or create simulated one
            status_obj, created = ProductionStatus.objects.get_or_create(
                mc_cd=mc,
                defaults=self._generate_machine_status(mc)
            )

            if not created and random.random() > 0.7:  # Update 30% of the time
                for key, value in self._generate_machine_status(mc).items():
                    setattr(status_obj, key, value)
                status_obj.save()

            statuses.append(ProductionStatusSerializer(status_obj).data)

        return Response({
            "timestamp": timezone.now().isoformat(),
            "machines": statuses,
            "total_machines": len(machines),
            "running": len([s for s in statuses if s["status"] == "RUNNING"]),
            "idle": len([s for s in statuses if s["status"] == "IDLE"]),
            "down": len([s for s in statuses if s["status"] in ["BREAKDOWN", "MAINTENANCE"]]),
        })

    @action(detail=False, methods=["get"])
    def kpi_summary(self, request):
        """
        GET /api/aps/monitoring/kpi_summary/
        Get current KPI summary
        """
        # Create or get latest snapshot
        latest = KPISnapshot.objects.filter(
            snapshot_type="REALTIME"
        ).order_by("-timestamp").first()

        if not latest or (timezone.now() - latest.timestamp).total_seconds() > 300:  # 5 minutes
            latest = self._create_kpi_snapshot()

        return Response(KPISnapshotSerializer(latest).data)

    @action(detail=False, methods=["get"])
    def performance_trends(self, request):
        """
        GET /api/aps/monitoring/performance_trends/?hours=24
        Get performance trends over time
        """
        hours = int(request.query_params.get("hours", 24))
        mc_cd = request.query_params.get("mc_cd")

        start_time = timezone.now() - timedelta(hours=hours)

        # Get hourly metrics
        query = MachineMetrics.objects.filter(
            timestamp__gte=start_time,
            bucket_type="HOUR"
        )

        if mc_cd:
            query = query.filter(mc_cd=mc_cd)

        metrics = query.order_by("timestamp")

        # If no data, generate sample data
        if not metrics.exists():
            metrics = self._generate_sample_metrics(hours, mc_cd)
        else:
            metrics = list(metrics.values())

        # Calculate trends
        if len(metrics) > 1:
            recent_avg = sum(m["oee"] for m in metrics[-6:]) / min(6, len(metrics))
            previous_avg = sum(m["oee"] for m in metrics[:6]) / min(6, len(metrics))
            trend = "up" if recent_avg > previous_avg else "down"
        else:
            trend = "stable"

        return Response({
            "metrics": metrics,
            "trend": trend,
            "period_hours": hours,
        })

    @action(detail=False, methods=["get"])
    def active_alerts(self, request):
        """
        GET /api/aps/monitoring/active_alerts/?severity=CRITICAL
        Get active alerts
        """
        severity = request.query_params.get("severity")
        category = request.query_params.get("category")

        alerts = Alert.objects.filter(status="ACTIVE")

        if severity:
            alerts = alerts.filter(severity=severity)
        if category:
            alerts = alerts.filter(category=category)

        alerts = alerts.order_by("-severity", "-created_at")[:50]

        # If no alerts, create some sample ones
        if not alerts.exists():
            alerts = self._create_sample_alerts()

        return Response({
            "alerts": AlertSerializer(alerts, many=True).data,
            "total_count": alerts.count(),
        })

    @action(detail=False, methods=["get"])
    def machine_details(self, request):
        """
        GET /api/aps/monitoring/machine_details/?mc_cd=MC001
        Get detailed machine information
        """
        mc_cd = request.query_params.get("mc_cd")
        if not mc_cd:
            return Response(
                {"error": "mc_cd parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Current status
        current_status = ProductionStatus.objects.filter(mc_cd=mc_cd).first()
        if not current_status:
            current_status = ProductionStatus.objects.create(
                mc_cd=mc_cd,
                **self._generate_machine_status(mc_cd)
            )

        # Recent metrics (last 24 hours)
        start_time = timezone.now() - timedelta(hours=24)
        recent_metrics = MachineMetrics.objects.filter(
            mc_cd=mc_cd,
            timestamp__gte=start_time
        ).order_by("-timestamp")[:24]

        # Machine alerts
        machine_alerts = Alert.objects.filter(
            mc_cd=mc_cd,
            status="ACTIVE"
        ).order_by("-created_at")[:10]

        return Response({
            "mc_cd": mc_cd,
            "current_status": ProductionStatusSerializer(current_status).data,
            "recent_metrics": MachineMetricsSerializer(recent_metrics, many=True).data,
            "active_alerts": AlertSerializer(machine_alerts, many=True).data,
        })

    def _generate_machine_status(self, mc_cd):
        """Generate realistic machine status"""
        statuses = ["RUNNING", "IDLE", "SETUP", "RUNNING", "RUNNING"]  # Weighted towards RUNNING
        current_status = random.choice(statuses)

        data = {
            "mc_nm": f"Machine {mc_cd}",
            "status": current_status,
            "last_updated": timezone.now(),
        }

        if current_status == "RUNNING":
            data.update({
                "current_wo_no": f"WO{random.randint(1000, 9999)}",
                "current_item_cd": f"ITEM{random.randint(100, 999)}",
                "planned_quantity": random.randint(100, 500),
                "completed_quantity": random.randint(30, 450),
                "progress_percentage": random.uniform(10, 95),
                "job_start_time": timezone.now() - timedelta(hours=random.uniform(0.5, 8)),
                "estimated_completion": timezone.now() + timedelta(hours=random.uniform(1, 6)),
                "current_cycle_time": random.uniform(30, 120),
                "average_cycle_time": random.uniform(40, 100),
                "utilization_rate": random.uniform(70, 95),
                "oee": random.uniform(65, 90),
            })
        else:
            data.update({
                "utilization_rate": random.uniform(0, 30),
                "oee": random.uniform(0, 40),
            })

        # Random alerts
        if random.random() < 0.2:  # 20% chance of alert
            data.update({
                "has_alert": True,
                "alert_type": random.choice(["QUALITY", "DELAY", "MAINTENANCE"]),
                "alert_message": "Attention required",
            })

        return data

    def _create_kpi_snapshot(self):
        """Create new KPI snapshot with realistic data"""
        total_machines = 6
        running = random.randint(3, 6)
        idle = random.randint(0, 2)
        down = total_machines - running - idle

        snapshot = KPISnapshot.objects.create(
            total_output=random.randint(500, 1200),
            total_planned=random.randint(600, 1300),
            plan_achievement_rate=random.uniform(85, 105),
            total_defects=random.randint(5, 30),
            overall_yield_rate=random.uniform(95, 99.5),
            first_pass_yield=random.uniform(92, 98),
            avg_utilization=random.uniform(70, 90),
            avg_oee=random.uniform(65, 85),
            machines_running=running,
            machines_idle=idle,
            machines_down=down,
            jobs_completed=random.randint(20, 50),
            jobs_in_progress=random.randint(10, 30),
            jobs_delayed=random.randint(0, 5),
            on_time_delivery_rate=random.uniform(92, 99),
            active_alerts=random.randint(0, 8),
            critical_alerts=random.randint(0, 2),
            snapshot_type="REALTIME",
        )

        return snapshot

    def _generate_sample_metrics(self, hours, mc_cd=None):
        """Generate sample hourly metrics"""
        metrics = []
        machines = [mc_cd] if mc_cd else ["MC001", "MC002", "MC003"]

        for hour in range(hours):
            timestamp = timezone.now() - timedelta(hours=hours - hour)

            for mc in machines:
                output = random.randint(40, 80)
                defects = random.randint(0, 5)
                runtime = random.uniform(40, 58)
                downtime = random.uniform(0, 10)

                availability = (runtime / 60) * 100
                performance = random.uniform(85, 98)
                quality = ((output - defects) / output * 100) if output > 0 else 100
                oee = (availability * performance * quality) / 10000

                metrics.append({
                    "mc_cd": mc,
                    "timestamp": timestamp.isoformat(),
                    "bucket_type": "HOUR",
                    "output_quantity": output,
                    "defect_quantity": defects,
                    "yield_rate": quality,
                    "runtime_minutes": runtime,
                    "downtime_minutes": downtime,
                    "utilization_rate": availability,
                    "availability": availability,
                    "performance": performance,
                    "quality": quality,
                    "oee": oee,
                })

        return metrics

    def _create_sample_alerts(self):
        """Create sample alerts"""
        alert_templates = [
            {
                "severity": "WARNING",
                "category": "QUALITY",
                "title": "High defect rate detected",
                "message": "Defect rate on MC003 exceeded 5% threshold",
                "mc_cd": "MC003",
            },
            {
                "severity": "CRITICAL",
                "category": "MACHINE",
                "title": "Machine temperature high",
                "message": "MC001 operating temperature reached 85°C",
                "mc_cd": "MC001",
            },
            {
                "severity": "WARNING",
                "category": "SCHEDULE",
                "title": "Job running behind schedule",
                "message": "WO1234 is 30 minutes behind planned completion",
                "wo_no": "WO1234",
            },
        ]

        alerts = []
        for template in alert_templates[:random.randint(1, 3)]:
            alert = Alert.objects.create(
                **template,
                recommended_action="Review and take corrective action",
                created_at=timezone.now() - timedelta(minutes=random.randint(5, 120))
            )
            alerts.append(alert)

        return alerts


class AlertViewSet(viewsets.ModelViewSet):
    """
    Alert management endpoints
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        """
        POST /api/aps/alerts/{id}/acknowledge/
        Acknowledge an alert
        """
        alert = self.get_object()
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.data.get("user", "system")
        alert.save()

        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """
        POST /api/aps/alerts/{id}/resolve/
        Resolve an alert
        """
        alert = self.get_object()
        alert.status = "RESOLVED"
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.data.get("user", "system")
        alert.action_taken = request.data.get("action_taken", "")
        alert.save()

        return Response(AlertSerializer(alert).data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        GET /api/aps/alerts/summary/
        Get alert summary statistics
        """
        active_alerts = Alert.objects.filter(status="ACTIVE")

        summary = {
            "total_active": active_alerts.count(),
            "by_severity": {
                "critical": active_alerts.filter(severity="CRITICAL").count(),
                "error": active_alerts.filter(severity="ERROR").count(),
                "warning": active_alerts.filter(severity="WARNING").count(),
                "info": active_alerts.filter(severity="INFO").count(),
            },
            "by_category": {},
            "oldest_unresolved": None,
        }

        # Count by category
        for category, _ in Alert.CATEGORY_CHOICES:
            summary["by_category"][category.lower()] = active_alerts.filter(
                category=category
            ).count()

        # Oldest unresolved
        oldest = active_alerts.order_by("created_at").first()
        if oldest:
            summary["oldest_unresolved"] = {
                "alert_id": oldest.alert_id,
                "title": oldest.title,
                "age_hours": (timezone.now() - oldest.created_at).total_seconds() / 3600,
            }

        return Response(summary)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from .constraint_models import Constraint, ConstraintViolation, ConstraintGroup, ConstraintTemplate
from rest_framework import serializers


class ConstraintSerializer(serializers.ModelSerializer):
    violation_count = serializers.SerializerMethodField()

    class Meta:
        model = Constraint
        fields = "__all__"
        read_only_fields = ["constraint_id", "created_at", "updated_at"]

    def get_violation_count(self, obj):
        return obj.violations.filter(is_resolved=False).count()


class ConstraintViolationSerializer(serializers.ModelSerializer):
    constraint_name = serializers.CharField(source="constraint.name", read_only=True)

    class Meta:
        model = ConstraintViolation
        fields = "__all__"
        read_only_fields = ["violation_id", "detected_at", "resolved_at"]


class ConstraintGroupSerializer(serializers.ModelSerializer):
    constraint_count = serializers.SerializerMethodField()

    class Meta:
        model = ConstraintGroup
        fields = "__all__"
        read_only_fields = ["group_id", "created_at"]

    def get_constraint_count(self, obj):
        return obj.constraints.count()


class ConstraintTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintTemplate
        fields = "__all__"
        read_only_fields = ["template_id", "created_at", "usage_count"]


class ConstraintViewSet(viewsets.ModelViewSet):
    """
    API endpoint for constraint management
    """
    queryset = Constraint.objects.all()
    serializer_class = ConstraintSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by type
        constraint_type = self.request.query_params.get("type")
        if constraint_type:
            qs = qs.filter(constraint_type=constraint_type)

        # Filter by active status
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")

        # Filter by priority
        priority = self.request.query_params.get("priority")
        if priority:
            qs = qs.filter(priority=priority)

        return qs

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        POST /api/aps/constraints/{id}/toggle_active/
        Toggle constraint active status
        """
        constraint = self.get_object()
        constraint.is_active = not constraint.is_active
        constraint.save()

        return Response(
            {
                "constraint_id": constraint.constraint_id,
                "is_active": constraint.is_active,
            }
        )

    @action(detail=True, methods=["post"])
    def validate(self, request, pk=None):
        """
        POST /api/aps/constraints/{id}/validate/
        Validate constraint against current schedule
        """
        constraint = self.get_object()

        # Simulate validation
        violations = self._validate_constraint(constraint)

        return Response(
            {
                "constraint_id": constraint.constraint_id,
                "is_valid": len(violations) == 0,
                "violation_count": len(violations),
                "violations": violations,
            }
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        GET /api/aps/constraints/summary/
        Get constraint summary statistics
        """
        total = Constraint.objects.count()
        active = Constraint.objects.filter(is_active=True).count()
        by_type = list(
            Constraint.objects.values("constraint_type")
            .annotate(count=Count("constraint_id"))
            .order_by("-count")
        )
        by_priority = list(
            Constraint.objects.values("priority")
            .annotate(count=Count("constraint_id"))
            .order_by("-count")
        )

        # Violation stats
        unresolved_violations = ConstraintViolation.objects.filter(is_resolved=False).count()
        critical_violations = ConstraintViolation.objects.filter(
            severity="CRITICAL", is_resolved=False
        ).count()

        return Response(
            {
                "total_constraints": total,
                "active_constraints": active,
                "by_type": by_type,
                "by_priority": by_priority,
                "unresolved_violations": unresolved_violations,
                "critical_violations": critical_violations,
            }
        )

    def _validate_constraint(self, constraint):
        """Simulate constraint validation"""
        violations = []

        # Simulate some violations based on constraint type
        if constraint.constraint_type == "MACHINE_AVAILABILITY":
            # Simulate validation
            if not constraint.parameters.get("machine"):
                violations.append(
                    {
                        "severity": "WARNING",
                        "description": "Machine not specified in constraint parameters",
                    }
                )

        elif constraint.constraint_type == "PRECEDENCE":
            # Check if jobs exist
            job_a = constraint.parameters.get("job_a")
            job_b = constraint.parameters.get("job_b")
            if not job_a or not job_b:
                violations.append(
                    {
                        "severity": "CRITICAL",
                        "description": "Both jobs must be specified for precedence constraint",
                    }
                )

        return violations


class ConstraintViolationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for constraint violations
    """
    queryset = ConstraintViolation.objects.all()
    serializer_class = ConstraintViolationSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by severity
        severity = self.request.query_params.get("severity")
        if severity:
            qs = qs.filter(severity=severity)

        # Filter by resolved status
        is_resolved = self.request.query_params.get("is_resolved")
        if is_resolved is not None:
            qs = qs.filter(is_resolved=is_resolved.lower() == "true")

        # Filter by constraint
        constraint_id = self.request.query_params.get("constraint_id")
        if constraint_id:
            qs = qs.filter(constraint_id=constraint_id)

        return qs

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """
        POST /api/aps/violations/{id}/resolve/
        Mark violation as resolved
        """
        violation = self.get_object()
        violation.is_resolved = True
        violation.resolved_at = timezone.now()
        violation.resolution_notes = request.data.get("notes", "")
        violation.save()

        return Response(ConstraintViolationSerializer(violation).data)


class ConstraintGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for constraint groups
    """
    queryset = ConstraintGroup.objects.all()
    serializer_class = ConstraintGroupSerializer

    @action(detail=True, methods=["post"])
    def add_constraint(self, request, pk=None):
        """
        POST /api/aps/constraint-groups/{id}/add_constraint/
        Add constraint to group
        """
        group = self.get_object()
        constraint_id = request.data.get("constraint_id")

        try:
            constraint = Constraint.objects.get(constraint_id=constraint_id)
            group.constraints.add(constraint)
            return Response({"message": "Constraint added to group"})
        except Constraint.DoesNotExist:
            return Response(
                {"error": "Constraint not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"])
    def remove_constraint(self, request, pk=None):
        """
        POST /api/aps/constraint-groups/{id}/remove_constraint/
        Remove constraint from group
        """
        group = self.get_object()
        constraint_id = request.data.get("constraint_id")

        try:
            constraint = Constraint.objects.get(constraint_id=constraint_id)
            group.constraints.remove(constraint)
            return Response({"message": "Constraint removed from group"})
        except Constraint.DoesNotExist:
            return Response(
                {"error": "Constraint not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ConstraintTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for constraint templates
    """
    queryset = ConstraintTemplate.objects.all()
    serializer_class = ConstraintTemplateSerializer

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        """
        POST /api/aps/constraint-templates/{id}/apply/
        Create constraint from template
        """
        template = self.get_object()

        # Create constraint from template
        constraint = Constraint.objects.create(
            name=request.data.get("name", template.name),
            description=template.description,
            constraint_type=template.constraint_type,
            parameters=template.template_parameters.copy(),
            priority=request.data.get("priority", "MEDIUM"),
            created_by=request.data.get("created_by"),
        )

        # Increment usage count
        template.usage_count += 1
        template.save()

        return Response(
            ConstraintSerializer(constraint).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])
    def system_templates(self, request):
        """
        GET /api/aps/constraint-templates/system_templates/
        Get system-provided templates
        """
        templates = [
            {
                "name": "작업 간 최소 간격",
                "description": "두 작업 사이에 최소 시간 간격을 설정합니다",
                "constraint_type": "PRECEDENCE",
                "template_parameters": {
                    "job_a": "",
                    "job_b": "",
                    "min_lag": 60,
                },
            },
            {
                "name": "기계 가동 시간 제한",
                "description": "기계의 일일 가동 시간을 제한합니다",
                "constraint_type": "MACHINE_AVAILABILITY",
                "template_parameters": {
                    "machine": "",
                    "daily_hours": 16,
                    "start_time": "08:00",
                    "end_time": "00:00",
                },
            },
            {
                "name": "준비 시간 규칙",
                "description": "품목 간 전환 시 필요한 준비 시간을 설정합니다",
                "constraint_type": "SETUP_TIME",
                "template_parameters": {
                    "from_item": "",
                    "to_item": "",
                    "setup_time": 30,
                },
            },
            {
                "name": "배치 크기 제약",
                "description": "작업의 최소/최대 배치 크기를 제한합니다",
                "constraint_type": "BATCH_SIZE",
                "template_parameters": {
                    "item": "",
                    "min_batch": 10,
                    "max_batch": 100,
                },
            },
            {
                "name": "작업 시간 창",
                "description": "작업이 수행될 수 있는 시간 범위를 지정합니다",
                "constraint_type": "TIME_WINDOW",
                "template_parameters": {
                    "job": "",
                    "earliest_start": "",
                    "latest_finish": "",
                },
            },
        ]

        return Response({"templates": templates})

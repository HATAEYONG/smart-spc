from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import random
import time
from apps.core.models import StageFactPlanOut
from .sequence_models import JobSequence, SequenceOptimization, SequenceComparison
from rest_framework import serializers


class JobSequenceSerializer(serializers.ModelSerializer):
    job_count = serializers.SerializerMethodField()

    class Meta:
        model = JobSequence
        fields = "__all__"
        read_only_fields = ["sequence_id", "created_at", "updated_at"]

    def get_job_count(self, obj):
        return len(obj.job_sequence) if obj.job_sequence else 0


class SequenceOptimizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceOptimization
        fields = "__all__"
        read_only_fields = ["optimization_id", "created_at", "execution_time"]


class SequenceComparisonSerializer(serializers.ModelSerializer):
    sequence_count = serializers.SerializerMethodField()

    class Meta:
        model = SequenceComparison
        fields = "__all__"
        read_only_fields = ["comparison_id", "created_at"]

    def get_sequence_count(self, obj):
        return obj.sequences.count()


class JobSequenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for job sequence management
    """
    queryset = JobSequence.objects.all()
    serializer_class = JobSequenceSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by machine
        mc_cd = self.request.query_params.get("mc_cd")
        if mc_cd:
            qs = qs.filter(mc_cd=mc_cd)

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        """
        POST /api/aps/job-sequences/{id}/apply/
        Apply this sequence to the schedule
        """
        sequence = self.get_object()

        # In a real implementation, this would update the actual schedule
        # For now, we simulate the application
        try:
            # Update sequence status
            sequence.status = "ACTIVE"
            sequence.save()

            # Archive other sequences for the same machine
            if sequence.mc_cd:
                JobSequence.objects.filter(
                    mc_cd=sequence.mc_cd,
                    status="ACTIVE"
                ).exclude(sequence_id=sequence.sequence_id).update(status="ARCHIVED")

            return Response({
                "message": f"Sequence '{sequence.name}' applied successfully",
                "sequence_id": sequence.sequence_id,
                "job_count": len(sequence.job_sequence),
            })

        except Exception as e:
            return Response(
                {"error": f"Failed to apply sequence: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def reorder(self, request, pk=None):
        """
        POST /api/aps/job-sequences/{id}/reorder/
        Reorder jobs in the sequence
        Body: { "job_sequence": ["job1", "job2", "job3"] }
        """
        sequence = self.get_object()
        new_sequence = request.data.get("job_sequence", [])

        if not new_sequence:
            return Response(
                {"error": "job_sequence is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update sequence
        sequence.job_sequence = new_sequence
        sequence.updated_at = timezone.now()

        # Recalculate metrics
        metrics = self._calculate_sequence_metrics(new_sequence)
        sequence.estimated_makespan = metrics.get("makespan")
        sequence.estimated_tardiness = metrics.get("tardiness")
        sequence.estimated_flowtime = metrics.get("flowtime")

        sequence.save()

        return Response(JobSequenceSerializer(sequence).data)

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        """
        POST /api/aps/job-sequences/{id}/clone/
        Clone a sequence
        """
        original = self.get_object()

        clone = JobSequence.objects.create(
            name=f"{original.name} (Copy)",
            description=original.description,
            mc_cd=original.mc_cd,
            job_sequence=original.job_sequence.copy() if original.job_sequence else [],
            sequencing_rule=original.sequencing_rule,
            status="DRAFT",
            created_by=request.data.get("created_by"),
        )

        return Response(
            JobSequenceSerializer(clone).data,
            status=status.HTTP_201_CREATED
        )

    def _calculate_sequence_metrics(self, job_sequence):
        """Calculate estimated metrics for a job sequence"""
        if not job_sequence:
            return {"makespan": 0, "tardiness": 0, "flowtime": 0}

        # Simulate metric calculation
        # In real implementation, this would use actual job data
        job_count = len(job_sequence)
        avg_processing_time = 45  # minutes

        makespan = job_count * avg_processing_time * random.uniform(0.8, 1.0)
        tardiness = sum([random.uniform(0, 30) for _ in range(int(job_count * 0.3))])
        flowtime = makespan * random.uniform(1.2, 1.5)

        return {
            "makespan": round(makespan, 2),
            "tardiness": round(tardiness, 2),
            "flowtime": round(flowtime, 2),
        }


class SequenceOptimizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for sequence optimization
    """
    queryset = SequenceOptimization.objects.all()
    serializer_class = SequenceOptimizationSerializer

    @action(detail=False, methods=["post"])
    def optimize(self, request):
        """
        POST /api/aps/sequence-optimizations/optimize/
        Run sequence optimization with multiple rules
        """
        mc_cd = request.data.get("mc_cd")
        job_ids = request.data.get("job_ids", [])
        objective = request.data.get("objective", "MAKESPAN")

        if not job_ids:
            return Response(
                {"error": "job_ids is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create optimization record
        optimization = SequenceOptimization.objects.create(
            name=request.data.get("name", f"Optimization {timezone.now().strftime('%Y-%m-%d %H:%M')}"),
            description=request.data.get("description", ""),
            mc_cd=mc_cd or "",
            job_ids=job_ids,
            objective=objective,
            created_by=request.data.get("created_by"),
        )

        # Run optimization
        start_time = time.time()
        results = self._run_optimization(job_ids, objective)
        execution_time = time.time() - start_time

        # Save results
        optimization.results = results
        optimization.execution_time = execution_time

        # Find best sequence
        best_result = min(results, key=lambda x: x["score"])

        # Create best sequence
        best_sequence = JobSequence.objects.create(
            name=f"{optimization.name} - Best ({best_result['rule']})",
            description=f"Optimized using {best_result['rule']} rule",
            mc_cd=mc_cd or "",
            job_sequence=best_result["sequence"],
            sequencing_rule=best_result["rule"],
            estimated_makespan=best_result["metrics"]["makespan"],
            estimated_tardiness=best_result["metrics"]["tardiness"],
            estimated_flowtime=best_result["metrics"]["flowtime"],
            status="DRAFT",
        )

        optimization.best_sequence = best_sequence
        optimization.save()

        return Response(
            SequenceOptimizationSerializer(optimization).data,
            status=status.HTTP_201_CREATED
        )

    def _run_optimization(self, job_ids, objective):
        """Run optimization with multiple sequencing rules"""
        results = []

        # Define sequencing rules to try
        rules = ["FIFO", "SPT", "LPT", "EDD", "CR", "SLACK", "WSPT"]

        for rule in rules:
            # Generate sequence based on rule
            sequence = self._apply_rule(job_ids, rule)

            # Calculate metrics
            metrics = self._calculate_metrics(sequence, objective)

            # Calculate score based on objective
            score = self._calculate_score(metrics, objective)

            results.append({
                "rule": rule,
                "sequence": sequence,
                "metrics": metrics,
                "score": score,
            })

        return results

    def _apply_rule(self, job_ids, rule):
        """Apply sequencing rule to job list"""
        # In real implementation, this would use actual job data
        # For simulation, we just reorder the job_ids

        if rule == "FIFO":
            return job_ids.copy()
        elif rule == "LIFO":
            return list(reversed(job_ids))
        elif rule == "SPT":
            # Simulate sorting by processing time
            return sorted(job_ids, key=lambda x: hash(x) % 100)
        elif rule == "LPT":
            return sorted(job_ids, key=lambda x: hash(x) % 100, reverse=True)
        elif rule == "EDD":
            # Simulate sorting by due date
            return sorted(job_ids, key=lambda x: hash(x + "due") % 1000)
        elif rule == "CR":
            # Critical Ratio
            return sorted(job_ids, key=lambda x: (hash(x + "due") % 1000) / max(hash(x) % 100, 1))
        elif rule == "SLACK":
            # Minimum Slack
            return sorted(job_ids, key=lambda x: (hash(x + "due") % 1000) - (hash(x) % 100))
        elif rule == "WSPT":
            # Weighted SPT
            return sorted(job_ids, key=lambda x: (hash(x) % 100) / max(hash(x + "weight") % 10, 1))
        else:
            return job_ids.copy()

    def _calculate_metrics(self, sequence, objective):
        """Calculate performance metrics for a sequence"""
        job_count = len(sequence)

        # Simulate metrics
        processing_times = [random.uniform(20, 80) for _ in sequence]
        due_dates = [random.uniform(100, 500) for _ in sequence]

        # Makespan
        makespan = sum(processing_times)

        # Flow times and tardiness
        completion_times = []
        current_time = 0
        total_tardiness = 0
        total_flowtime = 0

        for i, job in enumerate(sequence):
            current_time += processing_times[i]
            completion_times.append(current_time)
            flowtime = current_time
            tardiness = max(0, current_time - due_dates[i])

            total_flowtime += flowtime
            total_tardiness += tardiness

        return {
            "makespan": round(makespan, 2),
            "tardiness": round(total_tardiness, 2),
            "flowtime": round(total_flowtime, 2),
            "avg_flowtime": round(total_flowtime / job_count, 2) if job_count > 0 else 0,
        }

    def _calculate_score(self, metrics, objective):
        """Calculate score based on objective"""
        if objective == "MAKESPAN":
            return metrics["makespan"]
        elif objective == "TARDINESS":
            return metrics["tardiness"]
        elif objective == "FLOWTIME":
            return metrics["flowtime"]
        elif objective == "WEIGHTED_TARDINESS":
            return metrics["tardiness"] * 1.5
        elif objective == "MULTI_OBJECTIVE":
            # Weighted sum
            return (
                metrics["makespan"] * 0.3 +
                metrics["tardiness"] * 0.5 +
                metrics["flowtime"] * 0.2
            )
        else:
            return metrics["makespan"]


class SequenceComparisonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for sequence comparison
    """
    queryset = SequenceComparison.objects.all()
    serializer_class = SequenceComparisonSerializer

    @action(detail=False, methods=["post"])
    def create_comparison(self, request):
        """
        POST /api/aps/sequence-comparisons/create_comparison/
        Compare multiple sequences
        """
        sequence_ids = request.data.get("sequence_ids", [])

        if len(sequence_ids) < 2:
            return Response(
                {"error": "At least 2 sequences are required for comparison"},
                status=status.HTTP_400_BAD_REQUEST
            )

        sequences = JobSequence.objects.filter(sequence_id__in=sequence_ids)

        if sequences.count() != len(sequence_ids):
            return Response(
                {"error": "Some sequences not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create comparison
        comparison = SequenceComparison.objects.create(
            name=request.data.get("name", f"Comparison {timezone.now().strftime('%Y-%m-%d %H:%M')}"),
            description=request.data.get("description", ""),
            created_by=request.data.get("created_by"),
        )

        comparison.sequences.set(sequences)

        # Generate comparison data
        comparison_data = self._generate_comparison_data(sequences)
        comparison.comparison_data = comparison_data

        # Determine recommended sequence
        if comparison_data["sequences"]:
            best_sequence_id = min(
                comparison_data["sequences"],
                key=lambda x: x.get("score", float("inf"))
            )["sequence_id"]

            comparison.recommended_sequence = JobSequence.objects.get(
                sequence_id=best_sequence_id
            )

        comparison.save()

        return Response(
            SequenceComparisonSerializer(comparison).data,
            status=status.HTTP_201_CREATED
        )

    def _generate_comparison_data(self, sequences):
        """Generate comparison metrics for sequences"""
        data = {
            "sequences": [],
            "metrics": ["makespan", "tardiness", "flowtime"],
        }

        for sequence in sequences:
            sequence_data = {
                "sequence_id": sequence.sequence_id,
                "name": sequence.name,
                "rule": sequence.sequencing_rule,
                "job_count": len(sequence.job_sequence) if sequence.job_sequence else 0,
                "makespan": sequence.estimated_makespan or 0,
                "tardiness": sequence.estimated_tardiness or 0,
                "flowtime": sequence.estimated_flowtime or 0,
            }

            # Calculate composite score (lower is better)
            sequence_data["score"] = (
                sequence_data["makespan"] * 0.3 +
                sequence_data["tardiness"] * 0.5 +
                sequence_data["flowtime"] * 0.2
            )

            data["sequences"].append(sequence_data)

        # Sort by score
        data["sequences"].sort(key=lambda x: x["score"])

        return data

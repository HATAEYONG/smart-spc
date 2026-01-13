from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import random
import time
from apps.core.models import StageFactPlanOut
from .scenario_models import Scenario, ScenarioResult, ScenarioComparison
from rest_framework import serializers
from .services.or_repair import repair_schedule_with_cpsat
from .services.down_risk_predictor import DownRiskPredictor
import logging

logger = logging.getLogger(__name__)


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = "__all__"
        read_only_fields = ["scenario_id", "created_at", "updated_at"]


class ScenarioResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioResult
        fields = "__all__"
        read_only_fields = ["result_id", "created_at"]


class ScenarioComparisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioComparison
        fields = "__all__"
        read_only_fields = ["comparison_id", "created_at"]


class ScenarioViewSet(viewsets.ModelViewSet):
    """
    API endpoint for What-If scenarios
    """
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        """
        POST /api/aps/scenarios/{id}/run/
        Execute a scenario

        Optional parameters:
        - use_cpsat_repair (bool): Use CP-SAT based repair (default: True)
        - use_plant_calendar (bool): Use PlantCalendar for work hours (default: False)
        """
        scenario = self.get_object()

        if scenario.status == "RUNNING":
            return Response(
                {"error": "Scenario is already running"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get repair options from request
        use_cpsat_repair = request.data.get("use_cpsat_repair", True)
        use_plant_calendar = request.data.get("use_plant_calendar", False)
        use_machine_constraints = request.data.get("use_machine_constraints", True)
        use_down_risk = request.data.get("use_down_risk", False)  # STEP 2 추가
        risk_weight = request.data.get("risk_weight", 3.0)  # STEP 2 추가

        # Update status
        scenario.status = "RUNNING"
        scenario.save()

        try:
            # DOWN_RISK 예측 조회 (STEP 2)
            predictions = None
            if use_down_risk:
                from .ai_llm_models import Prediction
                predictions = Prediction.objects.filter(
                    target_id=scenario.scenario_id,
                    prediction_type='DOWN_RISK'
                )
                logger.info(f"Loaded {predictions.count()} DOWN_RISK predictions")

            # Execute scenario
            start_time = time.time()
            result = self._execute_scenario(
                scenario,
                use_cpsat_repair=use_cpsat_repair,
                use_plant_calendar=use_plant_calendar,
                predictions=predictions,
                risk_weight=risk_weight
            )
            execution_time = time.time() - start_time

            # Save results
            scenario_result = ScenarioResult.objects.create(
                scenario=scenario,
                makespan=result["makespan"],
                total_tardiness=result["total_tardiness"],
                max_tardiness=result["max_tardiness"],
                avg_utilization=result["avg_utilization"],
                total_cost=result["total_cost"],
                total_jobs=result["total_jobs"],
                completed_jobs=result["completed_jobs"],
                tardy_jobs=result["tardy_jobs"],
                total_machines=result["total_machines"],
                avg_machine_utilization=result["avg_machine_utilization"],
                bottleneck_machines=result["bottleneck_machines"],
                schedule=result["schedule"],
                execution_time=execution_time,
            )

            # Update scenario
            scenario.status = "COMPLETED"
            scenario.results = {
                "result_id": scenario_result.result_id,
                "makespan": result["makespan"],
                "total_tardiness": result["total_tardiness"],
                "execution_time": execution_time,
            }
            scenario.save()

            # ========================================
            # STEP 3: 미계획 원인 자동 분류
            # ========================================
            unplanned_reasons = []
            try:
                from apps.aps.services.analytics import UnplannedClassifier

                # 전체 주문 목록 조회
                base_date = scenario.base_plan_date or timezone.now()
                plans = StageFactPlanOut.objects.filter(fr_ts__date=base_date.date())

                # 원인 분석 실행
                classifier = UnplannedClassifier(scenario_id=scenario.scenario_id)
                unplanned_reasons = classifier.analyze(
                    schedule_rows=result['schedule'],
                    orders=list(plans)
                )

                logger.info(
                    f"UnplannedReason analysis: {len(unplanned_reasons)} records created "
                    f"for scenario {scenario.scenario_id}"
                )

            except Exception as e:
                logger.error(f"UnplannedReason analysis failed: {e}", exc_info=True)
                # 원인 분석 실패는 최적화 실행을 중단하지 않음

            # 응답에 미계획 분석 결과 추가
            response_data = {
                "scenario": ScenarioSerializer(scenario).data,
                "result": ScenarioResultSerializer(scenario_result).data,
            }

            # 미계획 원인 요약 추가
            if unplanned_reasons:
                reason_summary = {}
                for r in unplanned_reasons:
                    code = r.reason_code
                    reason_summary[code] = reason_summary.get(code, 0) + 1

                response_data["unplanned_analysis"] = {
                    "total_count": len(unplanned_reasons),
                    "reason_breakdown": reason_summary,
                    "unplanned_count": sum(1 for r in unplanned_reasons if r.status == 'UNPLANNED'),
                    "delayed_count": sum(1 for r in unplanned_reasons if r.status == 'DELAYED'),
                }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            scenario.status = "FAILED"
            scenario.results = {"error": str(e)}
            scenario.save()
            return Response(
                {"error": f"Scenario execution failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        """
        POST /api/aps/scenarios/{id}/clone/
        Clone a scenario
        """
        original = self.get_object()

        # Create clone
        clone = Scenario.objects.create(
            name=f"{original.name} (Copy)",
            description=original.description,
            base_plan_date=original.base_plan_date,
            modifications=original.modifications.copy() if original.modifications else [],
            algorithm=original.algorithm,
            algorithm_params=original.algorithm_params.copy() if original.algorithm_params else None,
            status="DRAFT",
            baseline_scenario=original.baseline_scenario,
            created_by=request.data.get("created_by"),
        )

        return Response(
            ScenarioSerializer(clone).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])
    def templates(self, request):
        """
        GET /api/aps/scenarios/templates/
        Get predefined scenario templates
        """
        templates = [
            {
                "name": "기계 증설 시나리오",
                "description": "특정 기계를 추가하여 병목 해소 효과 분석",
                "modifications": [
                    {
                        "type": "add_machine",
                        "machine": "MC_NEW_001",
                        "capacity": 1.0,
                    }
                ],
            },
            {
                "name": "기계 고장 시나리오",
                "description": "주요 기계 고장 시 영향도 분석",
                "modifications": [
                    {
                        "type": "remove_machine",
                        "machine": "MC001",
                        "start_time": "2024-01-01T08:00:00",
                        "duration": 240,  # minutes
                    }
                ],
            },
            {
                "name": "긴급 작업 추가",
                "description": "긴급 작업 투입 시 전체 일정 변화 분석",
                "modifications": [
                    {
                        "type": "add_jobs",
                        "jobs": [
                            {
                                "wo_no": "URGENT_001",
                                "priority": 10,
                                "processing_time": 60,
                            }
                        ],
                    }
                ],
            },
            {
                "name": "생산 능력 향상",
                "description": "기계 성능 개선 시 효과 분석 (20% 향상)",
                "modifications": [
                    {
                        "type": "change_capacity",
                        "machines": ["MC001", "MC002"],
                        "factor": 1.2,
                    }
                ],
            },
        ]

        return Response({"templates": templates})

    @action(detail=True, methods=["post"])
    def predict(self, request, pk=None):
        """
        POST /api/aps/scenarios/{id}/predict/
        Generate DOWN_RISK predictions for resources

        Request body:
        {
            "prediction_types": ["PROC_TIME", "SETUP_TIME", "DOWN_RISK"],
            "lookback_days": 60,
            "resource_codes": ["MC-001", "MC-002"] (optional)
        }

        Response:
        {
            "scenario_id": 1,
            "predictions_created": {
                "DOWN_RISK": 5
            },
            "down_risk_details": [...]
        }
        """
        scenario = self.get_object()

        # Parse request parameters
        prediction_types = request.data.get("prediction_types", ["DOWN_RISK"])
        lookback_days = request.data.get("lookback_days", 60)
        resource_codes = request.data.get("resource_codes", None)

        logger.info(
            f"Generating predictions for scenario {scenario.scenario_id}: "
            f"types={prediction_types}, lookback={lookback_days}"
        )

        results = {
            "scenario_id": scenario.scenario_id,
            "predictions_created": {},
        }

        # DOWN_RISK 예측 생성
        if "DOWN_RISK" in prediction_types:
            try:
                predictor = DownRiskPredictor(lookback_days=lookback_days)
                predictions = predictor.build_all_predictions(
                    scenario_id=scenario.scenario_id,
                    resource_codes=resource_codes
                )

                results["predictions_created"]["DOWN_RISK"] = len(predictions)

                # 상세 정보 추가
                results["down_risk_details"] = [
                    {
                        "resource_code": pred.target_entity.split(':')[1],
                        "risk_value": pred.predicted_value,
                        "confidence": pred.confidence_score,
                        "explanation": pred.explanation,
                        "stats": pred.features_used
                    }
                    for pred in predictions
                ]

                logger.info(f"Created {len(predictions)} DOWN_RISK predictions")

            except Exception as e:
                logger.error(f"Failed to create DOWN_RISK predictions: {e}")
                return Response(
                    {"error": f"DOWN_RISK prediction failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # TODO: PROC_TIME, SETUP_TIME 예측 (향후 구현)
        if "PROC_TIME" in prediction_types:
            results["predictions_created"]["PROC_TIME"] = 0
            logger.info("PROC_TIME prediction not implemented yet")

        if "SETUP_TIME" in prediction_types:
            results["predictions_created"]["SETUP_TIME"] = 0
            logger.info("SETUP_TIME prediction not implemented yet")

        results["created_at"] = timezone.now().isoformat()

        return Response(results, status=status.HTTP_200_OK)

    def _execute_scenario(self, scenario, use_cpsat_repair=True, use_plant_calendar=False,
                          predictions=None, risk_weight=3.0):
        """
        Execute scenario and return results

        Args:
            scenario: Scenario object
            use_cpsat_repair: Use CP-SAT based schedule repair (default: True)
            use_plant_calendar: Use PlantCalendar for work hours (default: False)
            predictions: DOWN_RISK Prediction QuerySet (STEP 2)
            risk_weight: DOWN_RISK penalty weight (STEP 2)
        """
        # Get base plan
        base_date = scenario.base_plan_date or timezone.now()
        plans = StageFactPlanOut.objects.filter(fr_ts__date=base_date.date())

        # Apply modifications
        modified_jobs = list(plans)
        machines = list(plans.values_list("mc_cd", flat=True).distinct())

        for modification in scenario.modifications:
            mod_type = modification.get("type")

            if mod_type == "add_machine":
                machines.append(modification["machine"])

            elif mod_type == "remove_machine":
                machine_to_remove = modification["machine"]
                machines = [m for m in machines if m != machine_to_remove]
                # Remove jobs from this machine
                modified_jobs = [j for j in modified_jobs if j.mc_cd != machine_to_remove]

            elif mod_type == "add_jobs":
                # Simulated: would add new jobs to the schedule
                pass

            elif mod_type == "change_capacity":
                # Simulated: would adjust processing times
                factor = modification.get("factor", 1.0)
                target_machines = modification.get("machines", [])
                # Apply capacity change to jobs on these machines
                pass

        # Run scheduling algorithm
        if scenario.algorithm == "GA":
            result = self._run_genetic_algorithm(
                modified_jobs, machines, scenario.scenario_id,
                use_cpsat_repair, use_plant_calendar, predictions, risk_weight
            )
        else:
            result = self._run_dispatch_rule(
                modified_jobs, machines, scenario.algorithm,
                scenario.scenario_id, use_cpsat_repair, use_plant_calendar,
                predictions, risk_weight
            )

        return result

    def _run_genetic_algorithm(self, jobs, machines, scenario_id, use_cpsat_repair=True,
                               use_plant_calendar=False, predictions=None, risk_weight=3.0):
        """
        STEP 4: Hybrid GA + Local Search execution

        Args:
            jobs: List of job objects (StageFactPlanOut)
            machines: List of machine codes
            scenario_id: Scenario ID
            use_cpsat_repair: Apply CP-SAT repair to fix conflicts
            use_plant_calendar: Use PlantCalendar for work hours
            predictions: DOWN_RISK Prediction QuerySet (STEP 2)
            risk_weight: DOWN_RISK penalty weight (STEP 2)
        """
        from .services.ga_engine import run_ga_with_local_search, calculate_metrics

        total_jobs = len(jobs)
        total_machines = len(machines)

        if not jobs:
            logger.warning("Empty jobs list for GA execution")
            return self._empty_result()

        # Convert Django ORM objects to dict format for GA engine
        job_list = []
        for job in jobs:
            job_dict = {
                'wo_no': job.wo_no,
                'order_id': job.wo_no,  # Use wo_no as order_id
                'op_seq': 0,  # Default op_seq (can be extended later)
                'mc_cd': job.mc_cd,
                'resource_code': job.mc_cd,
                'fr_ts': job.fr_ts,
                'to_ts': job.to_ts,
                'due_date': job.to_ts,
                'duration_minutes': (job.to_ts - job.fr_ts).total_seconds() / 60,
            }
            job_list.append(job_dict)

        logger.info(f"Running Hybrid GA+LS for {len(job_list)} jobs on {total_machines} machines")

        # Run GA + Local Search
        try:
            ga_result = run_ga_with_local_search(
                jobs=job_list,
                population_size=30,  # Can be parameterized
                max_generations=50,  # Can be parameterized
                crossover_rate=0.8,
                mutation_rate=0.1,
                use_local_search=True,
                local_search_iterations=50,
                verbose=True
            )

            best_schedule = ga_result['best_schedule']
            metrics = ga_result['metrics']

            logger.info(
                f"GA+LS completed: makespan={metrics['makespan']:.0f} min, "
                f"tardiness={metrics['total_tardiness']:.0f} min, "
                f"time={ga_result['computation_time']:.2f}s"
            )

        except Exception as e:
            logger.error(f"GA engine failed: {e}, falling back to simulated GA", exc_info=True)
            # Fallback to simulated result
            return self._simulated_ga_result(jobs, machines, scenario_id, use_cpsat_repair, use_plant_calendar)

        # Convert GA schedule to API format
        schedule = [
            {
                "wo_no": job.get('wo_no', job.get('order_id')),
                "mc_cd": job.get('mc_cd', job.get('resource_code')),
                "fr_ts": job['start_dt'].isoformat() if 'start_dt' in job else None,
                "to_ts": job['end_dt'].isoformat() if 'end_dt' in job else None,
                "order_id": job.get('order_id'),
                "resource_code": job.get('resource_code'),
            }
            for job in best_schedule
        ]

        # Identify bottleneck machines (highest utilization)
        bottleneck_machines = []
        if metrics.get('resource_utilization'):
            sorted_resources = sorted(
                metrics['resource_utilization'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            bottleneck_machines = [r[0] for r in sorted_resources[:2]]

        # Apply CP-SAT Repair if enabled (optional post-processing)
        repair_applied = False
        if use_cpsat_repair:
            try:
                schedule_rows = [
                    {
                        'wo_no': s['wo_no'],
                        'order_id': s.get('order_id', s['wo_no']),
                        'op_seq': 0,
                        'resource_code': s['mc_cd'],
                        'mc_cd': s['mc_cd'],
                        'start_dt': timezone.datetime.fromisoformat(s['fr_ts']),
                        'end_dt': timezone.datetime.fromisoformat(s['to_ts']),
                        'duration_minutes': (
                            timezone.datetime.fromisoformat(s['to_ts']) -
                            timezone.datetime.fromisoformat(s['fr_ts'])
                        ).total_seconds() / 60,
                    }
                    for s in schedule if s['fr_ts'] and s['to_ts']
                ]

                repaired = repair_schedule_with_cpsat(
                    scenario_id=scenario_id,
                    schedule_rows=schedule_rows,
                    use_cpsat=True,
                    use_plant_calendar=use_plant_calendar,
                    use_machine_constraints=True,
                    predictions=predictions,
                    risk_weight=risk_weight
                )

                if repaired:
                    # Update schedule with repaired times
                    schedule = [
                        {
                            "wo_no": r['wo_no'],
                            "mc_cd": r['mc_cd'],
                            "fr_ts": r['start_dt'].isoformat(),
                            "to_ts": r['end_dt'].isoformat(),
                            "order_id": r.get('order_id'),
                            "resource_code": r.get('resource_code'),
                        }
                        for r in repaired
                    ]
                    repair_applied = True
                    logger.info("CP-SAT repair applied to GA schedule")

            except Exception as e:
                logger.warning(f"CP-SAT repair failed: {e}, using GA schedule as-is")

        return {
            "makespan": metrics['makespan'],
            "total_tardiness": metrics['total_tardiness'],
            "max_tardiness": metrics['total_tardiness'],  # Simplified
            "avg_utilization": metrics.get('avg_utilization', 0),
            "total_cost": metrics['makespan'] * 12.5,  # Cost estimate
            "total_jobs": total_jobs,
            "completed_jobs": metrics['total_jobs'],
            "tardy_jobs": metrics['tardy_jobs'],
            "total_machines": total_machines,
            "avg_machine_utilization": metrics.get('avg_utilization', 0),
            "bottleneck_machines": bottleneck_machines,
            "schedule": schedule,
            "repair_applied": repair_applied,
            "ga_info": {
                "algorithm": "Hybrid GA + Local Search",
                "generations": ga_result.get('ga_generations'),
                "computation_time": ga_result.get('computation_time'),
                "initial_fitness": ga_result.get('initial_fitness'),
                "ga_final_fitness": ga_result.get('ga_final_fitness'),
                "ls_final_fitness": ga_result.get('ls_final_fitness'),
            }
        }

    def _simulated_ga_result(self, jobs, machines, scenario_id, use_cpsat_repair, use_plant_calendar):
        """
        Fallback to simulated GA result (legacy behavior)
        """
        total_jobs = len(jobs)
        total_machines = len(machines)

        total_process_time = sum(
            [(j.to_ts - j.fr_ts).total_seconds() / 60 for j in jobs]
        ) if jobs else 0

        makespan = total_process_time / max(total_machines, 1) * random.uniform(0.85, 0.95)
        tardiness = sum([random.uniform(0, 30) for _ in range(int(total_jobs * 0.2))])
        utilization = random.uniform(70, 90)

        bottleneck_machines = []
        if total_machines > 0:
            num_bottlenecks = min(2, total_machines)
            bottleneck_machines = random.sample(machines, num_bottlenecks) if machines else []

        schedule = [
            {
                "wo_no": j.wo_no,
                "mc_cd": j.mc_cd,
                "fr_ts": j.fr_ts.isoformat(),
                "to_ts": j.to_ts.isoformat(),
            }
            for j in jobs[:100]
        ] if jobs else []

        return {
            "makespan": makespan,
            "total_tardiness": tardiness,
            "max_tardiness": tardiness / 2 if tardiness > 0 else 0,
            "avg_utilization": utilization,
            "total_cost": makespan * random.uniform(10, 15),
            "total_jobs": total_jobs,
            "completed_jobs": total_jobs,
            "tardy_jobs": int(total_jobs * 0.2),
            "total_machines": total_machines,
            "avg_machine_utilization": utilization,
            "bottleneck_machines": bottleneck_machines,
            "schedule": schedule,
            "repair_applied": False,
        }

    def _empty_result(self):
        """Empty result for edge cases"""
        return {
            "makespan": 0,
            "total_tardiness": 0,
            "max_tardiness": 0,
            "avg_utilization": 0,
            "total_cost": 0,
            "total_jobs": 0,
            "completed_jobs": 0,
            "tardy_jobs": 0,
            "total_machines": 0,
            "avg_machine_utilization": 0,
            "bottleneck_machines": [],
            "schedule": [],
            "repair_applied": False,
        }

    def _run_dispatch_rule(self, jobs, machines, rule, scenario_id, use_cpsat_repair=True,
                           use_plant_calendar=False, predictions=None, risk_weight=3.0):
        """
        Simulated dispatch rule execution with optional CP-SAT repair

        Args:
            jobs: List of job objects
            machines: List of machine codes
            rule: Dispatch rule (FIFO, SPT, etc.)
            scenario_id: Scenario ID
            use_cpsat_repair: Apply CP-SAT repair
            use_plant_calendar: Use PlantCalendar
            predictions: DOWN_RISK Prediction QuerySet (STEP 2)
            risk_weight: DOWN_RISK penalty weight (STEP 2)
        """
        # Similar to GA but with different makespan multiplier
        multipliers = {
            "FIFO": 1.0,
            "SPT": 0.92,
            "LPT": 1.08,
            "EDD": 0.95,
            "CR": 0.94,
        }

        total_jobs = len(jobs)
        total_machines = len(machines)
        total_process_time = sum(
            [(j.to_ts - j.fr_ts).total_seconds() / 60 for j in jobs]
        ) if jobs else 0

        multiplier = multipliers.get(rule, 1.0)
        makespan = total_process_time / max(total_machines, 1) * multiplier
        tardiness = sum([random.uniform(0, 50) for _ in range(int(total_jobs * random.uniform(0.15, 0.35)))])

        # Generate schedule
        schedule = [
            {
                "wo_no": j.wo_no,
                "mc_cd": j.mc_cd,
                "fr_ts": j.fr_ts.isoformat(),
                "to_ts": j.to_ts.isoformat(),
            }
            for j in jobs[:100]
        ] if jobs else []

        # Apply CP-SAT Repair if enabled
        if use_cpsat_repair and jobs:
            schedule = self._apply_cpsat_repair(
                jobs[:100], scenario_id, use_plant_calendar,
                plant_cd=None, use_machine_constraints=use_machine_constraints
            )

        return {
            "makespan": makespan,
            "total_tardiness": tardiness,
            "max_tardiness": tardiness / 2 if tardiness > 0 else 0,
            "avg_utilization": random.uniform(65, 85),
            "total_cost": makespan * random.uniform(10, 15),
            "total_jobs": total_jobs,
            "completed_jobs": total_jobs,
            "tardy_jobs": int(total_jobs * random.uniform(0.15, 0.35)),
            "total_machines": total_machines,
            "avg_machine_utilization": random.uniform(65, 85),
            "bottleneck_machines": random.sample(machines, min(2, len(machines))) if machines else [],
            "schedule": schedule,
            "repair_applied": use_cpsat_repair,
        }

    def _apply_cpsat_repair(self, jobs, scenario_id, use_plant_calendar=False, plant_cd=None, use_machine_constraints=True):
        """
        Apply CP-SAT repair to schedule

        Args:
            jobs: List of job objects (StageFactPlanOut)
            scenario_id: Scenario ID
            use_plant_calendar: Use PlantCalendar for work hours
            plant_cd: 공장 코드 (PlantCalendar 조회용)
            use_machine_constraints: Use MachineWorkTime/Downtime (Phase 3)

        Returns:
            Repaired schedule as list of dicts
        """
        try:
            # Convert jobs to schedule_rows format
            schedule_rows = []
            for idx, job in enumerate(jobs):
                duration = (job.to_ts - job.fr_ts).total_seconds() / 60

                schedule_rows.append({
                    'id': job.id if hasattr(job, 'id') else idx,
                    'order_id': job.wo_no,
                    'op_seq': getattr(job, 'op_seq', 1),
                    'resource_code': job.mc_cd,
                    'start_dt': job.fr_ts,
                    'end_dt': job.to_ts,
                    'duration_minutes': duration,
                    'due_date': getattr(job, 'due_dt', job.to_ts + timedelta(days=7)),
                })

            # Determine plant_cd (default to FAC01 if not provided)
            if not plant_cd and jobs:
                # Try to get from job's plant_cd field
                plant_cd = getattr(jobs[0], 'plant_cd', 'FAC01')

            # Apply CP-SAT repair
            logger.info(
                f"Applying CP-SAT repair to {len(schedule_rows)} jobs "
                f"(scenario={scenario_id}, plant={plant_cd}, "
                f"machine_constraints={use_machine_constraints})"
            )
            repaired_rows = repair_schedule_with_cpsat(
                scenario_id=scenario_id,
                schedule_rows=schedule_rows,
                use_cpsat=True,
                use_plant_calendar=use_plant_calendar,
                plant_cd=plant_cd,
                use_machine_constraints=use_machine_constraints
            )

            # Convert back to schedule format
            repaired_schedule = [
                {
                    "wo_no": row['order_id'],
                    "mc_cd": row['resource_code'],
                    "fr_ts": row['start_dt'].isoformat(),
                    "to_ts": row['end_dt'].isoformat(),
                }
                for row in repaired_rows
            ]

            logger.info(f"CP-SAT repair completed for scenario {scenario_id}")
            return repaired_schedule

        except Exception as e:
            logger.error(f"CP-SAT repair failed: {e}, returning original schedule")
            # Return original schedule on failure
            return [
                {
                    "wo_no": j.wo_no,
                    "mc_cd": j.mc_cd,
                    "fr_ts": j.fr_ts.isoformat(),
                    "to_ts": j.to_ts.isoformat(),
                }
                for j in jobs
            ]


class ScenarioComparisonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for scenario comparisons
    """
    queryset = ScenarioComparison.objects.all()
    serializer_class = ScenarioComparisonSerializer

    @action(detail=False, methods=["post"])
    def create_comparison(self, request):
        """
        POST /api/aps/scenario-comparisons/create_comparison/
        Create a comparison between multiple scenarios
        """
        scenario_ids = request.data.get("scenario_ids", [])

        if len(scenario_ids) < 2:
            return Response(
                {"error": "At least 2 scenarios are required for comparison"},
                status=status.HTTP_400_BAD_REQUEST
            )

        scenarios = Scenario.objects.filter(scenario_id__in=scenario_ids)

        if scenarios.count() != len(scenario_ids):
            return Response(
                {"error": "Some scenarios not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create comparison
        comparison = ScenarioComparison.objects.create(
            name=request.data.get("name", f"Comparison {timezone.now().strftime('%Y-%m-%d %H:%M')}"),
            description=request.data.get("description", ""),
            created_by=request.data.get("created_by"),
        )

        comparison.scenarios.set(scenarios)

        # Generate comparison data
        comparison_data = self._generate_comparison_data(scenarios)
        comparison.comparison_data = comparison_data
        comparison.save()

        return Response(
            ScenarioComparisonSerializer(comparison).data,
            status=status.HTTP_201_CREATED
        )

    def _generate_comparison_data(self, scenarios):
        """Generate comparison metrics for scenarios"""
        data = {
            "scenarios": [],
            "metrics": ["makespan", "total_tardiness", "avg_utilization", "total_cost"],
            "chart_data": [],
        }

        for scenario in scenarios:
            if scenario.status != "COMPLETED" or not scenario.results:
                continue

            scenario_data = {
                "scenario_id": scenario.scenario_id,
                "name": scenario.name,
                "makespan": scenario.results.get("makespan", 0),
                "total_tardiness": scenario.results.get("total_tardiness", 0),
                "avg_utilization": 0,  # Would be in detailed results
                "total_cost": 0,  # Would be in detailed results
            }

            # Get detailed results if available
            latest_result = scenario.detailed_results.order_by("-created_at").first()
            if latest_result:
                scenario_data["avg_utilization"] = latest_result.avg_utilization
                scenario_data["total_cost"] = latest_result.total_cost

            data["scenarios"].append(scenario_data)

        # Prepare chart data
        for metric in data["metrics"]:
            metric_data = {
                "metric": metric,
                "values": [s[metric] for s in data["scenarios"]]
            }
            data["chart_data"].append(metric_data)

        return data

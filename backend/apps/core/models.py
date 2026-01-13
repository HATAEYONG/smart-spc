from django.db import models


class APSEvent(models.Model):
    EVENT_TYPES = [
        ("EMERGENCY_ORDER", "EMERGENCY_ORDER"),
        ("BREAKDOWN", "BREAKDOWN"),
        ("QUALITY_ALERT", "QUALITY_ALERT"),
        ("JOB_START", "JOB_START"),
    ]

    event_ts = models.DateTimeField(auto_now_add=True, db_index=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    mc_cd = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    wc_cd = models.CharField(max_length=20, null=True, blank=True)
    wo_no = models.CharField(max_length=30, null=True, blank=True)
    itm_id = models.CharField(max_length=50, null=True, blank=True)
    payload = models.JSONField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        db_table = "aps_event"
        indexes = [
            models.Index(fields=["mc_cd", "event_ts"], name="ix_aps_event_mc_ts"),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.mc_cd or 'N/A'} at {self.event_ts}"


class APSDecisionLog(models.Model):
    DECISIONS = [("APPLY", "APPLY"), ("HOLD", "HOLD")]

    event = models.ForeignKey(
        APSEvent, null=True, blank=True, on_delete=models.SET_NULL, related_name="decisions"
    )
    mc_cd = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    scope_size = models.IntegerField(default=0)
    decision = models.CharField(max_length=10, choices=DECISIONS)
    reason = models.TextField(null=True, blank=True)
    kpi_json = models.JSONField(null=True, blank=True)
    created_ts = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        db_table = "aps_decision_log"
        indexes = [
            models.Index(fields=["decision", "created_ts"], name="ix_decision_ts"),
        ]

    def __str__(self):
        return f"{self.decision} - {self.mc_cd or 'N/A'} at {self.created_ts}"


class APSDepEdge(models.Model):
    EDGE_TYPES = [
        ("PRECEDENCE", "PRECEDENCE"),
        ("SAME_ITEM", "SAME_ITEM"),
        ("SAME_LOT", "SAME_LOT"),
        ("ALT_MACHINE", "ALT_MACHINE"),
    ]

    src_wo_no = models.CharField(max_length=30)
    dst_wo_no = models.CharField(max_length=30)
    edge_type = models.CharField(max_length=30, choices=EDGE_TYPES)
    edge_weight = models.IntegerField(default=1)
    created_ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        db_table = "aps_dep_edge"
        unique_together = (("src_wo_no", "dst_wo_no", "edge_type"),)
        indexes = [
            models.Index(fields=["src_wo_no"], name="ix_edge_src"),
            models.Index(fields=["dst_wo_no"], name="ix_edge_dst"),
            models.Index(fields=["edge_type"], name="ix_edge_type"),
        ]

    def __str__(self):
        return f"{self.src_wo_no} -> {self.dst_wo_no} ({self.edge_type})"


class StageFactPlanOut(models.Model):
    """
    APS result staging: stage_fact_plan_out
    """
    wo_no = models.CharField(max_length=30, primary_key=True)
    mc_cd = models.CharField(max_length=20, db_index=True)
    itm_id = models.CharField(max_length=50)
    plan_qty = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    fr_ts = models.DateTimeField()
    to_ts = models.DateTimeField()
    locked_yn = models.CharField(max_length=1, default="N")
    freeze_level = models.IntegerField(default=0)
    load_ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        db_table = "stage_fact_plan_out"
        indexes = [
            models.Index(fields=["mc_cd", "fr_ts"], name="ix_stage_mc_fr"),
        ]

    def __str__(self):
        return f"{self.wo_no} - {self.mc_cd}"

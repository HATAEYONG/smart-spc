"""
Unit tests for Core app models
"""
import pytest
from datetime import datetime, timedelta
from apps.core.models import APSEvent, APSDecisionLog, APSDepEdge, StageFactPlanOut
from .factories import (
    APSEventFactory,
    APSDecisionLogFactory,
    APSDepEdgeFactory,
    StageFactPlanOutFactory
)


@pytest.mark.django_db
class TestAPSEvent:
    """Tests for APSEvent model"""

    def test_create_event(self):
        """Test creating an APS event"""
        event = APSEventFactory(
            event_type='EMERGENCY_ORDER',
            mc_cd='MC001',
            wo_no='WO000001'
        )
        assert event.event_type == 'EMERGENCY_ORDER'
        assert event.mc_cd == 'MC001'
        assert event.wo_no == 'WO000001'
        assert event.event_ts is not None

    def test_event_str_representation(self):
        """Test string representation of event"""
        event = APSEventFactory(
            event_type='BREAKDOWN',
            mc_cd='MC002'
        )
        str_repr = str(event)
        assert 'BREAKDOWN' in str_repr
        assert 'MC002' in str_repr

    def test_event_with_payload(self):
        """Test event with JSON payload"""
        payload_data = {
            'priority': 'high',
            'estimated_duration': 120,
            'operator': 'John'
        }
        event = APSEventFactory(payload=payload_data)
        assert event.payload == payload_data
        assert event.payload['priority'] == 'high'

    def test_event_without_machine(self):
        """Test event without machine code"""
        event = APSEventFactory(mc_cd=None)
        assert event.mc_cd is None
        str_repr = str(event)
        assert 'N/A' in str_repr

    def test_event_type_choices(self):
        """Test valid event types"""
        valid_types = ['EMERGENCY_ORDER', 'BREAKDOWN', 'QUALITY_ALERT', 'JOB_START']
        for event_type in valid_types:
            event = APSEventFactory(event_type=event_type)
            assert event.event_type == event_type


@pytest.mark.django_db
class TestAPSDecisionLog:
    """Tests for APSDecisionLog model"""

    def test_create_decision(self):
        """Test creating a decision log"""
        event = APSEventFactory()
        decision = APSDecisionLogFactory(
            event=event,
            decision='APPLY',
            mc_cd='MC001',
            scope_size=50
        )
        assert decision.decision == 'APPLY'
        assert decision.event == event
        assert decision.scope_size == 50

    def test_decision_with_kpi(self):
        """Test decision with KPI metrics"""
        kpi_data = {
            'utilization': 0.82,
            'avg_delay': 15.3,
            'max_delay': 45.0,
            'total_jobs': 120
        }
        decision = APSDecisionLogFactory(kpi_json=kpi_data)
        assert decision.kpi_json['utilization'] == 0.82
        assert decision.kpi_json['total_jobs'] == 120

    def test_decision_without_event(self):
        """Test decision without associated event"""
        decision = APSDecisionLogFactory(event=None)
        assert decision.event is None
        assert decision.decision in ['APPLY', 'HOLD']

    def test_decision_str_representation(self):
        """Test string representation of decision"""
        decision = APSDecisionLogFactory(
            decision='HOLD',
            mc_cd='MC003'
        )
        str_repr = str(decision)
        assert 'HOLD' in str_repr
        assert 'MC003' in str_repr

    def test_decision_reason(self):
        """Test decision with reason text"""
        reason = "Utilization 85% exceeds threshold 80%"
        decision = APSDecisionLogFactory(
            decision='HOLD',
            reason=reason
        )
        assert decision.reason == reason


@pytest.mark.django_db
class TestAPSDepEdge:
    """Tests for APSDepEdge model"""

    def test_create_edge(self):
        """Test creating a dependency edge"""
        edge = APSDepEdgeFactory(
            src_wo_no='WO000001',
            dst_wo_no='WO000002',
            edge_type='PRECEDENCE'
        )
        assert edge.src_wo_no == 'WO000001'
        assert edge.dst_wo_no == 'WO000002'
        assert edge.edge_type == 'PRECEDENCE'

    def test_edge_unique_constraint(self):
        """Test unique constraint on (src, dst, type)"""
        APSDepEdgeFactory(
            src_wo_no='WO000001',
            dst_wo_no='WO000002',
            edge_type='PRECEDENCE'
        )

        # Creating duplicate should raise error
        with pytest.raises(Exception):
            APSDepEdgeFactory(
                src_wo_no='WO000001',
                dst_wo_no='WO000002',
                edge_type='PRECEDENCE'
            )

    def test_edge_str_representation(self):
        """Test string representation of edge"""
        edge = APSDepEdgeFactory(
            src_wo_no='WO000010',
            dst_wo_no='WO000020',
            edge_type='SAME_ITEM'
        )
        str_repr = str(edge)
        assert 'WO000010' in str_repr
        assert 'WO000020' in str_repr
        assert 'SAME_ITEM' in str_repr
        assert '->' in str_repr

    def test_edge_weight(self):
        """Test edge weight attribute"""
        edge = APSDepEdgeFactory(edge_weight=5)
        assert edge.edge_weight == 5

    def test_edge_types(self):
        """Test all valid edge types"""
        edge_types = ['PRECEDENCE', 'SAME_ITEM', 'SAME_LOT', 'ALT_MACHINE']
        for edge_type in edge_types:
            edge = APSDepEdgeFactory(edge_type=edge_type)
            assert edge.edge_type == edge_type


@pytest.mark.django_db
class TestStageFactPlanOut:
    """Tests for StageFactPlanOut model"""

    def test_create_plan(self):
        """Test creating a plan output record"""
        plan = StageFactPlanOutFactory(
            wo_no='WO000001',
            mc_cd='MC001',
            itm_id='ITM00001'
        )
        assert plan.wo_no == 'WO000001'
        assert plan.mc_cd == 'MC001'
        assert plan.itm_id == 'ITM00001'

    def test_plan_timestamps(self):
        """Test plan start/end timestamps"""
        now = datetime.now()
        later = now + timedelta(hours=3)

        plan = StageFactPlanOutFactory(
            fr_ts=now,
            to_ts=later
        )
        assert plan.fr_ts == now
        assert plan.to_ts == later
        assert plan.to_ts > plan.fr_ts

    def test_plan_freeze_level(self):
        """Test freeze level attribute"""
        plan = StageFactPlanOutFactory(freeze_level=2)
        assert plan.freeze_level == 2

    def test_plan_locked_status(self):
        """Test locked_yn attribute"""
        plan_locked = StageFactPlanOutFactory(locked_yn='Y')
        plan_unlocked = StageFactPlanOutFactory(locked_yn='N')

        assert plan_locked.locked_yn == 'Y'
        assert plan_unlocked.locked_yn == 'N'

    def test_plan_str_representation(self):
        """Test string representation of plan"""
        plan = StageFactPlanOutFactory(
            wo_no='WO999999',
            mc_cd='MC100'
        )
        str_repr = str(plan)
        assert 'WO999999' in str_repr
        assert 'MC100' in str_repr

    def test_plan_quantity(self):
        """Test plan quantity field"""
        from decimal import Decimal
        plan = StageFactPlanOutFactory(plan_qty=Decimal('1500.50'))
        assert plan.plan_qty == Decimal('1500.50')

    def test_plan_auto_timestamp(self):
        """Test auto-generated load_ts"""
        plan = StageFactPlanOutFactory()
        assert plan.load_ts is not None
        assert isinstance(plan.load_ts, datetime)


@pytest.mark.django_db
class TestModelRelationships:
    """Tests for relationships between models"""

    def test_decision_event_relationship(self):
        """Test ForeignKey relationship between Decision and Event"""
        event = APSEventFactory(event_type='BREAKDOWN')
        decision1 = APSDecisionLogFactory(event=event, decision='APPLY')
        decision2 = APSDecisionLogFactory(event=event, decision='HOLD')

        assert decision1.event == event
        assert decision2.event == event
        assert event.decisions.count() == 2

    def test_decision_event_cascade_on_delete(self):
        """Test SET_NULL on delete behavior"""
        event = APSEventFactory()
        decision = APSDecisionLogFactory(event=event)

        event_id = event.id
        event.delete()

        decision.refresh_from_db()
        assert decision.event is None

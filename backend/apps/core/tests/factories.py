"""
Factory Boy factories for Core app models
"""
import factory
from factory.django import DjangoModelFactory
from datetime import datetime, timedelta
from apps.core.models import APSEvent, APSDecisionLog, APSDepEdge, StageFactPlanOut


class APSEventFactory(DjangoModelFactory):
    class Meta:
        model = APSEvent

    event_type = factory.Iterator(['EMERGENCY_ORDER', 'BREAKDOWN', 'QUALITY_ALERT', 'JOB_START'])
    mc_cd = factory.Sequence(lambda n: f'MC{n:03d}')
    wc_cd = factory.Sequence(lambda n: f'WC{n:03d}')
    wo_no = factory.Sequence(lambda n: f'WO{n:06d}')
    itm_id = factory.Sequence(lambda n: f'ITM{n:05d}')
    payload = factory.LazyFunction(lambda: {'test_key': 'test_value'})


class APSDecisionLogFactory(DjangoModelFactory):
    class Meta:
        model = APSDecisionLog

    event = factory.SubFactory(APSEventFactory)
    mc_cd = factory.Sequence(lambda n: f'MC{n:03d}')
    scope_size = factory.Faker('random_int', min=1, max=100)
    decision = factory.Iterator(['APPLY', 'HOLD'])
    reason = factory.Faker('sentence')
    kpi_json = factory.LazyFunction(lambda: {
        'utilization': 0.75,
        'avg_delay': 10.5,
        'max_delay': 25.0
    })


class APSDepEdgeFactory(DjangoModelFactory):
    class Meta:
        model = APSDepEdge

    src_wo_no = factory.Sequence(lambda n: f'WO{n:06d}')
    dst_wo_no = factory.Sequence(lambda n: f'WO{n+1:06d}')
    edge_type = factory.Iterator(['PRECEDENCE', 'SAME_ITEM', 'SAME_LOT', 'ALT_MACHINE'])
    edge_weight = factory.Faker('random_int', min=1, max=10)


class StageFactPlanOutFactory(DjangoModelFactory):
    class Meta:
        model = StageFactPlanOut

    wo_no = factory.Sequence(lambda n: f'WO{n:06d}')
    mc_cd = factory.Sequence(lambda n: f'MC{n:03d}')
    itm_id = factory.Sequence(lambda n: f'ITM{n:05d}')
    plan_qty = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    fr_ts = factory.LazyFunction(lambda: datetime.now())
    to_ts = factory.LazyFunction(lambda: datetime.now() + timedelta(hours=2))
    locked_yn = factory.Iterator(['Y', 'N'])
    freeze_level = factory.Iterator([0, 1, 2])

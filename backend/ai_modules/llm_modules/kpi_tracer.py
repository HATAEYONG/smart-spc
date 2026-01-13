"""
온톨로지 기반 KPI 영향 분석 모듈
RDF 그래프로 인과관계 추적 + SPARQL 쿼리
"""
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path
from datetime import datetime


class APSKPITracer:
    """
    APS 온톨로지 기반 KPI 영향 분석 시스템
    """

    def __init__(self):
        """
        초기화 및 온톨로지 구축
        """
        # RDF 그래프 생성
        self.graph = Graph()

        # 네임스페이스 정의
        self.APS = Namespace("http://aps-system.com/ontology#")
        self.graph.bind("aps", self.APS)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)

        # 온톨로지 구축
        self._build_ontology()

    def _build_ontology(self):
        """
        APS 도메인 온톨로지 구축
        """
        # 클래스 정의
        classes = [
            'Equipment',      # 설비
            'Job',           # 작업
            'Process',       # 공정
            'KPI',           # KPI 지표
            'Event',         # 이벤트
            'Constraint',    # 제약조건
            'Resource',      # 자원
            'Bottleneck'     # 병목
        ]

        for cls in classes:
            class_uri = self.APS[cls]
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(cls)))

        # 프로퍼티 정의
        properties = {
            'causes': ('원인이 된다', 'Event', 'Event'),
            'affects': ('영향을 준다', 'Event', 'KPI'),
            'leadsTo': ('이어진다', 'Event', 'Event'),
            'dependsOn': ('의존한다', 'Process', 'Equipment'),
            'hasBottleneck': ('병목을 가진다', 'Equipment', 'Bottleneck'),
            'decreases': ('감소시킨다', 'Event', 'KPI'),
            'increases': ('증가시킨다', 'Event', 'KPI'),
            'blockedBy': ('차단된다', 'Job', 'Event'),
            'delaysJob': ('작업을 지연시킨다', 'Event', 'Job'),
            'utilizationOf': ('가동률', 'Equipment', 'KPI'),
            'tardinessOf': ('지연시간', 'Job', 'KPI'),
            'makespanOf': ('총 완료시간', 'Process', 'KPI')
        }

        for prop, (label, domain, range_) in properties.items():
            prop_uri = self.APS[prop]
            self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
            self.graph.add((prop_uri, RDFS.label, Literal(label, lang='ko')))
            self.graph.add((prop_uri, RDFS.domain, self.APS[domain]))
            self.graph.add((prop_uri, RDFS.range, self.APS[range_]))

    def add_event(
        self,
        event_id: str,
        event_type: str,
        description: str,
        timestamp: Optional[datetime] = None,
        severity: float = 0.5
    ):
        """
        이벤트 추가

        Args:
            event_id: 이벤트 ID
            event_type: 이벤트 유형 (예: 'overload', 'delay', 'failure')
            description: 설명
            timestamp: 발생 시간
            severity: 심각도 (0.0~1.0)
        """
        event_uri = self.APS[f"Event_{event_id}"]
        self.graph.add((event_uri, RDF.type, self.APS.Event))
        self.graph.add((event_uri, self.APS.eventType, Literal(event_type)))
        self.graph.add((event_uri, self.APS.description, Literal(description, lang='ko')))
        self.graph.add((event_uri, self.APS.severity, Literal(severity, datatype=XSD.float)))

        if timestamp:
            self.graph.add((event_uri, self.APS.timestamp, Literal(timestamp, datatype=XSD.dateTime)))

    def add_kpi(self, kpi_id: str, kpi_name: str, value: float, target: float):
        """
        KPI 추가

        Args:
            kpi_id: KPI ID
            kpi_name: KPI 이름 (예: 'production_efficiency', 'tardiness')
            value: 현재 값
            target: 목표 값
        """
        kpi_uri = self.APS[f"KPI_{kpi_id}"]
        self.graph.add((kpi_uri, RDF.type, self.APS.KPI))
        self.graph.add((kpi_uri, self.APS.kpiName, Literal(kpi_name)))
        self.graph.add((kpi_uri, self.APS.value, Literal(value, datatype=XSD.float)))
        self.graph.add((kpi_uri, self.APS.target, Literal(target, datatype=XSD.float)))
        self.graph.add((kpi_uri, self.APS.deviation, Literal(value - target, datatype=XSD.float)))

    def add_equipment(self, equipment_id: str, equipment_name: str, utilization: float):
        """
        설비 추가

        Args:
            equipment_id: 설비 ID (예: 'MC001')
            equipment_name: 설비 이름
            utilization: 가동률 (0.0~1.0)
        """
        equipment_uri = self.APS[f"Equipment_{equipment_id}"]
        self.graph.add((equipment_uri, RDF.type, self.APS.Equipment))
        self.graph.add((equipment_uri, self.APS.equipmentId, Literal(equipment_id)))
        self.graph.add((equipment_uri, self.APS.equipmentName, Literal(equipment_name, lang='ko')))
        self.graph.add((equipment_uri, self.APS.utilization, Literal(utilization, datatype=XSD.float)))

    def add_causal_relation(
        self,
        source_id: str,
        relation: str,
        target_id: str,
        weight: float = 1.0
    ):
        """
        인과관계 추가

        Args:
            source_id: 원인 엔티티 ID (Event, Equipment 등)
            relation: 관계 유형 ('causes', 'affects', 'leadsTo', 'decreases', 'increases')
            target_id: 결과 엔티티 ID
            weight: 영향 가중치 (0.0~1.0)
        """
        # ID로부터 URI 추론
        source_uri = self._infer_uri(source_id)
        target_uri = self._infer_uri(target_id)
        relation_uri = self.APS[relation]

        self.graph.add((source_uri, relation_uri, target_uri))
        self.graph.add((source_uri, self.APS.impactWeight, Literal(weight, datatype=XSD.float)))

    def _infer_uri(self, entity_id: str) -> URIRef:
        """
        엔티티 ID로부터 URI 추론
        """
        if entity_id.startswith('MC'):
            return self.APS[f"Equipment_{entity_id}"]
        elif entity_id.startswith('JOB'):
            return self.APS[f"Job_{entity_id}"]
        elif entity_id.startswith('KPI'):
            return self.APS[f"KPI_{entity_id}"]
        elif entity_id.startswith('Event'):
            return self.APS[entity_id]
        else:
            # 기본값
            return self.APS[entity_id]

    def trace_kpi_impact(self, kpi_id: str, max_depth: int = 5) -> List[Dict]:
        """
        KPI 변화의 인과 체인 추적

        Args:
            kpi_id: 추적할 KPI ID
            max_depth: 최대 추적 깊이

        Returns:
            인과 체인 리스트: [{'source': ..., 'relation': ..., 'target': ..., 'depth': ...}, ...]
        """
        kpi_uri = self.APS[f"KPI_{kpi_id}"]
        causal_chains = []

        # SPARQL 쿼리: KPI에 영향을 주는 이벤트 찾기
        query = f"""
        PREFIX aps: <{self.APS}>
        PREFIX rdf: <{RDF}>

        SELECT ?event ?relation ?description ?severity
        WHERE {{
            ?event ?relation aps:KPI_{kpi_id} .
            ?event aps:description ?description .
            ?event aps:severity ?severity .
            FILTER (?relation = aps:affects || ?relation = aps:decreases || ?relation = aps:increases)
        }}
        ORDER BY DESC(?severity)
        """

        results = self.graph.query(query)

        for row in results:
            event_uri = row.event
            relation = row.relation
            description = row.description
            severity = float(row.severity)

            # 이벤트의 원인 추적 (재귀적)
            root_causes = self._trace_event_causes(event_uri, depth=0, max_depth=max_depth)

            causal_chains.append({
                'event': str(event_uri).split('#')[-1],
                'relation': str(relation).split('#')[-1],
                'description': str(description),
                'severity': severity,
                'root_causes': root_causes
            })

        return causal_chains

    def _trace_event_causes(
        self,
        event_uri: URIRef,
        depth: int,
        max_depth: int
    ) -> List[Dict]:
        """
        이벤트의 근본 원인 재귀 추적
        """
        if depth >= max_depth:
            return []

        # SPARQL 쿼리: 이벤트의 원인 찾기
        query = f"""
        PREFIX aps: <{self.APS}>

        SELECT ?cause ?relation ?description
        WHERE {{
            ?cause ?relation <{event_uri}> .
            ?cause aps:description ?description .
            FILTER (?relation = aps:causes || ?relation = aps:leadsTo)
        }}
        """

        results = self.graph.query(query)
        causes = []

        for row in results:
            cause_uri = row.cause
            relation = row.relation
            description = row.description

            # 재귀적으로 원인 추적
            sub_causes = self._trace_event_causes(cause_uri, depth + 1, max_depth)

            causes.append({
                'cause': str(cause_uri).split('#')[-1],
                'relation': str(relation).split('#')[-1],
                'description': str(description),
                'depth': depth + 1,
                'sub_causes': sub_causes
            })

        return causes

    def find_bottlenecks(self, threshold: float = 0.9) -> List[Dict]:
        """
        병목 설비 탐지

        Args:
            threshold: 가동률 임계값 (기본 0.9 = 90%)

        Returns:
            병목 설비 리스트
        """
        query = f"""
        PREFIX aps: <{self.APS}>
        PREFIX xsd: <{XSD}>

        SELECT ?equipment ?equipmentId ?utilization
        WHERE {{
            ?equipment rdf:type aps:Equipment .
            ?equipment aps:equipmentId ?equipmentId .
            ?equipment aps:utilization ?utilization .
            FILTER (?utilization >= {threshold})
        }}
        ORDER BY DESC(?utilization)
        """

        results = self.graph.query(query)
        bottlenecks = []

        for row in results:
            bottlenecks.append({
                'equipment_id': str(row.equipmentId),
                'utilization': float(row.utilization),
                'severity': min(1.0, (float(row.utilization) - threshold) / (1.0 - threshold))
            })

        return bottlenecks

    def export_graph(self, output_path: str, format: str = 'turtle'):
        """
        RDF 그래프 내보내기

        Args:
            output_path: 저장 경로
            format: 포맷 ('turtle', 'xml', 'json-ld')
        """
        self.graph.serialize(destination=output_path, format=format, encoding='utf-8')
        print(f"✅ RDF 그래프 저장: {output_path} (format: {format})")

    def import_graph(self, input_path: str, format: str = 'turtle'):
        """
        RDF 그래프 불러오기

        Args:
            input_path: 파일 경로
            format: 포맷 ('turtle', 'xml', 'json-ld')
        """
        self.graph.parse(input_path, format=format)
        print(f"✅ RDF 그래프 로드: {input_path}")


def create_example_scenario():
    """
    예제 시나리오 생성: MC001 과부하 → 생산 지연 → KPI 감소
    """
    print("=" * 80)
    print("🧪 KPI 영향 분석 예제 시나리오")
    print("=" * 80)

    tracer = APSKPITracer()

    # 1. 설비 추가
    print("\n📦 설비 등록...")
    tracer.add_equipment('MC001', '가공기 1호', utilization=0.95)
    tracer.add_equipment('MC002', '가공기 2호', utilization=0.65)
    tracer.add_equipment('MC003', '조립기 1호', utilization=0.75)

    # 2. 이벤트 추가
    print("📅 이벤트 등록...")
    tracer.add_event(
        'E001',
        'overload',
        'MC001 설비 과부하 발생 (가동률 95%)',
        timestamp=datetime.now(),
        severity=0.9
    )

    tracer.add_event(
        'E002',
        'wait_time_increase',
        '작업 대기 시간 증가 (평균 45분)',
        timestamp=datetime.now(),
        severity=0.7
    )

    tracer.add_event(
        'E003',
        'production_delay',
        '전체 생산 일정 지연',
        timestamp=datetime.now(),
        severity=0.8
    )

    # 3. KPI 추가
    print("📊 KPI 등록...")
    tracer.add_kpi(
        'production_efficiency',
        '생산효율',
        value=72.0,  # 현재 72%
        target=85.0  # 목표 85%
    )

    tracer.add_kpi(
        'total_tardiness',
        '총 지연시간',
        value=180.0,  # 현재 180분
        target=60.0   # 목표 60분
    )

    # 4. 인과관계 추가
    print("🔗 인과관계 구축...")

    # MC001 과부하 → 대기시간 증가
    tracer.add_causal_relation('Event_E001', 'causes', 'Event_E002', weight=0.9)

    # 대기시간 증가 → 생산 지연
    tracer.add_causal_relation('Event_E002', 'leadsTo', 'Event_E003', weight=0.8)

    # 생산 지연 → 생산효율 KPI 감소
    tracer.add_causal_relation('Event_E003', 'decreases', 'KPI_production_efficiency', weight=0.85)

    # 생산 지연 → 지연시간 KPI 증가
    tracer.add_causal_relation('Event_E003', 'increases', 'KPI_total_tardiness', weight=0.9)

    # 5. 인과 체인 추적
    print("\n🔍 KPI 영향 분석 (생산효율)...")
    causal_chains = tracer.trace_kpi_impact('production_efficiency', max_depth=3)

    print(f"\n발견된 인과 체인: {len(causal_chains)}개")
    for i, chain in enumerate(causal_chains, 1):
        print(f"\n[체인 {i}]")
        print(f"  이벤트: {chain['event']}")
        print(f"  설명: {chain['description']}")
        print(f"  관계: {chain['relation']}")
        print(f"  심각도: {chain['severity']:.2f}")

        if chain['root_causes']:
            print(f"  근본 원인:")
            for cause in chain['root_causes']:
                print(f"    → {cause['description']} (depth: {cause['depth']})")
                if cause['sub_causes']:
                    for sub in cause['sub_causes']:
                        print(f"      → {sub['description']} (depth: {sub['depth']})")

    # 6. 병목 탐지
    print("\n⚠️  병목 설비 탐지...")
    bottlenecks = tracer.find_bottlenecks(threshold=0.9)

    for bottleneck in bottlenecks:
        print(f"  • {bottleneck['equipment_id']}: 가동률 {bottleneck['utilization']*100:.1f}% (심각도: {bottleneck['severity']:.2f})")

    # 7. 그래프 저장
    output_path = Path(__file__).parent / 'kpi_analysis_example.ttl'
    tracer.export_graph(str(output_path), format='turtle')

    print("\n" + "=" * 80)
    print("✅ 예제 시나리오 완료!")
    print("=" * 80)

    return tracer, causal_chains, bottlenecks


if __name__ == '__main__':
    create_example_scenario()

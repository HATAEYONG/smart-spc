"""
Inspection Schemas - INSP-01/02
Matches frontend/src/types/inspection.ts
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProcessFlowDTO(BaseModel):
    """Process flow"""
    flow_id: str
    site_id: str
    flow_name: str
    rev_no: int
    status: str  # 'DRAFT' | 'ACTIVE' | 'OBSOLETE'
    description: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class ProcessStepDTO(BaseModel):
    """Process step"""
    step_id: str
    flow_id: str
    seq_no: int
    step_name: str
    workcenter: Optional[str]
    machine_group: Optional[str]
    is_inspection_point: bool
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class AIProcessDesignRequest(BaseModel):
    """AI process design request"""
    company: dict
    product: dict
    constraints: dict
    known_defects: List[str]
    customer_requirements: List[str]


class AIProcessDesignResponse(BaseModel):
    """AI process design response"""
    ai_id: str
    process_flow: List[dict]
    inspection_points: List[dict]
    assumptions: List[str]
    risks: List[str]
    confidence: float


class AICriteriaChecklistRequest(BaseModel):
    """AI criteria checklist request"""
    item: str
    step: str
    inspection_type: str
    defect_modes: List[str]
    acceptance_policy: dict


class AICriteriaChecklistResponse(BaseModel):
    """AI criteria checklist response"""
    ai_id: str
    criteria_table: List[dict]
    checklist: List[dict]


class InspectionRunDTO(BaseModel):
    """Inspection run"""
    run_id: str
    site_id: str
    lot_id: str
    plan_id: str
    step_id: str
    run_dt: datetime
    inspector_id: Optional[str]
    sample_n: int
    environment: dict = {}
    overall_judgement: str  # 'PASS' | 'FAIL' | 'HOLD'
    ai_summary_id: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class InspectionResultDTO(BaseModel):
    """Inspection result"""
    result_id: str
    run_id: str
    char_id: str
    spec_id: str
    sample_no: int
    value_num: Optional[float]
    value_text: Optional[str]
    value_enum: Optional[str]
    is_out_of_spec: bool
    defect_code_id: Optional[str]
    remark: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class BulkResultRequest(BaseModel):
    """Bulk result request"""
    results: List[dict]


class BulkResultResponse(BaseModel):
    """Bulk result response"""
    inserted: int
    oos_count: int


class InspectionJudgeResponse(BaseModel):
    """Inspection judgement response"""
    run_id: str
    overall_judgement: str  # 'PASS' | 'FAIL' | 'HOLD'
    oos_count: int

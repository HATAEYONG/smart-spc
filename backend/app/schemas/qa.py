"""
QA/CAPA Schemas - QA-01
Matches frontend/src/types/qa.ts
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class QaProcessDTO(BaseModel):
    """QA process"""
    qa_proc_id: str
    site_id: str
    proc_name: str
    rev_no: int
    status: str  # 'DRAFT' | 'ACTIVE' | 'OBSOLETE'
    owner_dept_id: Optional[str]
    description: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class QaRequirementDTO(BaseModel):
    """QA requirement"""
    req_id: str
    qa_proc_id: str
    req_type: str  # 'ISO' | 'IATF' | 'INHOUSE' | 'CUSTOMER'
    clause: Optional[str]
    req_text: str
    priority: int
    evidence_needed: Optional[str]
    control_method: str  # 'DOC' | 'RECORD' | 'SYSTEM'
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class QaAssessmentDTO(BaseModel):
    """QA assessment"""
    assess_id: str
    site_id: str
    qa_proc_id: str
    assess_dt: date
    assessor_id: Optional[str]
    scope: Optional[str]
    overall_level: Optional[str]
    ai_summary_id: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class QaFindingDTO(BaseModel):
    """QA gap finding"""
    finding_id: str
    assess_id: str
    req_id: str
    finding_type: str  # 'MISSING' | 'UPDATE' | 'IMPROVE'
    severity: int
    as_is: Optional[str]
    to_be: Optional[str]
    evidence: Optional[str]
    due_dt: Optional[date]
    status: str  # 'OPEN' | 'IN_PROGRESS' | 'DONE'
    owner_user_id: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class CapaDTO(BaseModel):
    """CAPA case"""
    capa_id: str
    site_id: str
    source_type: str  # 'SPC_EVENT' | 'INSPECTION_FAIL' | 'QA_FINDING' | 'CUSTOMER_CLAIM'
    source_id: Optional[str]
    problem_statement: str
    containment_action: Optional[str]
    root_cause: Optional[str]
    corrective_action: Optional[str]
    preventive_action: Optional[str]
    owner_user_id: Optional[str]
    due_dt: Optional[date]
    status: str  # 'OPEN' | 'IN_PROGRESS' | 'DONE' | 'VERIFIED' | 'CLOSED'
    effectiveness_check_dt: Optional[date]
    ai_support_id: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class AIRootCauseCAPARequest(BaseModel):
    """AI root cause & CAPA request"""
    context: dict
    facts: List[str]
    constraints: List[str]


class AIRootCauseCAPAResponse(BaseModel):
    """AI root cause & CAPA response"""
    ai_id: str
    root_cause: str
    actions: List[dict]
    confidence: float

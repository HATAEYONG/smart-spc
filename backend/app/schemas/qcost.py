"""
Q-COST Schemas - QCOST-01/02
Matches frontend/src/types/qcost.ts
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class QCostCategoryDTO(BaseModel):
    """Quality cost category"""
    qcat_id: str
    site_id: str
    lvl1: str  # 'PREVENTION' | 'APPRAISAL' | 'INTERNAL_FAILURE' | 'EXTERNAL_FAILURE'
    lvl2: Optional[str]
    lvl3: Optional[str]
    code: str
    name: str
    description: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class QCostItemDTO(BaseModel):
    """Quality cost item"""
    qitem_id: str
    site_id: str
    qcat_id: str
    item_name: str
    unit_cost_rule: str  # 'FIXED' | 'RATE' | 'MANUAL'
    gl_account: Optional[str]
    dept_id: Optional[str]
    copq_flag: bool
    is_active: bool
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class QCostEntryDTO(BaseModel):
    """Quality cost entry"""
    entry_id: str
    site_id: str
    qitem_id: str
    dept_id: str
    occur_dt: date  # YYYY-MM-DD
    amount: float
    currency: str = "KRW"
    qty: Optional[float]
    lot_id: Optional[str]
    run_id: Optional[str]
    evidence_file_id: Optional[str]
    memo: Optional[str]
    ai_classification: dict = {}
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class AIQCostClassifyRequest(BaseModel):
    """AI Q-COST classification request"""
    text: str
    amount: float
    context: dict = {}  # { dept: str, lot_no: str }


class AIQCostClassifyResponse(BaseModel):
    """AI Q-COST classification response"""
    ai_id: str
    classification: dict
    confidence: float
    rationale: list[str]


class COPQReportRequest(BaseModel):
    """COPQ report generation request"""
    period: str  # YYYY-MM
    sales_amount: int


class COPQReportResponse(BaseModel):
    """COPQ report response"""
    copq_id: str
    period: str
    ai_id: str
    report_json: dict

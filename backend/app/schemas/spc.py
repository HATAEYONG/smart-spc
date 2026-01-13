"""
SPC Schemas - SPC-01
Matches frontend/src/types/spc.ts
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SpcChartDefDTO(BaseModel):
    """SPC chart definition"""
    chart_def_id: str
    site_id: str
    char_id: str
    chart_type: str  # 'XBAR_R' | 'XBAR_S' | 'I_MR' | 'P' | 'NP' | 'C' | 'U'
    subgroup_size: Optional[int]
    calc_method: str  # 'STANDARD' | 'ROBUST'
    rule_set: dict = {}
    baseline_from_dt: Optional[datetime]
    baseline_to_dt: Optional[datetime]
    status: str  # 'DRAFT' | 'ACTIVE' | 'OBSOLETE'
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class SpcPointDTO(BaseModel):
    """SPC chart point"""
    point_id: str
    chart_def_id: str
    run_id: Optional[str]
    point_dt: datetime
    n: Optional[int]
    xbar: Optional[float]
    r: Optional[float]
    s: Optional[float]
    p: Optional[float]
    u: Optional[float]
    mr: Optional[float]
    ucl: float
    cl: float
    lcl: float
    cp: Optional[float]
    cpk: Optional[float]
    is_violation: bool
    violation_codes: list = []
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class SpcEventDTO(BaseModel):
    """SPC event"""
    event_id: str
    site_id: str
    chart_def_id: str
    point_id: str
    event_dt: datetime
    severity: int
    event_type: str  # 'OOS' | 'RULE_VIOLATION' | 'SHIFT' | 'TREND'
    status: str  # 'OPEN' | 'ACK' | 'INVESTIGATING' | 'CLOSED'
    owner_user_id: Optional[str]
    ai_rootcause_id: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class SamplingRuleDTO(BaseModel):
    """Sampling rule"""
    sample_rule_id: str
    site_id: str
    rule_name: str
    standard: str  # 'ISO2859' | 'ANSI_Z1_4' | 'INHOUSE'
    aql: float
    inspection_level: Optional[str]
    lot_size_min: int
    lot_size_max: int
    sample_size: int
    accept_num: int
    reject_num: int
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    updated_by: Optional[str]


class SpcChartCreateRequest(BaseModel):
    """SPC chart creation request"""
    char_id: str
    chart_type: str
    subgroup_size: Optional[int] = None
    rule_set: dict = {}
    status: str = 'DRAFT'


class SpcRecalcResponse(BaseModel):
    """SPC recalculation response"""
    chart_def_id: str
    points_created: int
    violations: int


class SpcEventCreateRequest(BaseModel):
    """SPC event creation request"""
    chart_def_id: str
    point_id: str
    event_type: str  # 'OOS' | 'RULE_VIOLATION' | 'SHIFT' | 'TREND'
    severity: int
    owner_user_id: Optional[str] = None

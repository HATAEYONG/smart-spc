"""
Dashboard Schemas - DASH-01
Matches frontend/src/types/dashboard.ts
"""
from pydantic import BaseModel
from typing import List, Optional


class KPIs(BaseModel):
    """KPI metrics"""
    copq_rate: float
    total_copq: int
    total_qcost: int
    oos_count: int
    spc_open_events: int


class TopDefect(BaseModel):
    """Top defect item"""
    defect: str
    count: int
    cost: int


class Alert(BaseModel):
    """SPC alert"""
    event_id: str
    type: str
    severity: int
    title: str


class AIInsight(BaseModel):
    """AI insight"""
    ai_id: str
    title: str
    summary: str
    confidence: float


class DashboardSummaryDTO(BaseModel):
    """Dashboard summary response"""
    period: str
    kpis: KPIs
    top_defects: List[TopDefect]
    alerts: List[Alert]
    ai_insights: List[AIInsight]

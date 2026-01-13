"""
Dashboard Endpoint - DASH-01
GET /dashboard/summary
"""
from fastapi import APIRouter, Query
from typing import List
from app.schemas.common import ApiResponse
from app.schemas.dashboard import DashboardSummaryDTO, KPIs, TopDefect, Alert, AIInsight

router = APIRouter()


@router.get("/dashboard/summary", response_model=ApiResponse[DashboardSummaryDTO])
async def get_dashboard_summary(
    period: str = Query(..., description="Period in YYYY-MM format")
):
    """
    Get dashboard summary
    
    Returns KPIs, top defects, alerts, and AI insights for the specified period.
    Matches frontend: dashboardService.getSummary(period)
    """
    # TODO: Implement actual database queries
    
    # Sample data (replace with actual database queries)
    kpis = KPIs(
        copq_rate=0.0342,
        total_copq=41000000,
        total_qcost=62000000,
        oos_count=18,
        spc_open_events=6
    )
    
    top_defects = [
        TopDefect(defect="스크래치", count=61, cost=8000000),
        TopDefect(defect="치수불량", count=45, cost=5000000),
        TopDefect(defect="이물", count=28, cost=2000000),
        TopDefect(defect="색상불량", count=15, cost=1000000),
        TopDefect(defect="기타", count=12, cost=500000)
    ]
    
    alerts = [
        Alert(event_id="evt-001", type="TREND", severity=4, title="내경 추세 발생"),
        Alert(event_id="evt-002", type="OOS", severity=5, title="외경 규격 이탈"),
        Alert(event_id="evt-003", type="RULE_1", severity=3, title="3σ 벗어남")
    ]
    
    ai_insights = [
        AIInsight(
            ai_id="ai-001",
            title="COPQ 주요 원인 분석",
            summary="치수불량이 전체 COPQ의 40% 차지. CNC 가공 공정에서 온도 보정 주기를 단축할 것을 권장합니다.",
            confidence=0.86
        ),
        AIInsight(
            ai_id="ai-002",
            title="세척 공정 개선 효과",
            summary="세척 시간 연장으로 이물 부착률이 15% 감소했습니다.",
            confidence=0.92
        )
    ]
    
    data = DashboardSummaryDTO(
        period=period,
        kpis=kpis,
        top_defects=top_defects,
        alerts=alerts,
        ai_insights=ai_insights
    )
    
    return ApiResponse(ok=True, data=data, error=None)

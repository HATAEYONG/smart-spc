/**
 * Dashboard Types
 * DASH-01: 대시보드 API 타입 정의
 */

export interface DashboardSummaryDTO {
  period: string;
  kpis: KPIs;
  top_defects: TopDefect[];
  alerts: Alert[];
  ai_insights: AIInsight[];
}

export interface KPIs {
  copq_rate: number;
  total_copq: number;
  total_qcost: number;
  oos_count: number;
  spc_open_events: number;
}

export interface TopDefect {
  defect: string;
  count: number;
  cost: number;
}

export interface Alert {
  event_id: string;
  type: string;
  severity: number;
  title: string;
}

export interface AIInsight {
  ai_id: string;
  title: string;
  summary: string;
  confidence: number;
}

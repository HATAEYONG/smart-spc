/**
 * SPC 품질관리 시스템 TypeScript 타입 정의
 */

// 제품 정보
export interface Product {
  id: number;
  product_code: string;
  product_name: string;
  usl: number; // Upper Specification Limit
  lsl: number; // Lower Specification Limit
  target_value?: number;
  unit: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 검사 계획
export interface InspectionPlan {
  id: number;
  product: number;
  product_name?: string;
  product_code?: string;
  plan_name: string;
  frequency: 'HOURLY' | 'SHIFT' | 'DAILY' | 'BATCH';
  sample_size: number;
  subgroup_size: number;
  sampling_method: 'ALL' | 'RANDOM' | 'PERIODIC';
  characteristic: string;
  measurement_method?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 품질 측정 데이터
export interface QualityMeasurement {
  id: number;
  product: number;
  product_name?: string;
  product_code?: string;
  inspection_plan?: number;
  measurement_value: number;
  sample_number: number;
  subgroup_number: number;
  measured_at: string;
  measured_by: string;
  machine_id?: string;
  lot_number?: string;
  is_within_spec: boolean;
  is_within_control: boolean;
  remarks?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

// 관리도 한계선
export interface ControlChart {
  id: number;
  product: number;
  product_name?: string;
  product_code?: string;
  inspection_plan: number;
  chart_type: 'XBAR_R' | 'XBAR_S' | 'I_MR' | 'P_CHART' | 'NP_CHART' | 'C_CHART' | 'U_CHART';

  // X-bar Chart 한계선
  xbar_ucl?: number;
  xbar_cl?: number;
  xbar_lcl?: number;

  // R Chart 한계선
  r_ucl?: number;
  r_cl?: number;
  r_lcl?: number;

  // S Chart 한계선
  s_ucl?: number;
  s_cl?: number;
  s_lcl?: number;

  // p, np, c, u Chart 한계선
  p_ucl?: number;
  p_cl?: number;
  p_lcl?: number;

  subgroup_size: number;
  num_subgroups: number;
  calculated_at: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 관리도 데이터 포인트
export interface ControlChartDataPoint {
  subgroup_number: number;
  xbar?: number;
  r?: number;
  s?: number;
  individual?: number;
  moving_range?: number;
  p?: number;
  np_value?: number;
  c?: number;
  u?: number;
  measured_at: string;
}

// 관리도 시각화 데이터
export interface ControlChartData {
  chart_type: string;
  data: ControlChartDataPoint[];
  limits: {
    xbar?: { ucl: number; cl: number; lcl: number };
    r?: { ucl: number; cl: number; lcl: number };
    s?: { ucl: number; cl: number; lcl: number };
    p?: { ucl: number; cl: number; lcl: number };
  };
}

// 공정능력 분석 결과
export interface ProcessCapability {
  id: number;
  product: number;
  product_name?: string;
  product_code?: string;
  control_chart?: number;

  cp: number;
  cpk: number;
  cpu: number;
  cpl: number;

  pp?: number;
  ppk?: number;

  mean: number;
  std_deviation: number;
  sample_size: number;

  is_normal: boolean;
  normality_test_statistic?: number;
  normality_test_p_value?: number;

  analysis_start: string;
  analysis_end: string;
  analyzed_at: string;
  notes?: string;
}

// Run Rule 위반
export interface RunRuleViolation {
  id: number;
  control_chart: number;
  chart_type?: string;
  measurement: number;
  measurement_value?: number;
  product_code?: string;

  rule_type: 'RULE_1' | 'RULE_2' | 'RULE_3' | 'RULE_4' | 'RULE_5' | 'RULE_6' | 'RULE_7' | 'RULE_8';
  description: string;
  severity: 1 | 2 | 3 | 4;

  violation_data: Record<string, any>;

  is_resolved: boolean;
  resolved_at?: string;
  resolution_notes?: string;

  detected_at: string;
}

// 품질 경고
export interface QualityAlert {
  id: number;
  product: number;
  product_name?: string;
  product_code?: string;
  measurement?: number;
  violation?: number;

  alert_type: 'OUT_OF_SPEC' | 'OUT_OF_CONTROL' | 'RUN_RULE' | 'TREND' | 'PREDICTION' | 'CAPABILITY';
  title: string;
  description: string;
  priority: 1 | 2 | 3 | 4;
  priority_display?: string;

  status: 'NEW' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'RESOLVED' | 'CLOSED';
  status_display?: string;
  alert_type_display?: string;
  assigned_to?: string;

  acknowledged_at?: string;
  acknowledged_by?: string;
  resolved_at?: string;
  resolved_by?: string;
  resolution_notes?: string;

  root_cause?: string;
  corrective_action?: string;
  preventive_action?: string;

  alert_data?: Record<string, any>;

  created_at: string;
  updated_at: string;
}

// 품질 보고서
export interface QualityReport {
  id: number;
  report_type: 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'CUSTOM';
  report_type_display?: string;
  title: string;

  start_date: string;
  end_date: string;

  products: number[];
  products_data?: Product[];

  summary?: string;
  key_findings?: string[];
  recommendations?: string[];

  total_measurements: number;
  out_of_spec_count: number;
  out_of_control_count: number;
  alert_count: number;

  report_file?: string;

  generated_by: string;
  generated_at: string;
}

// 제품 요약 통계
export interface ProductSummary {
  product_code: string;
  product_name: string;
  period: string;
  statistics: {
    total_measurements: number;
    out_of_spec_count: number;
    out_of_spec_rate: number;
    out_of_control_count: number;
    out_of_control_rate: number;
  };
  capability: {
    cp?: number;
    cpk?: number;
    analyzed_at?: string;
  };
}

// 경고 대시보드 요약
export interface AlertDashboard {
  total: number;
  by_priority: {
    urgent: number;
    high: number;
    medium: number;
    low: number;
  };
  by_status: {
    new: number;
    acknowledged: number;
    investigating: number;
    resolved: number;
    closed: number;
  };
  by_type: Record<string, number>;
}

// API 응답 타입
export interface ApiResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
  data?: T;
}

// API 에러 응답
export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

// 페이지네이션 파라미터
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

// 필터 파라미터
export interface FilterParams {
  product?: number;
  product_code?: string;
  start_date?: string;
  end_date?: string;
  is_active?: boolean;
  status?: string;
  alert_type?: string;
  priority?: number;
}

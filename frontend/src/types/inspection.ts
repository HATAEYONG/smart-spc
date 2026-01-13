/**
 * Inspection Types
 * INSP-01/02: 검사 프로세스 및 실행 API 타입 정의
 */

export interface ProcessFlowDTO {
  flow_id: string;
  site_id: string;
  flow_name: string;
  rev_no: number;
  status: 'DRAFT' | 'ACTIVE' | 'OBSOLETE';
  description: string | null;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface ProcessStepDTO {
  step_id: string;
  flow_id: string;
  seq_no: number;
  step_name: string;
  workcenter: string | null;
  machine_group: string | null;
  is_inspection_point: boolean;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface AIProcessDesignRequest {
  company: {
    industry: string;
    site: string;
  };
  product: {
    item_name: string;
    process: string;
  };
  constraints: {
    inspection_headcount: number;
    shift: number;
  };
  known_defects: string[];
  customer_requirements: string[];
}

export interface AIProcessDesignResponse {
  ai_id: string;
  process_flow: ProcessFlowDTO[];
  inspection_points: ProcessStepDTO[];
  assumptions: string[];
  risks: string[];
  confidence: number;
}

export interface AICriteriaChecklistRequest {
  item: string;
  step: string;
  inspection_type: string;
  defect_modes: string[];
  acceptance_policy: {
    A: string;
    B: string;
    C: string;
  };
}

export interface AICriteriaChecklistResponse {
  ai_id: string;
  criteria_table: CriteriaTable[];
  checklist: ChecklistItem[];
}

export interface CriteriaTable {
  category: string;
  check: string;
  method: string;
  accept: string;
  reject: string;
  action: string;
}

export interface ChecklistItem {
  no: number;
  question: string;
  type: string;
  photo_required: boolean;
}

export interface InspectionRunDTO {
  run_id: string;
  site_id: string;
  lot_id: string;
  plan_id: string;
  step_id: string;
  run_dt: string;
  inspector_id: string | null;
  sample_n: number;
  environment: Record<string, any>;
  overall_judgement: 'PASS' | 'FAIL' | 'HOLD';
  ai_summary_id: string | null;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface InspectionResultDTO {
  result_id: string;
  run_id: string;
  char_id: string;
  spec_id: string;
  sample_no: number;
  value_num: number | null;
  value_text: string | null;
  value_enum: string | null;
  is_out_of_spec: boolean;
  defect_code_id: string | null;
  remark: string | null;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface BulkResultRequest {
  results: Omit<InspectionResultDTO, 'result_id' | 'created_at' | 'created_by' | 'updated_at' | 'updated_by'>[];
}

export interface BulkResultResponse {
  inserted: number;
  oos_count: number;
}

export interface InspectionJudgeResponse {
  run_id: string;
  overall_judgement: 'PASS' | 'FAIL' | 'HOLD';
  oos_count: number;
}

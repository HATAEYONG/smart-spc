/**
 * Q-COST Types
 * QCOST-01/02: 품질비용 관리 API 타입 정의
 */

export interface QCostCategoryDTO {
  qcat_id: string;
  site_id: string;
  lvl1: 'PREVENTION' | 'APPRAISAL' | 'INTERNAL_FAILURE' | 'EXTERNAL_FAILURE';
  lvl2: string | null;
  lvl3: string | null;
  code: string;
  name: string;
  description: string | null;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface QCostItemDTO {
  qitem_id: string;
  site_id: string;
  qcat_id: string;
  item_name: string;
  unit_cost_rule: 'FIXED' | 'RATE' | 'MANUAL';
  gl_account: string | null;
  dept_id: string | null;
  copq_flag: boolean;
  is_active: boolean;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface QCostEntryDTO {
  entry_id: string;
  site_id: string;
  qitem_id: string;
  dept_id: string;
  occur_dt: string; // YYYY-MM-DD
  amount: number;
  currency: string;
  qty: number | null;
  lot_id: string | null;
  run_id: string | null;
  evidence_file_id: string | null;
  memo: string | null;
  ai_classification: Record<string, any>;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface AIQCostClassifyRequest {
  text: string;
  amount: number;
  context: {
    dept?: string;
    lot_no?: string;
  };
}

export interface AIQCostClassifyResponse {
  ai_id: string;
  classification: {
    lvl1: string;
    lvl2: string;
    qitem_suggested_name: string;
    copq_flag: boolean;
  };
  confidence: number;
  rationale: string[];
}

export interface COPQReportRequest {
  period: string; // YYYY-MM
  sales_amount: number;
}

export interface COPQReportResponse {
  copq_id: string;
  period: string;
  ai_id: string;
  report_json: Record<string, any>;
}

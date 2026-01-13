/**
 * QA/CAPA Types
 * QA-01: 품질 진단/GAP/CAPA API 타입 정의
 */

export interface QaProcessDTO {
  qa_proc_id: string;
  site_id: string;
  proc_name: string;
  rev_no: number;
  status: 'DRAFT' | 'ACTIVE' | 'OBSOLETE';
  owner_dept_id: string | null;
  description: string | null;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface QaRequirementDTO {
  req_id: string;
  qa_proc_id: string;
  req_type: 'ISO' | 'IATF' | 'INHOUSE' | 'CUSTOMER';
  clause: string | null;
  req_text: string;
  priority: number;
  evidence_needed: string | null;
  control_method: 'DOC' | 'RECORD' | 'SYSTEM';
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface QaAssessmentDTO {
  assess_id: string;
  site_id: string;
  qa_proc_id: string;
  assess_dt: string;
  assessor_id: string | null;
  scope: string | null;
  overall_level: string | null;
  ai_summary_id: string | null;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface QaFindingDTO {
  finding_id: string;
  assess_id: string;
  req_id: string;
  finding_type: 'MISSING' | 'UPDATE' | 'IMPROVE';
  severity: number;
  as_is: string | null;
  to_be: string | null;
  evidence: string | null;
  due_dt: string | null;
  status: 'OPEN' | 'IN_PROGRESS' | 'DONE';
  owner_user_id: string | null;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface CapaDTO {
  capa_id: string;
  site_id: string;
  source_type: 'SPC_EVENT' | 'INSPECTION_FAIL' | 'QA_FINDING' | 'CUSTOMER_CLAIM';
  source_id: string | null;
  problem_statement: string;
  containment_action: string | null;
  root_cause: string | null;
  corrective_action: string | null;
  preventive_action: string | null;
  owner_user_id: string | null;
  due_dt: string | null;
  status: 'OPEN' | 'IN_PROGRESS' | 'DONE' | 'VERIFIED' | 'CLOSED';
  effectiveness_check_dt: string | null;
  ai_support_id: string | null;
  created_at: string;
  created_by: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface AIRootCauseCAPARequest {
  context: {
    event_id?: string;
    chart?: string;
  };
  facts: string[];
  constraints: string[];
}

export interface AIRootCauseCAPAResponse {
  ai_id: string;
  root_cause: string;
  actions: {
    type: 'corrective' | 'preventive' | 'containment';
    text: string;
  }[];
  confidence: number;
}

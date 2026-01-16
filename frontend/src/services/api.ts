/**
 * SPC API 서비스
 * Backend와 통신하는 Axios 기반 API 클라이언트
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Product,
  InspectionPlan,
  QualityMeasurement,
  ControlChart,
  ControlChartData,
  ProcessCapability,
  RunRuleViolation,
  QualityAlert,
  QualityReport,
  ProductSummary,
  AlertDashboard,
  ApiResponse,
  ApiError,
  PaginationParams,
  FilterParams,
} from '@/types/spc';

// Axios 인스턴스 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1/spc',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 (인증 토큰 추가 등)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 (에러 처리)
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response) {
      // 서버 에러 응답
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // 요청은 보냈지만 응답 없음
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ============================================================
// Product API
// ============================================================
export const productApi = {
  list: async (params?: PaginationParams & FilterParams) => {
    const response = await apiClient.get<ApiResponse<Product>>('/products/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await apiClient.get<Product>(`/products/${id}/`);
    return response.data;
  },

  create: async (data: Partial<Product>) => {
    const response = await apiClient.post<Product>('/products/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Product>) => {
    const response = await apiClient.patch<Product>(`/products/${id}/`, data);
    return response.data;
  },

  delete: async (id: number) => {
    await apiClient.delete(`/products/${id}/`);
  },

  summary: async (id: number) => {
    const response = await apiClient.get<ProductSummary>(`/products/${id}/summary/`);
    return response.data;
  },
};

// ============================================================
// Inspection Plan API
// ============================================================
export const inspectionPlanApi = {
  list: async (params?: PaginationParams & FilterParams) => {
    const response = await apiClient.get<ApiResponse<InspectionPlan>>('/inspection-plans/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await apiClient.get<InspectionPlan>(`/inspection-plans/${id}/`);
    return response.data;
  },

  create: async (data: Partial<InspectionPlan>) => {
    const response = await apiClient.post<InspectionPlan>('/inspection-plans/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<InspectionPlan>) => {
    const response = await apiClient.patch<InspectionPlan>(`/inspection-plans/${id}/`, data);
    return response.data;
  },

  delete: async (id: number) => {
    await apiClient.delete(`/inspection-plans/${id}/`);
  },
};

// ============================================================
// Quality Measurement API
// ============================================================
export const measurementApi = {
  list: async (params?: PaginationParams & FilterParams) => {
    const response = await apiClient.get<ApiResponse<QualityMeasurement>>('/measurements/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await apiClient.get<QualityMeasurement>(`/measurements/${id}/`);
    return response.data;
  },

  create: async (data: Partial<QualityMeasurement>) => {
    const response = await apiClient.post<QualityMeasurement>('/measurements/', data);
    return response.data;
  },

  bulkCreate: async (measurements: Partial<QualityMeasurement>[]) => {
    const response = await apiClient.post('/measurements/bulk_create/', { measurements });
    return response.data;
  },

  chartData: async (params: {
    product_id: number;
    chart_type?: string;
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await apiClient.get<ControlChartData>('/measurements/chart_data/', { params });
    return response.data;
  },
};

// ============================================================
// Control Chart API
// ============================================================
export const controlChartApi = {
  list: async (params?: PaginationParams & FilterParams) => {
    const response = await apiClient.get<ApiResponse<ControlChart>>('/control-charts/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await apiClient.get<ControlChart>(`/control-charts/${id}/`);
    return response.data;
  },

  calculate: async (data: { product_id: number; chart_type: string; num_subgroups?: number }) => {
    const response = await apiClient.post('/control-charts/calculate/', data);
    return response.data;
  },
};

// ============================================================
// Process Capability API
// ============================================================
export const processCapabilityApi = {
  list: async (params?: PaginationParams & FilterParams) => {
    const response = await apiClient.get<ApiResponse<ProcessCapability>>('/process-capability/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await apiClient.get<ProcessCapability>(`/process-capability/${id}/`);
    return response.data;
  },

  analyze: async (data: {
    product_id: number;
    start_date: string;
    end_date: string;
    chart_type: string;
  }) => {
    const response = await apiClient.post<ProcessCapability>('/process-capability/analyze/', data);
    return response.data;
  },
};

// ============================================================
// Run Rule Violation API
// ============================================================
export const runRuleViolationApi = {
  list: async (params?: PaginationParams & FilterParams) => {
    const response = await apiClient.get<ApiResponse<RunRuleViolation>>('/run-rule-violations/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await apiClient.get<RunRuleViolation>(`/run-rule-violations/${id}/`);
    return response.data;
  },

  resolve: async (id: number, resolution_notes: string) => {
    const response = await apiClient.post(`/run-rule-violations/${id}/resolve/`, { resolution_notes });
    return response.data;
  },
};

// ============================================================
// Quality Alert API
// ============================================================
export const qualityAlertApi = {
  list: async (params?: PaginationParams & FilterParams) => {
    const response = await apiClient.get<ApiResponse<QualityAlert>>('/alerts/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await apiClient.get<QualityAlert>(`/alerts/${id}/`);
    return response.data;
  },

  create: async (data: Partial<QualityAlert>) => {
    const response = await apiClient.post<QualityAlert>('/alerts/', data);
    return response.data;
  },

  acknowledge: async (id: number, acknowledged_by: string) => {
    const response = await apiClient.post(`/alerts/${id}/acknowledge/`, { acknowledged_by });
    return response.data;
  },

  resolve: async (id: number, data: {
    resolved_by: string;
    resolution_notes?: string;
    root_cause?: string;
    corrective_action?: string;
    preventive_action?: string;
  }) => {
    const response = await apiClient.post(`/alerts/${id}/resolve/`, data);
    return response.data;
  },

  dashboard: async () => {
    const response = await apiClient.get<AlertDashboard>('/alerts/dashboard/');
    return response.data;
  },
};

// ============================================================
// Quality Report API
// ============================================================
export const qualityReportApi = {
  list: async (params?: PaginationParams & FilterParams) => {
    const response = await apiClient.get<ApiResponse<QualityReport>>('/reports/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await apiClient.get<QualityReport>(`/reports/${id}/`);
    return response.data;
  },

  generate: async (data: {
    report_type: string;
    product_ids: number[];
    start_date: string;
    end_date: string;
  }) => {
    const response = await apiClient.post<QualityReport>('/reports/generate/', data);
    return response.data;
  },
};

// Export 전체 API 객체
export const spcApi = {
  products: productApi,
  inspectionPlans: inspectionPlanApi,
  measurements: measurementApi,
  controlCharts: controlChartApi,
  processCapability: processCapabilityApi,
  runRuleViolations: runRuleViolationApi,
  qualityAlerts: qualityAlertApi,
  reports: qualityReportApi,
};

// Export axios instance for direct API calls
export const api = apiClient;

export default spcApi;

// ============================================================
// Django Backend - New Apps API
// ============================================================

// 새로운 API 클라이언트 생성 (Django 백엔드용)
const djangoApiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_DJANGO_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
djangoApiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// -----
// 품질 이슈 타입
// -----
export interface QualityIssue {
  id: number;
  issue_number: string;
  title: string;
  description?: string;
  product_code: string;
  product_name: string;
  defect_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  severity_display?: string;
  status: 'OPEN' | 'INVESTIGATING' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  status_display?: string;
  reported_date: string;
  reporter?: number;
  reporter_name?: string;
  department: string;
  defect_quantity: number;
  cost_impact: number;
  responsible_person?: string;
  target_resolution_date: string;
  actual_resolution_date?: string;
  completion_notes?: string;
  analyses_4m?: any[];
  solving_steps?: any[];
}

// 품질 이슈 API
export const qualityIssuesApi = {
  list: async (params?: any) => {
    const response = await djangoApiClient.get<{results: QualityIssue[]; count: number}>('/quality/issues/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await djangoApiClient.get<QualityIssue>(`/quality/issues/${id}/`);
    return response.data;
  },

  create: async (data: Partial<QualityIssue>) => {
    const response = await djangoApiClient.post<QualityIssue>('/quality/issues/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<QualityIssue>) => {
    const response = await djangoApiClient.put<QualityIssue>(`/quality/issues/${id}/`, data);
    return response.data;
  },

  delete: async (id: number) => {
    await djangoApiClient.delete(`/quality/issues/${id}/`);
  },

  statistics: async () => {
    const response = await djangoApiClient.get('/quality/issues/statistics/');
    return response.data;
  },
};

// -----
// 설비 타입
// -----
export interface Equipment {
  id: number;
  code: string;
  name: string;
  type: string;
  manufacturer: string;
  model: string;
  serial_number: string;
  location: string;
  installation_date: string;
  status: 'OPERATIONAL' | 'MAINTENANCE' | 'DAMAGED' | 'RETIRED';
  status_display?: string;
  department: string;
  cost: number;
  health_score: number;
  predicted_failure_days?: number;
}

export interface PreventiveMaintenance {
  id: number;
  task_number: string;
  task_name: string;
  description: string;
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'QUARTERLY' | 'YEARLY';
  frequency_display?: string;
  scheduled_date: string;
  status: 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'COMPLETED' | 'OVERDUE';
  status_display?: string;
  equipment: number;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  priority_display?: string;
  estimated_duration: number;
  assigned_to?: number;
  assigned_to_name?: string;
  next_due: string;
  completion_notes?: string;
}

// 설비 API
export const equipmentApi = {
  list: async (params?: any) => {
    const response = await djangoApiClient.get<{results: Equipment[]; count: number}>('/equipment/equipment/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await djangoApiClient.get<Equipment>(`/equipment/equipment/${id}/`);
    return response.data;
  },

  health: async (id: number) => {
    const response = await djangoApiClient.get(`/equipment/equipment/${id}/health/`);
    return response.data;
  },

  statistics: async () => {
    const response = await djangoApiClient.get('/equipment/equipment/statistics/');
    return response.data;
  },
};

// 예방 보전 API
export const preventiveMaintenanceApi = {
  list: async (params?: any) => {
    const response = await djangoApiClient.get<{results: PreventiveMaintenance[]; count: number}>('/equipment/preventive-maintenance/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await djangoApiClient.get<PreventiveMaintenance>(`/equipment/preventive-maintenance/${id}/`);
    return response.data;
  },

  complete: async (id: number, completionNotes: string) => {
    const response = await djangoApiClient.post<PreventiveMaintenance>(
      `/equipment/preventive-maintenance/${id}/complete/`,
      { completion_notes: completionNotes }
    );
    return response.data;
  },

  overdue: async () => {
    const response = await djangoApiClient.get<PreventiveMaintenance[]>('/equipment/preventive-maintenance/overdue/');
    return response.data;
  },
};

// -----
// 치공구 타입
// -----
export interface Tool {
  id: number;
  code: string;
  name: string;
  type: string;
  manufacturer: string;
  model: string;
  serial_number: string;
  location: string;
  purchase_date: string;
  status: 'AVAILABLE' | 'IN_USE' | 'MAINTENANCE' | 'DAMAGED' | 'RETIRED';
  status_display?: string;
  department: string;
  cost: number;
  expected_life_days: number;
  predicted_remaining_days?: number;
  usage_count: number;
  usage_percentage?: number;
  replacement_urgency?: 'NORMAL' | 'WARNING' | 'URGENT' | 'CRITICAL';
  optimal_replacement_date?: string;
}

// 치공구 API
export const toolsApi = {
  list: async (params?: any) => {
    const response = await djangoApiClient.get<{results: Tool[]; count: number}>('/tools/tools/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await djangoApiClient.get<Tool>(`/tools/tools/${id}/`);
    return response.data;
  },

  prediction: async (id: number) => {
    const response = await djangoApiClient.get(`/tools/tools/${id}/prediction/`);
    return response.data;
  },

  statistics: async () => {
    const response = await djangoApiClient.get('/tools/tools/statistics/');
    return response.data;
  },
};

// -----
// 작업지시 타입
// -----
export interface WorkOrder {
  id: number;
  order_number: string;
  product_code: string;
  product_name: string;
  quantity: number;
  status: 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'ON_HOLD';
  status_display?: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  priority_display?: string;
  start_date: string;
  target_end_date: string;
  actual_end_date?: string;
  equipment?: number;
  equipment_code?: string;
  equipment_name?: string;
  equipment_health_score?: number;
  assigned_to?: number;
  assigned_to_name?: string;
  progress_percentage: number;
  completed_quantity: number;
  predicted_completion_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  risk_reasons: string[];
  estimated_cost?: number;
  actual_cost?: number;
  notes?: string;
}

// 작업지시 API
export const workOrdersApi = {
  list: async (params?: any) => {
    const response = await djangoApiClient.get<{results: WorkOrder[]; count: number}>('/work-orders/work-orders/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await djangoApiClient.get<WorkOrder>(`/work-orders/work-orders/${id}/`);
    return response.data;
  },

  create: async (data: Partial<WorkOrder>) => {
    const response = await djangoApiClient.post<WorkOrder>('/work-orders/work-orders/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<WorkOrder>) => {
    const response = await djangoApiClient.patch<WorkOrder>(`/work-orders/work-orders/${id}/`, data);
    return response.data;
  },

  analyzeRisk: async (id: number) => {
    const response = await djangoApiClient.get(`/work-orders/work-orders/${id}/analyze_risk/`);
    return response.data;
  },

  progressLogs: async (id: number) => {
    const response = await djangoApiClient.get(`/work-orders/work-orders/${id}/progress_logs/`);
    return response.data;
  },

  addProgress: async (id: number, data: any) => {
    const response = await djangoApiClient.post(`/work-orders/work-orders/${id}/add_progress/`, data);
    return response.data;
  },

  statistics: async () => {
    const response = await djangoApiClient.get('/work-orders/work-orders/statistics/');
    return response.data;
  },
};

// -----
// ERP 연계 타입
// -----
export interface ERPIntegration {
  id: number;
  name: string;
  system_type: 'ERP' | 'MES' | 'PLM' | 'WMS' | 'QMS';
  system_type_display?: string;
  description?: string;
  endpoint_url: string;
  auth_method: 'API_KEY' | 'OAUTH' | 'BASIC_AUTH';
  sync_frequency_minutes: number;
  auto_sync: boolean;
  last_sync?: string;
  next_sync?: string;
  status: 'CONNECTED' | 'DISCONNECTED' | 'ERROR' | 'TESTING';
  status_display?: string;
  is_active: boolean;
}

export interface ManualQualityInput {
  id: number;
  record_number: string;
  inspection_type: 'INCOMING' | 'PROCESS' | 'FINAL' | 'OUTGOING';
  inspection_type_display?: string;
  inspection_date: string;
  product_code: string;
  product_name: string;
  batch_number?: string;
  lot_number?: string;
  sample_size: number;
  defect_count: number;
  defect_rate: number;
  department: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  status_display?: string;
  notes?: string;
}

// ERP 연계 API
export const integrationApi = {
  list: async () => {
    const response = await djangoApiClient.get<ERPIntegration[]>('/integration/erp-integrations/');
    return response.data;
  },

  get: async (id: number) => {
    const response = await djangoApiClient.get<ERPIntegration>(`/integration/erp-integrations/${id}/`);
    return response.data;
  },

  testConnection: async (id: number) => {
    const response = await djangoApiClient.post(`/integration/erp-integrations/${id}/test_connection/`);
    return response.data;
  },

  sync: async (id: number) => {
    const response = await djangoApiClient.post(`/integration/erp-integrations/${id}/sync/`);
    return response.data;
  },

  syncHistory: async (id: number) => {
    const response = await djangoApiClient.get(`/integration/erp-integrations/${id}/sync_history/`);
    return response.data;
  },
};

// 자체 입력 API
export const manualInputApi = {
  list: async (params?: any) => {
    const response = await djangoApiClient.get<{results: ManualQualityInput[]; count: number}>('/integration/manual-inputs/', { params });
    return response.data;
  },

  get: async (id: number) => {
    const response = await djangoApiClient.get<ManualQualityInput>(`/integration/manual-inputs/${id}/`);
    return response.data;
  },

  create: async (data: Partial<ManualQualityInput>) => {
    const response = await djangoApiClient.post<ManualQualityInput>('/integration/manual-inputs/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<ManualQualityInput>) => {
    const response = await djangoApiClient.patch<ManualQualityInput>(`/integration/manual-inputs/${id}/`, data);
    return response.data;
  },

  approve: async (id: number) => {
    const response = await djangoApiClient.post<ManualQualityInput>(`/integration/manual-inputs/${id}/approve/`);
    return response.data;
  },

  reject: async (id: number, notes?: string) => {
    const response = await djangoApiClient.post<ManualQualityInput>(`/integration/manual-inputs/${id}/reject/`, { notes });
    return response.data;
  },
};

// Django API 통합 객체
export const djangoApi = {
  qualityIssues: qualityIssuesApi,
  equipment: equipmentApi,
  preventiveMaintenance: preventiveMaintenanceApi,
  tools: toolsApi,
  workOrders: workOrdersApi,
  integration: integrationApi,
  manualInput: manualInputApi,
};

// 헬스체크
export const healthCheck = async () => {
  const response = await djangoApiClient.get('/health/');
  return response.data;
};

export { djangoApiClient };

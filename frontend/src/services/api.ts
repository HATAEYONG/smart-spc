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
  baseURL: '/api/spc',
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

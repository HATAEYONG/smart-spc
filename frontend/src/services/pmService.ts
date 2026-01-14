/**
 * Predictive Maintenance API Service
 * 설비 예지 보전 API 서비스
 */

import axios, { AxiosInstance } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1/pm',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 타입 정의
export interface Equipment {
  id: number;
  code: string;
  name: string;
  category: string;
  category_display: string;
  status: string;
  status_display: string;
  location: string;
  manufacturer: string;
  model_number: string;
  installation_date: string;
  health_score: number;
  failure_probability: number;
  availability_current: number;
  next_maintenance_date: string | null;
  maintenance_overdue: boolean;
}

export interface SensorData {
  id: number;
  equipment: number;
  equipment_code: string;
  equipment_name: string;
  sensor_type: string;
  sensor_type_display: string;
  value: number;
  unit: string;
  is_normal: boolean;
  anomaly_score: number;
  timestamp: string;
}

export interface MaintenanceRecord {
  id: number;
  equipment: number;
  equipment_code: string;
  equipment_name: string;
  record_type: string;
  record_type_display: string;
  status: string;
  title: string;
  scheduled_date: string;
  completed_at: string | null;
  total_cost: number;
}

export interface FailurePrediction {
  id: number;
  equipment: number;
  equipment_code: string;
  equipment_name: string;
  severity: string;
  severity_display: string;
  failure_probability: number;
  predicted_failure_date: string;
  potential_causes: string;
  recommended_actions: string;
  is_acknowledged: boolean;
}

export interface MaintenancePlan {
  id: number;
  equipment: number;
  equipment_code: string;
  equipment_name: string;
  name: string;
  frequency: string;
  frequency_display: string;
  status: string;
  next_due_date: string;
  days_until_due: number;
  assigned_to_name: string;
  estimated_cost: number;
}

export interface PMDashboardData {
  total_equipment: number;
  operational: number;
  maintenance: number;
  breakdown: number;
  high_risk: number;
  avg_availability: number;
  recent_sensor_data: SensorData[];
  critical_predictions: FailurePrediction[];
}

// API 메서드
export const pmService = {
  // 대시보드
  getDashboard: async (): Promise<PMDashboardData> => {
    const response = await apiClient.get<PMDashboardData>('/equipment/dashboard/');
    return response.data;
  },

  // 설비
  getEquipment: async (params?: any): Promise<{ results: Equipment[]; count: number }> => {
    const response = await apiClient.get('/equipment/', { params });
    return response.data;
  },

  getEquipmentDetail: async (id: number): Promise<Equipment> => {
    const response = await apiClient.get<Equipment>(`/equipment/${id}/`);
    return response.data;
  },

  // 센서 데이터
  getSensorData: async (equipmentId: number, hours: number = 24, sensorType?: string): Promise<SensorData[]> => {
    const params: any = { hours };
    if (sensorType) params.sensor_type = sensorType;
    const response = await apiClient.get<SensorData[]>(`/equipment/${equipmentId}/sensor_data/`, { params });
    return response.data;
  },

  getLatestSensorData: async (equipmentId?: number, sensorType?: string): Promise<SensorData[]> => {
    const params: any = {};
    if (equipmentId) params.equipment = equipmentId;
    if (sensorType) params.sensor_type = sensorType;
    const response = await apiClient.get<SensorData[]>('/sensor-data/latest/', { params });
    return response.data;
  },

  // 점검 이력
  getMaintenanceRecords: async (equipmentId?: number): Promise<MaintenanceRecord[]> => {
    const params: any = {};
    if (equipmentId) params.equipment = equipmentId;
    const response = await apiClient.get<MaintenanceRecord[]>('/maintenance-records/', { params });
    return response.data;
  },

  // 고장 예측
  getFailurePredictions: async (equipmentId?: number): Promise<FailurePrediction[]> => {
    const params: any = {};
    if (equipmentId) params.equipment = equipmentId;
    const response = await apiClient.get<FailurePrediction[]>('/failure-predictions/', { params });
    return response.data;
  },

  getCriticalPredictions: async (): Promise<FailurePrediction[]> => {
    const response = await apiClient.get<FailurePrediction[]>('/failure-predictions/critical/');
    return response.data;
  },

  acknowledgePrediction: async (id: number): Promise<FailurePrediction> => {
    const response = await apiClient.post<FailurePrediction>(`/failure-predictions/${id}/acknowledge/`);
    return response.data;
  },

  // 예방 보전 계획
  getMaintenancePlans: async (): Promise<MaintenancePlan[]> => {
    const response = await apiClient.get<MaintenancePlan[]>('/maintenance-plans/');
    return response.data;
  },
};

export default pmService;

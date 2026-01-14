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
    try {
      const response = await apiClient.get<PMDashboardData>('/equipment/dashboard/');
      return response.data;
    } catch (error: any) {
      console.error('Dashboard API error:', error);
      // 기본값 반환
      return {
        total_equipment: 0,
        operational: 0,
        maintenance: 0,
        breakdown: 0,
        high_risk: 0,
        avg_availability: 0,
        recent_sensor_data: [],
        critical_predictions: [],
      };
    }
  },

  // 설비
  getEquipment: async (params?: any): Promise<Equipment[]> => {
    try {
      const response = await apiClient.get<{ results: Equipment[]; count: number }>('/equipment/', { params });
      return response.data?.results || response.data || [];
    } catch (error: any) {
      console.error('Equipment API error:', error);
      return [];
    }
  },

  getEquipmentDetail: async (id: number): Promise<Equipment | null> => {
    try {
      const response = await apiClient.get<Equipment>(`/equipment/${id}/`);
      return response.data;
    } catch (error: any) {
      console.error('Equipment detail API error:', error);
      return null;
    }
  },

  // 센서 데이터
  getSensorData: async (equipmentId: number, hours: number = 24, sensorType?: string): Promise<SensorData[]> => {
    try {
      const params: any = { hours };
      if (sensorType) params.sensor_type = sensorType;
      const response = await apiClient.get<SensorData[]>(`/equipment/${equipmentId}/sensor_data/`, { params });
      return response.data || [];
    } catch (error: any) {
      console.error('Sensor data API error:', error);
      return [];
    }
  },

  getLatestSensorData: async (equipmentId?: number, sensorType?: string): Promise<SensorData[]> => {
    try {
      const params: any = {};
      if (equipmentId) params.equipment = equipmentId;
      if (sensorType) params.sensor_type = sensorType;
      const response = await apiClient.get<SensorData[]>('/sensor-data/latest/', { params });
      return response.data || [];
    } catch (error: any) {
      console.error('Latest sensor data API error:', error);
      return [];
    }
  },

  // 점검 이력
  getMaintenanceRecords: async (equipmentId?: number): Promise<MaintenanceRecord[]> => {
    try {
      const params: any = {};
      if (equipmentId) params.equipment = equipmentId;
      const response = await apiClient.get<MaintenanceRecord[]>('/maintenance-records/', { params });
      return response.data?.results || response.data || [];
    } catch (error: any) {
      console.error('Maintenance records API error:', error);
      return [];
    }
  },

  // 고장 예측
  getFailurePredictions: async (equipmentId?: number): Promise<FailurePrediction[]> => {
    try {
      const params: any = {};
      if (equipmentId) params.equipment = equipmentId;
      const response = await apiClient.get<FailurePrediction[]>('/failure-predictions/', { params });
      return response.data?.results || response.data || [];
    } catch (error: any) {
      console.error('Failure predictions API error:', error);
      return [];
    }
  },

  getCriticalPredictions: async (): Promise<FailurePrediction[]> => {
    try {
      const response = await apiClient.get<FailurePrediction[]>('/failure-predictions/critical/');
      return response.data || [];
    } catch (error: any) {
      console.error('Critical predictions API error:', error);
      return [];
    }
  },

  acknowledgePrediction: async (id: number): Promise<FailurePrediction | null> => {
    try {
      const response = await apiClient.post<FailurePrediction>(`/failure-predictions/${id}/acknowledge/`);
      return response.data;
    } catch (error: any) {
      console.error('Acknowledge prediction API error:', error);
      return null;
    }
  },

  // 예방 보전 계획
  getMaintenancePlans: async (): Promise<MaintenancePlan[]> => {
    try {
      const response = await apiClient.get<MaintenancePlan[]>('/maintenance-plans/');
      return response.data?.results || response.data || [];
    } catch (error: any) {
      console.error('Maintenance plans API error:', error);
      return [];
    }
  },

  getCalendarEvents: async (startDate?: string, endDate?: string, equipmentId?: number): Promise<any[]> => {
    try {
      const params: any = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (equipmentId) params.equipment = equipmentId;

      const response = await apiClient.get<any[]>('/maintenance-plans/calendar/', { params });
      return response.data || [];
    } catch (error: any) {
      console.error('Calendar events API error:', error);
      return [];
    }
  },

  getUpcomingMaintenance: async (): Promise<MaintenancePlan[]> => {
    try {
      const response = await apiClient.get<MaintenancePlan[]>('/maintenance-plans/upcoming/');
      return response.data?.results || response.data || [];
    } catch (error: any) {
      console.error('Upcoming maintenance API error:', error);
      return [];
    }
  },

  getOverdueMaintenance: async (): Promise<MaintenancePlan[]> => {
    try {
      const response = await apiClient.get<MaintenancePlan[]>('/maintenance-plans/overdue/');
      return response.data?.results || response.data || [];
    } catch (error: any) {
      console.error('Overdue maintenance API error:', error);
      return [];
    }
  },
};

export default pmService;

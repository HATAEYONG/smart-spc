/**
 * Dashboard API Service
 * DASH-01: 대시보드 관련 API
 */

import { api, ApiResponse } from './apiV1';
import { DashboardSummaryDTO } from '../types/dashboard';

export const dashboardService = {
  /**
   * 대시보드 요약 조회
   * GET /dashboard/summary?period=2026-01
   */
  async getSummary(period: string): Promise<ApiResponse<DashboardSummaryDTO>> {
    return api.get<DashboardSummaryDTO>('/dashboard/summary', { period });
  },
};

/**
 * SPC API Service
 * SPC-01: 통계적 공정관리 API
 */

import { api, ApiResponse, PaginationParams } from './apiV1';
import {
  SpcChartDefDTO,
  SpcPointDTO,
  SpcEventDTO,
  SamplingRuleDTO,
  SpcChartCreateRequest,
  SpcRecalcResponse,
  SpcEventCreateRequest,
} from '../types/spc';

export const spcService = {
  /**
   * 샘플링 룰 조회
   * GET /sampling/rules?standard=ISO2859&aql=1.0&lot_size=1200
   */
  async getSamplingRule(
    standard: string,
    aql: number,
    lotSize: number
  ): Promise<ApiResponse<SamplingRuleDTO>> {
    return api.get<SamplingRuleDTO>('/sampling/rules', {
      standard,
      aql,
      lot_size: lotSize,
    });
  },

  /**
   * SPC 차트 정의 생성
   * POST /spc/charts
   */
  async createChart(
    data: SpcChartCreateRequest
  ): Promise<ApiResponse<SpcChartDefDTO>> {
    return api.post<SpcChartDefDTO>('/spc/charts', data);
  },

  /**
   * SPC 차트 재계산
   * POST /spc/charts/{chart_def_id}/recalc?from=2026-01-01&to=2026-01-31
   */
  async recalcChart(
    chartDefId: string,
    from: string,
    to: string
  ): Promise<ApiResponse<SpcRecalcResponse>> {
    return api.post<SpcRecalcResponse>(
      `/spc/charts/${chartDefId}/recalc`,
      {},
      { from, to }
    );
  },

  /**
   * SPC 데이터 포인트 조회
   * GET /spc/charts/{chart_def_id}/points?from=...&to=...
   */
  async getPoints(
    chartDefId: string,
    from?: string,
    to?: string,
    params?: PaginationParams
  ): Promise<ApiResponse<{ chart_type: string; points: SpcPointDTO[] }>> {
    return api.get<{ chart_type: string; points: SpcPointDTO[] }>(
      `/spc/charts/${chartDefId}/points`,
      { from, to, ...params }
    );
  },

  /**
   * SPC 이벤트 생성
   * POST /spc/events
   */
  async createEvent(
    data: SpcEventCreateRequest
  ): Promise<ApiResponse<SpcEventDTO>> {
    return api.post<SpcEventDTO>('/spc/events', data);
  },
};

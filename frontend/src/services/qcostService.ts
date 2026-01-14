/**
 * Q-COST API Service
 * QCOST-01/02: 품질비용 관리 API
 */

import { api, ApiResponse, PaginatedResponse, PaginationParams } from './apiV1';
import {
  QCostCategoryDTO,
  QCostItemDTO,
  QCostEntryDTO,
  AIQCostClassifyRequest,
  AIQCostClassifyResponse,
  COPQReportRequest,
  COPQReportResponse,
} from '../types/qcost';

export const qcostService = {
  /**
   * 품질비용 카테고리 목록 조회
   * GET /qcost/categories
   */
  async getCategories(): Promise<ApiResponse<QCostCategoryDTO[]>> {
    return api.get<QCostCategoryDTO[]>('/qcost/categories');
  },

  /**
   * 품질비용 카테고리 생성
   * POST /qcost/categories
   */
  async createCategory(
    data: Omit<QCostCategoryDTO, 'qcat_id' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<QCostCategoryDTO>> {
    return api.post<QCostCategoryDTO>('/qcost/categories', data);
  },

  /**
   * 품질비용 항목 목록 조회
   * GET /qcost/items
   */
  async getItems(
    params?: PaginationParams
  ): Promise<ApiResponse<PaginatedResponse<QCostItemDTO>>> {
    return api.get<PaginatedResponse<QCostItemDTO>>('/qcost/items', params);
  },

  /**
   * 품질비용 항목 생성
   * POST /qcost/items
   */
  async createItem(
    data: Omit<QCostItemDTO, 'qitem_id' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<QCostItemDTO>> {
    return api.post<QCostItemDTO>('/qcost/items', data);
  },

  /**
   * 품질비용 입출내역 조회
   * GET /qcost/entries?from_date=2026-01-01&to_date=2026-01-31
   */
  async getEntries(
    from: string,
    to: string,
    params?: PaginationParams
  ): Promise<ApiResponse<PaginatedResponse<QCostEntryDTO>>> {
    return api.get<PaginatedResponse<QCostEntryDTO>>('/qcost/entries', {
      from_date: from,
      to_date: to,
      ...params,
    });
  },

  /**
   * 품질비용 입출내역 생성
   * POST /qcost/entries
   */
  async createEntry(
    data: Omit<QCostEntryDTO, 'entry_id' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<QCostEntryDTO>> {
    return api.post<QCostEntryDTO>('/qcost/entries', data);
  },

  /**
   * AI 품질비용 분류
   * POST /ai/qcost-classify
   */
  async classifyQCost(
    request: AIQCostClassifyRequest
  ): Promise<ApiResponse<AIQCostClassifyResponse>> {
    return api.post<AIQCostClassifyResponse>('/ai/qcost-classify', request);
  },

  /**
   * COPQ 리포트 생성
   * POST /reports/copq
   */
  async generateCOPQReport(
    request: COPQReportRequest
  ): Promise<ApiResponse<COPQReportResponse>> {
    return api.post<COPQReportResponse>('/reports/copq', request);
  },
};

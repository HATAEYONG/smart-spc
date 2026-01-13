/**
 * QA/CAPA API Service
 * QA-01: 품질 진단/GAP/CAPA API
 */

import { api, ApiResponse } from './apiV1';
import {
  QaProcessDTO,
  QaRequirementDTO,
  QaAssessmentDTO,
  QaFindingDTO,
  CapaDTO,
  AIRootCauseCAPARequest,
  AIRootCauseCAPAResponse,
} from '../types/qa';

export const qaService = {
  /**
   * QA 프로세스 생성
   * POST /qa/process
   */
  async createProcess(
    data: Omit<QaProcessDTO, 'qa_proc_id' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<QaProcessDTO>> {
    return api.post<QaProcessDTO>('/qa/process', data);
  },

  /**
   * QA 요구사항 대량 생성
   * POST /qa/process/{qa_proc_id}/requirements/bulk
   */
  async addBulkRequirements(
    qaProcId: string,
    requirements: Omit<QaRequirementDTO, 'req_id' | 'qa_proc_id' | 'created_at' | 'updated_at'>[]
  ): Promise<ApiResponse<QaRequirementDTO[]>> {
    return api.post<QaRequirementDTO[]>(
      `/qa/process/${qaProcId}/requirements/bulk`,
      { requirements }
    );
  },

  /**
   * QA 평가 생성
   * POST /qa/assessments
   */
  async createAssessment(
    data: Omit<QaAssessmentDTO, 'assess_id' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<QaAssessmentDTO>> {
    return api.post<QaAssessmentDTO>('/qa/assessments', data);
  },

  /**
   * QA GAP Finding 생성
   * POST /qa/assessments/{assess_id}/findings
   */
  async createFinding(
    assessId: string,
    data: Omit<QaFindingDTO, 'finding_id' | 'assess_id' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<QaFindingDTO>> {
    return api.post<QaFindingDTO>(`/qa/assessments/${assessId}/findings`, data);
  },

  /**
   * CAPA 생성
   * POST /capa
   */
  async createCAPA(
    data: Omit<CapaDTO, 'capa_id' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<CapaDTO>> {
    return api.post<CapaDTO>('/capa', data);
  },

  /**
   * AI 근본원인/CAPA 분석
   * POST /ai/rootcause-capa
   */
  async analyzeRootCauseCAPA(
    request: AIRootCauseCAPARequest
  ): Promise<ApiResponse<AIRootCauseCAPAResponse>> {
    return api.post<AIRootCauseCAPAResponse>('/ai/rootcause-capa', request);
  },
};

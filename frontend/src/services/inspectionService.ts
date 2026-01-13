/**
 * Inspection API Service
 * INSP-01/02: 검사 프로세스 및 실행 API
 */

import { api, ApiResponse, PaginatedResponse, PaginationParams } from './apiV1';
import {
  ProcessFlowDTO,
  ProcessStepDTO,
  AIProcessDesignRequest,
  AIProcessDesignResponse,
  AICriteriaChecklistRequest,
  AICriteriaChecklistResponse,
  InspectionRunDTO,
  InspectionResultDTO,
  BulkResultRequest,
  BulkResultResponse,
  InspectionJudgeResponse,
} from '../types/inspection';

export const inspectionService = {
  /**
   * 공정 흐름 목록 조회
   * GET /process/flows
   */
  async getFlows(): Promise<ApiResponse<ProcessFlowDTO[]>> {
    return api.get<ProcessFlowDTO[]>('/process/flows');
  },

  /**
   * 공정 흐름 생성
   * POST /process/flows
   */
  async createFlow(
    data: Omit<ProcessFlowDTO, 'flow_id' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<ProcessFlowDTO>> {
    return api.post<ProcessFlowDTO>('/process/flows', data);
  },

  /**
   * 공정 단계 목록 조회
   * GET /process/flows/{flow_id}/steps
   */
  async getSteps(flowId: string): Promise<ApiResponse<ProcessStepDTO[]>> {
    return api.get<ProcessStepDTO[]>(`/process/flows/${flowId}/steps`);
  },

  /**
   * 공정 단계 생성
   * POST /process/flows/{flow_id}/steps
   */
  async createStep(
    flowId: string,
    data: Omit<ProcessStepDTO, 'step_id' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<ProcessStepDTO>> {
    return api.post<ProcessStepDTO>(`/process/flows/${flowId}/steps`, data);
  },

  /**
   * AI 검사 프로세스 설계
   * POST /ai/process-design
   */
  async designProcess(
    request: AIProcessDesignRequest
  ): Promise<ApiResponse<AIProcessDesignResponse>> {
    return api.post<AIProcessDesignResponse>('/ai/process-design', request);
  },

  /**
   * AI 기준표/체크리스트 생성
   * POST /ai/criteria-checklist
   */
  async generateCriteriaChecklist(
    request: AICriteriaChecklistRequest
  ): Promise<ApiResponse<AICriteriaChecklistResponse>> {
    return api.post<AICriteriaChecklistResponse>('/ai/criteria-checklist', request);
  },

  /**
   * 검사 실행 생성
   * POST /inspection/runs
   */
  async createRun(
    data: Omit<InspectionRunDTO, 'run_id' | 'run_dt' | 'created_at' | 'updated_at'>
  ): Promise<ApiResponse<InspectionRunDTO>> {
    return api.post<InspectionRunDTO>('/inspection/runs', data);
  },

  /**
   * 검사 결과 대량 입력
   * POST /inspection/runs/{run_id}/results/bulk
   */
  async addBulkResults(
    runId: string,
    data: BulkResultRequest
  ): Promise<ApiResponse<BulkResultResponse>> {
    return api.post<BulkResultResponse>(`/inspection/runs/${runId}/results/bulk`, data);
  },

  /**
   * 검사 판정 실행
   * POST /inspection/runs/{run_id}/judge
   */
  async judgeRun(runId: string): Promise<ApiResponse<InspectionJudgeResponse>> {
    return api.post<InspectionJudgeResponse>(`/inspection/runs/${runId}/judge`);
  },
};

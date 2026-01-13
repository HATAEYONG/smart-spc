/**
 * API v1 Service Layer
 * REST API 클라이언트 - 타입 안전한 API 호출
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';

// 표준 응답 래퍼
export interface ApiResponse<T> {
  ok: boolean;
  data: T;
  error: string | null;
}

// 페이징 파라미터
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

// 페이징 응답
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 요청 인터셉터 - 토큰 추가
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // 응답 인터셉터 - 에러 처리
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // 인증 실패 처리
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
    url: string,
    data?: any,
    params?: any
  ): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.client.request({
        method,
        url,
        data,
        params,
      });
      return response.data;
    } catch (error: any) {
      return {
        ok: false,
        data: null as any,
        error: error.response?.data?.error || error.message || 'API 요청 실패',
      };
    }
  }

  async get<T>(url: string, params?: any): Promise<ApiResponse<T>> {
    return this.request<T>('GET', url, undefined, params);
  }

  async post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>('POST', url, data);
  }

  async put<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', url, data);
  }

  async patch<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', url, data);
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', url);
  }
}

// 싱글톤 인스턴스 내보내기
export const api = new APIClient();

// 기본 URL 내보내기 (테스트용)
export const BASE_URL = '/api/v1';

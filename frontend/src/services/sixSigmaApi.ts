/**
 * Six Sigma DMAIC API Service
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface DMAICProject {
  id: number;
  project_code: string;
  project_name: string;
  description: string;
  phase: 'DEFINE' | 'MEASURE' | 'ANALYZE' | 'IMPROVE' | 'CONTROL' | 'CLOSED';
  status: string;
  priority: string;
  champion_name: string;
  progress_percentage: number;
  start_date: string;
  target_end_date: string;
  days_remaining: number;
}

export interface DashboardStats {
  total_projects: number;
  by_phase: Record<string, number>;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  recent_projects: DMAICProject[];
}

// DMAIC Projects
export const getDMAICProjects = async (params?: {
  phase?: string;
  status?: string;
  priority?: string;
}): Promise<DMAICProject[]> => {
  const response = await axios.get(`${API_BASE_URL}/six-sigma/projects/`, { params });
  return response.data;
};

export const getDMAICProject = async (id: number): Promise<DMAICProject> => {
  const response = await axios.get(`${API_BASE_URL}/six-sigma/projects/${id}/`);
  return response.data;
};

export const createDMAICProject = async (data: any): Promise<DMAICProject> => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/projects/`, data);
  return response.data;
};

export const updateDMAICProject = async (id: number, data: any): Promise<DMAICProject> => {
  const response = await axios.put(`${API_BASE_URL}/six-sigma/projects/${id}/`, data);
  return response.data;
};

export const advanceProjectPhase = async (id: number): Promise<any> => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/projects/${id}/advance_phase/`);
  return response.data;
};

// Dashboard
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await axios.get(`${API_BASE_URL}/six-sigma/projects/dashboard/`);
  return response.data;
};

// Statistical Tools
export const descriptiveStatistics = async (data: number[]) => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/statistical-tools/descriptive_statistics/`, {
    data,
    variable_name: 'Variable',
  });
  return response.data;
};

export const histogramAnalysis = async (data: number[], bins = 10) => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/statistical-tools/histogram/`, {
    data,
    bins,
    variable_name: 'Variable',
  });
  return response.data;
};

export const paretoAnalysis = async (categories: string[], values: number[]) => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/statistical-tools/pareto/`, {
    categories,
    values,
    chart_title: 'Pareto Chart',
  });
  return response.data;
};

export const boxPlotAnalysis = async (groups: Record<string, number[]>) => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/statistical-tools/box_plot/`, {
    groups,
  });
  return response.data;
};

export const correlationAnalysis = async (x_data: number[], y_data: number[]) => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/statistical-tools/correlation/`, {
    x_data,
    y_data,
    x_label: 'X',
    y_label: 'Y',
  });
  return response.data;
};

export const tTest = async (
  sample1: number[],
  sample2?: number[],
  mu0 = 0,
  test_type = 'one_sample',
  alpha = 0.05
) => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/statistical-tools/t_test/`, {
    sample1,
    sample2,
    mu0,
    test_type,
    alpha,
  });
  return response.data;
};

export const anovaAnalysis = async (groups: Record<string, number[]>, alpha = 0.05) => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/statistical-tools/anova/`, {
    groups,
    alpha,
  });
  return response.data;
};

export const capabilityAnalysis = async (
  data: number[],
  lsl: number,
  usl: number,
  target?: number
) => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/statistical-tools/capability_analysis/`, {
    data,
    lsl,
    usl,
    target,
  });
  return response.data;
};

export const gageRRAnalysis = async (measurements: any[]) => {
  const response = await axios.post(`${API_BASE_URL}/six-sigma/statistical-tools/gage_rr/`, {
    measurements,
  });
  return response.data;
};

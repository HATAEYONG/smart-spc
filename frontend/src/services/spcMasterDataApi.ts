/**
 * SPC Master Data API Service
 * 품질 기본정보 API 서비스
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// ============================================================================
// Types
// ============================================================================

export interface QualityItem {
  quality_item_id: number;
  itm_id: string;
  itm_nm: string;
  itm_type: string;
  itm_type_display?: string;
  itm_family: string;
  quality_grade: string;
  quality_grade_display?: string;
  inspection_type: string;
  inspection_type_display?: string;
  sampling_plan: string;
  sample_size: number;
  sampling_frequency: string;
  supplier_code: string;
  supplier_nm: string;
  quality_manager: string;
  notes: string;
  active_yn: string;
  erp_sync_ts: string;
  total_characteristics?: number;
}

export interface QualityProcess {
  process_id: number;
  process_cd: string;
  process_nm: string;
  process_type: string;
  process_type_display?: string;
  workcenter_cd: string;
  workcenter_nm: string;
  line_cd: string;
  process_seq: number;
  total_characteristics: number;
  process_manager: string;
  notes: string;
  active_yn: string;
  mes_sync_ts: string;
}

export interface QualityCharacteristic {
  characteristic_id: number;
  characteristic_cd: string;
  characteristic_nm: string;
  item?: number;
  itm_id?: string;
  itm_nm?: string;
  process?: number;
  process_cd?: string;
  process_nm?: string;
  characteristic_type: string;
  characteristic_type_display?: string;
  data_type: string;
  data_type_display?: string;
  unit: string;
  lsl: number;
  target: number;
  usl: number;
  cpk_target: number;
  cpk_minimum: number;
  control_chart_type: string;
  control_chart_type_display?: string;
  subgroup_size: number;
  measurement_method: string;
  measurement_location: string;
  quality_manager: string;
  notes: string;
  active_yn: string;
}

export interface MeasurementInstrument {
  instrument_id: number;
  instrument_cd: string;
  instrument_nm: string;
  instrument_type: string;
  instrument_type_display?: string;
  manufacturer: string;
  model_no: string;
  serial_no: string;
  measurement_range_min: number;
  measurement_range_max: number;
  resolution: number;
  unit: string;
  accuracy: number;
  calibration_cycle: number;
  last_calibration_date: string;
  next_calibration_date: string;
  calibration_institution: string;
  status: string;
  status_display?: string;
  location: string;
  responsible_person: string;
  gage_rr_required: boolean;
  gage_rr_last_date: string;
  gage_rr_result: string;
  notes: string;
  active_yn: string;
  is_calibration_due?: boolean;
}

export interface MeasurementSystem {
  system_id: number;
  system_cd: string;
  system_nm: string;
  instrument_count?: number;
  components?: MeasurementSystemComponent[];
  measurement_process: string;
  temperature_min: number;
  temperature_max: number;
  humidity_min: number;
  humidity_max: number;
  system_manager: string;
  location: string;
  msa_method: string;
  msa_method_display?: string;
  notes: string;
  active_yn: string;
}

export interface MeasurementSystemComponent {
  component_id: number;
  system: number;
  instrument: number;
  instrument_cd: string;
  instrument_nm: string;
  component_role: string;
  seq: number;
  ev_contribution: number;
}

export interface InspectionStandard {
  standard_id: number;
  standard_cd: string;
  standard_nm: string;
  item?: number;
  itm_id?: string;
  itm_nm?: string;
  characteristic?: number;
  characteristic_cd?: string;
  characteristic_nm?: string;
  standard_type: string;
  standard_type_display?: string;
  inspection_condition: string;
  acceptance_criteria: string;
  rejection_criteria: string;
  sampling_method: string;
  sample_size: number;
  aql: number;
  test_method: string;
  test_equipment: string;
  reference_doc: string;
  revision: string;
  effective_date: string;
  notes: string;
  active_yn: string;
}

export interface QualitySyncLog {
  sync_id: number;
  sync_type: string;
  sync_type_display?: string;
  sync_source: string;
  sync_source_display?: string;
  sync_status: string;
  sync_status_display?: string;
  records_total: number;
  records_success: number;
  records_failed: number;
  error_message: string;
  sync_details: any;
  source_system: string;
  source_file: string;
  sync_start_ts: string;
  sync_end_ts: string;
  duration_seconds?: number;
  sync_ts: string;
}

export interface SyncResult {
  total: number;
  created: number;
  updated: number;
  failed: number;
  errors: Array<{
    [key: string]: string;
  }>;
}

// ============================================================================
// Quality Item Master API
// ============================================================================

export const getQualityItems = async (params?: {
  itm_type?: string;
  itm_family?: string;
  quality_grade?: string;
}): Promise<QualityItem[]> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/items/`, { params });
  // Handle paginated response
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getQualityItem = async (itm_id: string): Promise<QualityItem> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/items/${itm_id}/`);
  return response.data;
};

export const createQualityItem = async (data: Partial<QualityItem>): Promise<QualityItem> => {
  const response = await axios.post(`${API_BASE_URL}/spc/master-data/items/`, data);
  return response.data;
};

export const updateQualityItem = async (itm_id: string, data: Partial<QualityItem>): Promise<QualityItem> => {
  const response = await axios.put(`${API_BASE_URL}/spc/master-data/items/${itm_id}/`, data);
  return response.data;
};

export const deleteQualityItem = async (itm_id: string): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/spc/master-data/items/${itm_id}/`);
};

export const importItemsFromERP = async (items: Partial<QualityItem>[]): Promise<SyncResult> => {
  const response = await axios.post(`${API_BASE_URL}/spc/master-data/items/import_from_erp/`, {
    items
  });
  return response.data;
};

// ============================================================================
// Quality Process Master API
// ============================================================================

export const getQualityProcesses = async (params?: {
  process_type?: string;
  workcenter_cd?: string;
  line_cd?: string;
}): Promise<QualityProcess[]> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/processes/`, { params });
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getQualityProcess = async (process_cd: string): Promise<QualityProcess> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/processes/${process_cd}/`);
  return response.data;
};

export const createQualityProcess = async (data: Partial<QualityProcess>): Promise<QualityProcess> => {
  const response = await axios.post(`${API_BASE_URL}/spc/master-data/processes/`, data);
  return response.data;
};

export const updateQualityProcess = async (process_cd: string, data: Partial<QualityProcess>): Promise<QualityProcess> => {
  const response = await axios.put(`${API_BASE_URL}/spc/master-data/processes/${process_cd}/`, data);
  return response.data;
};

export const deleteQualityProcess = async (process_cd: string): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/spc/master-data/processes/${process_cd}/`);
};

export const importProcessesFromMES = async (processes: Partial<QualityProcess>[]): Promise<SyncResult> => {
  const response = await axios.post(`${API_BASE_URL}/spc/master-data/processes/import_from_mes/`, {
    processes
  });
  return response.data;
};

// ============================================================================
// Quality Characteristic Master API
// ============================================================================

export const getQualityCharacteristics = async (params?: {
  item_id?: string;
  process_id?: string;
  characteristic_type?: string;
}): Promise<QualityCharacteristic[]> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/characteristics/`, { params });
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getQualityCharacteristic = async (characteristic_cd: string): Promise<QualityCharacteristic> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/characteristics/${characteristic_cd}/`);
  return response.data;
};

export const createQualityCharacteristic = async (data: Partial<QualityCharacteristic>): Promise<QualityCharacteristic> => {
  const response = await axios.post(`${API_BASE_URL}/spc/master-data/characteristics/`, data);
  return response.data;
};

export const updateQualityCharacteristic = async (
  characteristic_cd: string,
  data: Partial<QualityCharacteristic>
): Promise<QualityCharacteristic> => {
  const response = await axios.put(
    `${API_BASE_URL}/spc/master-data/characteristics/${characteristic_cd}/`,
    data
  );
  return response.data;
};

export const deleteQualityCharacteristic = async (characteristic_cd: string): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/spc/master-data/characteristics/${characteristic_cd}/`);
};

// ============================================================================
// Measurement Instrument Master API
// ============================================================================

export const getMeasurementInstruments = async (params?: {
  instrument_type?: string;
  status?: string;
}): Promise<MeasurementInstrument[]> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/instruments/`, { params });
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getMeasurementInstrument = async (instrument_cd: string): Promise<MeasurementInstrument> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/instruments/${instrument_cd}/`);
  return response.data;
};

export const createMeasurementInstrument = async (data: Partial<MeasurementInstrument>): Promise<MeasurementInstrument> => {
  const response = await axios.post(`${API_BASE_URL}/spc/master-data/instruments/`, data);
  return response.data;
};

export const updateMeasurementInstrument = async (
  instrument_cd: string,
  data: Partial<MeasurementInstrument>
): Promise<MeasurementInstrument> => {
  const response = await axios.put(`${API_BASE_URL}/spc/master-data/instruments/${instrument_cd}/`, data);
  return response.data;
};

export const deleteMeasurementInstrument = async (instrument_cd: string): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/spc/master-data/instruments/${instrument_cd}/`);
};

export const getCalibrationDueInstruments = async (): Promise<MeasurementInstrument[]> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/instruments/calibration_due/`);
  return response.data;
};

export const getGageRRDueInstruments = async (): Promise<MeasurementInstrument[]> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/instruments/gage_rr_due/`);
  return response.data;
};

// ============================================================================
// Measurement System Master API
// ============================================================================

export const getMeasurementSystems = async (): Promise<MeasurementSystem[]> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/systems/`);
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getMeasurementSystem = async (system_cd: string): Promise<MeasurementSystem> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/systems/${system_cd}/`);
  return response.data;
};

export const createMeasurementSystem = async (data: Partial<MeasurementSystem>): Promise<MeasurementSystem> => {
  const response = await axios.post(`${API_BASE_URL}/spc/master-data/systems/`, data);
  return response.data;
};

export const updateMeasurementSystem = async (
  system_cd: string,
  data: Partial<MeasurementSystem>
): Promise<MeasurementSystem> => {
  const response = await axios.put(`${API_BASE_URL}/spc/master-data/systems/${system_cd}/`, data);
  return response.data;
};

export const deleteMeasurementSystem = async (system_cd: string): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/spc/master-data/systems/${system_cd}/`);
};

export const addInstrumentToSystem = async (
  system_cd: string,
  instrument_cd: string,
  component_role: string,
  seq: number = 1
): Promise<MeasurementSystemComponent> => {
  const response = await axios.post(`${API_BASE_URL}/spc/master-data/systems/${system_cd}/add_instrument/`, {
    instrument_cd,
    component_role,
    seq
  });
  return response.data;
};

export const removeInstrumentFromSystem = async (system_cd: string, instrument_cd: string): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/spc/master-data/systems/${system_cd}/remove_instrument/?instrument_cd=${instrument_cd}`);
};

// ============================================================================
// Inspection Standard Master API
// ============================================================================

export const getInspectionStandards = async (params?: {
  item_id?: string;
  characteristic_id?: string;
  standard_type?: string;
}): Promise<InspectionStandard[]> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/standards/`, { params });
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getInspectionStandard = async (standard_cd: string): Promise<InspectionStandard> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/standards/${standard_cd}/`);
  return response.data;
};

export const createInspectionStandard = async (data: Partial<InspectionStandard>): Promise<InspectionStandard> => {
  const response = await axios.post(`${API_BASE_URL}/spc/master-data/standards/`, data);
  return response.data;
};

export const updateInspectionStandard = async (
  standard_cd: string,
  data: Partial<InspectionStandard>
): Promise<InspectionStandard> => {
  const response = await axios.put(`${API_BASE_URL}/spc/master-data/standards/${standard_cd}/`, data);
  return response.data;
};

export const deleteInspectionStandard = async (standard_cd: string): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/spc/master-data/standards/${standard_cd}/`);
};

// ============================================================================
// Quality Sync Log API
// ============================================================================

export const getQualitySyncLogs = async (params?: {
  sync_type?: string;
  sync_source?: string;
  sync_status?: string;
}): Promise<QualitySyncLog[]> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/sync-logs/`, { params });
  return Array.isArray(response.data) ? response.data : response.data.results || [];
};

export const getSyncStatistics = async (): Promise<{
  total_syncs: number;
  by_type: Record<string, number>;
  by_source: Record<string, number>;
  by_status: Record<string, number>;
  total_records: number;
  total_success: number;
  total_failed: number;
}> => {
  const response = await axios.get(`${API_BASE_URL}/spc/master-data/sync-logs/statistics/`);
  return response.data;
};

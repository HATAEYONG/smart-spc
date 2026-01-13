import React, { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, AlertTriangle, CheckCircle, Search } from 'lucide-react';
import {
  getMeasurementInstruments,
  createMeasurementInstrument,
  updateMeasurementInstrument,
  deleteMeasurementInstrument,
  getCalibrationDueInstruments,
  MeasurementInstrument,
} from '../services/spcMasterDataApi';

const MasterDataInstrumentsPage: React.FC = () => {
  const [instruments, setInstruments] = useState<MeasurementInstrument[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingInstrument, setEditingInstrument] = useState<MeasurementInstrument | null>(null);
  const [showCalibrationOnly, setShowCalibrationOnly] = useState(false);

  useEffect(() => {
    fetchInstruments();
  }, [showCalibrationOnly]);

  const fetchInstruments = async () => {
    try {
      let data;
      if (showCalibrationOnly) {
        data = await getCalibrationDueInstruments();
      } else {
        data = await getMeasurementInstruments();
      }
      setInstruments(data);
    } catch (error) {
      console.error('Failed to fetch instruments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingInstrument(null);
    setShowModal(true);
  };

  const handleEdit = (instrument: MeasurementInstrument) => {
    setEditingInstrument(instrument);
    setShowModal(true);
  };

  const handleDelete = async (instrument_cd: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await deleteMeasurementInstrument(instrument_cd);
      setInstruments(instruments.filter(inst => inst.instrument_cd !== instrument_cd));
    } catch (error) {
      console.error('Failed to delete instrument:', error);
      alert('삭제 실패');
    }
  };

  const handleSave = async (data: any) => {
    try {
      if (editingInstrument) {
        const updated = await updateMeasurementInstrument(editingInstrument.instrument_cd, data);
        setInstruments(instruments.map(inst => inst.instrument_cd === updated.instrument_cd ? updated : inst));
      } else {
        const created = await createMeasurementInstrument(data);
        setInstruments([...instruments, created]);
      }
      setShowModal(false);
      setEditingInstrument(null);
    } catch (error) {
      console.error('Failed to save instrument:', error);
      alert('저장 실패');
    }
  };

  const filteredInstruments = instruments.filter(instrument => {
    const matchesSearch = instrument.instrument_nm.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         instrument.instrument_cd.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = !selectedType || instrument.instrument_type === selectedType;
    const matchesStatus = !selectedStatus || instrument.status === selectedStatus;
    return matchesSearch && matchesType && matchesStatus;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">측정기구 마스터</h1>
          <p className="text-gray-600 mt-1">품질 검사에 사용되는 모든 측정기구 및 장비 관리</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowCalibrationOnly(!showCalibrationOnly)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              showCalibrationOnly
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <AlertTriangle className="w-5 h-5" />
            보정 만료만 보기
          </button>
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5" />
            신규 등록
          </button>
        </div>
      </div>

      {/* Warning for calibration due */}
      {showCalibrationOnly && filteredInstruments.length > 0 && (
        <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4">
          <div className="flex">
            <AlertTriangle className="w-6 h-6 text-red-500 mr-3" />
            <div>
              <p className="font-medium text-red-800">보정 만료 기구 {filteredInstruments.length}건</p>
              <p className="text-sm text-red-600">즉시 보정이 필요합니다.</p>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="기구코드 또는 기구명 검색..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
          >
            <option value="">전체 유형</option>
            <option value="CALIPER">노규자</option>
            <option value="MICROMETER">마이크로미터</option>
            <option value="CMM">3차원측정기</option>
            <option value="SCALE">저울</option>
            <option value="MULTIMETER">멀티미터</option>
            <option value="OSCILLOSCOPE">오실로스코프</option>
            <option value="VISUAL">육안검사</option>
          </select>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
          >
            <option value="">전체 상태</option>
            <option value="ACTIVE">사용가능</option>
            <option value="CALIBRATION_DUE">보정만료</option>
            <option value="MAINTENANCE">정비중</option>
            <option value="SCRAPPED">폐기</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">기구코드</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">기구명</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">유형</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">제조사/모델</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">측정범위</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">다음보정일</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">상태</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gage R&R</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">작업</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredInstruments.map((inst) => (
              <tr key={inst.instrument_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap font-medium">{inst.instrument_cd}</td>
                <td className="px-6 py-4">{inst.instrument_nm}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                    {inst.instrument_type_display || inst.instrument_type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <div>{inst.manufacturer}</div>
                    <div className="text-gray-500">{inst.model_no}</div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm">
                    {inst.measurement_range_min} ~ {inst.measurement_range_max} {inst.unit}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`text-sm font-medium ${
                    inst.is_calibration_due ? 'text-red-600' : 'text-gray-900'
                  }`}>
                    {inst.next_calibration_date || '-'}
                  </span>
                  {inst.is_calibration_due && (
                    <div className="text-xs text-red-500">보정만료</div>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded ${
                    inst.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                    inst.status === 'CALIBRATION_DUE' ? 'bg-red-100 text-red-800' :
                    inst.status === 'MAINTENANCE' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {inst.status_display || inst.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded ${
                    inst.gage_rr_result === 'PASS' ? 'bg-green-100 text-green-800' :
                    inst.gage_rr_result === 'FAIL' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {inst.gage_rr_result_display || inst.gage_rr_result}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleEdit(inst)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    <Pencil className="w-4 h-4 inline" />
                  </button>
                  <button
                    onClick={() => handleDelete(inst.instrument_cd)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="w-4 h-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
            {filteredInstruments.length === 0 && (
              <tr>
                <td colSpan={9} className="px-6 py-12 text-center text-gray-500">
                  데이터가 없습니다
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">
                {editingInstrument ? '측정기구 수정' : '신규 측정기구 등록'}
              </h2>
              <form onSubmit={(e) => {
                e.preventDefault();
                handleSave({});
              }}>
                <div className="grid grid-cols-2 gap-4">
                  {/* 기본 정보 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">기구코드 *</label>
                    <input
                      type="text"
                      defaultValue={editingInstrument?.instrument_cd}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                      disabled={!!editingInstrument}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">기구명 *</label>
                    <input
                      type="text"
                      defaultValue={editingInstrument?.instrument_nm}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">기구유형</label>
                    <select
                      defaultValue={editingInstrument?.instrument_type || 'CALIPER'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="CALIPER">노규자</option>
                      <option value="MICROMETER">마이크로미터</option>
                      <option value="CMM">3차원측정기</option>
                      <option value="SCALE">저울</option>
                      <option value="MULTIMETER">멀티미터</option>
                      <option value="OSCILLOSCOPE">오실로스코프</option>
                      <option value="VISUAL">육안검사</option>
                      <option value="OTHER">기타</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">단위</label>
                    <input
                      type="text"
                      defaultValue={editingInstrument?.unit || 'mm'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>

                  {/* 제조사 정보 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">제조사</label>
                    <input
                      type="text"
                      defaultValue={editingInstrument?.manufacturer}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">모델번호</label>
                    <input
                      type="text"
                      defaultValue={editingInstrument?.model_no}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">일련번호</label>
                    <input
                      type="text"
                      defaultValue={editingInstrument?.serial_no}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>

                  {/* 측정 범위 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">측정범위 최소</label>
                    <input
                      type="number"
                      step="0.001"
                      defaultValue={editingInstrument?.measurement_range_min}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">측정범위 최대</label>
                    <input
                      type="number"
                      step="0.001"
                      defaultValue={editingInstrument?.measurement_range_max}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">분해능</label>
                    <input
                      type="number"
                      step="0.0001"
                      defaultValue={editingInstrument?.resolution}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">정밀도</label>
                    <input
                      type="number"
                      step="0.001"
                      defaultValue={editingInstrument?.accuracy}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>

                  {/* 보정 정보 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">보정주기(일)</label>
                    <input
                      type="number"
                      defaultValue={editingInstrument?.calibration_cycle || 365}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">마지막보정일</label>
                    <input
                      type="date"
                      defaultValue={editingInstrument?.last_calibration_date}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">다음보정일</label>
                    <input
                      type="date"
                      defaultValue={editingInstrument?.next_calibration_date}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">보정기관</label>
                    <input
                      type="text"
                      defaultValue={editingInstrument?.calibration_institution}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>

                  {/* 상태 및 관리 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">상태</label>
                    <select
                      defaultValue={editingInstrument?.status || 'ACTIVE'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="ACTIVE">사용가능</option>
                      <option value="CALIBRATION_DUE">보정만료</option>
                      <option value="MAINTENANCE">정비중</option>
                      <option value="SCRAPPED">폐기</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">보관위치</label>
                    <input
                      type="text"
                      defaultValue={editingInstrument?.location}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">담당자</label>
                    <input
                      type="text"
                      defaultValue={editingInstrument?.responsible_person}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>

                  {/* Gage R&R */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Gage R&R 필수</label>
                    <select
                      defaultValue={editingInstrument?.gage_rr_required ? 'true' : 'false'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="true">예</option>
                      <option value="false">아니오</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Gage R&R 결과</label>
                    <select
                      defaultValue={editingInstrument?.gage_rr_result || 'PENDING'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="PASS">적합</option>
                      <option value="FAIL">부적합</option>
                      <option value="PENDING">미실시</option>
                    </select>
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">비고</label>
                    <textarea
                      defaultValue={editingInstrument?.notes}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>
                <div className="mt-6 flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    취소
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    저장
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MasterDataInstrumentsPage;

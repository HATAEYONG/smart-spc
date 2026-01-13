import React, { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Search, Database, Settings } from 'lucide-react';
import {
  getMeasurementSystems,
  createMeasurementSystem,
  updateMeasurementSystem,
  deleteMeasurementSystem,
  addInstrumentToSystem,
  removeInstrumentFromSystem,
  getMeasurementInstruments,
  MeasurementSystem,
  MeasurementInstrument,
} from '../services/spcMasterDataApi';

const MasterDataSystemsPage: React.FC = () => {
  const [systems, setSystems] = useState<MeasurementSystem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showAddInstrumentModal, setShowAddInstrumentModal] = useState(false);
  const [editingSystem, setEditingSystem] = useState<MeasurementSystem | null>(null);
  const [selectedSystem, setSelectedSystem] = useState<MeasurementSystem | null>(null);
  const [availableInstruments, setAvailableInstruments] = useState<MeasurementInstrument[]>([]);

  useEffect(() => {
    fetchSystems();
  }, []);

  const fetchSystems = async () => {
    try {
      const data = await getMeasurementSystems();
      setSystems(data);
    } catch (error) {
      console.error('Failed to fetch measurement systems:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInstruments = async () => {
    try {
      const data = await getMeasurementInstruments();
      setAvailableInstruments(data);
    } catch (error) {
      console.error('Failed to fetch instruments:', error);
    }
  };

  const handleCreate = () => {
    setEditingSystem(null);
    setShowModal(true);
  };

  const handleEdit = (system: MeasurementSystem) => {
    setEditingSystem(system);
    setShowModal(true);
  };

  const handleDelete = async (system_cd: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await deleteMeasurementSystem(system_cd);
      setSystems(systems.filter(sys => sys.system_cd !== system_cd));
    } catch (error) {
      console.error('Failed to delete system:', error);
      alert('삭제 실패');
    }
  };

  const handleSave = async (data: any) => {
    try {
      if (editingSystem) {
        const updated = await updateMeasurementSystem(editingSystem.system_cd, data);
        setSystems(systems.map(sys => sys.system_cd === updated.system_cd ? updated : sys));
      } else {
        const created = await createMeasurementSystem(data);
        setSystems([...systems, created]);
      }
      setShowModal(false);
      setEditingSystem(null);
    } catch (error) {
      console.error('Failed to save system:', error);
      alert('저장 실패');
    }
  };

  const handleManageInstruments = async (system: MeasurementSystem) => {
    setSelectedSystem(system);
    await fetchInstruments();
    setShowAddInstrumentModal(true);
  };

  const handleAddInstrument = async (instrument_cd: string, component_role: string) => {
    if (!selectedSystem) return;

    try {
      await addInstrumentToSystem(selectedSystem.system_cd, instrument_cd, component_role);
      alert('측정기구가 추가되었습니다.');
      await fetchSystems();
      setShowAddInstrumentModal(false);
    } catch (error) {
      console.error('Failed to add instrument:', error);
      alert('추가 실패');
    }
  };

  const handleRemoveInstrument = async (system_cd: string, instrument_cd: string) => {
    if (!confirm('정말 제거하시겠습니까?')) return;

    try {
      await removeInstrumentFromSystem(system_cd, instrument_cd);
      alert('측정기구가 제거되었습니다.');
      await fetchSystems();
    } catch (error) {
      console.error('Failed to remove instrument:', error);
      alert('제거 실패');
    }
  };

  const filteredSystems = systems.filter(sys => {
    return sys.system_nm.toLowerCase().includes(searchTerm.toLowerCase()) ||
           sys.system_cd.toLowerCase().includes(searchTerm.toLowerCase());
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
          <h1 className="text-3xl font-bold text-gray-900">측정 시스템 마스터</h1>
          <p className="text-gray-600 mt-1">측정 시스템 구성 정보 관리</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          신규 등록
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="시스템코드 또는 시스템명 검색..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Systems Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredSystems.map((sys) => (
          <div key={sys.system_id} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{sys.system_nm}</h3>
                <p className="text-sm text-gray-500">{sys.system_cd}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleManageInstruments(sys)}
                  className="text-blue-600 hover:text-blue-900 p-1"
                  title="기구 관리"
                >
                  <Settings className="w-5 h-5" />
                </button>
                <button
                  onClick={() => handleEdit(sys)}
                  className="text-blue-600 hover:text-blue-900 p-1"
                  title="수정"
                >
                  <Pencil className="w-5 h-5" />
                </button>
                <button
                  onClick={() => handleDelete(sys.system_cd)}
                  className="text-red-600 hover:text-red-900 p-1"
                  title="삭제"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">측정공정:</span>
                <span className="font-medium">{sys.measurement_process}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">구성기구수:</span>
                <span className="font-medium text-blue-600">{sys.instrument_count || sys.components?.length || 0}개</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">환경 조건:</span>
                <span className="font-medium">
                  {sys.temperature_min}°C ~ {sys.temperature_max}°C / {sys.humidity_min}% ~ {sys.humidity_max}%
                </span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">MSA 방법:</span>
                <span className="px-2 py-1 text-xs rounded bg-teal-100 text-teal-800">
                  {sys.msa_method_display || sys.msa_method}
                </span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">담당자:</span>
                <span className="font-medium">{sys.system_manager}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">위치:</span>
                <span className="font-medium">{sys.location}</span>
              </div>

              {sys.components && sys.components.length > 0 && (
                <div className="pt-3 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">구성 기구:</p>
                  <div className="space-y-2">
                    {sys.components.map((comp, idx) => (
                      <div key={comp.component_id} className="flex items-center justify-between bg-gray-50 rounded px-3 py-2">
                        <div className="flex-1">
                          <div className="text-sm font-medium">{comp.instrument_nm}</div>
                          <div className="text-xs text-gray-500">{comp.instrument_cd}</div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">{comp.component_role}</span>
                          <button
                            onClick={() => handleRemoveInstrument(sys.system_cd, comp.instrument_cd)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {filteredSystems.length === 0 && (
          <div className="col-span-2 bg-white rounded-lg shadow p-12 text-center text-gray-500">
            데이터가 없습니다
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">
                {editingSystem ? '측정 시스템 수정' : '신규 측정 시스템 등록'}
              </h2>
              <form onSubmit={(e) => {
                e.preventDefault();
                handleSave({});
              }}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">시스템코드 *</label>
                    <input
                      type="text"
                      defaultValue={editingSystem?.system_cd}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                      disabled={!!editingSystem}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">시스템명 *</label>
                    <input
                      type="text"
                      defaultValue={editingSystem?.system_nm}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">측정공정</label>
                    <input
                      type="text"
                      defaultValue={editingSystem?.measurement_process}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">온도 범위 (Min ~ Max °C)</label>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        defaultValue={editingSystem?.temperature_min || 20}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                      />
                      <input
                        type="number"
                        defaultValue={editingSystem?.temperature_max || 25}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">습도 범위 (Min ~ Max %)</label>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        defaultValue={editingSystem?.humidity_min || 40}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                      />
                      <input
                        type="number"
                        defaultValue={editingSystem?.humidity_max || 60}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">MSA 방법</label>
                    <select
                      defaultValue={editingSystem?.msa_method || 'GAGE_RR'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="GAGE_RR">Gage R&R</option>
                      <option value="BIAS">Bias</option>
                      <option value="LINEARITY">Linearity</option>
                      <option value="STABILITY">Stability</option>
                      <option value="KAPPA">Kappa (Attribute)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">시스템 담당자</label>
                    <input
                      type="text"
                      defaultValue={editingSystem?.system_manager}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">위치</label>
                    <input
                      type="text"
                      defaultValue={editingSystem?.location}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">비고</label>
                    <textarea
                      defaultValue={editingSystem?.notes}
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

      {/* Add Instrument Modal */}
      {showAddInstrumentModal && selectedSystem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">측정기구 추가</h2>
              <p className="text-gray-600 mb-4">
                {selectedSystem.system_nm} 시스템에 측정기구를 추가합니다.
              </p>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {availableInstruments.map((inst) => (
                  <div key={inst.instrument_id} className="flex items-center justify-between bg-gray-50 rounded p-3">
                    <div className="flex-1">
                      <div className="font-medium">{inst.instrument_nm}</div>
                      <div className="text-sm text-gray-500">{inst.instrument_cd}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <select
                        id={`role-${inst.instrument_id}`}
                        className="px-3 py-1 border border-gray-300 rounded text-sm"
                      >
                        <option value="PRIMARY">주측정기</option>
                        <option value="SECONDARY">보조측정기</option>
                        <option value="AUXILIARY">보조장비</option>
                      </select>
                      <button
                        onClick={() => {
                          const roleSelect = document.getElementById(`role-${inst.instrument_id}`) as HTMLSelectElement;
                          handleAddInstrument(inst.instrument_cd, roleSelect.value);
                        }}
                        className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                      >
                        추가
                      </button>
                    </div>
                  </div>
                ))}

                {availableInstruments.length === 0 && (
                  <div className="text-center text-gray-500 py-8">
                    추가 가능한 측정기구가 없습니다.
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowAddInstrumentModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  닫기
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MasterDataSystemsPage;

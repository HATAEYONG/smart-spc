import React, { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Search, Filter, BarChart3 } from 'lucide-react';
import {
  getQualityCharacteristics,
  createQualityCharacteristic,
  updateQualityCharacteristic,
  deleteQualityCharacteristic,
  QualityCharacteristic,
} from '../services/spcMasterDataApi';

const MasterDataCharacteristicsPage: React.FC = () => {
  const [characteristics, setCharacteristics] = useState<QualityCharacteristic[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedItem, setSelectedItem] = useState('');
  const [selectedProcess, setSelectedProcess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCharacteristic, setEditingCharacteristic] = useState<QualityCharacteristic | null>(null);

  useEffect(() => {
    fetchCharacteristics();
  }, [selectedType, selectedItem, selectedProcess]);

  const fetchCharacteristics = async () => {
    try {
      const data = await getQualityCharacteristics({
        characteristic_type: selectedType || undefined,
        item_id: selectedItem || undefined,
        process_id: selectedProcess || undefined,
      });
      setCharacteristics(data);
    } catch (error) {
      console.error('Failed to fetch characteristics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingCharacteristic(null);
    setShowModal(true);
  };

  const handleEdit = (characteristic: QualityCharacteristic) => {
    setEditingCharacteristic(characteristic);
    setShowModal(true);
  };

  const handleDelete = async (characteristic_cd: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await deleteQualityCharacteristic(characteristic_cd);
      setCharacteristics(characteristics.filter(char => char.characteristic_cd !== characteristic_cd));
    } catch (error) {
      console.error('Failed to delete characteristic:', error);
      alert('삭제 실패');
    }
  };

  const handleSave = async (data: any) => {
    try {
      if (editingCharacteristic) {
        const updated = await updateQualityCharacteristic(editingCharacteristic.characteristic_cd, data);
        setCharacteristics(characteristics.map(char => char.characteristic_cd === updated.characteristic_cd ? updated : char));
      } else {
        const created = await createQualityCharacteristic(data);
        setCharacteristics([...characteristics, created]);
      }
      setShowModal(false);
      setEditingCharacteristic(null);
    } catch (error) {
      console.error('Failed to save characteristic:', error);
      alert('저장 실패');
    }
  };

  const filteredCharacteristics = characteristics.filter(char => {
    const matchesSearch = char.characteristic_nm.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         char.characteristic_cd.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = !selectedType || char.characteristic_type === selectedType;
    const matchesItem = !selectedItem || char.item?.toString() === selectedItem;
    const matchesProcess = !selectedProcess || char.process?.toString() === selectedProcess;
    return matchesSearch && matchesType && matchesItem && matchesProcess;
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
          <h1 className="text-3xl font-bold text-gray-900">품질 특성 마스터</h1>
          <p className="text-gray-600 mt-1">품질 측정 특성 정보 관리</p>
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
              placeholder="특성코드 또는 특성명 검색..."
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
            <option value="DIMENSION">치수</option>
            <option value="WEIGHT">중량</option>
            <option value="VOLTAGE">전압</option>
            <option value="CURRENT">전류</option>
            <option value="TEMPERATURE">온도</option>
            <option value="PRESSURE">압력</option>
            <option value="APPEARANCE">외관</option>
          </select>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedItem}
            onChange={(e) => setSelectedItem(e.target.value)}
          >
            <option value="">전체 품목</option>
            {[...new Set(characteristics.map(c => c.itm_id).filter(Boolean))].map(itemId => (
              <option key={itemId} value={itemId}>{itemId}</option>
            ))}
          </select>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedProcess}
            onChange={(e) => setSelectedProcess(e.target.value)}
          >
            <option value="">전체 공정</option>
            {[...new Set(characteristics.map(c => c.process_cd).filter(Boolean))].map(procCd => (
              <option key={procCd} value={procCd}>{procCd}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">특성코드</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">특성명</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">유형</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">품목</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">공정</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">LSL</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Target</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">USL</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">관리도</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">활성화</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">작업</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredCharacteristics.map((char) => (
              <tr key={char.characteristic_cd} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap font-medium">{char.characteristic_cd}</td>
                <td className="px-6 py-4">{char.characteristic_nm}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                    {char.characteristic_type_display || char.characteristic_type}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm">{char.itm_id || '-'}</td>
                <td className="px-6 py-4 text-sm">{char.process_cd || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-red-600">
                  {char.lsl}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-green-600">
                  {char.target}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-blue-600">
                  {char.usl}
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs rounded bg-purple-100 text-purple-800">
                    {char.control_chart_type_display || char.control_chart_type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded ${
                    char.active_yn === 'Y' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {char.active_yn === 'Y' ? '활성' : '비활성'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleEdit(char)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    <Pencil className="w-4 h-4 inline" />
                  </button>
                  <button
                    onClick={() => handleDelete(char.characteristic_cd)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="w-4 h-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
            {filteredCharacteristics.length === 0 && (
              <tr>
                <td colSpan={11} className="px-6 py-12 text-center text-gray-500">
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
                {editingCharacteristic ? '특성 수정' : '신규 특성 등록'}
              </h2>
              <form onSubmit={(e) => {
                e.preventDefault();
                handleSave({});
              }}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">특성코드 *</label>
                    <input
                      type="text"
                      defaultValue={editingCharacteristic?.characteristic_cd}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                      disabled={!!editingCharacteristic}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">특성명 *</label>
                    <input
                      type="text"
                      defaultValue={editingCharacteristic?.characteristic_nm}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">특성유형</label>
                    <select
                      defaultValue={editingCharacteristic?.characteristic_type || 'DIMENSION'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="DIMENSION">치수</option>
                      <option value="WEIGHT">중량</option>
                      <option value="VOLTAGE">전압</option>
                      <option value="CURRENT">전류</option>
                      <option value="TEMPERATURE">온도</option>
                      <option value="PRESSURE">압력</option>
                      <option value="APPEARANCE">외관</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">데이터유형</label>
                    <select
                      defaultValue={editingCharacteristic?.data_type || 'CONTINUOUS'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="CONTINUOUS">연속형</option>
                      <option value="DISCRETE">이산형</option>
                      <option value="ATTRIBUTE">속성형</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">단위</label>
                    <input
                      type="text"
                      defaultValue={editingCharacteristic?.unit || 'mm'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">품목</label>
                    <input
                      type="text"
                      defaultValue={editingCharacteristic?.itm_id}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="품목 ID"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">공정</label>
                    <input
                      type="text"
                      defaultValue={editingCharacteristic?.process_cd}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="공정코드"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">관리도유형</label>
                    <select
                      defaultValue={editingCharacteristic?.control_chart_type || 'XBAR_R'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="XBAR_R">Xbar-R 관리도</option>
                      <option value="XBAR_S">Xbar-S 관리도</option>
                      <option value="I_MR">I-MR 관리도</option>
                      <option value="P_chart">P 관리도</option>
                      <option value="U_chart">U 관리도</option>
                      <option value="C_chart">C 관리도</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">LSL (하한)</label>
                    <input
                      type="number"
                      step="0.01"
                      defaultValue={editingCharacteristic?.lsl}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Target (목표)</label>
                    <input
                      type="number"
                      step="0.01"
                      defaultValue={editingCharacteristic?.target}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">USL (상한)</label>
                    <input
                      type="number"
                      step="0.01"
                      defaultValue={editingCharacteristic?.usl}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cpk 목표</label>
                    <input
                      type="number"
                      step="0.01"
                      defaultValue={editingCharacteristic?.cpk_target || 1.33}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cpk 최소</label>
                    <input
                      type="number"
                      step="0.01"
                      defaultValue={editingCharacteristic?.cpk_minimum || 1.0}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">부그룹 크기</label>
                    <input
                      type="number"
                      defaultValue={editingCharacteristic?.subgroup_size || 5}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">측정방법</label>
                    <input
                      type="text"
                      defaultValue={editingCharacteristic?.measurement_method}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">측정위치</label>
                    <input
                      type="text"
                      defaultValue={editingCharacteristic?.measurement_location}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">품질담당자</label>
                    <input
                      type="text"
                      defaultValue={editingCharacteristic?.quality_manager}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">비고</label>
                    <textarea
                      defaultValue={editingCharacteristic?.notes}
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

export default MasterDataCharacteristicsPage;

import React, { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Search, Filter, FileText } from 'lucide-react';
import {
  getInspectionStandards,
  createInspectionStandard,
  updateInspectionStandard,
  deleteInspectionStandard,
  InspectionStandard,
} from '../services/spcMasterDataApi';

const MasterDataStandardsPage: React.FC = () => {
  const [standards, setStandards] = useState<InspectionStandard[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedItem, setSelectedItem] = useState('');
  const [selectedCharacteristic, setSelectedCharacteristic] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingStandard, setEditingStandard] = useState<InspectionStandard | null>(null);

  useEffect(() => {
    fetchStandards();
  }, [selectedType, selectedItem, selectedCharacteristic]);

  const fetchStandards = async () => {
    try {
      const data = await getInspectionStandards({
        standard_type: selectedType || undefined,
        item_id: selectedItem || undefined,
        characteristic_id: selectedCharacteristic || undefined,
      });
      setStandards(data);
    } catch (error) {
      console.error('Failed to fetch inspection standards:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingStandard(null);
    setShowModal(true);
  };

  const handleEdit = (standard: InspectionStandard) => {
    setEditingStandard(standard);
    setShowModal(true);
  };

  const handleDelete = async (standard_cd: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await deleteInspectionStandard(standard_cd);
      setStandards(standards.filter(std => std.standard_cd !== standard_cd));
    } catch (error) {
      console.error('Failed to delete standard:', error);
      alert('삭제 실패');
    }
  };

  const handleSave = async (data: any) => {
    try {
      if (editingStandard) {
        const updated = await updateInspectionStandard(editingStandard.standard_cd, data);
        setStandards(standards.map(std => std.standard_cd === updated.standard_cd ? updated : std));
      } else {
        const created = await createInspectionStandard(data);
        setStandards([...standards, created]);
      }
      setShowModal(false);
      setEditingStandard(null);
    } catch (error) {
      console.error('Failed to save standard:', error);
      alert('저장 실패');
    }
  };

  const filteredStandards = standards.filter(std => {
    const matchesSearch = std.standard_nm.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         std.standard_cd.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = !selectedType || std.standard_type === selectedType;
    const matchesItem = !selectedItem || std.item?.toString() === selectedItem;
    const matchesCharacteristic = !selectedCharacteristic || std.characteristic?.toString() === selectedCharacteristic;
    return matchesSearch && matchesType && matchesItem && matchesCharacteristic;
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
          <h1 className="text-3xl font-bold text-gray-900">검사 기준 마스터</h1>
          <p className="text-gray-600 mt-1">검사 기준서 정보 관리</p>
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
              placeholder="기준코드 또는 기준명 검색..."
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
            <option value="INCOMING">입고검사</option>
            <option value="PROCESS">공정검사</option>
            <option value="FINAL">최종검사</option>
            <option value="OUTGOING">출하검사</option>
          </select>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedItem}
            onChange={(e) => setSelectedItem(e.target.value)}
          >
            <option value="">전체 품목</option>
            {[...new Set(standards.map(s => s.itm_id).filter(Boolean))].map(itemId => (
              <option key={itemId} value={itemId}>{itemId}</option>
            ))}
          </select>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedCharacteristic}
            onChange={(e) => setSelectedCharacteristic(e.target.value)}
          >
            <option value="">전체 특성</option>
            {[...new Set(standards.map(s => s.characteristic_cd).filter(Boolean))].map(charCd => (
              <option key={charCd} value={charCd}>{charCd}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">기준코드</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">기준명</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">유형</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">품목</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">특성</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">검사조건</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">AQL</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">시험방법</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">개정</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">활성화</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">작업</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredStandards.map((std) => (
              <tr key={std.standard_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap font-medium">{std.standard_cd}</td>
                <td className="px-6 py-4">{std.standard_nm}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded ${
                    std.standard_type === 'INCOMING' ? 'bg-blue-100 text-blue-800' :
                    std.standard_type === 'PROCESS' ? 'bg-purple-100 text-purple-800' :
                    std.standard_type === 'FINAL' ? 'bg-green-100 text-green-800' :
                    'bg-orange-100 text-orange-800'
                  }`}>
                    {std.standard_type_display || std.standard_type}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm">{std.itm_id || '-'}</td>
                <td className="px-6 py-4 text-sm">{std.characteristic_cd || '-'}</td>
                <td className="px-6 py-4 text-sm">{std.inspection_condition}</td>
                <td className="px-6 py-4 text-sm">{std.aql ? `${std.aql}%` : '-'}</td>
                <td className="px-6 py-4 text-sm">{std.test_method}</td>
                <td className="px-6 py-4 text-sm">{std.revision}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded ${
                    std.active_yn === 'Y' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {std.active_yn === 'Y' ? '활성' : '비활성'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleEdit(std)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    <Pencil className="w-4 h-4 inline" />
                  </button>
                  <button
                    onClick={() => handleDelete(std.standard_cd)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="w-4 h-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
            {filteredStandards.length === 0 && (
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
                {editingStandard ? '검사 기준 수정' : '신규 검사 기준 등록'}
              </h2>
              <form onSubmit={(e) => {
                e.preventDefault();
                handleSave({});
              }}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">기준코드 *</label>
                    <input
                      type="text"
                      defaultValue={editingStandard?.standard_cd}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                      disabled={!!editingStandard}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">기준명 *</label>
                    <input
                      type="text"
                      defaultValue={editingStandard?.standard_nm}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">기준유형</label>
                    <select
                      defaultValue={editingStandard?.standard_type || 'PROCESS'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="INCOMING">입고검사</option>
                      <option value="PROCESS">공정검사</option>
                      <option value="FINAL">최종검사</option>
                      <option value="OUTGOING">출하검사</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">품목</label>
                    <input
                      type="text"
                      defaultValue={editingStandard?.itm_id}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="품목 ID"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">특성</label>
                    <input
                      type="text"
                      defaultValue={editingStandard?.characteristic_cd}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="특성코드"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">개정번호</label>
                    <input
                      type="text"
                      defaultValue={editingStandard?.revision || 'A'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">검사조건</label>
                    <textarea
                      defaultValue={editingStandard?.inspection_condition}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="검사 환경 조건 등"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">합격기준</label>
                    <textarea
                      defaultValue={editingStandard?.acceptance_criteria}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">불합격기준</label>
                    <textarea
                      defaultValue={editingStandard?.rejection_criteria}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">샘플링방법</label>
                    <input
                      type="text"
                      defaultValue={editingStandard?.sampling_method}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">샘플크기</label>
                    <input
                      type="number"
                      defaultValue={editingStandard?.sample_size}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">AQL (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      defaultValue={editingStandard?.aql || 1.5}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">시험장비</label>
                    <input
                      type="text"
                      defaultValue={editingStandard?.test_equipment}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">시험방법</label>
                    <textarea
                      defaultValue={editingStandard?.test_method}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">참조문서</label>
                    <input
                      type="text"
                      defaultValue={editingStandard?.reference_doc}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">시작일</label>
                    <input
                      type="date"
                      defaultValue={editingStandard?.effective_date}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">비고</label>
                    <textarea
                      defaultValue={editingStandard?.notes}
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

export default MasterDataStandardsPage;

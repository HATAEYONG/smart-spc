import React, { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Upload, Filter, Search } from 'lucide-react';
import {
  getQualityItems,
  createQualityItem,
  updateQualityItem,
  deleteQualityItem,
  importItemsFromERP,
  QualityItem,
} from '../services/spcMasterDataApi';

const MasterDataItemsPage: React.FC = () => {
  const [items, setItems] = useState<QualityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState<QualityItem | null>(null);
  const [showImportModal, setShowImportModal] = useState(false);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const data = await getQualityItems();
      setItems(data);
    } catch (error) {
      console.error('Failed to fetch items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingItem(null);
    setShowModal(true);
  };

  const handleEdit = (item: QualityItem) => {
    setEditingItem(item);
    setShowModal(true);
  };

  const handleDelete = async (itm_id: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await deleteQualityItem(itm_id);
      setItems(items.filter(item => item.itm_id !== itm_id));
    } catch (error) {
      console.error('Failed to delete item:', error);
      alert('삭제 실패');
    }
  };

  const handleSave = async (data: any) => {
    try {
      if (editingItem) {
        const updated = await updateQualityItem(editingItem.itm_id, data);
        setItems(items.map(item => item.itm_id === updated.itm_id ? updated : item));
      } else {
        const created = await createQualityItem(data);
        setItems([...items, created]);
      }
      setShowModal(false);
      setEditingItem(null);
    } catch (error) {
      console.error('Failed to save item:', error);
      alert('저장 실패');
    }
  };

  const handleImportFromERP = async () => {
    // For demo purposes, create sample data
    const sampleItems = [
      {
        itm_id: 'ERP-001',
        itm_nm: '배터리 셀 18650',
        itm_type: 'FINISHED_GOOD',
        itm_family: '배터리',
        quality_grade: 'A',
        inspection_type: 'SAMPLING',
        sampling_plan: 'MIL-STD-105E',
        sample_size: 50,
        sampling_frequency: '2시간말',
        supplier_code: 'SUP-001',
        supplier_nm: '(주)한국배터리',
        quality_manager: '홍길동',
        notes: '고용량 배터리 셀',
        active_yn: 'Y',
      },
      {
        itm_id: 'ERP-002',
        itm_nm: 'PCB 보드',
        itm_type: 'COMPONENT',
        itm_family: '전자부품',
        quality_grade: 'B',
        inspection_type: 'SAMPLING',
        sampling_plan: 'AQL=1.5',
        sample_size: 32,
        sampling_frequency: '배치별',
        quality_manager: '김철수',
        notes: '전자기판',
        active_yn: 'Y',
      },
    ];

    try {
      const result = await importItemsFromERP(sampleItems);
      alert(`Import 완료:\n생성: ${result.created}\n수정: ${result.updated}\n실패: ${result.failed}`);
      await fetchItems();
      setShowImportModal(false);
    } catch (error) {
      console.error('Failed to import:', error);
      alert('Import 실패');
    }
  };

  const filteredItems = items.filter(item => {
    const matchesSearch = item.itm_nm.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.itm_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = !selectedType || item.itm_type === selectedType;
    return matchesSearch && matchesType;
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
          <h1 className="text-3xl font-bold text-gray-900">품목 마스터</h1>
          <p className="text-gray-600 mt-1">품질 관리 대상 품목 정보</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowImportModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Upload className="w-5 h-5" />
            ERP Import
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

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="품목코드 또는 품목명 검색..."
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
            <option value="RAW_MATERIAL">원자재</option>
            <option value="WIP">재공품</option>
            <option value="FINISHED_GOOD">완제품</option>
            <option value="COMPONENT">부품</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">품목코드</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">품목명</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">유형</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">등급</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">검사유형</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">특성수</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">활성화</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">작업</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredItems.map((item) => (
              <tr key={item.itm_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap font-medium">{item.itm_id}</td>
                <td className="px-6 py-4">{item.itm_nm}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                    {item.itm_type_display || item.itm_type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded ${
                    item.quality_grade === 'A' ? 'bg-red-100 text-red-800' :
                    item.quality_grade === 'B' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {item.quality_grade_display || item.quality_grade}급
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-800">
                    {item.inspection_type_display || item.inspection_type}
                  </span>
                </td>
                <td className="px-6 py-4 text-center">{item.total_characteristics || 0}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded ${
                    item.active_yn === 'Y' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {item.active_yn === 'Y' ? '활성' : '비활성'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleEdit(item)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    <Pencil className="w-4 h-4 inline" />
                  </button>
                  <button
                    onClick={() => handleDelete(item.itm_id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="w-4 h-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
            {filteredItems.length === 0 && (
              <tr>
                <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
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
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">
                {editingItem ? '품목 수정' : '신규 품목 등록'}
              </h2>
              <form onSubmit={(e) => {
                e.preventDefault();
                handleSave({});
              }}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">품목코드 *</label>
                    <input
                      type="text"
                      defaultValue={editingItem?.itm_id}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                      disabled={!!editingItem}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">품목명 *</label>
                    <input
                      type="text"
                      defaultValue={editingItem?.itm_nm}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">품목유형</label>
                    <select
                      defaultValue={editingItem?.itm_type || 'FINISHED_GOOD'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="RAW_MATERIAL">원자재</option>
                      <option value="WIP">재공품</option>
                      <option value="FINISHED_GOOD">완제품</option>
                      <option value="COMPONENT">부품</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">품목패밀리</label>
                    <input
                      type="text"
                      defaultValue={editingItem?.itm_family}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">품질등급</label>
                    <select
                      defaultValue={editingItem?.quality_grade || 'B'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="A">A급 - 핵심</option>
                      <option value="B">B급 - 일반</option>
                      <option value="C">C급 - 일반</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">검사유형</label>
                    <select
                      defaultValue={editingItem?.inspection_type || 'SAMPLING'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="FULL">전수검사</option>
                      <option value="SAMPLING">샘플링검사</option>
                      <option value="SKIP">Skip 검사</option>
                      <option value="NONE">검사안함</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">샘플링기준</label>
                    <input
                      type="text"
                      defaultValue={editingItem?.sampling_plan}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">샘플크기</label>
                    <input
                      type="number"
                      defaultValue={editingItem?.sample_size}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">샘플링빈도</label>
                    <input
                      type="text"
                      defaultValue={editingItem?.sampling_frequency}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">공급자코드</label>
                    <input
                      type="text"
                      defaultValue={editingItem?.supplier_code}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">공급자명</label>
                    <input
                      type="text"
                      defaultValue={editingItem?.supplier_nm}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">품질담당자</label>
                    <input
                      type="text"
                      defaultValue={editingItem?.quality_manager}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">비고</label>
                    <textarea
                      defaultValue={editingItem?.notes}
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

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-4">ERP 데이터 Import</h2>
              <p className="text-gray-600 mb-6">
                ERP 시스템에서 품목 마스터 데이터를 가져옵니다. 데모를 위해 샘플 데이터를 생성합니다.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowImportModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  취소
                </button>
                <button
                  onClick={handleImportFromERP}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Import 실행
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MasterDataItemsPage;

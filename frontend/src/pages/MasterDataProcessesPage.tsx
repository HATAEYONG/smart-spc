import React, { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Upload, Filter, Search, Settings } from 'lucide-react';
import {
  getQualityProcesses,
  createQualityProcess,
  updateQualityProcess,
  deleteQualityProcess,
  importProcessesFromMES,
  QualityProcess,
} from '../services/spcMasterDataApi';

const MasterDataProcessesPage: React.FC = () => {
  const [processes, setProcesses] = useState<QualityProcess[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedWorkCenter, setSelectedWorkCenter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingProcess, setEditingProcess] = useState<QualityProcess | null>(null);
  const [showImportModal, setShowImportModal] = useState(false);

  useEffect(() => {
    fetchProcesses();
  }, [selectedType, selectedWorkCenter]);

  const fetchProcesses = async () => {
    try {
      const data = await getQualityProcesses({
        process_type: selectedType || undefined,
        workcenter_cd: selectedWorkCenter || undefined,
      });
      setProcesses(data);
    } catch (error) {
      console.error('Failed to fetch processes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingProcess(null);
    setShowModal(true);
  };

  const handleEdit = (process: QualityProcess) => {
    setEditingProcess(process);
    setShowModal(true);
  };

  const handleDelete = async (process_cd: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await deleteQualityProcess(process_cd);
      setProcesses(processes.filter(proc => proc.process_cd !== process_cd));
    } catch (error) {
      console.error('Failed to delete process:', error);
      alert('삭제 실패');
    }
  };

  const handleSave = async (data: any) => {
    try {
      if (editingProcess) {
        const updated = await updateQualityProcess(editingProcess.process_cd, data);
        setProcesses(processes.map(proc => proc.process_cd === updated.process_cd ? updated : proc));
      } else {
        const created = await createQualityProcess(data);
        setProcesses([...processes, created]);
      }
      setShowModal(false);
      setEditingProcess(null);
    } catch (error) {
      console.error('Failed to save process:', error);
      alert('저장 실패');
    }
  };

  const handleImportFromMES = async () => {
    // For demo purposes, create sample data
    const sampleProcesses = [
      {
        process_cd: 'MES-001',
        process_nm: '배터리 셀 조립',
        process_type: 'ASSEMBLY',
        workcenter_cd: 'WC-001',
        workcenter_nm: '1라인 조립공정',
        line_cd: 'L01',
        process_seq: 10,
        process_manager: '김철수',
        notes: '주요 조립 공정',
        active_yn: 'Y',
      },
      {
        process_cd: 'MES-002',
        process_nm: '배터리 셀 용접',
        process_type: 'WELDING',
        workcenter_cd: 'WC-002',
        workcenter_nm: '1라인 용접공정',
        line_cd: 'L01',
        process_seq: 20,
        process_manager: '이영희',
        notes: '레이저 용접 공정',
        active_yn: 'Y',
      },
      {
        process_cd: 'MES-003',
        process_nm: '품질 검사',
        process_type: 'INSPECTION',
        workcenter_cd: 'WC-003',
        workcenter_nm: '검사실',
        line_cd: 'L01',
        process_seq: 30,
        process_manager: '박민수',
        notes: '외관 및 치수 검사',
        active_yn: 'Y',
      },
    ];

    try {
      const result = await importProcessesFromMES(sampleProcesses);
      alert(`Import 완료:\n생성: ${result.created}\n수정: ${result.updated}\n실패: ${result.failed}`);
      await fetchProcesses();
      setShowImportModal(false);
    } catch (error) {
      console.error('Failed to import:', error);
      alert('Import 실패');
    }
  };

  const filteredProcesses = processes.filter(proc => {
    const matchesSearch = proc.process_nm.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         proc.process_cd.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         proc.workcenter_nm.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = !selectedType || proc.process_type === selectedType;
    const matchesWorkCenter = !selectedWorkCenter || proc.workcenter_cd === selectedWorkCenter;
    return matchesSearch && matchesType && matchesWorkCenter;
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
          <h1 className="text-3xl font-bold text-gray-900">공정 마스터</h1>
          <p className="text-gray-600 mt-1">품질 관리 대상 공정 정보 (MES 연계)</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowImportModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            <Upload className="w-5 h-5" />
            MES Import
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
              placeholder="공정코드, 공정명, 작업장명 검색..."
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
            <option value="ASSEMBLY">조립</option>
            <option value="WELDING">용접</option>
            <option value="MACHINING">가공</option>
            <option value="INSPECTION">검사</option>
            <option value="TESTING">시험</option>
            <option value="PACKAGING">포장</option>
          </select>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedWorkCenter}
            onChange={(e) => setSelectedWorkCenter(e.target.value)}
          >
            <option value="">전체 작업장</option>
            {[...new Set(processes.map(p => p.workcenter_cd))].map(wc => (
              <option key={wc} value={wc}>{wc}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">공정코드</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">공정명</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">유형</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">작업장</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">라인</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">순서</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">담당자</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">특성수</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">활성화</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">작업</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredProcesses.map((proc) => (
              <tr key={proc.process_cd} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap font-medium">{proc.process_cd}</td>
                <td className="px-6 py-4">{proc.process_nm}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs rounded bg-purple-100 text-purple-800">
                    {proc.process_type_display || proc.process_type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm">{proc.workcenter_cd}</div>
                  <div className="text-xs text-gray-500">{proc.workcenter_nm}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">{proc.line_cd}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm">{proc.process_seq}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{proc.process_manager}</td>
                <td className="px-6 py-4 text-center text-sm">{proc.total_characteristics || 0}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded ${
                    proc.active_yn === 'Y' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {proc.active_yn === 'Y' ? '활성' : '비활성'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleEdit(proc)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    <Pencil className="w-4 h-4 inline" />
                  </button>
                  <button
                    onClick={() => handleDelete(proc.process_cd)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="w-4 h-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
            {filteredProcesses.length === 0 && (
              <tr>
                <td colSpan={10} className="px-6 py-12 text-center text-gray-500">
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
                {editingProcess ? '공정 수정' : '신규 공정 등록'}
              </h2>
              <form onSubmit={(e) => {
                e.preventDefault();
                handleSave({});
              }}>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">공정코드 *</label>
                    <input
                      type="text"
                      defaultValue={editingProcess?.process_cd}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                      disabled={!!editingProcess}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">공정명 *</label>
                    <input
                      type="text"
                      defaultValue={editingProcess?.process_nm}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">공정유형</label>
                    <select
                      defaultValue={editingProcess?.process_type || 'ASSEMBLY'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      <option value="ASSEMBLY">조립</option>
                      <option value="WELDING">용접</option>
                      <option value="MACHINING">가공</option>
                      <option value="INSPECTION">검사</option>
                      <option value="TESTING">시험</option>
                      <option value="PACKAGING">포장</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">작업장코드 *</label>
                    <input
                      type="text"
                      defaultValue={editingProcess?.workcenter_cd}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">작업장명</label>
                    <input
                      type="text"
                      defaultValue={editingProcess?.workcenter_nm}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">라인코드</label>
                    <input
                      type="text"
                      defaultValue={editingProcess?.line_cd}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">공정순서</label>
                    <input
                      type="number"
                      defaultValue={editingProcess?.process_seq || 10}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">공정담당자</label>
                    <input
                      type="text"
                      defaultValue={editingProcess?.process_manager}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">비고</label>
                    <textarea
                      defaultValue={editingProcess?.notes}
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
              <h2 className="text-2xl font-bold mb-4">MES 데이터 Import</h2>
              <p className="text-gray-600 mb-6">
                MES 시스템에서 공정 마스터 데이터를 가져옵니다. 데모를 위해 샘플 데이터를 생성합니다.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowImportModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  취소
                </button>
                <button
                  onClick={handleImportFromMES}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
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

export default MasterDataProcessesPage;

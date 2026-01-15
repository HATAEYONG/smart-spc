/**
 * 자체 입력 CRUD 페이지
 * 사용자가 직접 품질 데이터를 입력하는 완전한 CRUD 기능
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Plus,
  Edit,
  Trash2,
  Eye,
  Search,
  Filter,
  Download,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle
} from 'lucide-react';

interface QualityRecord {
  id: number;
  record_number: string;
  product_code: string;
  product_name: string;
  inspection_date: string;
  inspector: string;
  department: string;
  inspection_type: 'INCOMING' | 'PROCESS' | 'FINAL' | 'OUTGOING';
  sample_size: number;
  defect_count: number;
  defect_rate: number;
  characteristics: {
    name: string;
    target_value: number;
    tolerance: number;
    measured_value: number;
    status: 'OK' | 'NG';
  }[];
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  notes: string;
}

const mockRecords: QualityRecord[] = [
  {
    id: 1,
    record_number: 'QI-2025-001',
    product_code: 'PROD-001',
    product_name: '자동차 부품 A-Type',
    inspection_date: '2025-01-15',
    inspector: '홍검사원',
    department: '품질팀',
    inspection_type: 'FINAL',
    sample_size: 50,
    defect_count: 2,
    defect_rate: 4.0,
    characteristics: [
      { name: '길이', target_value: 100, tolerance: 0.5, measured_value: 100.2, status: 'OK' },
      { name: '두께', target_value: 5, tolerance: 0.1, measured_value: 5.05, status: 'OK' },
      { name: '직각도', target_value: 90, tolerance: 1, measured_value: 91.5, status: 'NG' }
    ],
    status: 'APPROVED',
    notes: '전체 합격, 2개 불량품 발견'
  },
  {
    id: 2,
    record_number: 'QI-2025-002',
    product_code: 'PROD-002',
    product_name: '전자 부품 B-Type',
    inspection_date: '2025-01-15',
    inspector: '이검사원',
    department: '품질팀',
    inspection_type: 'PROCESS',
    sample_size: 30,
    defect_count: 8,
    defect_rate: 26.7,
    characteristics: [
      { name: '전압', target_value: 5, tolerance: 0.2, measured_value: 5.3, status: 'NG' },
      { name: '저항', target_value: 1000, tolerance: 50, measured_value: 1020, status: 'OK' }
    ],
    status: 'REJECTED',
    notes: '불량률 초과로 반품'
  },
  {
    id: 3,
    record_number: 'QI-2025-003',
    product_code: 'PROD-003',
    product_name: '금속 부품 C-Type',
    inspection_date: '2025-01-14',
    inspector: '박검사원',
    department: '품질팀',
    inspection_type: 'INCOMING',
    sample_size: 20,
    defect_count: 0,
    defect_rate: 0.0,
    characteristics: [
      { name: '경도', target_value: 45, tolerance: 2, measured_value: 45.5, status: 'OK' },
      { name: '표면 조도', target_value: 1.6, tolerance: 0.4, measured_value: 1.5, status: 'OK' }
    ],
    status: 'APPROVED',
    notes: '전량 합격'
  }
];

const ManualInputPage: React.FC = () => {
  const [records, setRecords] = useState<QualityRecord[]>(mockRecords);
  const [selectedRecord, setSelectedRecord] = useState<QualityRecord | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const [formData, setFormData] = useState({
    product_code: '',
    product_name: '',
    inspection_date: new Date().toISOString().split('T')[0],
    inspector: '',
    department: '',
    inspection_type: 'FINAL' as const,
    sample_size: '',
    defect_count: '0',
    notes: ''
  });

  const resetForm = () => {
    setFormData({
      product_code: '',
      product_name: '',
      inspection_date: new Date().toISOString().split('T')[0],
      inspector: '',
      department: '',
      inspection_type: 'FINAL',
      sample_size: '',
      defect_count: '0',
      notes: ''
    });
  };

  const handleOpenAddModal = () => {
    setIsEditMode(false);
    resetForm();
    setShowModal(true);
  };

  const handleOpenEditModal = (record: QualityRecord) => {
    setIsEditMode(true);
    setSelectedRecord(record);
    setFormData({
      product_code: record.product_code,
      product_name: record.product_name,
      inspection_date: record.inspection_date,
      inspector: record.inspector,
      department: record.department,
      inspection_type: record.inspection_type,
      sample_size: record.sample_size.toString(),
      defect_count: record.defect_count.toString(),
      notes: record.notes
    });
    setShowModal(true);
  };

  const handleSave = () => {
    const sampleSize = parseInt(formData.sample_size) || 0;
    const defectCount = parseInt(formData.defect_count) || 0;
    const defectRate = sampleSize > 0 ? (defectCount / sampleSize) * 100 : 0;

    const newRecord: QualityRecord = {
      id: isEditMode && selectedRecord ? selectedRecord.id : Date.now(),
      record_number: isEditMode && selectedRecord
        ? selectedRecord.record_number
        : `QI-${new Date().getFullYear()}-${String(records.length + 1).padStart(3, '0')}`,
      product_code: formData.product_code,
      product_name: formData.product_name,
      inspection_date: formData.inspection_date,
      inspector: formData.inspector,
      department: formData.department,
      inspection_type: formData.inspection_type,
      sample_size: sampleSize,
      defect_count: defectCount,
      defect_rate: defectRate,
      characteristics: [],
      status: 'PENDING',
      notes: formData.notes
    };

    if (isEditMode && selectedRecord) {
      setRecords(records.map(r => r.id === selectedRecord.id ? { ...newRecord, characteristics: selectedRecord.characteristics } : r));
    } else {
      setRecords([newRecord, ...records]);
    }

    setShowModal(false);
    resetForm();
  };

  const handleDelete = (id: number) => {
    if (window.confirm('정말 삭제하시겠습니까?')) {
      setRecords(records.filter(r => r.id !== id));
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      PENDING: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      APPROVED: 'bg-green-100 text-green-800 border-green-300',
      REJECTED: 'bg-red-100 text-red-800 border-red-300',
    };
    const labels = {
      PENDING: '대기',
      APPROVED: '승인',
      REJECTED: '반려',
    };
    const icons = {
      PENDING: Clock,
      APPROVED: CheckCircle,
      REJECTED: XCircle,
    };
    const Icon = icons[status as keyof typeof icons];
    return (
      <Badge className={styles[status as keyof typeof styles]}>
        <Icon className="w-3 h-3 mr-1" />
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  const getTypeBadge = (type: string) => {
    const styles = {
      INCOMING: 'bg-blue-100 text-blue-800',
      PROCESS: 'bg-purple-100 text-purple-800',
      FINAL: 'bg-green-100 text-green-800',
      OUTGOING: 'bg-orange-100 text-orange-800',
    };
    const labels = {
      INCOMING: '입고',
      PROCESS: '공정',
      FINAL: '최종',
      OUTGOING: '출고',
    };
    return (
      <Badge className={styles[type as keyof typeof styles]}>
        {labels[type as keyof typeof labels]}
      </Badge>
    );
  };

  const filteredRecords = records.filter(record => {
    const matchStatus = selectedStatus === 'ALL' || record.status === selectedStatus;
    const matchType = selectedType === 'ALL' || record.inspection_type === selectedType;
    const matchSearch = searchTerm === '' ||
      record.record_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.product_code.toLowerCase().includes(searchTerm.toLowerCase());
    return matchStatus && matchType && matchSearch;
  });

  const stats = {
    total: records.length,
    pending: records.filter(r => r.status === 'PENDING').length,
    approved: records.filter(r => r.status === 'APPROVED').length,
    rejected: records.filter(r => r.status === 'REJECTED').length,
    avgDefectRate: records.length > 0
      ? (records.reduce((sum, r) => sum + r.defect_rate, 0) / records.length).toFixed(2)
      : '0.00'
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Edit className="w-8 h-8 text-green-600" />
            자체 입력 관리
          </h1>
          <p className="text-gray-600 mt-2">
            품질 검사 데이터 직접 입력 및 관리
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            내보내기
          </Button>
          <Button className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700" onClick={handleOpenAddModal}>
            <Plus className="w-4 h-4" />
            새 검사 기록
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">전체 기록</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
              </div>
              <FileText className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-yellow-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">대기</p>
                <p className="text-3xl font-bold text-yellow-600 mt-1">{stats.pending}</p>
              </div>
              <Clock className="w-12 h-12 text-yellow-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">승인</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.approved}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-red-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">반려</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{stats.rejected}</p>
              </div>
              <XCircle className="w-12 h-12 text-red-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-orange-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">평균 불량률</p>
                <p className="text-3xl font-bold text-orange-600 mt-1">{stats.avgDefectRate}%</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-orange-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">검색</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="기록 번호, 제품, 코드..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">상태</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
              >
                <option value="ALL">전체</option>
                <option value="PENDING">대기</option>
                <option value="APPROVED">승인</option>
                <option value="REJECTED">반려</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">검사 유형</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
              >
                <option value="ALL">전체</option>
                <option value="INCOMING">입고</option>
                <option value="PROCESS">공정</option>
                <option value="FINAL">최종</option>
                <option value="OUTGOING">출고</option>
              </select>
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setSearchTerm('');
                  setSelectedStatus('ALL');
                  setSelectedType('ALL');
                }}
              >
                <Filter className="w-4 h-4 mr-2" />
                필터 초기화
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Records Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            검사 기록 목록 ({filteredRecords.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left p-4 font-semibold text-gray-700">기록 번호</th>
                  <th className="text-left p-4 font-semibold text-gray-700">제품</th>
                  <th className="text-left p-4 font-semibold text-gray-700">검사일</th>
                  <th className="text-left p-4 font-semibold text-gray-700">검사자</th>
                  <th className="text-left p-4 font-semibold text-gray-700">검사 유형</th>
                  <th className="text-left p-4 font-semibold text-gray-700">샘플/불량</th>
                  <th className="text-left p-4 font-semibold text-gray-700">불량률</th>
                  <th className="text-left p-4 font-semibold text-gray-700">상태</th>
                  <th className="text-left p-4 font-semibold text-gray-700">작업</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((record) => (
                  <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="p-4 font-medium text-purple-600">{record.record_number}</td>
                    <td className="p-4">
                      <div className="font-medium">{record.product_name}</div>
                      <div className="text-sm text-gray-500">{record.product_code}</div>
                    </td>
                    <td className="p-4 text-sm">{record.inspection_date}</td>
                    <td className="p-4">
                      <div className="font-medium">{record.inspector}</div>
                      <div className="text-sm text-gray-500">{record.department}</div>
                    </td>
                    <td className="p-4">{getTypeBadge(record.inspection_type)}</td>
                    <td className="p-4">
                      <div className="text-sm">
                        <div>{record.sample_size}개 샘플</div>
                        <div className="text-red-600">{record.defect_count}개 불량</div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`font-semibold ${record.defect_rate > 5 ? 'text-red-600' : 'text-green-600'}`}>
                        {record.defect_rate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="p-4">{getStatusBadge(record.status)}</td>
                    <td className="p-4">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedRecord(record);
                            setShowDetailModal(true);
                          }}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleOpenEditModal(record)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(record.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                {isEditMode ? '검사 기록 수정' : '새 검사 기록 등록'}
              </h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowModal(false)}
              >
                ✕
              </Button>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    제품 코드 <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    value={formData.product_code}
                    onChange={(e) => setFormData({ ...formData, product_code: e.target.value })}
                    placeholder="예: PROD-001"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    제품명 <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    value={formData.product_name}
                    onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                    placeholder="제품명 입력"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    검사일 <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="date"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    value={formData.inspection_date}
                    onChange={(e) => setFormData({ ...formData, inspection_date: e.target.value })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    검사자 <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    value={formData.inspector}
                    onChange={(e) => setFormData({ ...formData, inspector: e.target.value })}
                    placeholder="검사자명"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    부서 <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    placeholder="예: 품질팀"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    검사 유형 <span className="text-red-600">*</span>
                  </label>
                  <select
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    value={formData.inspection_type}
                    onChange={(e) => setFormData({ ...formData, inspection_type: e.target.value as any })}
                  >
                    <option value="INCOMING">입고 검사</option>
                    <option value="PROCESS">공정 검사</option>
                    <option value="FINAL">최종 검사</option>
                    <option value="OUTGOING">출고 검사</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    샘플 수 <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    min="1"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    value={formData.sample_size}
                    onChange={(e) => setFormData({ ...formData, sample_size: e.target.value })}
                    placeholder="예: 50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    불량 수 <span className="text-red-600">*</span>
                  </label>
                  <input
                    type="number"
                    min="0"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    value={formData.defect_count}
                    onChange={(e) => setFormData({ ...formData, defect_count: e.target.value })}
                    placeholder="예: 2"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    비고
                  </label>
                  <textarea
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    rows={3}
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    placeholder="추가 비고 입력"
                  />
                </div>
              </div>
            </div>

            <div className="sticky bottom-0 bg-gray-50 border-t p-6 flex justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => setShowModal(false)}
              >
                취소
              </Button>
              <Button
                className="bg-purple-600 hover:bg-purple-700"
                onClick={handleSave}
              >
                {isEditMode ? '수정' : '등록'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedRecord && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">{selectedRecord.record_number}</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDetailModal(false)}
              >
                ✕
              </Button>
            </div>

            <div className="p-6 space-y-6">
              {/* Basic Info */}
              <Card>
                <CardHeader>
                  <CardTitle>기본 정보</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="text-sm font-medium text-gray-500">제품</label>
                      <p className="font-semibold">{selectedRecord.product_name}</p>
                      <p className="text-sm text-gray-600">{selectedRecord.product_code}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">검사일</label>
                      <p className="font-semibold">{selectedRecord.inspection_date}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">검사 유형</label>
                      <div>{getTypeBadge(selectedRecord.inspection_type)}</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">검사자</label>
                      <p className="font-semibold">{selectedRecord.inspector}</p>
                      <p className="text-sm text-gray-600">{selectedRecord.department}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">샘플 수</label>
                      <p className="font-semibold text-lg">{selectedRecord.sample_size}개</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">불량 수</label>
                      <p className="font-semibold text-lg text-red-600">{selectedRecord.defect_count}개</p>
                    </div>
                    <div className="md:col-span-2">
                      <label className="text-sm font-medium text-gray-500">비고</label>
                      <p className="text-gray-900">{selectedRecord.notes || '없음'}</p>
                    </div>
                    <div className="md:col-span-1">
                      <label className="text-sm font-medium text-gray-500">상태</label>
                      <div>{getStatusBadge(selectedRecord.status)}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="sticky bottom-0 bg-gray-50 border-t p-6 flex justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => setShowDetailModal(false)}
              >
                닫기
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManualInputPage;
export { ManualInputPage };

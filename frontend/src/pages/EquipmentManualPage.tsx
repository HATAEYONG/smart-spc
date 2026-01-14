import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import {
  Select,
  SelectItem,
} from '../components/ui/Select';
import {
  Plus,
  Edit,
  Trash2,
  Search,
  BookOpen,
  FileText,
  Download,
  Upload,
  Eye,
  Calendar,
  User,
  Save,
  X,
} from 'lucide-react';

interface Manual {
  id: number;
  title: string;
  equipment_id: number;
  equipment_name: string;
  category: 'OPERATION' | 'MAINTENANCE' | 'SAFETY' | 'TROUBLESHOOTING';
  version: string;
  file_url: string;
  file_size: number;
  upload_date: string;
  uploaded_by: string;
  description: string;
  tags: string[];
  view_count: number;
}

interface ManualFormData {
  title: string;
  equipment_id: string;
  equipment_name: string;
  category: 'OPERATION' | 'MAINTENANCE' | 'SAFETY' | 'TROUBLESHOOTING';
  version: string;
  file_url: string;
  file_size: string;
  upload_date: string;
  uploaded_by: string;
  description: string;
  tags: string;
}

const MOCK_MANUALS: Manual[] = [
  {
    id: 1,
    title: 'CNC 머신 A 운영 매뉴얼',
    equipment_id: 1,
    equipment_name: 'CNC 머신 A',
    category: 'OPERATION',
    version: 'v2.1',
    file_url: '/manuals/cnc-a-operation.pdf',
    file_size: 15728640,
    upload_date: '2026-01-10',
    uploaded_by: '김엔지니어',
    description: 'CNC 머신 A의 기본 운영 방법 및 주의사항',
    tags: ['운영', 'CNC', '기본'],
    view_count: 156,
  },
  {
    id: 2,
    title: '주간 정비 절차서',
    equipment_id: 1,
    equipment_name: 'CNC 머신 A',
    category: 'MAINTENANCE',
    version: 'v1.5',
    file_url: '/manuals/cnc-a-maintenance.pdf',
    file_size: 8388608,
    upload_date: '2026-01-08',
    uploaded_by: '박기술',
    description: '주간 예방 보전을 위한 표준 절차서',
    tags: ['정비', '주간', '예방'],
    view_count: 89,
  },
  {
    id: 3,
    title: '안전 작업 가이드라인',
    equipment_id: 1,
    equipment_name: 'CNC 머신 A',
    category: 'SAFETY',
    version: 'v3.0',
    file_url: '/manuals/cnc-a-safety.pdf',
    file_size: 5242880,
    upload_date: '2025-12-20',
    uploaded_by: '안전팀',
    description: '설비 작업 시 필수 안전 수칙 및 비상조치 요령',
    tags: ['안전', '비상', '작업'],
    view_count: 234,
  },
  {
    id: 4,
    title: '일반 고장 해결법',
    equipment_id: 4,
    equipment_name: '컨베이어 벨트 C-1',
    category: 'TROUBLESHOOTING',
    version: 'v1.2',
    file_url: '/manuals/conveyor-troubleshooting.pdf',
    file_size: 10485760,
    upload_date: '2026-01-05',
    uploaded_by: '이기술',
    description: '컨베이어 벨트의 흔한 고장 원인 및 해결 방법',
    tags: ['고장', '트러블슈팅', '수리'],
    view_count: 67,
  },
];

const MOCK_EQUIPMENTS = [
  { id: 1, name: 'CNC 머신 A' },
  { id: 2, name: '프레스 기계 B' },
  { id: 3, name: '로봇 팔 R-1' },
  { id: 4, name: '컨베이어 벨트 C-1' },
];

export const EquipmentManualPage: React.FC = () => {
  const [manuals, setManuals] = useState<Manual[]>(MOCK_MANUALS);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedEquipment, setSelectedEquipment] = useState('ALL');
  const [selectedManual, setSelectedManual] = useState<Manual | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [formData, setFormData] = useState<ManualFormData>({
    title: '',
    equipment_id: '',
    equipment_name: '',
    category: 'OPERATION',
    version: 'v1.0',
    file_url: '',
    file_size: '',
    upload_date: new Date().toISOString().split('T')[0],
    uploaded_by: '',
    description: '',
    tags: '',
  });

  const filteredManuals = manuals.filter(manual => {
    const matchesSearch =
      manual.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      manual.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesCategory = selectedCategory === 'ALL' || manual.category === selectedCategory;
    const matchesEquipment = selectedEquipment === 'ALL' || manual.equipment_id.toString() === selectedEquipment;

    return matchesSearch && matchesCategory && matchesEquipment;
  });

  const categories = [
    { value: 'OPERATION', label: '운영 매뉴얼', color: 'bg-blue-100 text-blue-800' },
    { value: 'MAINTENANCE', label: '정비 매뉴얼', color: 'bg-green-100 text-green-800' },
    { value: 'SAFETY', label: '안전 가이드', color: 'bg-red-100 text-red-800' },
    { value: 'TROUBLESHOOTING', label: '고장 해결', color: 'bg-yellow-100 text-yellow-800' },
  ];

  const getCategoryConfig = (category: string) => {
    return categories.find(c => c.value === category) || { label: category, color: 'bg-gray-100 text-gray-800' };
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // 신규 등록 모달 열기
  const handleOpenAddModal = () => {
    setIsEditMode(false);
    setFormData({
      title: '',
      equipment_id: '',
      equipment_name: '',
      category: 'OPERATION',
      version: 'v1.0',
      file_url: '',
      file_size: '',
      upload_date: new Date().toISOString().split('T')[0],
      uploaded_by: '',
      description: '',
      tags: '',
    });
    setIsFormModalOpen(true);
  };

  // 수정 모달 열기
  const handleOpenEditModal = (manual: Manual) => {
    setIsEditMode(true);
    setSelectedManual(manual);
    setFormData({
      title: manual.title,
      equipment_id: manual.equipment_id.toString(),
      equipment_name: manual.equipment_name,
      category: manual.category,
      version: manual.version,
      file_url: manual.file_url,
      file_size: manual.file_size.toString(),
      upload_date: manual.upload_date,
      uploaded_by: manual.uploaded_by,
      description: manual.description,
      tags: manual.tags.join(', '),
    });
    setIsFormModalOpen(true);
  };

  // 저장 처리
  const handleSave = () => {
    const equipment = MOCK_EQUIPMENTS.find(eq => eq.id.toString() === formData.equipment_id);

    const manualData: Manual = {
      id: isEditMode && selectedManual ? selectedManual.id : Date.now(),
      title: formData.title,
      equipment_id: parseInt(formData.equipment_id) || 0,
      equipment_name: equipment?.name || formData.equipment_name,
      category: formData.category,
      version: formData.version,
      file_url: formData.file_url,
      file_size: parseInt(formData.file_size) || 0,
      upload_date: formData.upload_date,
      uploaded_by: formData.uploaded_by,
      description: formData.description,
      tags: formData.tags.split(',').map(t => t.trim()).filter(t => t.length > 0),
      view_count: isEditMode && selectedManual ? selectedManual.view_count : 0,
    };

    if (isEditMode && selectedManual) {
      setManuals(manuals.map(m => (m.id === selectedManual.id ? manualData : m)));
    } else {
      setManuals([...manuals, manualData]);
    }

    setIsFormModalOpen(false);
  };

  // 삭제 처리
  const handleDelete = (id: number) => {
    if (window.confirm('정말로 이 매뉴얼을 삭제하시겠습니까?')) {
      setManuals(manuals.filter(m => m.id !== id));
    }
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">설비 매뉴얼 관리</h1>
          <p className="text-sm text-gray-500 mt-1">
            설비 운영, 정비, 안전 매뉴얼 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Upload className="w-4 h-4 mr-2" />
            일괄 업로드
          </Button>
          <Button
            className="bg-purple-600 hover:bg-purple-700"
            onClick={handleOpenAddModal}
          >
            <Plus className="w-4 h-4 mr-2" />
            매뉴얼 등록
          </Button>
        </div>
      </div>

      {/* 필터 영역 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="매뉴얼명, 태그 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory} className="w-48">
              <SelectItem value="ALL">전체 카테고리</SelectItem>
              {categories.map(cat => (
                <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
              ))}
            </Select>
            <Select value={selectedEquipment} onValueChange={setSelectedEquipment} className="w-48">
              <SelectItem value="ALL">전체 설비</SelectItem>
              {MOCK_EQUIPMENTS.map(eq => (
                <SelectItem key={eq.id} value={eq.id.toString()}>{eq.name}</SelectItem>
              ))}
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 요약 정보 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-purple-100 mb-1">총 매뉴얼 수</div>
            <div className="text-2xl font-bold">{manuals.length}개</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-blue-100 mb-1">운영 매뉴얼</div>
            <div className="text-2xl font-bold">
              {manuals.filter(m => m.category === 'OPERATION').length}개
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-green-100 mb-1">정비 매뉴얼</div>
            <div className="text-2xl font-bold">
              {manuals.filter(m => m.category === 'MAINTENANCE').length}개
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-orange-100 mb-1">총 조회 수</div>
            <div className="text-2xl font-bold">
              {manuals.reduce((sum, m) => sum + m.view_count, 0)}회
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 매뉴얼 목록 그리드 */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">매뉴얼 목록</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredManuals.map((manual) => {
            const categoryConfig = getCategoryConfig(manual.category);
            return (
              <Card
                key={manual.id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => {
                  setSelectedManual(manual);
                  setIsDetailModalOpen(true);
                }}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-base line-clamp-2">{manual.title}</CardTitle>
                      <p className="text-sm text-gray-500 mt-1">{manual.equipment_name}</p>
                    </div>
                    <FileText className="w-8 h-8 text-purple-600 flex-shrink-0" />
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 line-clamp-2 mb-3">{manual.description}</p>

                  <div className="flex flex-wrap gap-1 mb-3">
                    {manual.tags.map(tag => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                    <span className={`px-2 py-1 rounded ${categoryConfig.color}`}>
                      {categoryConfig.label}
                    </span>
                    <span>{manual.version}</span>
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t">
                    <div className="flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      <span>{manual.view_count}회 조회</span>
                    </div>
                    <span>{formatFileSize(manual.file_size)}</span>
                  </div>

                  <div className="flex items-center gap-2 mt-3 pt-3 border-t">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex-1 h-8"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenEditModal(manual);
                      }}
                    >
                      <Edit className="w-3 h-3 mr-1" />
                      수정
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex-1 h-8 text-red-600 hover:text-red-700"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(manual.id);
                      }}
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      삭제
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {filteredManuals.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>검색 결과가 없습니다</p>
          </div>
        )}
      </div>

      {/* 상세 모달 */}
      {isDetailModalOpen && selectedManual && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsDetailModalOpen(false)} />
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-xl font-semibold">매뉴얼 상세 정보</h3>
                <button
                  onClick={() => setIsDetailModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <div className="p-6">
                <div className="flex items-start gap-4 mb-4">
                  <FileText className="w-12 h-12 text-purple-600 flex-shrink-0" />
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900">{selectedManual.title}</h4>
                    <p className="text-sm text-gray-500 mt-1">{selectedManual.description}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div>
                    <label className="text-sm font-medium text-gray-500">카테고리</label>
                    <p className="text-gray-900">{getCategoryConfig(selectedManual.category).label}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">버전</label>
                    <p className="text-gray-900">{selectedManual.version}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">설비</label>
                    <p className="text-gray-900">{selectedManual.equipment_name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">파일 크기</label>
                    <p className="text-gray-900">{formatFileSize(selectedManual.file_size)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">업로드일</label>
                    <p className="text-gray-900">{selectedManual.upload_date}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">업로더</label>
                    <p className="text-gray-900">{selectedManual.uploaded_by}</p>
                  </div>
                  <div className="col-span-2">
                    <label className="text-sm font-medium text-gray-500 mb-2">태그</label>
                    <div className="flex flex-wrap gap-2">
                      {selectedManual.tags.map(tag => (
                        <Badge key={tag} variant="outline" className="text-sm">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button className="flex-1 bg-blue-600 hover:bg-blue-700">
                    <Eye className="w-4 h-4 mr-2" />
                    미리보기
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => {
                      setIsDetailModalOpen(false);
                      handleOpenEditModal(selectedManual);
                    }}
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    수정
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 등록/수정 모달 */}
      {isFormModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsFormModalOpen(false)} />
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-xl font-semibold">
                  {isEditMode ? '매뉴얼 정보 수정' : '신규 매뉴얼 등록'}
                </h3>
                <button
                  onClick={() => setIsFormModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      매뉴얼 제목 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      placeholder="예: CNC 머신 A 운영 매뉴얼"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      카테고리 <span className="text-red-500">*</span>
                    </label>
                    <Select
                      value={formData.category}
                      onValueChange={(value) => setFormData({ ...formData, category: value as any })}
                      className="w-full"
                    >
                      <SelectItem value="OPERATION">운영 매뉴얼</SelectItem>
                      <SelectItem value="MAINTENANCE">정비 매뉴얼</SelectItem>
                      <SelectItem value="SAFETY">안전 가이드</SelectItem>
                      <SelectItem value="TROUBLESHOOTING">고장 해결</SelectItem>
                    </Select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      버전 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.version}
                      onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                      placeholder="예: v1.0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      적용 설비 <span className="text-red-500">*</span>
                    </label>
                    <Select
                      value={formData.equipment_id}
                      onValueChange={(value) => {
                        const eq = MOCK_EQUIPMENTS.find(e => e.id.toString() === value);
                        setFormData({
                          ...formData,
                          equipment_id: value,
                          equipment_name: eq?.name || ''
                        });
                      }}
                      className="w-full"
                    >
                      <SelectItem value="">설비 선택</SelectItem>
                      {MOCK_EQUIPMENTS.map(eq => (
                        <SelectItem key={eq.id} value={eq.id.toString()}>{eq.name}</SelectItem>
                      ))}
                    </Select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      업로더 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.uploaded_by}
                      onChange={(e) => setFormData({ ...formData, uploaded_by: e.target.value })}
                      placeholder="예: 김엔지니어"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      설명 <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 min-h-[80px]"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="매뉴얼에 대한 간단한 설명"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      파일 URL <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.file_url}
                      onChange={(e) => setFormData({ ...formData, file_url: e.target.value })}
                      placeholder="예: /manuals/cnc-operation.pdf"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      파일 크기 (bytes) <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="number"
                      value={formData.file_size}
                      onChange={(e) => setFormData({ ...formData, file_size: e.target.value })}
                      placeholder="예: 15728640"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      업로드일 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="date"
                      value={formData.upload_date}
                      onChange={(e) => setFormData({ ...formData, upload_date: e.target.value })}
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      태그 (쉼표로 구분)
                    </label>
                    <Input
                      value={formData.tags}
                      onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                      placeholder="예: 운영, CNC, 기본"
                    />
                  </div>
                </div>

                <div className="flex gap-2 mt-6">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => setIsFormModalOpen(false)}
                  >
                    <X className="w-4 h-4 mr-2" />
                    취소
                  </Button>
                  <Button
                    className="flex-1 bg-purple-600 hover:bg-purple-700"
                    onClick={handleSave}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {isEditMode ? '저장' : '등록'}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

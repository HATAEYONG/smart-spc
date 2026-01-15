import React, { useState } from 'react';
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
  Wrench,
  AlertCircle,
  CheckCircle,
  Clock,
  FileText,
  Save,
  X,
} from 'lucide-react';

interface ToolRepairRecord {
  id: number;
  tool_id: number;
  tool_name: string;
  tool_code: string;
  repair_date: string;
  repair_description: string;
  repair_type: 'SHARPENING' | 'REPLACEMENT' | 'CALIBRATION' | 'DAMAGE_REPAIR' | 'PREVENTIVE_MAINTENANCE' | 'OTHER';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  reported_by: string;
  assigned_to: string;
  start_date: string;
  completion_date?: string;
  duration_minutes: number;
  labor_cost: number;
  parts_cost: number;
  total_cost: number;
  repair_notes: string;
  next_maintenance_date?: string;
}

interface ToolRepairFormData {
  tool_id: string;
  tool_name: string;
  tool_code: string;
  repair_date: string;
  repair_description: string;
  repair_type: 'SHARPENING' | 'REPLACEMENT' | 'CALIBRATION' | 'DAMAGE_REPAIR' | 'PREVENTIVE_MAINTENANCE' | 'OTHER';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  reported_by: string;
  assigned_to: string;
  start_date: string;
  completion_date: string;
  duration_minutes: string;
  labor_cost: string;
  parts_cost: string;
  repair_notes: string;
  next_maintenance_date: string;
}

const MOCK_TOOL_REPAIRS: ToolRepairRecord[] = [
  {
    id: 1,
    tool_id: 1,
    tool_name: '드릴 10mm HSS',
    tool_code: 'TL-001',
    repair_date: '2026-01-10',
    repair_description: '드릴 날 무뎌짐으로 인한 재연마 필요',
    repair_type: 'SHARPENING',
    severity: 'MEDIUM',
    status: 'COMPLETED',
    reported_by: '오퍼레이터1',
    assigned_to: '박기술',
    start_date: '2026-01-10T09:00:00',
    completion_date: '2026-01-10T11:30:00',
    duration_minutes: 150,
    labor_cost: 30000,
    parts_cost: 0,
    total_cost: 30000,
    repair_notes: '연마 완료, 날각 확인 정상',
    next_maintenance_date: '2026-02-10',
  },
  {
    id: 2,
    tool_id: 2,
    tool_name: '엔드밀 12mm',
    tool_code: 'TL-002',
    repair_date: '2026-01-12',
    repair_description: '엔드밀 날 파손으로 교체 필요',
    repair_type: 'REPLACEMENT',
    severity: 'HIGH',
    status: 'IN_PROGRESS',
    reported_by: '오퍼레이터2',
    assigned_to: '김기술',
    start_date: '2026-01-12T14:00:00',
    duration_minutes: 60,
    labor_cost: 20000,
    parts_cost: 85000,
    total_cost: 105000,
    repair_notes: '새 엔드밀 대기 중',
    next_maintenance_date: undefined,
  },
  {
    id: 3,
    tool_id: 4,
    tool_name: '레이저 CMM',
    tool_code: 'TL-004',
    repair_date: '2026-01-08',
    repair_description: '정기 정밀도 교정',
    repair_type: 'CALIBRATION',
    severity: 'LOW',
    status: 'COMPLETED',
    reported_by: '품질팀',
    assigned_to: '이메트로',
    start_date: '2026-01-08T10:00:00',
    completion_date: '2026-01-08T16:00:00',
    duration_minutes: 360,
    labor_cost: 150000,
    parts_cost: 0,
    total_cost: 150000,
    repair_notes: '교정 완료, 정밀도 ±0.001mm 유지',
    next_maintenance_date: '2026-07-08',
  },
];

const MOCK_TOOLS = [
  { id: 1, name: '드릴 10mm HSS', code: 'TL-001' },
  { id: 2, name: '엔드밀 12mm', code: 'TL-002' },
  { id: 3, name: '탭 M8', code: 'TL-003' },
  { id: 4, name: '레이저 CMM', code: 'TL-004' },
];

export const ToolRepairHistoryPage: React.FC = () => {
  const [repairs, setRepairs] = useState<ToolRepairRecord[]>(MOCK_TOOL_REPAIRS);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTool, setSelectedTool] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedRepair, setSelectedRepair] = useState<ToolRepairRecord | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [formData, setFormData] = useState<ToolRepairFormData>({
    tool_id: '',
    tool_name: '',
    tool_code: '',
    repair_date: new Date().toISOString().split('T')[0],
    repair_description: '',
    repair_type: 'SHARPENING',
    severity: 'MEDIUM',
    status: 'PENDING',
    reported_by: '',
    assigned_to: '',
    start_date: new Date().toISOString().slice(0, 16),
    completion_date: '',
    duration_minutes: '0',
    labor_cost: '0',
    parts_cost: '0',
    repair_notes: '',
    next_maintenance_date: '',
  });

  const filteredRepairs = repairs.filter(repair => {
    const matchesSearch =
      repair.tool_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      repair.tool_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      repair.repair_description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesTool = selectedTool === 'ALL' || repair.tool_id.toString() === selectedTool;
    const matchesStatus = selectedStatus === 'ALL' || repair.status === selectedStatus;
    const matchesSeverity = selectedSeverity === 'ALL' || repair.severity === selectedSeverity;

    return matchesSearch && matchesTool && matchesStatus && matchesSeverity;
  });

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'PENDING':
        return { label: '대기 중', color: 'bg-gray-100 text-gray-800', icon: Clock };
      case 'IN_PROGRESS':
        return { label: '진행 중', color: 'bg-blue-100 text-blue-800', icon: Wrench };
      case 'COMPLETED':
        return { label: '완료', color: 'bg-green-100 text-green-800', icon: CheckCircle };
      case 'CANCELLED':
        return { label: '취소', color: 'bg-red-100 text-red-800', icon: AlertCircle };
      default:
        return { label: status, color: 'bg-gray-100 text-gray-800', icon: Clock };
    }
  };

  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'URGENT':
        return { label: '긴급', color: 'bg-red-100 text-red-800' };
      case 'HIGH':
        return { label: '높음', color: 'bg-orange-100 text-orange-800' };
      case 'MEDIUM':
        return { label: '중간', color: 'bg-yellow-100 text-yellow-800' };
      case 'LOW':
        return { label: '낮음', color: 'bg-blue-100 text-blue-800' };
      default:
        return { label: severity, color: 'bg-gray-100 text-gray-800' };
    }
  };

  const repairTypes = [
    { value: 'SHARPENING', label: '연마' },
    { value: 'REPLACEMENT', label: '교체' },
    { value: 'CALIBRATION', label: '교정' },
    { value: 'DAMAGE_REPAIR', label: '파손 수리' },
    { value: 'PREVENTIVE_MAINTENANCE', label: '예방 정비' },
    { value: 'OTHER', label: '기타' },
  ];

  const totalCost = repairs.reduce((sum, r) => sum + r.total_cost, 0);
  const avgRepairTime = repairs.reduce((sum, r) => sum + r.duration_minutes, 0) / repairs.length;

  // 신규 등록 모달 열기
  const handleOpenAddModal = () => {
    setIsEditMode(false);
    setFormData({
      tool_id: '',
      tool_name: '',
      tool_code: '',
      repair_date: new Date().toISOString().split('T')[0],
      repair_description: '',
      repair_type: 'SHARPENING',
      severity: 'MEDIUM',
      status: 'PENDING',
      reported_by: '',
      assigned_to: '',
      start_date: new Date().toISOString().slice(0, 16),
      completion_date: '',
      duration_minutes: '0',
      labor_cost: '0',
      parts_cost: '0',
      repair_notes: '',
      next_maintenance_date: '',
    });
    setIsFormModalOpen(true);
  };

  // 수정 모달 열기
  const handleOpenEditModal = (repair: ToolRepairRecord) => {
    setIsEditMode(true);
    setSelectedRepair(repair);
    setFormData({
      tool_id: repair.tool_id.toString(),
      tool_name: repair.tool_name,
      tool_code: repair.tool_code,
      repair_date: repair.repair_date,
      repair_description: repair.repair_description,
      repair_type: repair.repair_type,
      severity: repair.severity,
      status: repair.status,
      reported_by: repair.reported_by,
      assigned_to: repair.assigned_to,
      start_date: repair.start_date,
      completion_date: repair.completion_date || '',
      duration_minutes: repair.duration_minutes.toString(),
      labor_cost: repair.labor_cost.toString(),
      parts_cost: repair.parts_cost.toString(),
      repair_notes: repair.repair_notes,
      next_maintenance_date: repair.next_maintenance_date || '',
    });
    setIsFormModalOpen(true);
  };

  // 저장 처리
  const handleSave = () => {
    const tool = MOCK_TOOLS.find(t => t.id.toString() === formData.tool_id);

    const repairData: ToolRepairRecord = {
      id: isEditMode && selectedRepair ? selectedRepair.id : Date.now(),
      tool_id: parseInt(formData.tool_id) || 0,
      tool_name: tool?.name || formData.tool_name,
      tool_code: tool?.code || formData.tool_code,
      repair_date: formData.repair_date,
      repair_description: formData.repair_description,
      repair_type: formData.repair_type,
      severity: formData.severity,
      status: formData.status,
      reported_by: formData.reported_by,
      assigned_to: formData.assigned_to,
      start_date: formData.start_date,
      completion_date: formData.completion_date || undefined,
      duration_minutes: parseInt(formData.duration_minutes) || 0,
      labor_cost: parseInt(formData.labor_cost) || 0,
      parts_cost: parseInt(formData.parts_cost) || 0,
      total_cost: (parseInt(formData.labor_cost) || 0) + (parseInt(formData.parts_cost) || 0),
      repair_notes: formData.repair_notes,
      next_maintenance_date: formData.next_maintenance_date || undefined,
    };

    if (isEditMode && selectedRepair) {
      setRepairs(repairs.map(r => (r.id === selectedRepair.id ? repairData : r)));
    } else {
      setRepairs([...repairs, repairData]);
    }

    setIsFormModalOpen(false);
  };

  // 삭제 처리
  const handleDelete = (id: number) => {
    if (window.confirm('정말로 이 수리 기록을 삭제하시겠습니까?')) {
      setRepairs(repairs.filter(r => r.id !== id));
    }
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">치공구 수리 이력</h1>
          <p className="text-sm text-gray-500 mt-1">
            치공구 정비 및 수리 기록 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileText className="w-4 h-4 mr-2" />
            수리 보고서
          </Button>
          <Button
            className="bg-purple-600 hover:bg-purple-700"
            onClick={handleOpenAddModal}
          >
            <Plus className="w-4 h-4 mr-2" />
            수리 기록 등록
          </Button>
        </div>
      </div>

      {/* 필터 영역 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="치공구명, 내용 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedTool} onValueChange={setSelectedTool} className="w-48">
              <SelectItem value="ALL">전체 치공구</SelectItem>
              {MOCK_TOOLS.map(tool => (
                <SelectItem key={tool.id} value={tool.id.toString()}>{tool.name}</SelectItem>
              ))}
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus} className="w-40">
              <SelectItem value="ALL">전체 상태</SelectItem>
              <SelectItem value="PENDING">대기 중</SelectItem>
              <SelectItem value="IN_PROGRESS">진행 중</SelectItem>
              <SelectItem value="COMPLETED">완료</SelectItem>
              <SelectItem value="CANCELLED">취소</SelectItem>
            </Select>
            <Select value={selectedSeverity} onValueChange={setSelectedSeverity} className="w-40">
              <SelectItem value="ALL">전체 중요도</SelectItem>
              <SelectItem value="URGENT">긴급</SelectItem>
              <SelectItem value="HIGH">높음</SelectItem>
              <SelectItem value="MEDIUM">중간</SelectItem>
              <SelectItem value="LOW">낮음</SelectItem>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 요약 정보 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-purple-100 mb-1">총 수리 건수</div>
            <div className="text-2xl font-bold">{repairs.length}건</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-orange-100 mb-1">총 수리 비용</div>
            <div className="text-2xl font-bold">₩{(totalCost / 10000).toFixed(1)}만</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-blue-100 mb-1">평균 수리 시간</div>
            <div className="text-2xl font-bold">{Math.round(avgRepairTime)}분</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-green-100 mb-1">완료 건수</div>
            <div className="text-2xl font-bold">
              {repairs.filter(r => r.status === 'COMPLETED').length}건
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 진행 중인 수리 건 알림 */}
      {repairs.filter(r => r.status === 'IN_PROGRESS').length > 0 && (
        <Card className="border-l-4 border-blue-500 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-3">
              <Wrench className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-blue-900">진행 중인 수리</h3>
              <Badge className="bg-blue-100 text-blue-800">
                {repairs.filter(r => r.status === 'IN_PROGRESS').length}건
              </Badge>
            </div>
            <div className="space-y-2">
              {repairs.filter(r => r.status === 'IN_PROGRESS').map(repair => (
                <div key={repair.id} className="bg-white p-3 rounded-lg border border-blue-200">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{repair.tool_name}</div>
                      <div className="text-sm text-gray-600">{repair.repair_description}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-blue-600">{repair.assigned_to}</div>
                      <div className="text-xs text-gray-500">{Math.round(repair.duration_minutes)}분 경과</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 수리 이력 목록 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wrench className="w-5 h-5 text-purple-600" />
            수리 이력 목록
            <Badge variant="outline" className="ml-2">
              {filteredRepairs.length}건
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">치공구</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">수리 내용</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">유형</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">중요도</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">상태</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">담당자</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">비용</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">관리</th>
                </tr>
              </thead>
              <tbody>
                {filteredRepairs.map((repair) => {
                  const statusConfig = getStatusConfig(repair.status);
                  const severityConfig = getSeverityConfig(repair.severity);
                  const StatusIcon = statusConfig.icon;
                  return (
                    <tr
                      key={repair.id}
                      className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedRepair(repair);
                        setIsDetailModalOpen(true);
                      }}
                    >
                      <td className="py-3 px-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{repair.tool_name}</div>
                          <div className="text-xs text-gray-500">{repair.tool_code}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-sm text-gray-700 max-w-xs truncate">{repair.repair_description}</div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {repairTypes.find(t => t.value === repair.repair_type)?.label || repair.repair_type}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${severityConfig.color}`}>
                          {severityConfig.label}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${statusConfig.color}`}>
                          <StatusIcon className="w-3 h-3" />
                          {statusConfig.label}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{repair.assigned_to}</td>
                      <td className="py-3 px-4 text-sm font-semibold text-gray-900">
                        ₩{repair.total_cost.toLocaleString()}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOpenEditModal(repair);
                            }}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(repair.id);
                            }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {filteredRepairs.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Wrench className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>검색 결과가 없습니다</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 상세 모달 */}
      {isDetailModalOpen && selectedRepair && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsDetailModalOpen(false)} />
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b sticky top-0 bg-white">
                <h3 className="text-xl font-semibold">수리 기록 상세</h3>
                <button
                  onClick={() => setIsDetailModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <div className="p-6 space-y-6">
                {/* 기본 정보 */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">기본 정보</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-500">치공구</label>
                      <p className="text-gray-900">{selectedRepair.tool_name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">수리 일자</label>
                      <p className="text-gray-900">{selectedRepair.repair_date}</p>
                    </div>
                    <div className="col-span-2">
                      <label className="text-sm font-medium text-gray-500">수리 내용</label>
                      <p className="text-gray-900">{selectedRepair.repair_description}</p>
                    </div>
                  </div>
                </div>

                {/* 진행 상황 */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">진행 상황</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-500">상태</label>
                      <p className="text-gray-900">{getStatusConfig(selectedRepair.status).label}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">중요도</label>
                      <p className="text-gray-900">{getSeverityConfig(selectedRepair.severity).label}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">담당자</label>
                      <p className="text-gray-900">{selectedRepair.assigned_to}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">수리 시간</label>
                      <p className="text-gray-900">{Math.round(selectedRepair.duration_minutes / 60)}시간 {selectedRepair.duration_minutes % 60}분</p>
                    </div>
                  </div>
                </div>

                {/* 비용 정보 */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">비용 정보</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <div className="text-xs text-gray-500">인건비</div>
                        <div className="text-lg font-semibold text-gray-900">₩{selectedRepair.labor_cost.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">부품비</div>
                        <div className="text-lg font-semibold text-gray-900">₩{selectedRepair.parts_cost.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">총비용</div>
                        <div className="text-lg font-bold text-purple-600">₩{selectedRepair.total_cost.toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 비고 */}
                {selectedRepair.repair_notes && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">비고</h4>
                    <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">{selectedRepair.repair_notes}</p>
                  </div>
                )}

                {/* 다음 정비일 */}
                {selectedRepair.next_maintenance_date && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">다음 정비 예정일</h4>
                    <p className="text-gray-900">{selectedRepair.next_maintenance_date}</p>
                  </div>
                )}

                {/* 관리 버튼 */}
                <div className="flex gap-2 pt-4 border-t">
                  <Button
                    variant="outline"
                    className="flex-1 text-red-600 border-red-600 hover:bg-red-50"
                    onClick={() => {
                      setIsDetailModalOpen(false);
                      handleDelete(selectedRepair.id);
                    }}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    삭제
                  </Button>
                  <Button
                    className="flex-1 bg-purple-600 hover:bg-purple-700"
                    onClick={() => {
                      setIsDetailModalOpen(false);
                      handleOpenEditModal(selectedRepair);
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
            <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-xl font-semibold">
                  {isEditMode ? '수리 기록 수정' : '신규 수리 기록 등록'}
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
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      치공구 <span className="text-red-500">*</span>
                    </label>
                    <Select
                      value={formData.tool_id}
                      onValueChange={(value) => {
                        const tool = MOCK_TOOLS.find(t => t.id.toString() === value);
                        setFormData({
                          ...formData,
                          tool_id: value,
                          tool_name: tool?.name || '',
                          tool_code: tool?.code || ''
                        });
                      }}
                      className="w-full"
                    >
                      <SelectItem value="">치공구 선택</SelectItem>
                      {MOCK_TOOLS.map(tool => (
                        <SelectItem key={tool.id} value={tool.id.toString()}>{tool.name}</SelectItem>
                      ))}
                    </Select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      수리 일자 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="date"
                      value={formData.repair_date}
                      onChange={(e) => setFormData({ ...formData, repair_date: e.target.value })}
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      수리 내용 <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 min-h-[80px]"
                      value={formData.repair_description}
                      onChange={(e) => setFormData({ ...formData, repair_description: e.target.value })}
                      placeholder="수리 필요 사항을 상세히 기술"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      수리 유형 <span className="text-red-500">*</span>
                    </label>
                    <Select
                      value={formData.repair_type}
                      onValueChange={(value) => setFormData({ ...formData, repair_type: value as any })}
                      className="w-full"
                    >
                      {repairTypes.map(type => (
                        <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                      ))}
                    </Select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      중요도 <span className="text-red-500">*</span>
                    </label>
                    <Select
                      value={formData.severity}
                      onValueChange={(value) => setFormData({ ...formData, severity: value as any })}
                      className="w-full"
                    >
                      <SelectItem value="LOW">낮음</SelectItem>
                      <SelectItem value="MEDIUM">중간</SelectItem>
                      <SelectItem value="HIGH">높음</SelectItem>
                      <SelectItem value="URGENT">긴급</SelectItem>
                    </Select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      상태 <span className="text-red-500">*</span>
                    </label>
                    <Select
                      value={formData.status}
                      onValueChange={(value) => setFormData({ ...formData, status: value as any })}
                      className="w-full"
                    >
                      <SelectItem value="PENDING">대기 중</SelectItem>
                      <SelectItem value="IN_PROGRESS">진행 중</SelectItem>
                      <SelectItem value="COMPLETED">완료</SelectItem>
                      <SelectItem value="CANCELLED">취소</SelectItem>
                    </Select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      보고자 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.reported_by}
                      onChange={(e) => setFormData({ ...formData, reported_by: e.target.value })}
                      placeholder="예: 오퍼레이터1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      담당자 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.assigned_to}
                      onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                      placeholder="예: 박기술"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      시작 일시 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="datetime-local"
                      value={formData.start_date}
                      onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      완료 일시
                    </label>
                    <Input
                      type="datetime-local"
                      value={formData.completion_date}
                      onChange={(e) => setFormData({ ...formData, completion_date: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      소요 시간 (분) <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="number"
                      value={formData.duration_minutes}
                      onChange={(e) => setFormData({ ...formData, duration_minutes: e.target.value })}
                      placeholder="예: 60"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      인건비 (원) <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="number"
                      value={formData.labor_cost}
                      onChange={(e) => setFormData({ ...formData, labor_cost: e.target.value })}
                      placeholder="예: 30000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      부품비 (원) <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="number"
                      value={formData.parts_cost}
                      onChange={(e) => setFormData({ ...formData, parts_cost: e.target.value })}
                      placeholder="예: 50000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      다음 정비 예정일
                    </label>
                    <Input
                      type="date"
                      value={formData.next_maintenance_date}
                      onChange={(e) => setFormData({ ...formData, next_maintenance_date: e.target.value })}
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      비고
                    </label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 min-h-[80px]"
                      value={formData.repair_notes}
                      onChange={(e) => setFormData({ ...formData, repair_notes: e.target.value })}
                      placeholder="추가 정보 입력"
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

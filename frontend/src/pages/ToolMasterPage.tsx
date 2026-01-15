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
  Package,
  Wrench,
  CheckCircle,
  Clock,
  AlertTriangle,
  Save,
  X,
} from 'lucide-react';

interface Tool {
  id: number;
  code: string;
  name: string;
  type: string;
  specification: string;
  manufacturer: string;
  model: string;
  serial_number: string;
  location: string;
  purchase_date: string;
  status: 'AVAILABLE' | 'IN_USE' | 'MAINTENANCE' | 'DAMAGED' | 'RETIRED';
  useful_life: number;
  current_usage: number;
  usage_unit: string;
  calibration_date: string;
  next_calibration_date: string;
  cost: number;
  supplier: string;
}

interface ToolFormData {
  code: string;
  name: string;
  type: string;
  specification: string;
  manufacturer: string;
  model: string;
  serial_number: string;
  location: string;
  purchase_date: string;
  status: 'AVAILABLE' | 'IN_USE' | 'MAINTENANCE' | 'DAMAGED' | 'RETIRED';
  useful_life: string;
  current_usage: string;
  usage_unit: string;
  calibration_date: string;
  next_calibration_date: string;
  cost: string;
  supplier: string;
}

const MOCK_TOOLS: Tool[] = [
  {
    id: 1,
    code: 'TL-001',
    name: '드릴 10mm HSS',
    type: '드릴',
    specification: '직경 10mm, 길이 100mm',
    manufacturer: 'YG-1',
    model: 'HSS-D10',
    serial_number: 'SN-TL-2024-001',
    location: '공구실 A-1',
    purchase_date: '2024-01-15',
    status: 'AVAILABLE',
    useful_life: 100,
    current_usage: 45,
    usage_unit: '시간',
    calibration_date: '2024-01-15',
    next_calibration_date: '2024-07-15',
    cost: 25000,
    supplier: 'YG-1 Tool',
  },
  {
    id: 2,
    code: 'TL-002',
    name: '엔드밀 12mm',
    type: '엔드밀',
    specification: '직경 12mm, 날수 4',
    manufacturer: 'OSG',
    model: 'EM-12-4F',
    serial_number: 'SN-TL-2024-002',
    location: '공구실 A-2',
    purchase_date: '2024-02-20',
    status: 'IN_USE',
    useful_life: 80,
    current_usage: 35,
    usage_unit: '시간',
    calibration_date: '2024-02-20',
    next_calibration_date: '2024-08-20',
    cost: 85000,
    supplier: 'OSG Korea',
  },
  {
    id: 3,
    code: 'TL-003',
    name: '탭 M8',
    type: '탭',
    specification: 'M8 x 1.25',
    manufacturer: 'Guhring',
    model: 'TAP-M8',
    serial_number: 'SN-TL-2024-003',
    location: '공구실 B-1',
    purchase_date: '2024-03-10',
    status: 'MAINTENANCE',
    useful_life: 50,
    current_usage: 48,
    usage_unit: '회',
    calibration_date: '2024-03-10',
    next_calibration_date: '2024-09-10',
    cost: 45000,
    supplier: 'Guhring Korea',
  },
  {
    id: 4,
    code: 'TL-004',
    name: '레이저 CMM',
    type: '측정기',
    specification: '정밀도 ±0.001mm',
    manufacturer: 'Hexagon',
    model: 'CMM-L500',
    serial_number: 'SN-TL-2024-004',
    location: '측정실 1',
    purchase_date: '2023-06-05',
    status: 'AVAILABLE',
    useful_life: 1000,
    current_usage: 250,
    usage_unit: '시간',
    calibration_date: '2024-01-05',
    next_calibration_date: '2024-07-05',
    cost: 150000000,
    supplier: 'Hexagon Metrology',
  },
];

export const ToolMasterPage: React.FC = () => {
  const [tools, setTools] = useState<Tool[]>(MOCK_TOOLS);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [formData, setFormData] = useState<ToolFormData>({
    code: '',
    name: '',
    type: '',
    specification: '',
    manufacturer: '',
    model: '',
    serial_number: '',
    location: '',
    purchase_date: '',
    status: 'AVAILABLE',
    useful_life: '100',
    current_usage: '0',
    usage_unit: '시간',
    calibration_date: '',
    next_calibration_date: '',
    cost: '',
    supplier: '',
  });

  const filteredTools = tools.filter(tool => {
    const matchesSearch =
      tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tool.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tool.type.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = selectedType === 'ALL' || tool.type === selectedType;
    const matchesStatus = selectedStatus === 'ALL' || tool.status === selectedStatus;

    return matchesSearch && matchesType && matchesStatus;
  });

  const toolTypes = Array.from(new Set(tools.map(t => t.type)));

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return {
          label: '사용 가능',
          color: 'bg-green-100 text-green-800',
          icon: CheckCircle,
        };
      case 'IN_USE':
        return {
          label: '사용 중',
          color: 'bg-blue-100 text-blue-800',
          icon: Package,
        };
      case 'MAINTENANCE':
        return {
          label: '정비 중',
          color: 'bg-yellow-100 text-yellow-800',
          icon: Wrench,
        };
      case 'DAMAGED':
        return {
          label: '파손',
          color: 'bg-red-100 text-red-800',
          icon: AlertTriangle,
        };
      case 'RETIRED':
        return {
          label: '폐기',
          color: 'bg-gray-100 text-gray-800',
          icon: Clock,
        };
      default:
        return {
          label: status,
          color: 'bg-gray-100 text-gray-800',
          icon: Clock,
        };
    }
  };

  const getUsagePercentage = (tool: Tool) => {
    return (tool.current_usage / tool.useful_life) * 100;
  };

  const getUsageStatus = (percentage: number) => {
    if (percentage >= 90) return { label: '교체 필요', color: 'bg-red-500' };
    if (percentage >= 70) return { label: '주의', color: 'bg-yellow-500' };
    return { label: '정상', color: 'bg-green-500' };
  };

  // 신규 등록 모달 열기
  const handleOpenAddModal = () => {
    setIsEditMode(false);
    setFormData({
      code: '',
      name: '',
      type: '',
      specification: '',
      manufacturer: '',
      model: '',
      serial_number: '',
      location: '',
      purchase_date: new Date().toISOString().split('T')[0],
      status: 'AVAILABLE',
      useful_life: '100',
      current_usage: '0',
      usage_unit: '시간',
      calibration_date: new Date().toISOString().split('T')[0],
      next_calibration_date: '',
      cost: '',
      supplier: '',
    });
    setIsFormModalOpen(true);
  };

  // 수정 모달 열기
  const handleOpenEditModal = (tool: Tool) => {
    setIsEditMode(true);
    setSelectedTool(tool);
    setFormData({
      code: tool.code,
      name: tool.name,
      type: tool.type,
      specification: tool.specification,
      manufacturer: tool.manufacturer,
      model: tool.model,
      serial_number: tool.serial_number,
      location: tool.location,
      purchase_date: tool.purchase_date,
      status: tool.status,
      useful_life: tool.useful_life.toString(),
      current_usage: tool.current_usage.toString(),
      usage_unit: tool.usage_unit,
      calibration_date: tool.calibration_date,
      next_calibration_date: tool.next_calibration_date,
      cost: tool.cost.toString(),
      supplier: tool.supplier,
    });
    setIsFormModalOpen(true);
  };

  // 저장 처리
  const handleSave = () => {
    const toolData: Tool = {
      id: isEditMode && selectedTool ? selectedTool.id : Date.now(),
      code: formData.code,
      name: formData.name,
      type: formData.type,
      specification: formData.specification,
      manufacturer: formData.manufacturer,
      model: formData.model,
      serial_number: formData.serial_number,
      location: formData.location,
      purchase_date: formData.purchase_date,
      status: formData.status,
      useful_life: parseInt(formData.useful_life) || 100,
      current_usage: parseInt(formData.current_usage) || 0,
      usage_unit: formData.usage_unit,
      calibration_date: formData.calibration_date,
      next_calibration_date: formData.next_calibration_date,
      cost: parseInt(formData.cost) || 0,
      supplier: formData.supplier,
    };

    if (isEditMode && selectedTool) {
      setTools(tools.map(t => (t.id === selectedTool.id ? toolData : t)));
    } else {
      setTools([...tools, toolData]);
    }

    setIsFormModalOpen(false);
  };

  // 삭제 처리
  const handleDelete = (id: number) => {
    if (window.confirm('정말로 이 치공구를 삭제하시겠습니까?')) {
      setTools(tools.filter(t => t.id !== id));
    }
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">치공구 마스터 관리</h1>
          <p className="text-sm text-gray-500 mt-1">
            치공구 기본 정보 및 수명 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Package className="w-4 h-4 mr-2" />
            재고 실사
          </Button>
          <Button
            className="bg-purple-600 hover:bg-purple-700"
            onClick={handleOpenAddModal}
          >
            <Plus className="w-4 h-4 mr-2" />
            신규 치공구 등록
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
                  placeholder="치공구명, 코드, 유형 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedType} onValueChange={setSelectedType} className="w-48">
              <SelectItem value="ALL">전체 유형</SelectItem>
              {toolTypes.map(type => (
                <SelectItem key={type} value={type}>{type}</SelectItem>
              ))}
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus} className="w-40">
              <SelectItem value="ALL">전체 상태</SelectItem>
              <SelectItem value="AVAILABLE">사용 가능</SelectItem>
              <SelectItem value="IN_USE">사용 중</SelectItem>
              <SelectItem value="MAINTENANCE">정비 중</SelectItem>
              <SelectItem value="DAMAGED">파손</SelectItem>
              <SelectItem value="RETIRED">폐기</SelectItem>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 요약 정보 */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-purple-100 mb-1">총 치공구 수</div>
            <div className="text-2xl font-bold">{tools.length}개</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <CheckCircle className="w-4 h-4" />
              <div className="text-sm font-medium text-green-100">사용 가능</div>
            </div>
            <div className="text-2xl font-bold">
              {tools.filter(t => t.status === 'AVAILABLE').length}개
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <Package className="w-4 h-4" />
              <div className="text-sm font-medium text-blue-100">사용 중</div>
            </div>
            <div className="text-2xl font-bold">
              {tools.filter(t => t.status === 'IN_USE').length}개
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <Wrench className="w-4 h-4" />
              <div className="text-sm font-medium text-yellow-100">정비 중</div>
            </div>
            <div className="text-2xl font-bold">
              {tools.filter(t => t.status === 'MAINTENANCE').length}개
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <AlertTriangle className="w-4 h-4" />
              <div className="text-sm font-medium text-red-100">수명 임박</div>
            </div>
            <div className="text-2xl font-bold">
              {tools.filter(t => getUsagePercentage(t) >= 70).length}개
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 치공구 목록 테이블 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="w-5 h-5 text-purple-600" />
            치공구 목록
            <Badge variant="outline" className="ml-2">
              {filteredTools.length}개
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">코드</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">치공구명</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">유형</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">규격</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">위치</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">수명</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">상태</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">관리</th>
                </tr>
              </thead>
              <tbody>
                {filteredTools.map((tool) => {
                  const statusConfig = getStatusConfig(tool.status);
                  const StatusIcon = statusConfig.icon;
                  const usagePercent = getUsagePercentage(tool);
                  const usageStatus = getUsageStatus(usagePercent);
                  return (
                    <tr
                      key={tool.id}
                      className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedTool(tool);
                        setIsDetailModalOpen(true);
                      }}
                    >
                      <td className="py-3 px-4 text-sm font-mono text-gray-700">
                        {tool.code}
                      </td>
                      <td className="py-3 px-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{tool.name}</div>
                          <div className="text-xs text-gray-500">{tool.manufacturer}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="text-xs">
                          {tool.type}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {tool.specification}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {tool.location}
                      </td>
                      <td className="py-3 px-4">
                        <div className="w-full">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-600">{tool.current_usage}/{tool.useful_life} {tool.usage_unit}</span>
                            <span className={`px-1.5 py-0.5 rounded text-white text-xs ${usageStatus.color}`}>
                              {usageStatus.label}
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${usageStatus.color}`}
                              style={{ width: `${Math.min(usagePercent, 100)}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${statusConfig.color}`}>
                          <StatusIcon className="w-3 h-3" />
                          {statusConfig.label}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOpenEditModal(tool);
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
                              handleDelete(tool.id);
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

          {filteredTools.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Package className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>검색 결과가 없습니다</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 상세 모달 */}
      {isDetailModalOpen && selectedTool && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsDetailModalOpen(false)} />
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-xl font-semibold">치공구 상세 정보</h3>
                <button
                  onClick={() => setIsDetailModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">치공구 코드</label>
                    <p className="text-lg font-semibold text-gray-900 font-mono">{selectedTool.code}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">치공구명</label>
                    <p className="text-lg font-semibold text-gray-900">{selectedTool.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">유형</label>
                    <p className="text-gray-900">{selectedTool.type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">규격</label>
                    <p className="text-gray-900">{selectedTool.specification}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">제조사</label>
                    <p className="text-gray-900">{selectedTool.manufacturer}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">모델</label>
                    <p className="text-gray-900">{selectedTool.model}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">시리얼 번호</label>
                    <p className="text-gray-900 font-mono">{selectedTool.serial_number}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">위치</label>
                    <p className="text-gray-900">{selectedTool.location}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">구입일</label>
                    <p className="text-gray-900">{selectedTool.purchase_date}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">구입 비용</label>
                    <p className="text-gray-900">₩{selectedTool.cost.toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">공급사</label>
                    <p className="text-gray-900">{selectedTool.supplier}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">상태</label>
                    <p className="text-gray-900">{getStatusConfig(selectedTool.status).label}</p>
                  </div>
                  <div className="col-span-2">
                    <label className="text-sm font-medium text-gray-500 mb-2">수명 현황</label>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600">
                          {selectedTool.current_usage} / {selectedTool.useful_life} {selectedTool.usage_unit}
                        </span>
                        <span className="text-sm font-semibold">
                          {getUsagePercentage(selectedTool).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full ${getUsageStatus(getUsagePercentage(selectedTool)).color}`}
                          style={{ width: `${Math.min(getUsagePercentage(selectedTool), 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">교정일</label>
                    <p className="text-gray-900">{selectedTool.calibration_date}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">다음 교정일</label>
                    <p className="text-gray-900">{selectedTool.next_calibration_date}</p>
                  </div>
                </div>

                <div className="flex gap-2 mt-6">
                  <Button
                    variant="outline"
                    className="flex-1 text-red-600 border-red-600 hover:bg-red-50"
                    onClick={() => {
                      setIsDetailModalOpen(false);
                      handleDelete(selectedTool.id);
                    }}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    삭제
                  </Button>
                  <Button
                    className="flex-1 bg-purple-600 hover:bg-purple-700"
                    onClick={() => {
                      setIsDetailModalOpen(false);
                      handleOpenEditModal(selectedTool);
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
                  {isEditMode ? '치공구 정보 수정' : '신규 치공구 등록'}
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
                      치공구 코드 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.code}
                      onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                      placeholder="예: TL-001"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      치공구명 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="예: 드릴 10mm HSS"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      유형 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      placeholder="예: 드릴"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      규격 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.specification}
                      onChange={(e) => setFormData({ ...formData, specification: e.target.value })}
                      placeholder="예: 직경 10mm, 길이 100mm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      제조사 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.manufacturer}
                      onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                      placeholder="예: YG-1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      모델 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.model}
                      onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                      placeholder="예: HSS-D10"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      시리얼 번호 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.serial_number}
                      onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                      placeholder="예: SN-TL-2024-001"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      위치 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      placeholder="예: 공구실 A-1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      구입일 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="date"
                      value={formData.purchase_date}
                      onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      구입 비용 (원) <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="number"
                      value={formData.cost}
                      onChange={(e) => setFormData({ ...formData, cost: e.target.value })}
                      placeholder="예: 25000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      공급사 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.supplier}
                      onChange={(e) => setFormData({ ...formData, supplier: e.target.value })}
                      placeholder="예: YG-1 Tool"
                    />
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
                      <SelectItem value="AVAILABLE">사용 가능</SelectItem>
                      <SelectItem value="IN_USE">사용 중</SelectItem>
                      <SelectItem value="MAINTENANCE">정비 중</SelectItem>
                      <SelectItem value="DAMAGED">파손</SelectItem>
                      <SelectItem value="RETIRED">폐기</SelectItem>
                    </Select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      수명 (사용 가능량) <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="number"
                      value={formData.useful_life}
                      onChange={(e) => setFormData({ ...formData, useful_life: e.target.value })}
                      placeholder="예: 100"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      현재 사용량 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="number"
                      value={formData.current_usage}
                      onChange={(e) => setFormData({ ...formData, current_usage: e.target.value })}
                      placeholder="예: 0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      사용 단위 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      value={formData.usage_unit}
                      onChange={(e) => setFormData({ ...formData, usage_unit: e.target.value })}
                      placeholder="예: 시간"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      교정일 <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="date"
                      value={formData.calibration_date}
                      onChange={(e) => setFormData({ ...formData, calibration_date: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      다음 교정일
                    </label>
                    <Input
                      type="date"
                      value={formData.next_calibration_date}
                      onChange={(e) => setFormData({ ...formData, next_calibration_date: e.target.value })}
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

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
  Search,
  Filter,
  Wrench,
  AlertCircle,
  CheckCircle,
  Clock,
  User,
  Calendar,
  DollarSign,
  FileText,
} from 'lucide-react';

interface RepairRecord {
  id: number;
  equipment_id: number;
  equipment_name: string;
  equipment_code: string;
  failure_date: string;
  failure_description: string;
  failure_type: 'MECHANICAL' | 'ELECTRICAL' | 'HYDRAULIC' | 'PNEUMATIC' | 'SOFTWARE' | 'OTHER';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CLOSED';
  reported_by: string;
  assigned_to: string;
  start_date: string;
  completion_date?: string;
  duration_minutes: number;
  parts_used: string[];
  labor_cost: number;
  parts_cost: number;
  total_cost: number;
  root_cause: string;
  corrective_action: string;
  preventive_action: string;
  notes: string;
}

const MOCK_REPAIRS: RepairRecord[] = [
  {
    id: 1,
    equipment_id: 1,
    equipment_name: 'CNC 머신 A',
    equipment_code: 'EQ-001',
    failure_date: '2026-01-12',
    failure_description: '스핀들 모터 과열로 인한 정지',
    failure_type: 'ELECTRICAL',
    severity: 'HIGH',
    status: 'COMPLETED',
    reported_by: '오퍼레이터1',
    assigned_to: '김기술',
    start_date: '2026-01-12T09:00:00',
    completion_date: '2026-01-12T16:30:00',
    duration_minutes: 450,
    parts_used: ['모터 어셈블리', '온도 센서'],
    labor_cost: 120000,
    parts_cost: 850000,
    total_cost: 970000,
    root_cause: '모터 내부 베어링 마모로 인한 과열',
    corrective_action: '모터 어셈블리 교체 및 냉각 시스템 점검',
    preventive_action: '정기적인 모터 온도 모니터링 및 베어링 윤활 주기 확대',
    notes: '정상 운영 확인 완료',
  },
  {
    id: 2,
    equipment_id: 4,
    equipment_name: '컨베이어 벨트 C-1',
    equipment_code: 'EQ-004',
    failure_date: '2026-01-13',
    failure_description: '벨트 파단으로 인한 컨베이어 멈춤',
    failure_type: 'MECHANICAL',
    severity: 'CRITICAL',
    status: 'IN_PROGRESS',
    reported_by: '오퍼레이터2',
    assigned_to: '이기술',
    start_date: '2026-01-13T08:00:00',
    duration_minutes: 180,
    parts_used: ['교체 벨트'],
    labor_cost: 80000,
    parts_cost: 150000,
    total_cost: 230000,
    root_cause: '벨트 노후화로 인한 강도 저하',
    corrective_action: '벨트 교체 및 텐션롤러 정렬 조정',
    preventive_action: '벨트 수명 주기에 맞춘 예방 교체 계획 수립',
    notes: '부품 대기 중으로 완료 예정: 2026-01-14',
  },
  {
    id: 3,
    equipment_id: 2,
    equipment_name: '프레스 기계 B',
    equipment_code: 'EQ-002',
    failure_date: '2026-01-10',
    failure_description: '유압 시스템 압력 강하',
    failure_type: 'HYDRAULIC',
    severity: 'MEDIUM',
    status: 'COMPLETED',
    reported_by: '오퍼레이터3',
    assigned_to: '박기술',
    start_date: '2026-01-10T10:00:00',
    completion_date: '2026-01-10T14:00:00',
    duration_minutes: 240,
    parts_used: ['오일 실', '유압 호스'],
    labor_cost: 95000,
    parts_cost: 320000,
    total_cost: 415000,
    root_cause: '유압 호스 파손으로 인한 오일 누유',
    corrective_action: '호스 교체 및 오일 보충',
    preventive_action: '호스 상태 정기 점검',
    notes: '정상 복귀',
  },
];

export const EquipmentRepairHistoryPage: React.FC = () => {
  const [repairs, setRepairs] = useState<RepairRecord[]>(MOCK_REPAIRS);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEquipment, setSelectedEquipment] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedRepair, setSelectedRepair] = useState<RepairRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredRepairs = repairs.filter(repair => {
    const matchesSearch =
      repair.equipment_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      repair.equipment_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      repair.failure_description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesEquipment = selectedEquipment === 'ALL' || repair.equipment_id.toString() === selectedEquipment;
    const matchesStatus = selectedStatus === 'ALL' || repair.status === selectedStatus;
    const matchesSeverity = selectedSeverity === 'ALL' || repair.severity === selectedSeverity;

    return matchesSearch && matchesEquipment && matchesStatus && matchesSeverity;
  });

  const equipments = Array.from(new Set(repairs.map(r => ({ id: r.equipment_id, name: r.equipment_name, code: r.equipment_code }))));

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'PENDING':
        return { label: '대기 중', color: 'bg-gray-100 text-gray-800', icon: Clock };
      case 'IN_PROGRESS':
        return { label: '진행 중', color: 'bg-blue-100 text-blue-800', icon: Wrench };
      case 'COMPLETED':
        return { label: '완료', color: 'bg-green-100 text-green-800', icon: CheckCircle };
      case 'CLOSED':
        return { label: '종료', color: 'bg-purple-100 text-purple-800', icon: CheckCircle };
      default:
        return { label: status, color: 'bg-gray-100 text-gray-800', icon: Clock };
    }
  };

  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
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

  const failureTypes = [
    { value: 'MECHANICAL', label: '기계적' },
    { value: 'ELECTRICAL', label: '전기적' },
    { value: 'HYDRAULIC', label: '유압' },
    { value: 'PNEUMATIC', label: '공압' },
    { value: 'SOFTWARE', label: '소프트웨어' },
    { value: 'OTHER', label: '기타' },
  ];

  const totalCost = repairs.reduce((sum, r) => sum + r.total_cost, 0);
  const avgRepairTime = repairs.reduce((sum, r) => sum + r.duration_minutes, 0) / repairs.length;

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">설비 수리 이력</h1>
          <p className="text-sm text-gray-500 mt-1">
            설비 고장 및 수리 기록 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileText className="w-4 h-4 mr-2" />
            수리 보고서
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
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
                  placeholder="설비명, 고장 내용 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedEquipment} onValueChange={setSelectedEquipment} className="w-48">
              <SelectItem value="ALL">전체 설비</SelectItem>
              {equipments.map(eq => (
                <SelectItem key={eq.id} value={eq.id.toString()}>{eq.name}</SelectItem>
              ))}
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus} className="w-40">
              <SelectItem value="ALL">전체 상태</SelectItem>
              <SelectItem value="PENDING">대기 중</SelectItem>
              <SelectItem value="IN_PROGRESS">진행 중</SelectItem>
              <SelectItem value="COMPLETED">완료</SelectItem>
              <SelectItem value="CLOSED">종료</SelectItem>
            </Select>
            <Select value={selectedSeverity} onValueChange={setSelectedSeverity} className="w-40">
              <SelectItem value="ALL">전체 중요도</SelectItem>
              <SelectItem value="CRITICAL">긴급</SelectItem>
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
            <div className="text-2xl font-bold">₩{(totalCost / 1000000).toFixed(1)}M</div>
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
              {repairs.filter(r => r.status === 'COMPLETED' || r.status === 'CLOSED').length}건
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
                      <div className="font-medium text-gray-900">{repair.equipment_name}</div>
                      <div className="text-sm text-gray-600">{repair.failure_description}</div>
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
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">설비</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">고장 내용</th>
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
                        setIsModalOpen(true);
                      }}
                    >
                      <td className="py-3 px-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{repair.equipment_name}</div>
                          <div className="text-xs text-gray-500">{repair.equipment_code}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="text-sm text-gray-700 max-w-xs truncate">{repair.failure_description}</div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {failureTypes.find(t => t.value === repair.failure_type)?.label || repair.failure_type}
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
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedRepair(repair);
                            setIsModalOpen(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
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
      {isModalOpen && selectedRepair && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsModalOpen(false)} />
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b sticky top-0 bg-white">
                <h3 className="text-xl font-semibold">수리 기록 상세</h3>
                <button
                  onClick={() => setIsModalOpen(false)}
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
                      <label className="text-sm font-medium text-gray-500">설비</label>
                      <p className="text-gray-900">{selectedRepair.equipment_name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">고장 일시</label>
                      <p className="text-gray-900">{selectedRepair.failure_date}</p>
                    </div>
                    <div className="col-span-2">
                      <label className="text-sm font-medium text-gray-500">고장 내용</label>
                      <p className="text-gray-900">{selectedRepair.failure_description}</p>
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

                {/* 원인 및 조치 */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">원인 및 조치</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-gray-500">원인 규명</label>
                      <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded">{selectedRepair.root_cause}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">수리 조치</label>
                      <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded">{selectedRepair.corrective_action}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">예방 조치</label>
                      <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded">{selectedRepair.preventive_action}</p>
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

                {/* 사용 부품 */}
                {selectedRepair.parts_used.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">사용 부품</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedRepair.parts_used.map((part, index) => (
                        <Badge key={index} variant="outline" className="text-sm">
                          {part}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* 비고 */}
                {selectedRepair.notes && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">비고</h4>
                    <p className="text-sm text-gray-600">{selectedRepair.notes}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

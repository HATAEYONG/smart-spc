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
  Filter,
  Wrench,
  MapPin,
  AlertTriangle,
  CheckCircle,
  Clock,
} from 'lucide-react';

interface Equipment {
  id: number;
  code: string;
  name: string;
  type: string;
  manufacturer: string;
  model: string;
  serial_number: string;
  location: string;
  installation_date: string;
  status: 'OPERATIONAL' | 'MAINTENANCE' | 'DOWN' | 'RETIRED';
  department: string;
  cost: number;
  specifications?: Record<string, string>;
}

const MOCK_EQUIPMENT: Equipment[] = [
  {
    id: 1,
    code: 'EQ-001',
    name: 'CNC 머신 A',
    type: 'CNC',
    manufacturer: 'FANUC',
    model: 'DMG Mori NLX 2500',
    serial_number: 'SN-2024-001',
    location: '생산라인 1',
    installation_date: '2023-01-15',
    status: 'OPERATIONAL',
    department: '생산팀',
    cost: 250000000,
    specifications: {
      '최대 회전수': '12000 RPM',
      '출력': '15kW',
      '정밀도': '±0.001mm',
    },
  },
  {
    id: 2,
    code: 'EQ-002',
    name: '프레스 기계 B',
    type: 'PRESS',
    manufacturer: 'AIDA',
    model: 'AIDA NS1-200',
    serial_number: 'SN-2024-002',
    location: '생산라인 2',
    installation_date: '2023-03-20',
    status: 'MAINTENANCE',
    department: '생산팀',
    cost: 180000000,
    specifications: {
      '가용력': '200톤',
      '스트로크': '200mm',
      '속도': '30SPM',
    },
  },
  {
    id: 3,
    code: 'EQ-003',
    name: '로봇 팔 R-1',
    type: 'ROBOT',
    manufacturer: 'KUKA',
    model: 'KR 10 R1420',
    serial_number: 'SN-2024-003',
    location: '조립라인 1',
    installation_date: '2023-06-10',
    status: 'OPERATIONAL',
    department: '조립팀',
    cost: 95000000,
    specifications: {
      '하중': '10kg',
      '작업 반경': '1420mm',
      '자유도': '6축',
    },
  },
  {
    id: 4,
    code: 'EQ-004',
    name: '컨베이어 벨트 C-1',
    type: 'CONVEYOR',
    manufacturer: 'Dorner',
    model: '2200 Series',
    serial_number: 'SN-2024-004',
    location: '포장라인',
    installation_date: '2023-08-05',
    status: 'DOWN',
    department: '포장팀',
    cost: 35000000,
    specifications: {
      '폭': '220mm',
      '길이': '10m',
      '속도': '10m/min',
    },
  },
];

export const EquipmentMasterPage: React.FC = () => {
  const [equipment, setEquipment] = useState<Equipment[]>(MOCK_EQUIPMENT);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredEquipment = equipment.filter(eq => {
    const matchesSearch =
      eq.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      eq.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      eq.type.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = selectedType === 'ALL' || eq.type === selectedType;
    const matchesStatus = selectedStatus === 'ALL' || eq.status === selectedStatus;

    return matchesSearch && matchesType && matchesStatus;
  });

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'OPERATIONAL':
        return {
          label: '가동 중',
          color: 'bg-green-100 text-green-800',
          icon: CheckCircle,
        };
      case 'MAINTENANCE':
        return {
          label: '점검 중',
          color: 'bg-yellow-100 text-yellow-800',
          icon: Wrench,
        };
      case 'DOWN':
        return {
          label: '고장',
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

  const equipmentTypes = Array.from(new Set(equipment.map(eq => eq.type)));

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">설비 마스터 관리</h1>
          <p className="text-sm text-gray-500 mt-1">
            설비 기본 정보 및 사양 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Filter className="w-4 h-4 mr-2" />
            상세 필터
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4 mr-2" />
            신규 설비 등록
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
                  placeholder="설비명, 코드, 유형 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedType} onValueChange={setSelectedType} className="w-48">
              <SelectItem value="ALL">전체 유형</SelectItem>
              {equipmentTypes.map(type => (
                <SelectItem key={type} value={type}>{type}</SelectItem>
              ))}
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus} className="w-40">
              <SelectItem value="ALL">전체 상태</SelectItem>
              <SelectItem value="OPERATIONAL">가동 중</SelectItem>
              <SelectItem value="MAINTENANCE">점검 중</SelectItem>
              <SelectItem value="DOWN">고장</SelectItem>
              <SelectItem value="RETIRED">폐기</SelectItem>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 요약 정보 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-blue-100 mb-1">총 설비 수</div>
            <div className="text-2xl font-bold">{equipment.length}대</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <CheckCircle className="w-4 h-4" />
              <div className="text-sm font-medium text-green-100">가동 중</div>
            </div>
            <div className="text-2xl font-bold">
              {equipment.filter(e => e.status === 'OPERATIONAL').length}대
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <Wrench className="w-4 h-4" />
              <div className="text-sm font-medium text-yellow-100">점검 중</div>
            </div>
            <div className="text-2xl font-bold">
              {equipment.filter(e => e.status === 'MAINTENANCE').length}대
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <AlertTriangle className="w-4 h-4" />
              <div className="text-sm font-medium text-red-100">고장</div>
            </div>
            <div className="text-2xl font-bold">
              {equipment.filter(e => e.status === 'DOWN').length}대
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 설비 목록 테이블 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wrench className="w-5 h-5 text-purple-600" />
            설비 목록
            <Badge variant="outline" className="ml-2">
              {filteredEquipment.length}대
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">코드</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">설비명</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">유형</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">제조사/모델</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">위치</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">상태</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">관리</th>
                </tr>
              </thead>
              <tbody>
                {filteredEquipment.map((eq) => {
                  const statusConfig = getStatusConfig(eq.status);
                  const StatusIcon = statusConfig.icon;
                  return (
                    <tr
                      key={eq.id}
                      className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedEquipment(eq);
                        setIsModalOpen(true);
                      }}
                    >
                      <td className="py-3 px-4 text-sm font-mono text-gray-700">
                        {eq.code}
                      </td>
                      <td className="py-3 px-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{eq.name}</div>
                          <div className="text-xs text-gray-500">{eq.serial_number}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="text-xs">
                          {eq.type}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div>
                          <div>{eq.manufacturer}</div>
                          <div className="text-xs text-gray-500">{eq.model}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          {eq.location}
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
                              setSelectedEquipment(eq);
                              setIsModalOpen(true);
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
                              // 삭제 로직
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

          {filteredEquipment.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Wrench className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>검색 결과가 없습니다</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 상세 모달 */}
      {isModalOpen && selectedEquipment && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsModalOpen(false)} />
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-xl font-semibold">설비 상세 정보</h3>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">설비 코드</label>
                    <p className="text-lg font-semibold text-gray-900 font-mono">{selectedEquipment.code}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">설비명</label>
                    <p className="text-lg font-semibold text-gray-900">{selectedEquipment.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">유형</label>
                    <p className="text-gray-900">{selectedEquipment.type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">시리얼 번호</label>
                    <p className="text-gray-900 font-mono">{selectedEquipment.serial_number}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">제조사</label>
                    <p className="text-gray-900">{selectedEquipment.manufacturer}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">모델</label>
                    <p className="text-gray-900">{selectedEquipment.model}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">위치</label>
                    <p className="text-gray-900">{selectedEquipment.location}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">관리 부서</label>
                    <p className="text-gray-900">{selectedEquipment.department}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">설치일</label>
                    <p className="text-gray-900">{selectedEquipment.installation_date}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">취득 비용</label>
                    <p className="text-gray-900">₩{selectedEquipment.cost.toLocaleString()}</p>
                  </div>
                </div>

                {selectedEquipment.specifications && (
                  <div className="mt-6">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">기술 사양</h4>
                    <div className="bg-gray-50 rounded-lg p-4">
                      {Object.entries(selectedEquipment.specifications).map(([key, value]) => (
                        <div key={key} className="flex justify-between py-2 border-b last:border-0">
                          <span className="text-sm text-gray-600">{key}</span>
                          <span className="text-sm font-medium text-gray-900">{value}</span>
                        </div>
                      ))}
                    </div>
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

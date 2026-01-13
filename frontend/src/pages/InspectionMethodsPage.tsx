import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import {
  Plus,
  Search,
  Edit,
  Trash2,
  Settings,
  Gauge,
  Microscope,
  Ruler,
  TestTube,
  CheckCircle
} from 'lucide-react';

interface InspectionMethod {
  id: string;
  name: string;
  type: 'DIMENSION' | 'VISUAL' | 'PHYSICAL' | 'CHEMICAL' | 'MECHANICAL';
  instrument: string;
  accuracy: string;
  procedure: string;
  applicableItems: string[];
  status: 'ACTIVE' | 'MAINTENANCE' | 'CALIBRATION_DUE';
  calibrationDate: string;
  nextCalibration: string;
}

export const InspectionMethodsPage: React.FC = () => {
  const [methods, setMethods] = useState<InspectionMethod[]>([
    {
      id: '1',
      name: '마이크로미터 측정법',
      type: 'DIMENSION',
      instrument: '마이크로미터 (0-25mm)',
      accuracy: '±0.001mm',
      procedure: '1. 측정물 표면 청소\n2. 영점 확인\n3. 3점 측정 후 평균 기록\n4. 온도 보정 적용',
      applicableItems: ['내경', '외경', '두께'],
      status: 'ACTIVE',
      calibrationDate: '2025-12-01',
      nextCalibration: '2026-06-01',
    },
    {
      id: '2',
      name: '육안 검사법',
      type: 'VISUAL',
      instrument: '육안 + 확대경',
      accuracy: 'N/A',
      procedure: '1. 조명 800lux 확인\n2. 30cm 거리에서 관찰\n3. 3분간 회전 검사\n4. 이물/스크래치 확인',
      applicableItems: ['외관', '색상', '표면 상태'],
      status: 'ACTIVE',
      calibrationDate: 'N/A',
      nextCalibration: 'N/A',
    },
    {
      id: '3',
      name: '경도 측정법',
      type: 'PHYSICAL',
      instrument: '로크웰 경도계',
      accuracy: '±2 HRC',
      procedure: '1. 표면 평탄화\n2. 10kgf 하중 적용\n3. 15초 유지\n4. 경도값 판독\n5. 3점 측정',
      applicableItems: ['재질 경도', '열처리 확인'],
      status: 'CALIBRATION_DUE',
      calibrationDate: '2024-12-01',
      nextCalibration: '2025-12-01',
    },
    {
      id: '4',
      name: '초음파 두께 측정',
      type: 'DIMENSION',
      instrument: '초음파 두께계',
      accuracy: '±0.01mm',
      procedure: '1. 커플런트 도포\n2. 프로브 접촉\n3. 5점 측정\n4. 평균값 산출',
      applicableItems: ['벽 두께', '판재 두께'],
      status: 'ACTIVE',
      calibrationDate: '2025-10-15',
      nextCalibration: '2026-04-15',
    },
    {
      id: '5',
      name: '인장 강도 시험',
      type: 'MECHANICAL',
      instrument: '만능 재료 시험기',
      accuracy: '±0.5%',
      procedure: '1. 시편 채취\n2. 파지 장치 세팅\n3. 인장 속도 5mm/min\n4. 파점까지 시험\n5. 강도 계산',
      applicableItems: ['인장 강도', '항복점'],
      status: 'MAINTENANCE',
      calibrationDate: '2025-09-01',
      nextCalibration: '2026-03-01',
    },
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('ALL');

  const typeConfig = {
    DIMENSION: { label: '치수 측정', icon: Ruler, color: 'bg-blue-100 text-blue-700' },
    VISUAL: { label: '육안 검사', icon: CheckCircle, color: 'bg-green-100 text-green-700' },
    PHYSICAL: { label: '물성 시험', icon: Gauge, color: 'bg-purple-100 text-purple-700' },
    CHEMICAL: { label: '화학 분석', icon: TestTube, color: 'bg-orange-100 text-orange-700' },
    MECHANICAL: { label: '기계적 시험', icon: Settings, color: 'bg-red-100 text-red-700' },
  };

  const statusConfig = {
    ACTIVE: { label: '사용 가능', color: 'bg-green-100 text-green-700' },
    MAINTENANCE: { label: '정비 중', color: 'bg-yellow-100 text-yellow-700' },
    CALIBRATION_DUE: { label: '교정过期', color: 'bg-red-100 text-red-700' },
  };

  const filteredMethods = methods.filter(method => {
    const matchesSearch = searchTerm === '' ||
      method.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      method.instrument.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = selectedType === 'ALL' || method.type === selectedType;

    return matchesSearch && matchesType;
  });

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">검사 기법 관리</h1>
          <p className="text-sm text-gray-500 mt-1">
            검사 방법론 및 장비 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            교정 관리
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4 mr-2" />
            신규 검사법
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
                  placeholder="검사법, 장비명 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant={selectedType === 'ALL' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedType('ALL')}
                className={selectedType === 'ALL' ? 'bg-purple-600' : ''}
              >
                전체
              </Button>
              {Object.entries(typeConfig).map(([key, config]) => {
                const Icon = config.icon;
                return (
                  <Button
                    key={key}
                    variant={selectedType === key ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedType(key)}
                    className={selectedType === key ? 'bg-purple-600' : ''}
                  >
                    <Icon className="w-4 h-4 mr-1" />
                    {config.label}
                  </Button>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 검사법 카드 목록 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredMethods.map((method) => {
          const typeInfo = typeConfig[method.type];
          const statusInfo = statusConfig[method.status];
          const TypeIcon = typeInfo.icon;

          return (
            <Card key={method.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`p-2 rounded-lg ${typeInfo.color}`}>
                        <TypeIcon className="w-4 h-4" />
                      </div>
                      <CardTitle className="text-lg">{method.name}</CardTitle>
                    </div>
                    <Badge className={statusInfo.color}>
                      {statusInfo.label}
                    </Badge>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div>
                  <div className="text-sm text-gray-500 mb-1">사용 장비</div>
                  <div className="text-gray-900 font-medium">{method.instrument}</div>
                </div>

                {method.accuracy !== 'N/A' && (
                  <div>
                    <div className="text-sm text-gray-500 mb-1">정밀도</div>
                    <div className="text-gray-900 font-mono">{method.accuracy}</div>
                  </div>
                )}

                <div>
                  <div className="text-sm text-gray-500 mb-2">적용 항목</div>
                  <div className="flex flex-wrap gap-1">
                    {method.applicableItems.map((item, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>

                {method.nextCalibration !== 'N/A' && (
                  <div className={`p-3 rounded-lg border ${
                    method.status === 'CALIBRATION_DUE'
                      ? 'bg-red-50 border-red-200'
                      : method.status === 'ACTIVE'
                      ? 'bg-green-50 border-green-200'
                      : 'bg-yellow-50 border-yellow-200'
                  }`}>
                    <div className="flex items-center justify-between text-sm">
                      <div>
                        <div className="text-gray-600">차기 교정일</div>
                        <div className="font-semibold text-gray-900">
                          {new Date(method.nextCalibration).toLocaleDateString('ko-KR')}
                        </div>
                      </div>
                      <Microscope className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                )}

                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-500 mb-2">측정 절차</div>
                  <div className="text-sm text-gray-700 whitespace-pre-line">
                    {method.procedure}
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Edit className="w-4 h-4 mr-1" />
                    수정
                  </Button>
                  {method.status === 'CALIBRATION_DUE' && (
                    <Button size="sm" className="flex-1 bg-red-600 hover:bg-red-700">
                      교정 예약
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredMethods.length === 0 && (
        <Card>
          <CardContent className="text-center py-12 text-gray-500">
            <Microscope className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>검색 결과가 없습니다</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

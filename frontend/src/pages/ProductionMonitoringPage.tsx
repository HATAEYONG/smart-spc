/**
 * 실시간 생산 모니터링 대시보드
 * 생산 라인별 실시간 가동 현황, OEE 추이, 불량률 모니터링
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Activity,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Zap,
  Clock,
  Target,
  BarChart3,
  RefreshCw,
  Filter,
  Download,
  Users,
  Wrench,
  Package
} from 'lucide-react';

interface ProductionLine {
  id: number;
  name: string;
  status: 'RUNNING' | 'STOPPED' | 'MAINTENANCE' | 'IDLE';
  product_code: string;
  product_name: string;
  target_quantity: number;
  produced_quantity: number;
  defect_quantity: number;
  oee: number;
  availability: number;
  performance: number;
  quality: number;
  cycle_time: number;
  actual_cycle_time: number;
  downtime_minutes: number;
  operator: string;
  speed_loss: number;
}

const mockProductionLines: ProductionLine[] = [
  {
    id: 1,
    name: '라인 A - CNC 가공',
    status: 'RUNNING',
    product_code: 'PROD-001',
    product_name: '자동차 부품 A-Type',
    target_quantity: 500,
    produced_quantity: 342,
    defect_quantity: 8,
    oee: 87.5,
    availability: 92.3,
    performance: 89.1,
    quality: 98.4,
    cycle_time: 2.5,
    actual_cycle_time: 2.8,
    downtime_minutes: 25,
    operator: '홍작업자',
    speed_loss: 10.7
  },
  {
    id: 2,
    name: '라인 B - 사출 성형',
    status: 'RUNNING',
    product_code: 'PROD-002',
    product_name: '전자 부품 B-Type',
    target_quantity: 800,
    produced_quantity: 523,
    defect_quantity: 15,
    oee: 78.2,
    availability: 85.1,
    performance: 82.4,
    quality: 91.5,
    cycle_time: 1.8,
    actual_cycle_time: 2.1,
    downtime_minutes: 45,
    operator: '이작업자',
    speed_loss: 14.3
  },
  {
    id: 3,
    name: '라인 C - 레이저 절단',
    status: 'MAINTENANCE',
    product_code: 'PROD-003',
    product_name: '금속 부품 C-Type',
    target_quantity: 300,
    produced_quantity: 180,
    defect_quantity: 5,
    oee: 65.4,
    availability: 68.2,
    performance: 75.3,
    quality: 97.2,
    cycle_time: 3.2,
    actual_cycle_time: 4.0,
    downtime_minutes: 120,
    operator: '박작업자',
    speed_loss: 20.0
  },
  {
    id: 4,
    name: '라인 D - 프레스',
    status: 'STOPPED',
    product_code: 'PROD-004',
    product_name: '플라스틱 부품 D-Type',
    target_quantity: 1000,
    produced_quantity: 450,
    defect_quantity: 22,
    oee: 52.8,
    availability: 58.5,
    performance: 65.2,
    quality: 89.1,
    cycle_time: 1.2,
    actual_cycle_time: 1.8,
    downtime_minutes: 180,
    operator: '조작업자',
    speed_loss: 33.3
  },
  {
    id: 5,
    name: '라인 E - 조립',
    status: 'RUNNING',
    product_code: 'PROD-005',
    product_name: '정밀 부품 E-Type',
    target_quantity: 600,
    produced_quantity: 478,
    defect_quantity: 12,
    oee: 91.2,
    availability: 95.1,
    performance: 93.4,
    quality: 96.8,
    cycle_time: 2.0,
    actual_cycle_time: 2.1,
    downtime_minutes: 15,
    operator: '최작업자',
    speed_loss: 4.8
  },
  {
    id: 6,
    name: '라인 F - 열처리',
    status: 'IDLE',
    product_code: 'PROD-006',
    product_name: '열처리 부품 F-Type',
    target_quantity: 400,
    produced_quantity: 0,
    defect_quantity: 0,
    oee: 0,
    availability: 100,
    performance: 0,
    quality: 100,
    cycle_time: 4.5,
    actual_cycle_time: 0,
    downtime_minutes: 0,
    operator: '미할당',
    speed_loss: 0
  }
];

const ProductionMonitoringPage: React.FC = () => {
  const [lines, setLines] = useState<ProductionLine[]>(mockProductionLines);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const getStatusBadge = (status: string) => {
    const styles = {
      RUNNING: 'bg-green-100 text-green-800 border-green-300',
      STOPPED: 'bg-red-100 text-red-800 border-red-300',
      MAINTENANCE: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      IDLE: 'bg-gray-100 text-gray-800 border-gray-300',
    };
    const labels = {
      RUNNING: '가동중',
      STOPPED: '정지',
      MAINTENANCE: '보전중',
      IDLE: '대기',
    };
    const icons = {
      RUNNING: Activity,
      STOPPED: XCircle,
      MAINTENANCE: Wrench,
      IDLE: Clock,
    };
    const Icon = icons[status as keyof typeof icons];
    return (
      <Badge className={styles[status as keyof typeof styles]}>
        <Icon className="w-3 h-3 mr-1" />
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  const getOEEColor = (oee: number) => {
    if (oee >= 85) return 'text-green-600';
    if (oee >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getOEEBadge = (oee: number) => {
    if (oee >= 85) return 'bg-green-100 text-green-800 border-green-300';
    if (oee >= 60) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-red-100 text-red-800 border-red-300';
  };

  const filteredLines = selectedStatus === 'ALL'
    ? lines
    : lines.filter(line => line.status === selectedStatus);

  const totals = {
    lines: lines.length,
    running: lines.filter(l => l.status === 'RUNNING').length,
    stopped: lines.filter(l => l.status === 'STOPPED').length,
    totalTarget: lines.reduce((sum, l) => sum + l.target_quantity, 0),
    totalProduced: lines.reduce((sum, l) => sum + l.produced_quantity, 0),
    totalDefects: lines.reduce((sum, l) => sum + l.defect_quantity, 0),
    avgOEE: (lines.reduce((sum, l) => sum + l.oee, 0) / lines.filter(l => l.status !== 'IDLE').length).toFixed(1),
    totalDowntime: lines.reduce((sum, l) => sum + l.downtime_minutes, 0)
  };

  const achievementRate = totals.totalTarget > 0
    ? ((totals.totalProduced / totals.totalTarget) * 100).toFixed(1)
    : '0.0';

  const defectRate = totals.totalProduced > 0
    ? ((totals.totalDefects / totals.totalProduced) * 100).toFixed(2)
    : '0.00';

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Activity className="w-8 h-8 text-green-600" />
            실시간 생산 모니터링
          </h1>
          <p className="text-gray-600 mt-2">
            생산 라인별 실시간 가동 현황 및 OEE 모니터링
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={autoRefresh ? 'bg-green-50 border-green-300' : ''}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            {autoRefresh ? '자동 새로고침' : '수동 새로고침'}
          </Button>
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            내보내기
          </Button>
        </div>
      </div>

      {/* Overall Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">생산 라인</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {totals.running} / {totals.lines}
                </p>
                <p className="text-xs text-gray-500 mt-1">가동중</p>
              </div>
              <Activity className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">달성률</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{achievementRate}%</p>
                <p className="text-xs text-gray-500 mt-1">
                  {totals.totalProduced.toLocaleString()} / {totals.totalTarget.toLocaleString()}
                </p>
              </div>
              <Target className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">평균 OEE</p>
                <p className={`text-3xl font-bold mt-1 ${getOEEColor(parseFloat(totals.avgOEE))}`}>
                  {totals.avgOEE}%
                </p>
                <p className="text-xs text-gray-500 mt-1">전체 평균</p>
              </div>
              <BarChart3 className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-red-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">불량률</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{defectRate}%</p>
                <p className="text-xs text-gray-500 mt-1">
                  {totals.totalDefects.toLocaleString()}개 불량
                </p>
              </div>
              <AlertTriangle className="w-12 h-12 text-red-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Filter */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <Filter className="w-5 h-5 text-gray-500" />
            <span className="font-medium text-gray-700">상태 필터:</span>
            <div className="flex gap-2">
              {['ALL', 'RUNNING', 'STOPPED', 'MAINTENANCE', 'IDLE'].map((status) => (
                <Button
                  key={status}
                  size="sm"
                  variant={selectedStatus === status ? 'default' : 'outline'}
                  onClick={() => setSelectedStatus(status)}
                  className={selectedStatus === status ? 'bg-purple-600 hover:bg-purple-700' : ''}
                >
                  {status === 'ALL' ? '전체' :
                   status === 'RUNNING' ? '가동중' :
                   status === 'STOPPED' ? '정지' :
                   status === 'MAINTENANCE' ? '보전중' : '대기'}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Production Lines */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredLines.map((line) => {
          const progressPercent = (line.produced_quantity / line.target_quantity) * 100;
          const defectPercent = line.produced_quantity > 0
            ? (line.defect_quantity / line.produced_quantity) * 100
            : 0;

          return (
            <Card key={line.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-purple-600" />
                    {line.name}
                  </CardTitle>
                  {getStatusBadge(line.status)}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Product Info */}
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">생산 제품</p>
                    <p className="font-semibold">{line.product_name}</p>
                    <p className="text-sm text-gray-600">{line.product_code}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-gray-500" />
                    <span className="text-sm">{line.operator}</span>
                  </div>
                </div>

                {/* Production Progress */}
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">생산 진행률</span>
                    <span className="font-semibold">{progressPercent.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        progressPercent >= 90 ? 'bg-green-500' :
                        progressPercent >= 70 ? 'bg-yellow-500' :
                        progressPercent >= 50 ? 'bg-orange-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(progressPercent, 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs mt-1 text-gray-600">
                    <span>{line.produced_quantity.toLocaleString()}개 생산</span>
                    <span>목표: {line.target_quantity.toLocaleString()}개</span>
                  </div>
                </div>

                {/* OEE Breakdown */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-semibold">OEE</span>
                    <Badge className={getOEEBadge(line.oee)}>
                      {line.oee.toFixed(1)}%
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">가동률 (A)</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${line.availability >= 90 ? 'bg-green-500' : 'bg-yellow-500'}`}
                            style={{ width: `${line.availability}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">{line.availability.toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">성능률 (P)</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${line.performance >= 85 ? 'bg-green-500' : 'bg-yellow-500'}`}
                            style={{ width: `${line.performance}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">{line.performance.toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">양품률 (Q)</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${line.quality >= 95 ? 'bg-green-500' : 'bg-red-500'}`}
                            style={{ width: `${line.quality}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">{line.quality.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional Metrics */}
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-xs text-gray-500">불량률</p>
                    <p className={`text-lg font-bold ${defectPercent > 2 ? 'text-red-600' : 'text-green-600'}`}>
                      {defectPercent.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500">{line.defect_quantity}개</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">다운타임</p>
                    <p className="text-lg font-bold text-orange-600">
                      {line.downtime_minutes}분
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">속도 손실</p>
                    <p className="text-lg font-bold text-yellow-600">
                      {line.speed_loss.toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* Alerts */}
                {line.oee < 60 && (
                  <div className="flex items-start gap-2 p-3 bg-red-50 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-red-900">
                      <p className="font-semibold">OEE 낮음 ({line.oee.toFixed(1)}%)</p>
                      <p className="text-red-700">즉시 원인 파악 및 조치 필요</p>
                    </div>
                  </div>
                )}
                {defectPercent > 2 && (
                  <div className="flex items-start gap-2 p-3 bg-orange-50 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-orange-900">
                      <p className="font-semibold">불량률 높음 ({defectPercent.toFixed(1)}%)</p>
                      <p className="text-orange-700">품질 검토 강화 필요</p>
                    </div>
                  </div>
                )}
                {line.status === 'STOPPED' && (
                  <div className="flex items-start gap-2 p-3 bg-red-50 rounded-lg">
                    <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-red-900">
                      <p className="font-semibold">라인 정지</p>
                      <p className="text-red-700">가동 재개를 위해 확인 필요</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Legend */}
      <Card>
        <CardContent className="p-6">
          <h3 className="font-semibold mb-4">범례</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-500 rounded"></div>
              <span>OEE 85% 이상 (우수)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-500 rounded"></div>
              <span>OEE 60-85% (주의)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span>OEE 60% 미만 (긴급)</span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-green-600" />
              <span>실시간 업데이트</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProductionMonitoringPage;
export { ProductionMonitoringPage };

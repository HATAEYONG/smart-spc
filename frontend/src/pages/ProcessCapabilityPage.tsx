import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/Select';
import {
  Activity,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Target,
  BarChart3,
  AlertTriangle
} from 'lucide-react';
import { StatusBadge } from '../components/common';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  AreaChart,
  Area
} from 'recharts';

interface CapabilityData {
  characteristic: string;
  cp: number;
  cpk: number;
  pp: number;
  ppk: number;
  mean: number;
  target: number;
  usl: number;
  lsl: number;
  stdDev: number;
  sampleSize: number;
  status: 'EXCELLENT' | 'GOOD' | 'MARGINAL' | 'POOR';
}

export const ProcessCapabilityPage: React.FC = () => {
  const [selectedProduct, setSelectedProduct] = useState<string>('1');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('30');
  const [capabilities, setCapabilities] = useState<CapabilityData[]>([
    {
      characteristic: '내경',
      cp: 1.67,
      cpk: 1.45,
      pp: 1.55,
      ppk: 1.42,
      mean: 10.01,
      target: 10.00,
      usl: 10.05,
      lsl: 9.95,
      stdDev: 0.008,
      sampleSize: 150,
      status: 'EXCELLENT',
    },
    {
      characteristic: '외경',
      cp: 1.33,
      cpk: 1.28,
      pp: 1.25,
      ppk: 1.20,
      mean: 50.02,
      target: 50.00,
      usl: 50.10,
      lsl: 49.90,
      stdDev: 0.025,
      sampleSize: 150,
      status: 'GOOD',
    },
    {
      characteristic: '두께',
      cp: 1.15,
      cpk: 0.95,
      pp: 1.10,
      ppk: 0.92,
      mean: 5.03,
      target: 5.00,
      usl: 5.10,
      lsl: 4.90,
      stdDev: 0.028,
      sampleSize: 150,
      status: 'MARGINAL',
    },
    {
      characteristic: '깊이',
      cp: 0.85,
      cpk: 0.72,
      pp: 0.80,
      ppk: 0.68,
      mean: 2.52,
      target: 2.50,
      usl: 2.60,
      lsl: 2.40,
      stdDev: 0.045,
      sampleSize: 150,
      status: 'POOR',
    },
  ]);

  const products = [
    { id: '1', name: '브레이크 패드 - 전체' },
    { id: '2', name: '브레이크 패드 - Type A' },
    { id: '3', name: '브레이크 패드 - Type B' },
  ];

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'EXCELLENT':
        return { label: '우수', color: 'bg-green-100 text-green-700', icon: CheckCircle };
      case 'GOOD':
        return { label: '양호', color: 'bg-blue-100 text-blue-700', icon: CheckCircle };
      case 'MARGINAL':
        return { label: '한계', color: 'bg-yellow-100 text-yellow-700', icon: AlertTriangle };
      case 'POOR':
        return { label: '부족', color: 'bg-red-100 text-red-700', icon: AlertCircle };
      default:
        return { label: status, color: 'bg-gray-100 text-gray-700', icon: Activity };
    }
  };

  const getCpkColor = (cpk: number) => {
    if (cpk >= 1.67) return 'text-green-600';
    if (cpk >= 1.33) return 'text-blue-600';
    if (cpk >= 1.0) return 'text-yellow-600';
    return 'text-red-600';
  };

  // 히스토그램 데이터 생성 (정규분포 기반)
  const generateHistogramData = (mean: number, stdDev: number) => {
    const bins = 20;
    const binWidth = (0.2) / bins; // ±0.1 범위
    const data = [];

    for (let i = 0; i < bins; i++) {
      const binCenter = mean - 0.1 + (i + 0.5) * binWidth;
      const z = (binCenter - mean) / stdDev;
      const frequency = Math.exp(-0.5 * z * z) / (stdDev * Math.sqrt(2 * Math.PI));

      data.push({
        bin: binCenter.toFixed(3),
        frequency: Number((frequency * 100).toFixed(1)),
      });
    }

    return data;
  };

  const selectedCapability = capabilities[0]; // 첫 번째 특성 선택
  const histogramData = generateHistogramData(
    selectedCapability.mean,
    selectedCapability.stdDev
  );

  const avgCpk = capabilities.reduce((sum, c) => sum + c.cpk, 0) / capabilities.length;

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">공정능력 분석</h1>
          <p className="text-sm text-gray-500 mt-1">
            Cp, Cpk, Pp, Ppk 지수 분석 및 공정 능력 평가
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <BarChart3 className="w-4 h-4 mr-2" />
            히스토그램
          </Button>
          <Button variant="outline">
            <Activity className="w-4 h-4 mr-2" />
            정규성 검정
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <TrendingUp className="w-4 h-4 mr-2" />
            분석 실행
          </Button>
        </div>
      </div>

      {/* 필터 영역 */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">제품</label>
              <Select value={selectedProduct} onValueChange={setSelectedProduct}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {products.map((product) => (
                    <SelectItem key={product.id} value={product.id}>
                      {product.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">분석 기간</label>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">최근 7일</SelectItem>
                  <SelectItem value="30">최근 30일</SelectItem>
                  <SelectItem value="90">최근 90일</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">표본 크기</label>
              <Select defaultValue="150">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                  <SelectItem value="150">150</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 요약 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-purple-100 mb-1">평균 Cpk</div>
                <div className="text-3xl font-bold">{avgCpk.toFixed(2)}</div>
              </div>
              <Activity className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-500 mb-1">우수 (Cpk ≥ 1.67)</div>
            <div className="text-2xl font-bold text-green-600">
              {capabilities.filter(c => c.cpk >= 1.67).length}개
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-500 mb-1">부족 (Cpk &lt; 1.0)</div>
            <div className="text-2xl font-bold text-red-600">
              {capabilities.filter(c => c.cpk < 1.0).length}개
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-500 mb-1">총 항목</div>
            <div className="text-2xl font-bold text-gray-900">
              {capabilities.length}개
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 공정능력 테이블 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-600" />
            공정능력 지수
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">특성</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Cp</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Cpk</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Pp</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Ppk</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">평균</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">표준편차</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">상태</th>
                  <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">상세</th>
                </tr>
              </thead>
              <tbody>
                {capabilities.map((cap) => {
                  const statusConfig = getStatusConfig(cap.status);
                  const StatusIcon = statusConfig.icon;

                  return (
                    <tr key={cap.characteristic} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="font-medium text-gray-900">{cap.characteristic}</div>
                        <div className="text-xs text-gray-500">
                          목표: {cap.target} | 규격: {cap.lsl} ~ {cap.usl}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-center font-mono text-sm text-gray-900">
                        {cap.cp.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <div className={`text-lg font-bold ${getCpkColor(cap.cpk)}`}>
                          {cap.cpk.toFixed(2)}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-center font-mono text-sm text-gray-900">
                        {cap.pp.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-center font-mono text-sm text-gray-900">
                        {cap.ppk.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-center font-mono text-sm text-gray-900">
                        {cap.mean.toFixed(3)}
                      </td>
                      <td className="py-3 px-4 text-center font-mono text-sm text-gray-900">
                        {cap.stdDev.toFixed(4)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge className={statusConfig.color}>
                          <div className="flex items-center gap-1">
                            <StatusIcon className="w-3 h-3" />
                            {statusConfig.label}
                          </div>
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Button variant="outline" size="sm">
                          상세
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* 히스토그램 차트 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-purple-600" />
            분포 히스토그램 - {selectedCapability.characteristic}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={histogramData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="bin"
                label={{ value: '측정값 (mm)', position: 'insideBottom', offset: -5 }}
              />
              <YAxis label={{ value: '빈도', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                formatter={(value: number) => [value, '빈도']}
                labelFormatter={(label) => `측정값: ${label} mm`}
              />
              <Legend />
              <ReferenceLine
                x={selectedCapability.usl}
                stroke="#ef4444"
                strokeWidth={2}
                label="USL"
              />
              <ReferenceLine
                x={selectedCapability.lsl}
                stroke="#ef4444"
                strokeWidth={2}
                label="LSL"
              />
              <ReferenceLine
                x={selectedCapability.target}
                stroke="#22c55e"
                strokeWidth={2}
                strokeDasharray="5 5"
                label="목표값"
              />
              <Bar
                dataKey="frequency"
                fill="#8b5cf6"
                name="빈도"
              />
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
            <div className="flex items-center gap-2 p-2 bg-green-50 rounded">
              <div className="w-3 h-1 bg-green-500"></div>
              <span className="text-gray-700">목표값: {selectedCapability.target} mm</span>
            </div>
            <div className="flex items-center gap-2 p-2 bg-red-50 rounded">
              <div className="w-3 h-1 bg-red-500"></div>
              <span className="text-gray-700">USL: {selectedCapability.usl} mm</span>
            </div>
            <div className="flex items-center gap-2 p-2 bg-red-50 rounded">
              <div className="w-3 h-1 bg-red-500"></div>
              <span className="text-gray-700">LSL: {selectedCapability.lsl} mm</span>
            </div>
          </div>
          <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-700">평균: {selectedCapability.mean} mm</span>
              <span className="text-gray-700">표준편차: {selectedCapability.stdDev} mm</span>
              <span className="text-gray-700">표본크기: {selectedCapability.sampleSize}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Capability 지침 설명 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5 text-purple-600" />
            공정능력 지표 해석
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="font-semibold text-green-900">우수 (≥ 1.67)</span>
              </div>
              <p className="text-sm text-green-700">
                6시그마 수준, 공정 능력 매우 우수
              </p>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-blue-900">양호 (1.33 - 1.67)</span>
              </div>
              <p className="text-sm text-blue-700">
                4시그마 수준, 공정 능력 양호
              </p>
            </div>

            <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-5 h-5 text-yellow-600" />
                <span className="font-semibold text-yellow-900">한계 (1.0 - 1.33)</span>
              </div>
              <p className="text-sm text-yellow-700">
                3시그마 수준, 개선 필요
              </p>
            </div>

            <div className="p-4 bg-red-50 rounded-lg border border-red-200">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <span className="font-semibold text-red-900">부족 (&lt; 1.0)</span>
              </div>
              <p className="text-sm text-red-700">
                공정 능력 부족, 즉각적 개선 필요
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProcessCapabilityPage;

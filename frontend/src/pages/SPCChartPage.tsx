import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '../components/ui/Card';
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
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import {
  AlertTriangle,
  AlertCircle,
  Settings,
  RefreshCw,
  Plus,
  Link
} from 'lucide-react';
import { StatusBadge } from '../components/common';
import { spcService } from '../services/spcService';

// 샘플 데이터
const generateChartData = () => {
  const data = [];
  let value = 10.02;
  for (let i = 1; i <= 30; i++) {
    value += (Math.random() - 0.5) * 0.02;
    data.push({
      point: i,
      xbar: parseFloat(value.toFixed(3)),
      ucl: 10.05,
      cl: 10.00,
      lcl: 9.95,
    });
  }
  return data;
};

const chartData = generateChartData();

export const SPCChartPage: React.FC = () => {
  const [selectedChart, setSelectedChart] = useState('XBAR_R');
  const [loading, setLoading] = useState(false);

  const violations = [
  }
];

export const SPCChartPage: React.FC = () => {
  const [selectedProduct, setSelectedProduct] = useState('1');
  const [selectedCharacteristic, setSelectedCharacteristic] = useState('1');
  const [dateRange, setDateRange] = useState('30d');

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">SPC 관리도</h1>
          <p className="text-sm text-gray-500 mt-1">
            통계적 공정관리 및 관리도 분석
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            베이스라인 재설정
          </Button>
          <Button variant="outline">
            <Plus className="w-4 h-4 mr-2" />
            이상 이벤트 생성
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Link className="w-4 h-4 mr-2" />
            CAPA 연결
          </Button>
        </div>
      </div>

      {/* 필터 영역 */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">품목</label>
              <Select value={selectedProduct} onValueChange={setSelectedProduct}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">브레이크 패드</SelectItem>
                  <SelectItem value="2">클러치 디스크</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">공정</label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="공정 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">CNC 가공</SelectItem>
                  <SelectItem value="2">세척</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">CTQ</label>
              <Select value={selectedCharacteristic} onValueChange={setSelectedCharacteristic}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">내경</SelectItem>
                  <SelectItem value="2">외경</SelectItem>
                  <SelectItem value="3">깊이</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">기간</label>
              <Select value={dateRange} onValueChange={setDateRange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">최근 7일</SelectItem>
                  <SelectItem value="30d">최근 30일</SelectItem>
                  <SelectItem value="90d">최근 90일</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 관리도 차트 영역 */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <LineChart className="w-5 h-5 text-purple-600" />
                  X-bar & R Chart
                </div>
                <div className="flex gap-2">
                  <Badge variant="outline" className="text-xs">UCL: 10.05</Badge>
                  <Badge variant="outline" className="text-xs">CL: 10.00</Badge>
                  <Badge variant="outline" className="text-xs">LCL: 9.95</Badge>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="point" label={{ value: 'Sample', position: 'insideBottom', offset: -5 }} />
                  <YAxis label={{ value: 'Value (mm)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />

                  {/* 관리 한계선 */}
                  <ReferenceLine y={10.05} stroke="red" strokeDasharray="5 5" label="UCL" />
                  <ReferenceLine y={10.00} stroke="gray" strokeDasharray="3 3" label="CL" />
                  <ReferenceLine y={9.95} stroke="red" strokeDasharray="5 5" label="LCL" />

                  {/* 데이터 라인 */}
                  <Line
                    type="monotone"
                    dataKey="xbar"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    dot={(props) => {
                      const violation = violations.find(v => v.point === props.payload.point);
                      if (violation) {
                        return (
                          <AlertTriangle
                            className={`w-4 h-4 ${
                              violation.severity === 'high'
                                ? 'text-red-600 fill-red-100'
                                : violation.severity === 'medium'
                                ? 'text-orange-600 fill-orange-100'
                                : 'text-yellow-600 fill-yellow-100'
                            }`}
                          />
                        );
                      }
                      return <circle r={3} fill="#8b5cf6" />;
                    }}
                  />
                </LineChart>
              </ResponsiveContainer>

              {/* 범례 */}
              <div className="mt-4 flex items-center justify-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-purple-500 rounded"></div>
                  <span>측정값</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-0.5 bg-red-500 border-t-2 border-dashed"></div>
                  <span>관리 한계 (UCL/LCL)</span>
                </div>
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <span>위반 포인트</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 위반 리스트 */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-600" />
                Run Rule 위반
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {violations.map((violation) => (
                  <div
                    key={violation.id}
                    className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <Badge
                        variant={violation.severity === 'high' ? 'destructive' : 'outline'}
                        className={violation.severity === 'medium' ? 'bg-orange-100 text-orange-700' : ''}
                      >
                        {violation.ruleCode}
                      </Badge>
                      <StatusBadge status={violation.severity === 'high' ? 'OOS' : 'HOLD'} />
                    </div>
                    <p className="text-sm font-medium text-gray-800 mb-1">
                      {violation.ruleName}
                    </p>
                    <p className="text-xs text-gray-600">{violation.description}</p>
                    <div className="mt-2 flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1 text-xs">
                        상세
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1 text-xs">
                        CAPA
                      </Button>
                    </div>
                  </div>
                ))}

                {violations.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <CheckCircle className="w-12 h-12 mx-auto mb-3 opacity-50 text-green-500" />
                    <p className="text-sm">위반 없음</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

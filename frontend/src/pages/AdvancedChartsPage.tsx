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
  BarChart3,
  TrendingUp,
  Settings,
  AlertCircle,
  CheckCircle,
  Target,
  Activity,
  LineChart as LineChartIcon
} from 'lucide-react';
import {
  LineChart,
  Line,
  ReferenceLine,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart
} from 'recharts';

interface ChartType {
  id: string;
  name: string;
  description: string;
  useCase: string;
  sensitivity: 'HIGH' | 'MEDIUM' | 'LOW';
}

interface AnalysisResult {
  chartType: string;
  ucl: number;
  cl: number;
  lcl: number;
  violations: number;
  points: Array<{ point: number; value: number; ucl: number; cl: number; lcl: number }>;
}

// Custom tooltip for chart
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
        <p className="text-sm font-medium text-gray-900">Point #{label}</p>
        <p className="text-sm text-gray-600">측정값: <span className="font-bold text-purple-600">{data.value.toFixed(3)}</span></p>
        <p className="text-xs text-gray-500 mt-1">UCL: {data.ucl} | CL: {data.cl} | LCL: {data.lcl}</p>
        {data.isViolation && (
          <p className="text-xs text-red-600 mt-1 font-medium">⚠️ 관리선 이탈</p>
        )}
      </div>
    );
  }
  return null;
};

// Generate sample data with violations
const generateSampleData = () => {
  const baseValue = 10.0;
  const ucl = 10.05;
  const lcl = 9.95;
  const violationPoints = [12, 19, 26]; // Points that will violate control limits

  return Array.from({ length: 30 }, (_, i) => {
    const pointNum = i + 1;
    let value;

    if (violationPoints.includes(pointNum)) {
      // Generate values outside control limits for violation points
      value = pointNum === 12 ? 10.08 : pointNum === 19 ? 9.92 : 10.07;
    } else {
      // Generate random values within control limits
      value = baseValue + (Math.random() - 0.5) * 0.08;
    }

    return {
      point: pointNum,
      value: Number(value.toFixed(3)),
      ucl,
      cl: 10.0,
      lcl,
      isViolation: violationPoints.includes(pointNum),
    };
  });
};

export const AdvancedChartsPage: React.FC = () => {
  const [selectedChart, setSelectedChart] = useState<string>('CUSUM');
  const [selectedProduct, setSelectedProduct] = useState<string>('1');
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const chartTypes: ChartType[] = [
    {
      id: 'CUSUM',
      name: 'CUSUM 관리도',
      description: '累积合 관리도 - 작은 변동을 감지하는 데 탁월',
      useCase: '미세한 공정 이동 감지, 오프셋 변화 감지',
      sensitivity: 'HIGH',
    },
    {
      id: 'EWMA',
      name: 'EWMA 관리도',
      description: '지수가중이동평균 관리도 - 작은 변동 감지에 적합',
      useCase: '자동상관 데이터, 점진적 트렌드 변화 감지',
      sensitivity: 'HIGH',
    },
    {
      id: 'MA',
      name: '이동평균 관리도',
      description: '이동평균을 사용한 관리도 - 노이즈 감소',
      useCase: '변동성이 큰 공정, 단기 변동 평활화',
      sensitivity: 'MEDIUM',
    },
    {
      id: 'PRE_CONTROL',
      name: '사전 관리도',
      description: '규격 내 영역을 색상으로 구분',
      useCase: '설정 초기 단계, 신속한 피드백',
      sensitivity: 'MEDIUM',
    },
  ];

  const products = [
    { id: '1', name: '브레이크 패드 - 내경', cpk: 1.45 },
    { id: '2', name: '브레이크 패드 - 외경', cpk: 1.28 },
    { id: '3', name: '브레이크 패드 - 두께', cpk: 1.67 },
  ];

  const handleAnalyze = () => {
    const sampleData = generateSampleData();
    const violations = sampleData.filter(d => d.isViolation);

    setResults({
      chartType: selectedChart,
      ucl: 10.05,
      cl: 10.00,
      lcl: 9.95,
      violations: violations.length,
      points: sampleData,
    });
  };

  const selectedChartInfo = chartTypes.find(c => c.id === selectedChart);

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">고급 관리도</h1>
          <p className="text-sm text-gray-500 mt-1">
            CUSUM, EWMA 등 특수 관리도 분석
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            파라미터 설정
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700" onClick={handleAnalyze}>
            <BarChart3 className="w-4 h-4 mr-2" />
            분석 실행
          </Button>
        </div>
      </div>

      {/* 관리도 유형 선택 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {chartTypes.map((chart) => (
          <Card
            key={chart.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedChart === chart.id
                ? 'border-2 border-purple-600 bg-purple-50'
                : 'border border-gray-200'
            }`}
            onClick={() => setSelectedChart(chart.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between mb-2">
                <CardTitle className="text-lg">{chart.name}</CardTitle>
                {selectedChart === chart.id && (
                  <CheckCircle className="w-5 h-5 text-purple-600" />
                )}
              </div>
              <Badge className={
                chart.sensitivity === 'HIGH'
                  ? 'bg-red-100 text-red-700'
                  : chart.sensitivity === 'MEDIUM'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-green-100 text-green-700'
              }>
                감도: {chart.sensitivity === 'HIGH' ? '높음' : chart.sensitivity === 'MEDIUM' ? '중간' : '낮음'}
              </Badge>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-2">{chart.description}</p>
              <div className="text-xs text-gray-500">
                <div className="font-medium mb-1">용도:</div>
                <div>{chart.useCase}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 분석 조건 설정 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-purple-600" />
            분석 조건
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">제품/특성</label>
              <Select value={selectedProduct} onValueChange={setSelectedProduct}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {products.map((product) => (
                    <SelectItem key={product.id} value={product.id}>
                      <div className="flex items-center justify-between w-full">
                        <span>{product.name}</span>
                        <Badge variant="outline" className="ml-2 text-xs">
                          Cpk {product.cpk}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">표본 크기</label>
              <Select defaultValue="5">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3">3</SelectItem>
                  <SelectItem value="5">5</SelectItem>
                  <SelectItem value="10">10</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">분석 기간</label>
              <Select defaultValue="30">
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
          </div>

          {selectedChartInfo && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-blue-600" />
                <span className="font-semibold text-blue-900">{selectedChartInfo.name} 특징</span>
              </div>
              <p className="text-sm text-blue-700">{selectedChartInfo.useCase}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 분석 결과 */}
      {results && (
        <>
          {/* 요약 통계 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-500 mb-1">상한선 (UCL)</div>
                    <div className="text-2xl font-bold text-gray-900">{results.ucl}</div>
                  </div>
                  <TrendingUp className="w-8 h-8 text-red-500 opacity-50" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-500 mb-1">중심선 (CL)</div>
                    <div className="text-2xl font-bold text-gray-900">{results.cl}</div>
                  </div>
                  <Activity className="w-8 h-8 text-gray-500 opacity-50" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-500 mb-1">하한선 (LCL)</div>
                    <div className="text-2xl font-bold text-gray-900">{results.lcl}</div>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-500 opacity-50 rotate-180" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-purple-100 mb-1">검출된 이상</div>
                    <div className="text-2xl font-bold">{results.violations}건</div>
                  </div>
                  <AlertCircle className="w-8 h-8 text-purple-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 차트 영역 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChartIcon className="w-5 h-5 text-purple-600" />
                {selectedChartInfo?.name}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={results.points}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                      dataKey="point"
                      label={{ value: '샘플 번호', position: 'insideBottom', offset: -5 }}
                      stroke="#6b7280"
                    />
                    <YAxis
                      label={{ value: '측정값', angle: -90, position: 'insideLeft' }}
                      stroke="#6b7280"
                      domain={[9.90, 10.10]}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <ReferenceLine
                      y={results.ucl}
                      label="UCL"
                      stroke="#ef4444"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                    />
                    <ReferenceLine
                      y={results.cl}
                      label="CL"
                      stroke="#6b7280"
                      strokeWidth={2}
                    />
                    <ReferenceLine
                      y={results.lcl}
                      label="LCL"
                      stroke="#ef4444"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#8b5cf6"
                      strokeWidth={2}
                      dot={(props: any) => {
                        const { cx, cy, payload } = props;
                        if (payload.isViolation) {
                          return (
                            <g>
                              <circle
                                cx={cx}
                                cy={cy}
                                r={6}
                                fill="#ef4444"
                                stroke="#ffffff"
                                strokeWidth={2}
                              />
                            </g>
                          );
                        }
                        return (
                          <circle
                            cx={cx}
                            cy={cy}
                            r={4}
                            fill="#8b5cf6"
                            stroke="#ffffff"
                            strokeWidth={1}
                          />
                        );
                      }}
                      activeDot={{ r: 6, stroke: '#ffffff', strokeWidth: 2 }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>

              {/* 차트 설명 */}
              <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-1 bg-purple-500"></div>
                    <span className="text-gray-700">측정값 데이터</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-1 bg-red-500 border-dashed border-t-2 border-red-500"></div>
                    <span className="text-gray-700">관리 상한선/하한선 (UCL/LCL)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-red-500"></div>
                    <span className="text-gray-700">관리선 이탈 포인트 ({results.violations}건)</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 위반 목록 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-600" />
                이상 검출 목록
                <Badge variant="outline" className="ml-2">
                  {results.violations}건
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {results.points.filter(p => p.isViolation).map((point) => (
                  <div key={point.point} className="p-4 bg-white rounded-lg border border-gray-200 hover:border-orange-300 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-orange-100 rounded-lg">
                          <AlertCircle className="w-5 h-5 text-orange-600" />
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">Point #{point.point}</div>
                          <div className="text-sm text-gray-500">
                            측정값: {point.value} {point.value > results.ucl ? '(UCL 초과)' : '(LCL 미달)'}
                          </div>
                        </div>
                      </div>
                      <Badge className="bg-red-100 text-red-700">
                        중요도: 높음
                      </Badge>
                    </div>
                  </div>
                ))}

                {results.violations === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
                    <p>검출된 이상이 없습니다</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* 초기 상태 메시지 */}
      {!results && (
        <Card>
          <CardContent className="text-center py-16">
            <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">고급 관리도 분석</h3>
            <p className="text-gray-500 mb-6">
              관리도 유형을 선택하고 분석 조건을 설정한 후 분석을 실행하세요
            </p>
            <div className="flex justify-center gap-4 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                <span>관리도 유형 선택</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                <span>분석 조건 설정</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                <span>분석 실행</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AdvancedChartsPage;

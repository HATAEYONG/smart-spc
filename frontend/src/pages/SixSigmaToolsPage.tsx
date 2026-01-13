import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import {
  Sigma,
  BarChart3,
  AlignCenterVertical,
  TrendingUp,
  PieChart,
  Crosshair,
  Activity,
  GitBranch,
  Calculator,
  Box,
  ScatterChart,
  CheckCircle
} from 'lucide-react';

interface ToolType {
  id: string;
  name: string;
  description: string;
  category: 'DESCRIPTIVE' | 'GRAPHICAL' | 'INFERENCE' | 'CAPABILITY';
  icon: any;
  color: string;
  inputs?: string[];
}

interface AnalysisResult {
  tool: string;
  timestamp: string;
  summary: string;
  metrics: Record<string, number | string>;
  interpretation: string;
}

export const SixSigmaToolsPage: React.FC = () => {
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [inputData, setInputData] = useState<string>('');
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [lsl, setLsl] = useState<string>('');
  const [usl, setUsl] = useState<string>('');
  const [target, setTarget] = useState<string>('');

  const tools: ToolType[] = [
    {
      id: 'descriptive',
      name: '기술 통계',
      description: '평균, 표준편차, 왜도, 첨도 등 기술통계량 계산',
      category: 'DESCRIPTIVE',
      icon: Calculator,
      color: 'bg-blue-100 text-blue-700',
    },
    {
      id: 'histogram',
      name: '히스토그램',
      description: '데이터 분포 시각화 및 정규성 확인',
      category: 'GRAPHICAL',
      icon: BarChart3,
      color: 'bg-green-100 text-green-700',
    },
    {
      id: 'boxplot',
      name: '상자 수염 그림',
      description: '데이터 분포와 이상치 확인',
      category: 'GRAPHICAL',
      icon: AlignCenterVertical,
      color: 'bg-teal-100 text-teal-700',
    },
    {
      id: 'pareto',
      name: '파레토도',
      description: '80/20 법칙을 통한 중요 요인 식별',
      category: 'GRAPHICAL',
      icon: PieChart,
      color: 'bg-purple-100 text-purple-700',
    },
    {
      id: 'scatter',
      name: '산점도',
      description: '두 변수 간의 관계 시각화',
      category: 'GRAPHICAL',
      icon: ScatterChart,
      color: 'bg-pink-100 text-pink-700',
    },
    {
      id: 'correlation',
      name: '상관 분석',
      description: '두 변수 간의 상관계수 및 유의성 검정',
      category: 'INFERENCE',
      icon: Crosshair,
      color: 'bg-orange-100 text-orange-700',
    },
    {
      id: 'ttest',
      name: 'T-검정',
      description: '두 그룹 간 평균 차이 검정 (1-sample, 2-sample)',
      category: 'INFERENCE',
      icon: Activity,
      color: 'bg-indigo-100 text-indigo-700',
    },
    {
      id: 'anova',
      name: '분산분석 (ANOVA)',
      description: '세 그룹 이상 평균 차이 검정',
      category: 'INFERENCE',
      icon: GitBranch,
      color: 'bg-cyan-100 text-cyan-700',
    },
    {
      id: 'capability',
      name: '공정능력 분석',
      description: 'Cp, Cpk, Pp, Ppk 지수 계산 및 Six Sigma 수준 평가',
      category: 'CAPABILITY',
      icon: TrendingUp,
      color: 'bg-red-100 text-red-700',
      inputs: ['lsl', 'usl', 'target'],
    },
  ];

  const getCategoryConfig = (category: string) => {
    switch (category) {
      case 'DESCRIPTIVE':
        return { label: '기술 통계', color: 'bg-blue-50 border-blue-200' };
      case 'GRAPHICAL':
        return { label: '그래프', color: 'bg-green-50 border-green-200' };
      case 'INFERENCE':
        return { label: '추론 통계', color: 'bg-purple-50 border-purple-200' };
      case 'CAPABILITY':
        return { label: '공정능력', color: 'bg-red-50 border-red-200' };
      default:
        return { label: category, color: 'bg-gray-50 border-gray-200' };
    }
  };

  const handleToolSelect = (toolId: string) => {
    setSelectedTool(toolId);
    setInputData('');
    setLsl('');
    setUsl('');
    setTarget('');
  };

  const handleAnalyze = () => {
    if (!selectedTool || !inputData.trim()) return;

    const dataPoints = inputData.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));

    if (dataPoints.length < 2) {
      alert('최소 2개 이상의 데이터가 필요합니다.');
      return;
    }

    // Generate sample results
    const mean = (dataPoints.reduce((a, b) => a + b, 0) / dataPoints.length).toFixed(3);
    const stdDev = Math.sqrt(dataPoints.reduce((sq, n) => sq + Math.pow(n - parseFloat(mean), 2), 0) / dataPoints.length).toFixed(3);

    const result: AnalysisResult = {
      tool: tools.find(t => t.id === selectedTool)?.name || '',
      timestamp: new Date().toLocaleString('ko-KR'),
      summary: `${dataPoints.length}개 데이터 포인트 분석 완료`,
      metrics: {
        '표본 크기': dataPoints.length,
        '평균': mean,
        '표준편차': stdDev,
        '최소값': Math.min(...dataPoints).toFixed(3),
        '최대값': Math.max(...dataPoints).toFixed(3),
      },
      interpretation: '데이터가 정규 분포를 따르는 것으로 보입니다. 추가적인 정규성 검정이 권장됩니다.',
    };

    setResults([result, ...results]);
  };

  const sampleResults: AnalysisResult[] = [
    {
      tool: '공정능력 분석',
      timestamp: '2026-01-12 10:30:00',
      summary: '브레이크 패드 내경 공정능력 분석',
      metrics: {
        'Cp': '1.67',
        'Cpk': '1.45',
        'Pp': '1.55',
        'Ppk': '1.42',
        'Sigma Level': '4.35σ',
      },
      interpretation: '공정 능력이 우수합니다 (Cpk ≥ 1.33). Six Sigma 수준 도달을 위해 개선이 필요합니다.',
    },
    {
      tool: '파레토도',
      timestamp: '2026-01-12 09:15:00',
      summary: '불량 유형별 파레토 분석',
      metrics: {
        '총 불량수': '145건',
        'TOP 3 불량': '85% (123건)',
        '주요 불량': '치수불량 (62%)',
      },
      interpretation: '치수불량이 전체 불량의 62%를 차지합니다. 이에 대한 집중적 개선이 필요합니다.',
    },
  ];

  const displayedResults = results.length > 0 ? results : sampleResults;

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Sigma className="w-8 h-8 text-purple-600" />
            Six Sigma 통계 도구
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Minitab 스타일의 통계 분석 도구 모음
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <BarChart3 className="w-4 h-4 mr-2" />
            분석 기록
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <CheckCircle className="w-4 h-4 mr-2" />
            결과 내보내기
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-purple-100 mb-1">사용 가능 도구</div>
                <div className="text-3xl font-bold">{tools.length}개</div>
              </div>
              <Sigma className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">분석 완료</div>
                <div className="text-2xl font-bold text-gray-900">{displayedResults.length}회</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">DESCRIPTIVE</div>
                <div className="text-2xl font-bold text-blue-600">
                  {tools.filter(t => t.category === 'DESCRIPTIVE').length}개
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">INFERENCE</div>
                <div className="text-2xl font-bold text-purple-600">
                  {tools.filter(t => t.category === 'INFERENCE').length}개
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 도구 선택 패널 */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-600" />
                분석 도구 선택
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {tools.map((tool) => {
                  const Icon = tool.icon;
                  const isSelected = selectedTool === tool.id;

                  return (
                    <button
                      key={tool.id}
                      onClick={() => handleToolSelect(tool.id)}
                      className={`w-full p-3 rounded-lg border-2 text-left transition-all ${
                        isSelected
                          ? 'border-purple-500 bg-purple-50 shadow-md'
                          : 'border-gray-200 hover:border-purple-300 hover:bg-purple-50/50'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${tool.color} flex-shrink-0`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-sm">{tool.name}</div>
                          <div className="text-xs text-gray-500 truncate">{tool.description}</div>
                        </div>
                        {isSelected && (
                          <CheckCircle className="w-5 h-5 text-purple-600 flex-shrink-0" />
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* 도구 설명 */}
          {selectedTool && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="text-lg">도구 설명</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">분석 유형</div>
                    <Badge className={getCategoryConfig(tools.find(t => t.id === selectedTool)?.category || '').color}>
                      {getCategoryConfig(tools.find(t => t.id === selectedTool)?.category || '').label}
                    </Badge>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">설명</div>
                    <p className="text-sm text-gray-600">
                      {tools.find(t => t.id === selectedTool)?.description}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 분석 영역 */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-600" />
                {selectedTool ? tools.find(t => t.id === selectedTool)?.name : '분석 도구 선택'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedTool ? (
                <div className="space-y-4">
                  {/* 데이터 입력 */}
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">
                      데이터 입력 <span className="text-xs text-gray-500">(쉼표로 구분)</span>
                    </label>
                    <textarea
                      value={inputData}
                      onChange={(e) => setInputData(e.target.value)}
                      className="w-full h-24 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="예: 10.01, 10.02, 10.00, 10.03, 10.01, 10.08, 10.05, 10.03, 10.07, 10.02"
                    />
                    <p className="mt-2 text-xs text-gray-500">
                      숫자 데이터를 쉼표로 구분하여 입력하세요 (최소 2개 이상)
                    </p>
                  </div>

                  {/* 공정능력 분석 추가 입력 */}
                  {selectedTool === 'capability' && (
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-700 mb-2 block">
                          LSL (하한 규격)
                        </label>
                        <Input
                          type="number"
                          step="0.001"
                          value={lsl}
                          onChange={(e) => setLsl(e.target.value)}
                          placeholder="9.95"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 mb-2 block">
                          USL (상한 규격)
                        </label>
                        <Input
                          type="number"
                          step="0.001"
                          value={usl}
                          onChange={(e) => setUsl(e.target.value)}
                          placeholder="10.05"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700 mb-2 block">
                          Target (목표값)
                        </label>
                        <Input
                          type="number"
                          step="0.001"
                          value={target}
                          onChange={(e) => setTarget(e.target.value)}
                          placeholder="10.00"
                        />
                      </div>
                    </div>
                  )}

                  {/* 분석 실행 버튼 */}
                  <Button
                    className="w-full bg-purple-600 hover:bg-purple-700"
                    onClick={handleAnalyze}
                    disabled={!inputData.trim()}
                  >
                    <Activity className="w-4 h-4 mr-2" />
                    분석 실행
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <Sigma className="w-16 h-16 text-gray-300 mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">분석 도구 선택</h3>
                  <p className="text-gray-500 max-w-md">
                    왼쪽 패널에서 통계 분석 도구를 선택하면 데이터 입력 영역이 표시됩니다.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 최근 분석 결과 */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-purple-600" />
                최근 분석 결과
                <Badge variant="outline">{displayedResults.length}건</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {displayedResults.map((result, idx) => (
                  <div key={idx} className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-all">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="font-semibold text-gray-900">{result.tool}</div>
                        <div className="text-sm text-gray-600">{result.summary}</div>
                        <div className="text-xs text-gray-500 mt-1">{result.timestamp}</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                      {Object.entries(result.metrics).map(([key, value]) => (
                        <div key={key} className="text-center p-2 bg-gray-50 rounded">
                          <div className="text-xs text-gray-500">{key}</div>
                          <div className="text-lg font-bold text-purple-600">{value}</div>
                        </div>
                      ))}
                    </div>

                    <div className="p-3 bg-blue-50 rounded border border-blue-200">
                      <div className="text-sm text-blue-900">
                        <span className="font-semibold">해석:</span> {result.interpretation}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 빠른 참조 가이드 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-purple-600" />
            통계 도구 빠른 참조
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <Calculator className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-blue-900">기술 통계</span>
              </div>
              <p className="text-sm text-blue-800">
                데이터의 중심 경향과 산포를 파악합니다. 평균, 중앙값, 표준편차, 왜도, 첨도 등을 제공합니다.
              </p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
              <div className="flex items-center gap-2 mb-2">
                <PieChart className="w-5 h-5 text-purple-600" />
                <span className="font-semibold text-purple-900">파레토도</span>
              </div>
              <p className="text-sm text-purple-800">
                80/20 법칙을 적용하여 가장 중요한 요인을 식별합니다. 품질 문제의 원인 분석에 사용합니다.
              </p>
            </div>

            <div className="p-4 bg-red-50 rounded-lg border border-red-200">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-red-600" />
                <span className="font-semibold text-red-900">공정능력</span>
              </div>
              <p className="text-sm text-red-800">
                Cp, Cpk 지수를 통해 공정이 규격을 만족하는 능력을 평가합니다. Six Sigma 수준을 확인합니다.
              </p>
            </div>

            <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-indigo-600" />
                <span className="font-semibold text-indigo-900">T-검정/ANOVA</span>
              </div>
              <p className="text-sm text-indigo-800">
                그룹 간 평균 차이가 통계적으로 유의한지 검정합니다. 개선 효과 검증에 사용합니다.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SixSigmaToolsPage;

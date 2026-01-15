/**
 * 치공구 예측 고도화 페이지
 * AI 기반 치공구 수명 예측 및 최적 교체 시점 제안
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Brain,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  BarChart3,
  Zap,
  Settings,
  Download,
  RefreshCw,
  Calendar,
  Activity,
  DollarSign,
  Wrench,
  LineChart
} from 'lucide-react';

interface ToolPredictionData {
  id: number;
  code: string;
  name: string;
  current_usage: number;
  useful_life: number;
  predicted_remaining_days: number;
  optimal_replacement_date: string;
  confidence_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  predicted_failure_date: string;
  cost_savings: number;
  recommendation: string;
}

interface PredictionModel {
  name: string;
  accuracy: number;
  last_trained: string;
  status: 'ACTIVE' | 'TRAINING' | 'NEEDS_UPDATE';
}

const mockPredictionData: ToolPredictionData[] = [
  {
    id: 1,
    code: 'TOL-001',
    name: '프레스 금형 Type-A',
    current_usage: 8500,
    useful_life: 10000,
    predicted_remaining_days: 15,
    optimal_replacement_date: '2025-02-01',
    confidence_score: 94.5,
    risk_level: 'MEDIUM',
    predicted_failure_date: '2025-02-20',
    cost_savings: 2500000,
    recommendation: '교체 권장: 15일 내 교체 시 비용 절감 예상'
  },
  {
    id: 2,
    code: 'TOL-002',
    name: '컷터 공구 10mm',
    current_usage: 9200,
    useful_life: 10000,
    predicted_remaining_days: 7,
    optimal_replacement_date: '2025-01-24',
    confidence_score: 97.2,
    risk_level: 'HIGH',
    predicted_failure_date: '2025-01-31',
    cost_savings: 1800000,
    recommendation: '긴급 교체 필요: 7일 내 불량률 급증 예상'
  },
  {
    id: 3,
    code: 'TOL-003',
    name: '드릴 비트 5mm',
    current_usage: 4500,
    useful_life: 10000,
    predicted_remaining_days: 45,
    optimal_replacement_date: '2025-03-05',
    confidence_score: 89.3,
    risk_level: 'LOW',
    predicted_failure_date: '2025-04-15',
    cost_savings: 1200000,
    recommendation: '정상 범위: 정기 검사 후 사용 가능'
  },
  {
    id: 4,
    code: 'TOL-004',
    name: '연마 디스크 200mm',
    current_usage: 9800,
    useful_life: 10000,
    predicted_remaining_days: 3,
    optimal_replacement_date: '2025-01-20',
    confidence_score: 98.5,
    risk_level: 'CRITICAL',
    predicted_failure_date: '2025-01-23',
    cost_savings: 3200000,
    recommendation: '즉시 교체 필수: 3일 내 파손 위험 높음'
  },
  {
    id: 5,
    code: 'TOL-005',
    name: '탭 M6',
    current_usage: 7200,
    useful_life: 10000,
    predicted_remaining_days: 22,
    optimal_replacement_date: '2025-02-10',
    confidence_score: 91.8,
    risk_level: 'LOW',
    predicted_failure_date: '2025-03-05',
    cost_savings: 950000,
    recommendation: '주의 필요: 정기 모니터링 권장'
  },
];

const mockModels: PredictionModel[] = [
  {
    name: 'LSTM 시계열 예측 모델',
    accuracy: 94.5,
    last_trained: '2025-01-10',
    status: 'ACTIVE'
  },
  {
    name: 'Random Forest 회귀 모델',
    accuracy: 89.2,
    last_trained: '2025-01-08',
    status: 'ACTIVE'
  },
  {
    name: 'XGBoost 부품 실패 예측',
    accuracy: 96.8,
    last_trained: '2025-01-12',
    status: 'ACTIVE'
  },
];

const ToolPredictionPage: React.FC = () => {
  const [predictions, setPredictions] = useState<ToolPredictionData[]>(mockPredictionData);
  const [models] = useState<PredictionModel[]>(mockModels);
  const [selectedModel, setSelectedModel] = useState(mockModels[2].name);
  const [isTraining, setIsTraining] = useState(false);
  const [filterStatus, setFilterStatus] = useState<'ALL' | 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'>('ALL');

  const getRiskBadge = (risk: string) => {
    const styles = {
      CRITICAL: 'bg-red-100 text-red-800 border-red-300',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      LOW: 'bg-green-100 text-green-800 border-green-300',
    };
    const labels = {
      CRITICAL: '긴급',
      HIGH: '높음',
      MEDIUM: '중간',
      LOW: '낮음',
    };
    return (
      <Badge className={styles[risk as keyof typeof styles]}>
        {labels[risk as keyof typeof labels]}
      </Badge>
    );
  };

  const getUsagePercentage = (current: number, total: number) => {
    return (current / total) * 100;
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const filteredPredictions = filterStatus === 'ALL'
    ? predictions
    : predictions.filter(p => p.risk_level === filterStatus);

  const totalTools = predictions.length;
  const criticalCount = predictions.filter(p => p.risk_level === 'CRITICAL').length;
  const highCount = predictions.filter(p => p.risk_level === 'HIGH').length;
  const avgConfidence = (predictions.reduce((sum, p) => sum + p.confidence_score, 0) / predictions.length).toFixed(1);
  const totalCostSavings = predictions.reduce((sum, p) => sum + p.cost_savings, 0);

  const handleRetrainModel = async () => {
    setIsTraining(true);
    // 모델 재학습 시뮬레이션
    setTimeout(() => {
      setIsTraining(false);
      alert('모델 재학습이 완료되었습니다. 정확도가 0.5% 개선되었습니다.');
    }, 3000);
  };

  const handleExportPredictions = () => {
    const dataStr = JSON.stringify(predictions, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tool-predictions-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Brain className="w-8 h-8 text-purple-600" />
            치공구 예측 고도화
          </h1>
          <p className="text-gray-600 mt-2">
            AI 기반 수명 예측 및 최적 교체 시점 제안으로 비용 절감 및 생산성 향상
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleExportPredictions}
            className="flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            내보내기
          </Button>
          <Button
            onClick={handleRetrainModel}
            disabled={isTraining}
            className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700"
          >
            <RefreshCw className={`w-4 h-4 ${isTraining ? 'animate-spin' : ''}`} />
            {isTraining ? '재학습 중...' : '모델 재학습'}
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-l-4 border-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">예측 대상 치공구</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{totalTools}</p>
              </div>
              <Wrench className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-red-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">긴급/높음 위험</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{criticalCount + highCount}</p>
                <p className="text-xs text-red-500 mt-1">즉시 조치 필요</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-red-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">평균 예측 신뢰도</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">{avgConfidence}%</p>
                <p className="text-xs text-blue-500 mt-1">높은 정확도</p>
              </div>
              <Target className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">예상 비용 절감</p>
                <p className="text-3xl font-bold text-green-600 mt-1">
                  {(totalCostSavings / 1000000).toFixed(1)}M
                </p>
                <p className="text-xs text-green-500 mt-1">원화 절감 예상</p>
              </div>
              <DollarSign className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Models Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            AI 예측 모델 현황
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {models.map((model, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedModel === model.name
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
                onClick={() => setSelectedModel(model.name)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">{model.name}</h4>
                  <Badge
                    className={
                      model.status === 'ACTIVE'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }
                  >
                    {model.status === 'ACTIVE' ? '활성' : '학습중'}
                  </Badge>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">정확도</span>
                    <span className="font-semibold text-blue-600">{model.accuracy}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">마지막 학습</span>
                    <span className="text-gray-900">{model.last_trained}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Predictions Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              치공구별 예측 결과
            </CardTitle>
            <div className="flex gap-2">
              {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((status) => (
                <Button
                  key={status}
                  variant={filterStatus === status ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterStatus(status)}
                  className={filterStatus === status ? 'bg-purple-600 hover:bg-purple-700' : ''}
                >
                  {status === 'ALL' ? '전체' :
                   status === 'CRITICAL' ? '긴급' :
                   status === 'HIGH' ? '높음' :
                   status === 'MEDIUM' ? '중간' : '낮음'}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left p-4 font-semibold text-gray-700">치공구 코드</th>
                  <th className="text-left p-4 font-semibold text-gray-700">치공구명</th>
                  <th className="text-left p-4 font-semibold text-gray-700">사용량</th>
                  <th className="text-left p-4 font-semibold text-gray-700">잔존 수명</th>
                  <th className="text-left p-4 font-semibold text-gray-700">최적 교체일</th>
                  <th className="text-left p-4 font-semibold text-gray-700">위험도</th>
                  <th className="text-left p-4 font-semibold text-gray-700">신뢰도</th>
                  <th className="text-left p-4 font-semibold text-gray-700">비용 절감</th>
                  <th className="text-left p-4 font-semibold text-gray-700">AI 추천</th>
                </tr>
              </thead>
              <tbody>
                {filteredPredictions.map((prediction) => {
                  const usagePercent = getUsagePercentage(prediction.current_usage, prediction.useful_life);
                  return (
                    <tr key={prediction.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="p-4 font-medium text-purple-600">{prediction.code}</td>
                      <td className="p-4">{prediction.name}</td>
                      <td className="p-4">
                        <div className="w-48">
                          <div className="flex justify-between text-sm mb-1">
                            <span>{prediction.current_usage.toLocaleString()}</span>
                            <span className="text-gray-600">/ {prediction.useful_life.toLocaleString()}</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${getUsageColor(usagePercent)}`}
                              style={{ width: `${Math.min(usagePercent, 100)}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-gray-500" />
                          <span className="font-semibold">{prediction.predicted_remaining_days}일</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-gray-500" />
                          <span>{prediction.optimal_replacement_date}</span>
                        </div>
                      </td>
                      <td className="p-4">{getRiskBadge(prediction.risk_level)}</td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <Target className="w-4 h-4 text-blue-500" />
                          <span className="font-semibold text-blue-600">{prediction.confidence_score}%</span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <DollarSign className="w-4 h-4 text-green-500" />
                          <span className="font-semibold text-green-600">
                            {(prediction.cost_savings / 10000).toFixed(0)}만원
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="max-w-xs">
                          <p className="text-sm text-gray-700">{prediction.recommendation}</p>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              AI 인사이트
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-red-900">긴급 조치 항목</h4>
                    <p className="text-sm text-red-700 mt-1">
                      TOL-004 (연마 디스크)가 3일 내 파손 위험이 있습니다. 즉시 교체를 권장합니다.
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-start gap-3">
                  <Clock className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-yellow-900">주의 필요 항목</h4>
                    <p className="text-sm text-yellow-700 mt-1">
                      TOL-002 (컷터 공구)가 7일 내 수명 종료 예상입니다. 주문을 준비하세요.
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start gap-3">
                  <TrendingUp className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-blue-900">최적화 제안</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      전체 치공구의 40%를 예측 기반으로 교체 시 연간 5,000만원 절감 효과가 있습니다.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <LineChart className="w-5 h-5 text-purple-500" />
              예측 성능 추이
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-600">모델 정확도</span>
                  <span className="text-sm font-semibold text-blue-600">94.5%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-blue-500 h-3 rounded-full" style={{ width: '94.5%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-600">예측 신뢰도</span>
                  <span className="text-sm font-semibold text-green-600">91.2%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-green-500 h-3 rounded-full" style={{ width: '91.2%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-600">비용 절감 달성률</span>
                  <span className="text-sm font-semibold text-purple-600">87.8%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-purple-500 h-3 rounded-full" style={{ width: '87.8%' }} />
                </div>
              </div>

              <div className="pt-4 border-t">
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-gray-900">12</p>
                    <p className="text-xs text-gray-600">예방된 고장</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-green-600">35h</p>
                    <p className="text-xs text-gray-600">절감 가동시간</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ToolPredictionPage;
export { ToolPredictionPage };

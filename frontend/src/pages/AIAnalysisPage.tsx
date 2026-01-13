import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import {
  Brain,
  Sparkles,
  Lightbulb,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Target,
  BarChart3,
  Zap
} from 'lucide-react';
import { AIResultPanel } from '../components/common';

interface AIInsight {
  id: string;
  type: 'PREDICTION' | 'ANOMALY' | 'OPTIMIZATION' | 'RISK';
  title: string;
  description: string;
  confidence: number;
  impact: 'high' | 'medium' | 'low';
  rationale: string[];
  assumptions: string[];
  risks: Array<{
    risk: string;
    probability: string;
    mitigation: string;
  }>;
  actionable: boolean;
  actions?: string[];
}

export const AIAnalysisPage: React.FC = () => {
  const [insights, setInsights] = useState<AIInsight[]>([
    {
      id: '1',
      type: 'PREDICTION',
      title: '치수불량률 예측',
      description: '향후 2주간 치수불량률이 12% 증가할 것으로 예측됩니다. 온도 보정 주기를 조정할 것을 권장합니다.',
      confidence: 0.89,
      impact: 'high',
      rationale: [
        '최근 3개월간 패턴 분석 결과, 온도 변동률과 치수불량률 간 상관계수 0.87',
        '공구 마모도가 85% 도달하여 정밀도 저하 예상',
        '기후 데이터 분석 시 습도 상승이 재질 변형에 영향',
      ],
      assumptions: [
        '현재 생산 속도 유지',
        '정비 일정 준수',
        '외부 온도 ±3°C 이내 변동',
      ],
      risks: [
        {
          risk: '공구 교체 지연 발생 시',
          probability: '중간',
          mitigation: '예비 공구 2개 이상 확보',
        }
      ],
      actionable: true,
      actions: [
        '공구 교체 주기 50시간 → 40시간으로 단축',
        '온도 보정 간격 2시간 → 1시간으로 변경',
        '작업자 교육 강화',
      ],
    },
    {
      id: '2',
      type: 'OPTIMIZATION',
      title: '세척 공정 최적화 기회',
      description: '초음파 세척 시간을 3분에서 5분으로 연장 시 이물 불량률이 15% 감소할 수 있습니다.',
      confidence: 0.92,
      impact: 'medium',
      rationale: [
        'DOE(실험계획법) 결과 세척 시간과 이물 제거율 간 양의 상관관계 확인',
        '현재 3분 세척 후 잔여 이물 검출률 8%',
        '5분 세척 시 잔여 이물 검출률 2%로 개선',
      ],
      assumptions: [
        '세척액 농도 10% 유지',
        '초음파 출력 80% 고정',
        '부하량 일정',
      ],
      risks: [
        {
          risk: '사이클 타임 증가로 생산성 저하',
          probability: '낮음',
          mitigation: '병렬 세척 라인 도입 검토',
        }
      ],
      actionable: true,
      actions: [
        '시험 가동 1주일 진행',
        '생산성 영향 평가',
        'SOP 수정 및 작업자 교육',
      ],
    },
    {
      id: '3',
      type: 'ANOMALY',
      title: '외경 규격 이탈 패턴 감지',
      description: '매주 화요일 오전 9-11시 사이 외경 규격 이탈 빈도가 평균 대비 2.3배 높습니다.',
      confidence: 0.76,
      impact: 'medium',
      rationale: [
        '지난 3개월간 데이터 분석 결과 화요일 오전 불량률 4.2% (전체 평균 1.8%)',
        '작업자 교대 시간과 중복',
        '기온 상승으로 인한 열팽창 가능성',
      ],
      assumptions: [
        '작업자 숙련도 일정',
        '장비 웜업 시간 준수',
      ],
      risks: [],
      actionable: true,
      actions: [
        '화요일 오전 샘플링 빈도 증가 (2시간 → 1시간)',
        '장비 웜업 시간 연장 (30분 → 45분)',
        '실온 안정화 조치 추가',
      ],
    },
    {
      id: '4',
      type: 'RISK',
      title: '균열 불량 리스크 상승',
      description: '열처리 로 온도 편차가 ±10°C로 확대되어 균열 불량 리스크가 증가하고 있습니다.',
      confidence: 0.81,
      impact: 'high',
      rationale: [
        '열전대 데이터 분석 결과 온도 편차 추이 확인',
        '균열 불량률이 0.5% → 1.2%로 증가',
        '열처리 로 노후화 지수 75% 도달',
      ],
      assumptions: [
        '현재 온도 제어 로직 유지',
        '예정된 정비 일정 준수',
      ],
      risks: [
        {
          risk: '균열 불량률이 2% 이상 시 폐기 비용 급증',
          probability: '높음',
          mitigation: '조기 장비 교체 또는 보수',
        }
      ],
      actionable: true,
      actions: [
        '긴급 정비 요청',
        '열전대 교체 (2개 중 1개)',
        '온도 제어 파라미터 재튜닝',
      ],
    },
  ]);

  const [selectedType, setSelectedType] = useState('ALL');

  const typeConfig = {
    PREDICTION: { label: '예측', icon: TrendingUp, color: 'bg-blue-100 text-blue-700' },
    ANOMALY: { label: '이상 감지', icon: AlertTriangle, color: 'bg-orange-100 text-orange-700' },
    OPTIMIZATION: { label: '최적화', icon: Zap, color: 'bg-green-100 text-green-700' },
    RISK: { label: '리스크', icon: AlertTriangle, color: 'bg-red-100 text-red-700' },
  };

  const impactConfig = {
    high: { label: '높음', color: 'bg-red-100 text-red-700' },
    medium: { label: '중간', color: 'bg-yellow-100 text-yellow-700' },
    low: { label: '낮음', color: 'bg-gray-100 text-gray-700' },
  };

  const filteredInsights = selectedType === 'ALL'
    ? insights
    : insights.filter(insight => insight.type === selectedType);

  const stats = {
    total: insights.length,
    highImpact: insights.filter(i => i.impact === 'high').length,
    actionable: insights.filter(i => i.actionable).length,
    avgConfidence: (insights.reduce((sum, i) => sum + i.confidence, 0) / insights.length * 100).toFixed(0),
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Brain className="w-8 h-8 text-purple-600" />
            AI 분석·추천
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            AI 기반 품질 예측, 이상 감지 및 최적화 제안
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <BarChart3 className="w-4 h-4 mr-2" />
            분석 리포트
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Sparkles className="w-4 h-4 mr-2" />
            AI 모델 재학습
          </Button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-purple-100 mb-1">전체 인사이트</div>
                <div className="text-3xl font-bold">{stats.total}개</div>
              </div>
              <Lightbulb className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <div className="text-sm text-gray-500">높은 영향력</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.highImpact}개</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Target className="w-4 h-4 text-green-600" />
                  <div className="text-sm text-gray-500">실행 가능</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.actionable}개</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="w-4 h-4 text-blue-600" />
                  <div className="text-sm text-gray-500">평균 신뢰도</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.avgConfidence}%</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 필터 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Button
              variant={selectedType === 'ALL' ? 'default' : 'outline'}
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
                  onClick={() => setSelectedType(key)}
                  className={selectedType === key ? 'bg-purple-600' : ''}
                >
                  <Icon className="w-4 h-4 mr-1" />
                  {config.label}
                </Button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* AI 인사이트 목록 */}
      <div className="grid grid-cols-1 gap-6">
        {filteredInsights.map((insight) => {
          const typeInfo = typeConfig[insight.type];
          const impactInfo = impactConfig[insight.impact];
          const TypeIcon = typeInfo.icon;

          return (
            <Card key={insight.id} className="hover:shadow-lg transition-shadow border-2 border-purple-100">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`p-2 rounded-lg ${typeInfo.color}`}>
                        <TypeIcon className="w-5 h-5" />
                      </div>
                      <CardTitle className="text-xl">{insight.title}</CardTitle>
                      <Badge className={impactInfo.color}>
                        영향력: {impactInfo.label}
                      </Badge>
                    </div>
                    <p className="text-gray-600">{insight.description}</p>
                  </div>
                  {insight.actionable && (
                    <Button className="bg-green-600 hover:bg-green-700">
                      <Target className="w-4 h-4 mr-2" />
                      실행 가능
                    </Button>
                  )}
                </div>
              </CardHeader>

              <CardContent>
                <AIResultPanel
                  rationale={insight.rationale}
                  assumptions={insight.assumptions}
                  risks={insight.risks}
                  confidence={insight.confidence}
                />

                {insight.actionable && insight.actions && insight.actions.length > 0 && (
                  <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="w-5 h-5 text-green-600" />
                      <h4 className="font-semibold text-gray-900">권장 액션</h4>
                    </div>
                    <ul className="space-y-1">
                      {insight.actions.map((action, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                          <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

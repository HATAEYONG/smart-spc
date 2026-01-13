import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/Select';
import {
  Brain,
  Sparkles,
  AlertTriangle,
  AlertCircle,
  CheckCircle,
  BookOpen,
  TrendingUp,
  Target,
  BarChart3,
  Zap,
  Activity
} from 'lucide-react';
import { AIResultPanel } from '../components/common';

interface RuleType {
  id: string;
  name: string;
  description: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  color: string;
}

interface RuleViolation {
  id: string;
  ruleType: string;
  ruleName: string;
  detectedAt: string;
  product: string;
  characteristic: string;
  measurements: number[];
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  isResolved: boolean;
  aiPredicted: boolean;
  aiConfidence: number;
  aiRecommendation: string;
  predictedImpact: string;
  suggestedActions: string[];
}

export const RunRuleAnalysisPage: React.FC = () => {
  const [selectedProduct, setSelectedProduct] = useState<string>('1');
  const [selectedRule, setSelectedRule] = useState<string>('ALL');
  const [measurementInput, setMeasurementInput] = useState('');
  const [violations, setViolations] = useState<RuleViolation[]>([
    {
      id: '1',
      ruleType: 'RULE_1',
      ruleName: 'Rule 1: UCL/LCL 벗어남',
      detectedAt: '2026-01-12 10:30:00',
      product: '브레이크 패드',
      characteristic: '내径',
      measurements: [10.01, 10.02, 10.00, 10.03, 10.01, 10.08],
      severity: 'CRITICAL',
      isResolved: false,
      aiPredicted: true,
      aiConfidence: 0.94,
      aiRecommendation: '즉시 공정 중단 후 원인 분석 필요. 온도 제어 시스템 점검 권장.',
      predictedImpact: '불량률 15% 증가 예상, 클레임 리스크 높음',
      suggestedActions: [
        '공정 일시 중단',
        '온도 제어 로그 확인',
        '작업자 재교육',
        '샘플링 빈도 증가'
      ],
    },
    {
      id: '2',
      ruleType: 'RULE_2',
      ruleName: 'Rule 2: 연속 9개 점 중심선 한쪽',
      detectedAt: '2026-01-12 09:15:00',
      product: '브레이크 패드',
      characteristic: '외경',
      measurements: [50.02, 50.03, 50.02, 50.04, 50.03, 50.02, 50.03, 50.04, 50.03],
      severity: 'HIGH',
      isResolved: false,
      aiPredicted: true,
      aiConfidence: 0.87,
      aiRecommendation: '공정 평균이 이동하고 있음. Tool 마모 확인 필요.',
      predictedImpact: '치수 불량 8% 증가 가능',
      suggestedActions: [
        '공구 교체 주기 확인',
        '설정값 재보정',
        '원자재 검사 강화'
      ],
    },
    {
      id: '3',
      ruleType: 'RULE_3',
      ruleName: 'Rule 3: 연속 6개 점 증가/감소',
      detectedAt: '2026-01-12 08:00:00',
      product: '브레이크 패드',
      characteristic: '두께',
      measurements: [5.01, 5.02, 5.03, 5.04, 5.05, 5.06],
      severity: 'MEDIUM',
      isResolved: true,
      aiPredicted: true,
      aiConfidence: 0.82,
      aiRecommendation: '추세 발생 감지. 열처리 로 온도 변동 의심.',
      predictedImpact: '규격 이탈 가능성 있음',
      suggestedActions: [
        '열처리 로 온도 확인',
        '가열 시간 일관성 점검'
      ],
    },
    {
      id: '4',
      ruleType: 'RULE_5',
      ruleName: 'Rule 5: 3개 중 2개가 2σ 벗어남',
      detectedAt: '2026-01-11 16:45:00',
      product: '브레이크 패드',
      characteristic: '내경',
      measurements: [10.01, 10.04, 10.03, 10.01, 10.02, 10.04],
      severity: 'HIGH',
      isResolved: true,
      aiPredicted: true,
      aiConfidence: 0.79,
      aiRecommendation: '분산 증가. 공정 불안정 상태.',
      predictedImpact: '공정 능력 저하',
      suggestedActions: [
        '설비 정비 실시',
        '작업 방법标准化'
      ],
    },
  ]);

  const [showAIPanel, setShowAIPanel] = useState(false);
  const [selectedViolation, setSelectedViolation] = useState<RuleViolation | null>(null);

  const ruleTypes: RuleType[] = [
    {
      id: 'RULE_1',
      name: 'Rule 1',
      description: 'UCL/LCL 벗어남 - 공정 관리 상태 이탈',
      severity: 'CRITICAL',
      color: 'bg-red-100 border-red-300 text-red-800',
    },
    {
      id: 'RULE_2',
      name: 'Rule 2',
      description: '연속 9개 점이 중심선 한쪽 - 평균 이동',
      severity: 'HIGH',
      color: 'bg-orange-100 border-orange-300 text-orange-800',
    },
    {
      id: 'RULE_3',
      name: 'Rule 3',
      description: '연속 6개 점이 증가/감소 - 추세 발생',
      severity: 'MEDIUM',
      color: 'bg-yellow-100 border-yellow-300 text-yellow-800',
    },
    {
      id: 'RULE_4',
      name: 'Rule 4',
      description: '연속 14개 점이 교대로 증감 - 불안정한 변동',
      severity: 'MEDIUM',
      color: 'bg-lime-100 border-lime-300 text-lime-800',
    },
    {
      id: 'RULE_5',
      name: 'Rule 5',
      description: '연속 3개 중 2개가 2σ 벗어남 - 분산 증가',
      severity: 'HIGH',
      color: 'bg-cyan-100 border-cyan-300 text-cyan-800',
    },
    {
      id: 'RULE_6',
      name: 'Rule 6',
      description: '연속 5개 중 4개가 1σ 벗어남 - 분산 증가 조기 경고',
      severity: 'MEDIUM',
      color: 'bg-blue-100 border-blue-300 text-blue-800',
    },
    {
      id: 'RULE_7',
      name: 'Rule 7',
      description: '연속 15개 점이 1σ 이내 - 분산 감소 또는 데이터 조작',
      severity: 'LOW',
      color: 'bg-purple-100 border-purple-300 text-purple-800',
    },
    {
      id: 'RULE_8',
      name: 'Rule 8',
      description: '연속 8개 점이 1σ 밖 - 혼합 또는 층화',
      severity: 'MEDIUM',
      color: 'bg-pink-100 border-pink-300 text-pink-800',
    },
  ];

  const products = [
    { id: '1', name: '브레이크 패드 - 내경' },
    { id: '2', name: '브레이크 패드 - 외경' },
    { id: '3', name: '브레이크 패드 - 두께' },
  ];

  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return { label: '심각', color: 'bg-red-100 text-red-700', icon: AlertCircle };
      case 'HIGH':
        return { label: '높음', color: 'bg-orange-100 text-orange-700', icon: AlertTriangle };
      case 'MEDIUM':
        return { label: '중간', color: 'bg-yellow-100 text-yellow-700', icon: Activity };
      case 'LOW':
        return { label: '낮음', color: 'bg-blue-100 text-blue-700', icon: CheckCircle };
      default:
        return { label: severity, color: 'bg-gray-100 text-gray-700', icon: Activity };
    }
  };

  const getRuleConfig = (ruleType: string) => {
    return ruleTypes.find(r => r.id === ruleType) || ruleTypes[0];
  };

  const filteredViolations = selectedRule === 'ALL'
    ? violations
    : violations.filter(v => v.ruleType === selectedRule);

  const stats = {
    total: violations.length,
    critical: violations.filter(v => v.severity === 'CRITICAL' && !v.isResolved).length,
    high: violations.filter(v => v.severity === 'HIGH' && !v.isResolved).length,
    resolved: violations.filter(v => v.isResolved).length,
    avgConfidence: (violations.reduce((sum, v) => sum + v.aiConfidence, 0) / violations.length * 100).toFixed(0),
  };

  const handleAIPredict = () => {
    // In real app, this would call an API
    alert('AI 예측이 실행되었습니다. (데모)');
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Brain className="w-8 h-8 text-purple-600" />
            AI Run Rule 분석
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            AI 기반 Western Electric Rules 위반 감지 및 예측
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <BookOpen className="w-4 h-4 mr-2" />
            규칙 설명서
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <BarChart3 className="w-4 h-4 mr-2" />
            분석 리포트
          </Button>
        </div>
      </div>

      {/* AI 예측 섹션 */}
      <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            AI 예측 분석
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
                      {product.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="md:col-span-2">
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                측정값 입력 <span className="text-xs text-gray-500">(쉼표로 구분, 최소 6개)</span>
              </label>
              <div className="flex gap-2">
                <Input
                  value={measurementInput}
                  onChange={(e) => setMeasurementInput(e.target.value)}
                  placeholder="예: 10.01, 10.02, 10.00, 10.03, 10.01, 10.08"
                  className="flex-1"
                />
                <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700" onClick={handleAIPredict}>
                  <Brain className="w-4 h-4 mr-2" />
                  AI 예측
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-purple-100 mb-1">총 위반 건수</div>
                <div className="text-3xl font-bold">{stats.total}건</div>
              </div>
              <AlertTriangle className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  <div className="text-sm text-gray-500">심각/높음</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.critical + stats.high}건</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <div className="text-sm text-gray-500">해결됨</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.resolved}건</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Brain className="w-4 h-4 text-blue-600" />
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
          <div className="flex flex-wrap gap-2">
            <Button
              variant={selectedRule === 'ALL' ? 'default' : 'outline'}
              onClick={() => setSelectedRule('ALL')}
              className={selectedRule === 'ALL' ? 'bg-purple-600' : ''}
            >
              전체
            </Button>
            {ruleTypes.map((rule) => (
              <Button
                key={rule.id}
                variant={selectedRule === rule.id ? 'default' : 'outline'}
                onClick={() => setSelectedRule(rule.id)}
                className={selectedRule === rule.id ? 'bg-purple-600' : ''}
              >
                {rule.name}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 위반 목록 */}
      <div className="grid grid-cols-1 gap-6">
        {filteredViolations.map((violation) => {
          const severityConfig = getSeverityConfig(violation.severity);
          const ruleConfig = getRuleConfig(violation.ruleType);
          const SeverityIcon = severityConfig.icon;

          return (
            <Card key={violation.id} className={`hover:shadow-lg transition-shadow border-2 ${
              !violation.isResolved ? 'border-red-200' : 'border-green-200'
            }`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className={ruleConfig.color}>
                        {violation.ruleName}
                      </Badge>
                      <Badge className={severityConfig.color}>
                        <div className="flex items-center gap-1">
                          <SeverityIcon className="w-3 h-3" />
                          {severityConfig.label}
                        </div>
                      </Badge>
                      {violation.aiPredicted && (
                        <Badge className="bg-purple-100 text-purple-700">
                          <div className="flex items-center gap-1">
                            <Brain className="w-3 h-3" />
                            AI 예측
                          </div>
                        </Badge>
                      )}
                      <Badge className={violation.isResolved ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}>
                        {violation.isResolved ? '해결됨' : '미해결'}
                      </Badge>
                    </div>
                    <div className="text-sm text-gray-600">
                      {violation.product} | {violation.characteristic} | {violation.detectedAt}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">AI 신뢰도</div>
                    <div className="text-2xl font-bold text-purple-600">
                      {(violation.aiConfidence * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <div className="mb-4">
                  <div className="text-sm font-medium text-gray-700 mb-2">측정값</div>
                  <div className="flex gap-1 flex-wrap">
                    {violation.measurements.map((m, idx) => (
                      <div
                        key={idx}
                        className="px-3 py-2 bg-gray-50 rounded text-sm font-mono border border-gray-200"
                      >
                        #{idx + 1}: {m.toFixed(3)}
                      </div>
                    ))}
                  </div>
                </div>

                <AIResultPanel
                  rationale={[
                    `규칙 유형: ${ruleConfig.description}`,
                    `측정값 패턴 분석 결과 위반 감지`,
                    `연속 {violation.measurements.length}개 데이터 포인트 분석 완료`
                  ]}
                  assumptions={[
                    '정규 분포 가정',
                    '공정 안정 상태 가정',
                    '표본 크기 충분'
                  ]}
                  risks={[
                    {
                      risk: violation.isResolved ? '재발 가능성' : '불량률 증가',
                      probability: violation.severity === 'CRITICAL' ? '높음' : '중간',
                      mitigation: violation.isResolved ? '정기 모니터링' : '즉각적 조치 필요'
                    }
                  ]}
                  confidence={violation.aiConfidence}
                />

                <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                    <h4 className="font-semibold text-gray-900">AI 추천 사항</h4>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{violation.aiRecommendation}</p>
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">예상 영향:</span> {violation.predictedImpact}
                  </div>
                </div>

                {violation.suggestedActions && violation.suggestedActions.length > 0 && (
                  <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="w-5 h-5 text-green-600" />
                      <h4 className="font-semibold text-gray-900">권장 조치</h4>
                    </div>
                    <ul className="space-y-1">
                      {violation.suggestedActions.map((action, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                          <Zap className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
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

        {filteredViolations.length === 0 && (
          <Card>
            <CardContent className="text-center py-16">
              <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Run Rule 위반 없음</h3>
              <p className="text-gray-500">
                선택된 조건에 대한 위반이 없습니다. 공정이 안정적인 상태입니다.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Western Electric Rules 설명 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-purple-600" />
            Western Electric Rules 설명
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ruleTypes.map((rule) => {
              const SeverityIcon = getSeverityConfig(rule.severity).icon;

              return (
                <div key={rule.id} className={`p-4 rounded-lg border-l-4 ${rule.color}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <SeverityIcon className="w-5 h-5" />
                    <span className="font-semibold text-gray-900">{rule.name}</span>
                    <Badge className={getSeverityConfig(rule.severity).color} variant="outline">
                      {getSeverityConfig(rule.severity).label}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-700">{rule.description}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RunRuleAnalysisPage;

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
  ArrowRight,
  Plus,
  Edit,
  Trash2,
  Sparkles,
  GripVertical,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { AIResultPanel } from '../components/common';
import { inspectionService } from '../services/inspectionService';

interface ProcessStep {
  id: string;
  seqNo: number;
  stepName: string;
  workCenter: string;
  isInspectionPoint: boolean;
  inspectionPoints?: string[];
}

interface ProcessFlow {
  id: string;
  flowName: string;
  revNo: string;
  steps: ProcessStep[];
}

const MOCK_FLOW: ProcessFlow = {
  id: '1',
  flowName: '브레이크 패드 생산 공정',
  revNo: '1.2',
  steps: [
    {
      id: '1',
      seqNo: 10,
      stepName: 'CNC 가공',
      workCenter: 'WC-001',
      isInspectionPoint: true,
      inspectionPoints: ['내경', '외경', '깊이'],
    },
    {
      id: '2',
      seqNo: 20,
      stepName: '세척',
      workCenter: 'WC-002',
      isInspectionPoint: true,
      inspectionPoints: ['외관', '이물'],
    },
    {
      id: '3',
      seqNo: 30,
      stepName: '조립',
      workCenter: 'WC-003',
      isInspectionPoint: true,
      inspectionPoints: ['조립 완성도', '간섭'],
    }
  ]
};

export const InspectionProcessDesignPage: React.FC = () => {
  const [flows, setFlows] = useState<ProcessFlow[]>([MOCK_FLOW]);
  const [selectedFlow, setSelectedFlow] = useState<ProcessFlow>(MOCK_FLOW);
  const [loading, setLoading] = useState(false);
  const [selectedStep, setSelectedStep] = useState<ProcessStep | null>(null);

  useEffect(() => {
    fetchFlows();
  }, []);

  const fetchFlows = async () => {
    try {
      setLoading(true);
      const response = await inspectionService.getFlows();

      if (response.ok && response.data) {
        // API 데이터를 UI 형식으로 변환
        const transformedFlows: ProcessFlow[] = response.data.map((flow: any) => ({
          id: flow.flow_id,
          flowName: flow.product_id || flow.flow_id,
          revNo: flow.version || '1.0',
          steps: [], // 단계는 별도 API 호출 필요
        }));

        setFlows(transformedFlows.length > 0 ? transformedFlows : [MOCK_FLOW]);
        if (transformedFlows.length > 0) {
          setSelectedFlow(transformedFlows[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch flows:', error);
      setFlows([MOCK_FLOW]);
    } finally {
      setLoading(false);
    }
  };
  const [showAIPanel, setShowAIPanel] = useState(false);

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">검수 프로세스 설계</h1>
          <p className="text-sm text-gray-500 mt-1">
            기업별 맞춤형 검수 프로세스 설계 및 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="border-purple-600 text-purple-600 hover:bg-purple-50"
            onClick={() => setShowAIPanel(!showAIPanel)}
          >
            <Sparkles className="w-4 h-4 mr-2" />
            AI로 프로세스 초안 생성
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <CheckCircle className="w-4 h-4 mr-2" />
            저장
          </Button>
        </div>
      </div>

      {/* 상단 선택 영역 */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">품목</label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="품목 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">브레이크 패드</SelectItem>
                  <SelectItem value="2">클러치 디스크</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">공정 Flow</label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="공정 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">표준 공정 Flow A</SelectItem>
                  <SelectItem value="2">표준 공정 Flow B</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">리비전</label>
              <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg border">
                <Badge variant="outline">Rev {selectedFlow.revNo}</Badge>
                <Button variant="ghost" size="sm">
                  <Edit className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI 추천 패널 */}
      {showAIPanel && (
        <AIResultPanel
          rationale={[
            '브레이크 패드 생산 공정은 일반적으로 CNC 가공 → 세척 → 조립 순서로 진행됩니다',
            '각 공정 단계별 품질특성(CTQ)을 식별하여 검사 지점을 설정하는 것이 표준입니다',
            '자동차 부품 산업의 일반적인 공정을 기반으로 제안되었습니다'
          ]}
          assumptions={[
            'CNC 가공 공정능력 Cpk ≥ 1.33 가정',
            '세척 공정에서 외관 불량 90% 제거 가정'
          ]}
          risks={[
            {
              risk: '공구 마모로 인한 치수 불량 증가 가능성',
              probability: '중간',
              mitigation: '공구 교체 주기 설정 및 마모도 모니터링'
            }
          ]}
          confidence={0.87}
        />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 중앙: 공정 스텝 카드 (드래그 정렬) */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-purple-600" />
                공정 스텝 (드래그하여 순서 변경)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {selectedFlow.steps.map((step, idx) => (
                  <div
                    key={step.id}
                    className={`p-4 bg-white rounded-lg border-2 cursor-pointer transition-all hover:shadow-md ${
                      selectedStep?.id === step.id
                        ? 'border-purple-600 shadow-lg'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                    onClick={() => setSelectedStep(step)}
                  >
                    <div className="flex items-center gap-3">
                      <GripVertical className="w-5 h-5 text-gray-400" />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="font-mono">
                            {step.seqNo}
                          </Badge>
                          <h3 className="font-semibold text-gray-900">{step.stepName}</h3>
                          {step.isInspectionPoint && (
                            <Badge className="bg-green-100 text-green-700">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              검사 지점
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 mt-1">{step.workCenter}</p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-400" />
                    </div>

                    {/* 검사 포인트 미리보기 */}
                    {step.isInspectionPoint && step.inspectionPoints && (
                      <div className="mt-3 pl-8 flex flex-wrap gap-2">
                        {step.inspectionPoints.map((point, pointIdx) => (
                          <Badge key={pointIdx} variant="secondary" className="text-xs">
                            {point}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-4 flex gap-2">
                <Button variant="outline" className="flex-1">
                  <Plus className="w-4 h-4 mr-2" />
                  스텝 추가
                </Button>
                <Button variant="outline" className="flex-1">
                  <Edit className="w-4 h-4 mr-2" />
                  스텝 편집
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 우측: 검사 포인트 편집 */}
        <div>
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle className="text-base">검사 포인트 편집</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedStep ? (
                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-gray-500">선택된 스텝</label>
                    <p className="font-semibold text-gray-900">{selectedStep.stepName}</p>
                  </div>

                  <div>
                    <label className="text-xs text-gray-500 mb-2 block">검사 지점 (CTQ)</label>
                    <div className="space-y-2">
                      {selectedStep.inspectionPoints?.map((point, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded"
                        >
                          <span className="text-sm">{point}</span>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                            <Edit className="w-3 h-3" />
                          </Button>
                        </div>
                      )) || (
                        <p className="text-sm text-gray-500">검사 지점 없음</p>
                      )}
                    </div>
                    <Button variant="outline" size="sm" className="mt-2 w-full">
                      <Plus className="w-4 h-4 mr-2" />
                      검사 지점 추가
                    </Button>
                  </div>

                  <div>
                    <label className="text-xs text-gray-500 mb-2 block">검사 빈도</label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="빈도 선택" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="lot">LOT별</SelectItem>
                        <SelectItem value="shift">교대별</SelectItem>
                        <SelectItem value="hourly">시간당</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-xs text-gray-500 mb-2 block">검사 방법</label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="방법 선택" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="dimensional">치수 측정</SelectItem>
                        <SelectItem value="visual">외관 검사</SelectItem>
                        <SelectItem value="functional">기능 검사</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-xs text-gray-500 mb-2 block">샘플링 규칙</label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="규칙 선택" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="iso2859">ISO 2859 (AQL 1.0)</SelectItem>
                        <SelectItem value="all">전수 검사</SelectItem>
                        <SelectItem value="random">랜덤 샘플링</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Button className="w-full bg-purple-600 hover:bg-purple-700">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    적용
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">스텝을 선택하세요</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

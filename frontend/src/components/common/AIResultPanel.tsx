import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Badge } from '../ui/Badge';
import {
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  Info,
  Brain,
  Sparkles
} from 'lucide-react';

interface AIResultPanelProps {
  rationale?: string[];      // 근거
  assumptions?: string[];    // 가정
  risks?: Array<{           // 리스크
    risk: string;
    probability: string;
    mitigation: string;
  }>;
  confidence?: number;      // 신뢰도 (0~1)
  className?: string;
}

export const AIResultPanel: React.FC<AIResultPanelProps> = ({
  rationale = [],
  assumptions = [],
  risks = [],
  confidence = 0,
  className = ''
}) => {
  const getConfidenceColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600 bg-green-50';
    if (score >= 0.7) return 'text-blue-600 bg-blue-50';
    if (score >= 0.5) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.9) return '매우 높음';
    if (score >= 0.7) return '높음';
    if (score >= 0.5) return '보통';
    return '낮음';
  };

  return (
    <Card className={`${className} border-purple-200 bg-gradient-to-br from-purple-50 to-white`}>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-purple-700">
          <Brain className="w-5 h-5" />
          <span>AI 분석 결과</span>
          {confidence > 0 && (
            <Badge className={`ml-2 ${getConfidenceColor(confidence)}`}>
              <Sparkles className="w-3 h-3 mr-1" />
              신뢰도: {getConfidenceLabel(confidence)} ({(confidence * 100).toFixed(0)}%)
            </Badge>
          )}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 근거 (Rationale) */}
        {rationale.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-gray-700">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>근거 (Rationale)</span>
            </div>
            <ul className="space-y-1 ml-6">
              {rationale.map((item, idx) => (
                <li key={idx} className="text-sm text-gray-600 list-disc">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {rationale.length > 0 && (assumptions.length > 0 || risks.length > 0) && (
          <div className="border-t border-gray-200 my-3" />
        )}

        {/* 가정 (Assumptions) */}
        {assumptions.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-gray-700">
              <Info className="w-4 h-4 text-blue-600" />
              <span>가정사항 (Assumptions)</span>
            </div>
            <ul className="space-y-1 ml-6">
              {assumptions.map((item, idx) => (
                <li key={idx} className="text-sm text-gray-600 list-disc">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {assumptions.length > 0 && risks.length > 0 && (
          <div className="border-t border-gray-200 my-3" />
        )}

        {/* 리스크 (Risks) */}
        {risks.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-gray-700">
              <AlertTriangle className="w-4 h-4 text-orange-600" />
              <span>식별된 리스크</span>
            </div>
            <div className="space-y-2">
              {risks.map((risk, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-orange-50 rounded-lg border border-orange-200"
                >
                  <div className="flex items-start justify-between mb-1">
                    <span className="text-sm font-medium text-gray-800">
                      {risk.risk}
                    </span>
                    <Badge
                      variant="outline"
                      className={`text-xs ${
                        risk.probability === '높음'
                          ? 'bg-red-100 text-red-700 border-red-300'
                          : risk.probability === '중간'
                          ? 'bg-yellow-100 text-yellow-700 border-yellow-300'
                          : 'bg-blue-100 text-blue-700 border-blue-300'
                      }`}
                    >
                      확률: {risk.probability}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-600">
                    <Lightbulb className="w-3 h-3 text-orange-600" />
                    <span>
                      <strong>완화 조치:</strong> {risk.mitigation}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

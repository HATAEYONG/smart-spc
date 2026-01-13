import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Shield,
  CheckCircle,
  AlertCircle,
  Clock,
  FileText,
  Users,
  TrendingUp,
  Target,
  Award
} from 'lucide-react';
import { qaService } from '../services/qaService';

interface AuditRecord {
  id: string;
  date: string;
  type: 'INTERNAL' | 'EXTERNAL' | 'SUPPLIER';
  auditor: string;
  scope: string;
  findings: number;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'SCHEDULED';
  score?: number;
}

interface QualityObjective {
  id: string;
  name: string;
  target: number;
  current: number;
  unit: string;
  dueDate: string;
}

export const QASystemPage: React.FC = () => {
  const [audits, setAudits] = useState<AuditRecord[]>([
    {
      id: '1',
      date: '2026-01-15',
      type: 'INTERNAL',
      auditor: '김품질',
      scope: 'CNC 가공 공정',
      findings: 2,
      status: 'SCHEDULED',
    },
    {
      id: '2',
      date: '2025-12-20',
      type: 'EXTERNAL',
      auditor: 'ISO 인증기관',
      scope: '전사 품질 시스템',
      findings: 3,
      status: 'COMPLETED',
      score: 92,
    },
    {
      id: '3',
      date: '2025-11-10',
      type: 'SUPPLIER',
      auditor: '이구매',
      scope: '원자재 공급사',
      findings: 5,
      status: 'COMPLETED',
      score: 85,
    },
  ]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // QA 프로세스 데이터를 가져올 수 있습니다
    // 현재는 샘플 데이터를 사용
  }, []);

  const [objectives, setObjectives] = useState<QualityObjective[]>([
    {
      id: '1',
      name: '고객 불만족률',
      target: 2,
      current: 1.8,
      unit: '%',
      dueDate: '2026-03-31',
    },
    {
      id: '2',
      name: 'COPQ 비율',
      target: 50,
      current: 49.6,
      unit: '%',
      dueDate: '2026-03-31',
    },
    {
      id: '3',
      name: '공정 능력 지수 (Cpk)',
      target: 1.33,
      current: 1.28,
      unit: '',
      dueDate: '2026-03-31',
    },
    {
      id: '4',
      name: '공급자 온타임 납품률',
      target: 95,
      current: 97,
      unit: '%',
      dueDate: '2026-03-31',
    },
  ]);

  const auditTypeConfig = {
    INTERNAL: { label: '내부 감사', color: 'bg-blue-100 text-blue-700' },
    EXTERNAL: { label: '외부 감사', color: 'bg-purple-100 text-purple-700' },
    SUPPLIER: { label: '공급사 감사', color: 'bg-green-100 text-green-700' },
  };

  const statusConfig = {
    COMPLETED: { label: '완료', color: 'bg-green-100 text-green-700' },
    IN_PROGRESS: { label: '진행 중', color: 'bg-yellow-100 text-yellow-700' },
    SCHEDULED: { label: '예정', color: 'bg-gray-100 text-gray-700' },
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">품질보증(QA) 시스템</h1>
          <p className="text-sm text-gray-500 mt-1">
            품질 감사 및 목표 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileText className="w-4 h-4 mr-2" />
            감사 리포트
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Shield className="w-4 h-4 mr-2" />
            신규 감사 계획
          </Button>
        </div>
      </div>

      {/* KPI 요약 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-purple-100 mb-1">품질 목표 달성률</div>
                <div className="text-3xl font-bold">75%</div>
              </div>
              <Target className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <div className="text-sm text-gray-500">완료된 감사</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {audits.filter(a => a.status === 'COMPLETED').length}건
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="w-4 h-4 text-yellow-600" />
                  <div className="text-sm text-gray-500">진행/예정</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {audits.filter(a => a.status !== 'COMPLETED').length}건
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <AlertCircle className="w-4 h-4 text-orange-600" />
                  <div className="text-sm text-gray-500">미해결 Issue</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {audits.reduce((sum, a) => sum + (a.findings || 0), 0)}건
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 품질 감사 이력 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-purple-600" />
              품질 감사 이력
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {audits.map((audit) => {
                const typeInfo = auditTypeConfig[audit.type];
                const statusInfo = statusConfig[audit.status];

                return (
                  <div
                    key={audit.id}
                    className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={typeInfo.color}>
                            {typeInfo.label}
                          </Badge>
                          <Badge className={statusInfo.color}>
                            {statusInfo.label}
                          </Badge>
                        </div>
                        <h3 className="font-semibold text-gray-900">{audit.scope}</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          감사원: {audit.auditor} |{' '}
                          {new Date(audit.date).toLocaleDateString('ko-KR')}
                        </p>
                      </div>
                      {audit.score && (
                        <div className="text-right">
                          <div className="text-2xl font-bold text-purple-600">{audit.score}</div>
                          <div className="text-xs text-gray-500">점수</div>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center justify-between text-sm pt-2 border-t">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-orange-600" />
                        <span className="text-gray-600">
                          지적사항: <span className="font-semibold">{audit.findings}건</span>
                        </span>
                      </div>
                      <Button variant="outline" size="sm">
                        상세보기
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* 품질 목표 관리 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-purple-600" />
              품질 목표 현황
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {objectives.map((objective) => {
                const percentage = (objective.current / objective.target) * 100;
                const isAchieved = percentage >= 100;

                return (
                  <div key={objective.id} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-gray-900">{objective.name}</div>
                        <div className="text-xs text-gray-500">
                          목표: {objective.target}{objective.unit} / 마감: {new Date(objective.dueDate).toLocaleDateString('ko-KR')}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${isAchieved ? 'text-green-600' : 'text-gray-900'}`}>
                          {objective.current}
                          {objective.unit}
                        </div>
                        <Badge className={isAchieved ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}>
                          {percentage.toFixed(0)}%
                        </Badge>
                      </div>
                    </div>

                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          isAchieved ? 'bg-green-500' : 'bg-purple-600'
                        }`}
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>

                    {isAchieved && (
                      <div className="flex items-center gap-1 text-xs text-green-600">
                        <Award className="w-3 h-3" />
                        목표 달성
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

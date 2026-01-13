import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Sigma,
  Target,
  BarChart3,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Users,
  Calendar,
  Zap,
  FileText,
  Brain,
  Award,
  Activity,
  Clock
} from 'lucide-react';

interface DMAICProject {
  id: string;
  code: string;
  name: string;
  phase: 'DEFINE' | 'MEASURE' | 'ANALYZE' | 'IMPROVE' | 'CONTROL';
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ON_HOLD';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  champion: string;
  progress: number;
  startDate: string;
  targetEndDate: string;
  daysRemaining: number;
  savings: number;
  teamSize: number;
}

interface PhaseMetric {
  phase: string;
  label: string;
  count: number;
  icon: any;
  color: string;
}

export const SixSigmaDashboardPage: React.FC = () => {
  const [projects, setProjects] = useState<DMAICProject[]>([
    {
      id: '1',
      code: 'SS-2026-001',
      name: '브레이크 패드 내경 불량률 개선',
      phase: 'ANALYZE',
      status: 'IN_PROGRESS',
      priority: 'HIGH',
      champion: '김품질',
      progress: 45,
      startDate: '2025-11-01',
      targetEndDate: '2026-02-28',
      daysRemaining: 47,
      savings: 85000000,
      teamSize: 5,
    },
    {
      id: '2',
      code: 'SS-2026-002',
      name: '세척 공정 이물 제거율 향상',
      phase: 'IMPROVE',
      status: 'IN_PROGRESS',
      priority: 'CRITICAL',
      champion: '이개선',
      progress: 72,
      startDate: '2025-10-15',
      targetEndDate: '2026-01-31',
      daysRemaining: 19,
      savings: 120000000,
      teamSize: 7,
    },
    {
      id: '3',
      code: 'SS-2025-048',
      name: '열처리 로 온도 편차 최소화',
      phase: 'CONTROL',
      status: 'IN_PROGRESS',
      priority: 'MEDIUM',
      champion: '박공정',
      progress: 90,
      startDate: '2025-08-01',
      targetEndDate: '2025-12-31',
      daysRemaining: 19,
      savings: 65000000,
      teamSize: 4,
    },
    {
      id: '4',
      code: 'SS-2025-045',
      name: 'CNC 가공 공정능력 6시그마 도달',
      phase: 'COMPLETED',
      status: 'COMPLETED',
      priority: 'HIGH',
      champion: '최분석',
      progress: 100,
      startDate: '2025-05-01',
      targetEndDate: '2025-10-31',
      daysRemaining: 0,
      savings: 210000000,
      teamSize: 6,
    },
    {
      id: '5',
      code: 'SS-2026-003',
      name: '외관 검사 자동화 도입',
      phase: 'DEFINE',
      status: 'IN_PROGRESS',
      priority: 'LOW',
      champion: '정자동',
      progress: 15,
      startDate: '2026-01-01',
      targetEndDate: '2026-06-30',
      daysRemaining: 169,
      savings: 95000000,
      teamSize: 3,
    },
  ]);

  const phaseMetrics: PhaseMetric[] = [
    { phase: 'DEFINE', label: '정의 (Define)', count: projects.filter(p => p.phase === 'DEFINE').length, icon: Target, color: 'bg-blue-100 text-blue-700' },
    { phase: 'MEASURE', label: '측정 (Measure)', count: projects.filter(p => p.phase === 'MEASURE').length, icon: BarChart3, color: 'bg-green-100 text-green-700' },
    { phase: 'ANALYZE', label: '분석 (Analyze)', count: projects.filter(p => p.phase === 'ANALYZE').length, icon: TrendingUp, color: 'bg-purple-100 text-purple-700' },
    { phase: 'IMPROVE', label: '개선 (Improve)', count: projects.filter(p => p.phase === 'IMPROVE').length, icon: Zap, color: 'bg-orange-100 text-orange-700' },
    { phase: 'CONTROL', label: '관리 (Control)', count: projects.filter(p => p.phase === 'CONTROL').length, icon: CheckCircle, color: 'bg-red-100 text-red-700' },
  ];

  const getPhaseConfig = (phase: string) => {
    switch (phase) {
      case 'DEFINE':
        return { label: '정의', color: 'bg-blue-100 text-blue-700', icon: Target };
      case 'MEASURE':
        return { label: '측정', color: 'bg-green-100 text-green-700', icon: BarChart3 };
      case 'ANALYZE':
        return { label: '분석', color: 'bg-purple-100 text-purple-700', icon: TrendingUp };
      case 'IMPROVE':
        return { label: '개선', color: 'bg-orange-100 text-orange-700', icon: Zap };
      case 'CONTROL':
        return { label: '관리', color: 'bg-red-100 text-red-700', icon: CheckCircle };
      default:
        return { label: phase, color: 'bg-gray-100 text-gray-700', icon: Activity };
    }
  };

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'IN_PROGRESS':
        return { label: '진행 중', color: 'bg-yellow-100 text-yellow-700' };
      case 'COMPLETED':
        return { label: '완료', color: 'bg-green-100 text-green-700' };
      case 'ON_HOLD':
        return { label: '보류', color: 'bg-gray-100 text-gray-700' };
      default:
        return { label: status, color: 'bg-gray-100 text-gray-700' };
    }
  };

  const getPriorityConfig = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return { label: '긴급', color: 'bg-red-100 text-red-700' };
      case 'HIGH':
        return { label: '높음', color: 'bg-orange-100 text-orange-700' };
      case 'MEDIUM':
        return { label: '중간', color: 'bg-yellow-100 text-yellow-700' };
      case 'LOW':
        return { label: '낮음', color: 'bg-blue-100 text-blue-700' };
      default:
        return { label: priority, color: 'bg-gray-100 text-gray-700' };
    }
  };

  const stats = {
    total: projects.length,
    inProgress: projects.filter(p => p.status === 'IN_PROGRESS').length,
    completed: projects.filter(p => p.status === 'COMPLETED').length,
    totalSavings: projects.reduce((sum, p) => sum + p.savings, 0),
    avgProgress: (projects.reduce((sum, p) => sum + p.progress, 0) / projects.length).toFixed(0),
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Sigma className="w-8 h-8 text-purple-600" />
            Six Sigma DMAIC
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            품질 개선 프로젝트 관리 및 추적
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileText className="w-4 h-4 mr-2" />
            보고서
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Target className="w-4 h-4 mr-2" />
            신규 프로젝트
          </Button>
        </div>
      </div>

      {/* 요약 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-purple-100 mb-1">전체 프로젝트</div>
                <div className="text-3xl font-bold">{stats.total}개</div>
              </div>
              <Sigma className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="w-4 h-4 text-yellow-600" />
                  <div className="text-sm text-gray-500">진행 중</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.inProgress}개</div>
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
                  <div className="text-sm text-gray-500">완료됨</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.completed}개</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">총 절감액</div>
                <div className="text-2xl font-bold text-gray-900">
                  {(stats.totalSavings / 100000000).toFixed(1)}억원
                </div>
              </div>
              <Award className="w-8 h-8 text-yellow-500 opacity-50" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* DMAIC 단계별 현황 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-600" />
            DMAIC 단계별 현황
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-5 gap-4">
            {phaseMetrics.map((metric) => {
              const Icon = metric.icon;
              return (
                <div key={metric.phase} className={`p-4 rounded-lg border-2 ${metric.color} border-current`}>
                  <div className="flex flex-col items-center text-center">
                    <div className={`p-3 rounded-lg ${metric.color.split(' ')[0]} mb-2`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <div className="text-3xl font-bold">{metric.count}</div>
                    <div className="text-sm font-medium mt-1">{metric.label}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* 프로젝트 목록 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-600" />
            프로젝트 목록
            <Badge variant="outline">{projects.length}건</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {projects.map((project) => {
              const phaseConfig = getPhaseConfig(project.phase);
              const statusConfig = getStatusConfig(project.status);
              const priorityConfig = getPriorityConfig(project.priority);
              const PhaseIcon = phaseConfig.icon;

              return (
                <div
                  key={project.id}
                  className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className={phaseConfig.color}>
                          <PhaseIcon className="w-3 h-3 mr-1" />
                          {phaseConfig.label}
                        </Badge>
                        <Badge className={statusConfig.color}>
                          {statusConfig.label}
                        </Badge>
                        <Badge className={priorityConfig.color}>
                          {priorityConfig.label}
                        </Badge>
                      </div>
                      <div className="font-semibold text-gray-900">{project.code}</div>
                      <div className="text-lg font-bold text-gray-900">{project.name}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">예상 절감액</div>
                      <div className="text-xl font-bold text-green-600">
                        {(project.savings / 100000000).toFixed(1)}억원
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Champion</div>
                      <div className="flex items-center gap-1 text-sm">
                        <Users className="w-3 h-3 text-purple-600" />
                        <span className="font-medium">{project.champion}</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-1">팀 규모</div>
                      <div className="flex items-center gap-1 text-sm">
                        <Users className="w-3 h-3 text-purple-600" />
                        <span className="font-medium">{project.teamSize}명</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-1">목표 완료일</div>
                      <div className="flex items-center gap-1 text-sm">
                        <Calendar className="w-3 h-3 text-purple-600" />
                        <span className="font-medium">{new Date(project.targetEndDate).toLocaleDateString('ko-KR')}</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-1">남은 기간</div>
                      <div className="flex items-center gap-1 text-sm">
                        <Clock className="w-3 h-3 text-purple-600" />
                        <span className={`font-medium ${project.daysRemaining <= 30 ? 'text-red-600' : ''}`}>
                          {project.daysRemaining}일
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-600">진행률</span>
                      <span className="text-sm font-bold text-purple-600">{project.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          project.progress >= 100 ? 'bg-green-500' :
                          project.progress >= 70 ? 'bg-blue-500' :
                          project.progress >= 40 ? 'bg-yellow-500' :
                          'bg-purple-600'
                        }`}
                        style={{ width: `${Math.min(project.progress, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* DMAIC 프로세스 설명 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-600" />
            DMAIC 프로세스 안내
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-5 h-5 text-blue-600" />
                <span className="font-bold text-blue-900">Define (정의)</span>
              </div>
              <p className="text-sm text-blue-800">
                문제 정의, 프로젝트 범위 설정, 목표 수립
              </p>
            </div>

            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-5 h-5 text-green-600" />
                <span className="font-bold text-green-900">Measure (측정)</span>
              </div>
              <p className="text-sm text-green-800">
                현재 공정 성과 측정, 데이터 수집 계획 수립
              </p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                <span className="font-bold text-purple-900">Analyze (분석)</span>
              </div>
              <p className="text-sm text-purple-800">
                원인 분석, 근본 원인 파악, 가설 검증
              </p>
            </div>

            <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-5 h-5 text-orange-600" />
                <span className="font-bold text-orange-900">Improve (개선)</span>
              </div>
              <p className="text-sm text-orange-800">
                해결책 도출, 시뮬레이션, 개선안 실행
              </p>
            </div>

            <div className="p-4 bg-red-50 rounded-lg border border-red-200">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-red-600" />
                <span className="font-bold text-red-900">Control (관리)</span>
              </div>
              <p className="text-sm text-red-800">
                효과 지속 관리, 표준화, 모니터링
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SixSigmaDashboardPage;

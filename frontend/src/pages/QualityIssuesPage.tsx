/**
 * 품질 이슈 추적 시스템
 * 불량 발생 시 원인 분석 (4M), 재발 방지 대책 관리, 8-Step Problem Solving
 */
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { djangoApi, type QualityIssue as ApiQualityIssue } from '../services/api';
import {
  AlertTriangle,
  Search,
  Plus,
  Filter,
  TrendingUp,
  CheckCircle,
  Clock,
  User,
  Settings,
  Package,
  Wrench,
  Calendar,
  Download,
  BarChart3,
  Zap,
  Target,
  Lightbulb,
  FileText,
  Edit,
  Eye,
  XCircle
} from 'lucide-react';

// 품질 이슈 인터페이스 (API 타입과 호환)
interface QualityIssue {
  id: number;
  issue_number: string;
  title: string;
  description: string;
  product_code: string;
  product_name: string;
  defect_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'OPEN' | 'INVESTIGATING' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  reported_date: string;
  reporter?: string | number;
  reporter_name?: string;
  department: string;
  defect_quantity: number;
  cost_impact: number | string;
  responsible_person?: string;
  target_resolution_date: string;
  actual_resolution_date?: string;

  // 4M 분석 (API 데이터 형식)
  analyses_4m?: Array<{
    id: number;
    category: 'MAN' | 'MACHINE' | 'MATERIAL' | 'METHOD';
    description: string;
  }>;

  // 8-Step Problem Solving (API 데이터 형식)
  solving_steps?: Array<{
    id: number;
    step_number: number;
    step_name: string;
    content: string;
    completed: boolean;
  }>;
}

const QualityIssuesPage: React.FC = () => {
  const [issues, setIssues] = useState<QualityIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIssue, setSelectedIssue] = useState<QualityIssue | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // API에서 데이터 로드
  useEffect(() => {
    const fetchIssues = async () => {
      try {
        setLoading(true);
        const response = await djangoApi.qualityIssues.list();
        // API 데이터 변환
        const transformedIssues: QualityIssue[] = response.results.map((issue) => ({
          ...issue,
          reporter: issue.reporter_name || issue.reporter || '미지정',
          cost_impact: typeof issue.cost_impact === 'string'
            ? parseFloat(issue.cost_impact)
            : issue.cost_impact,
          reported_date: issue.reported_date?.split('T')[0] || issue.reported_date,
          target_resolution_date: issue.target_resolution_date?.split('T')[0] || issue.target_resolution_date,
          actual_resolution_date: issue.actual_resolution_date?.split('T')[0] || undefined,
        }));
        setIssues(transformedIssues);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch quality issues:', err);
        setError('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchIssues();
  }, []);

  // 로딩 상태 표시
  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  // 에러 상태 표시
  if (error) {
    return (
      <div className="p-6 flex items-center justify-center h-screen">
        <Card className="max-w-md">
          <CardContent className="p-6 text-center">
            <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-gray-900 font-semibold mb-2">오류 발생</p>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>다시 시도</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getSeverityBadge = (severity: string) => {
    const styles = {
      LOW: 'bg-gray-100 text-gray-800 border-gray-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
      CRITICAL: 'bg-red-100 text-red-800 border-red-300',
    };
    const labels = {
      LOW: '낮음',
      MEDIUM: '중간',
      HIGH: '높음',
      CRITICAL: '긴급',
    };
    return (
      <Badge className={styles[severity as keyof typeof styles]}>
        {labels[severity as keyof typeof labels]}
      </Badge>
    );
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      OPEN: 'bg-red-100 text-red-800 border-red-300',
      INVESTIGATING: 'bg-purple-100 text-purple-800 border-purple-300',
      IN_PROGRESS: 'bg-blue-100 text-blue-800 border-blue-300',
      RESOLVED: 'bg-green-100 text-green-800 border-green-300',
      CLOSED: 'bg-gray-100 text-gray-800 border-gray-300',
    };
    const labels = {
      OPEN: '접수',
      INVESTIGATING: '조사중',
      IN_PROGRESS: '진행중',
      RESOLVED: '해결',
      CLOSED: '종결',
    };
    const icons = {
      OPEN: AlertTriangle,
      INVESTIGATING: Search,
      IN_PROGRESS: Clock,
      RESOLVED: CheckCircle,
      CLOSED: XCircle,
    };
    const Icon = icons[status as keyof typeof icons];
    return (
      <Badge className={styles[status as keyof typeof styles]}>
        <Icon className="w-3 h-3 mr-1" />
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  const filteredIssues = issues.filter(issue => {
    const matchStatus = selectedStatus === 'ALL' || issue.status === selectedStatus;
    const matchSeverity = selectedSeverity === 'ALL' || issue.severity === selectedSeverity;
    const matchSearch = searchTerm === '' ||
      issue.issue_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.product_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchStatus && matchSeverity && matchSearch;
  });

  const stats = {
    total: issues.length,
    open: issues.filter(i => i.status === 'OPEN').length,
    inProgress: issues.filter(i => i.status === 'IN_PROGRESS' || i.status === 'INVESTIGATING').length,
    resolved: issues.filter(i => i.status === 'RESOLVED' || i.status === 'CLOSED').length,
    totalCost: issues.reduce((sum, i) => sum + i.cost_impact, 0)
  };

  const handleViewDetail = (issue: QualityIssue) => {
    setSelectedIssue(issue);
    setShowDetailModal(true);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-orange-600" />
            품질 이슈 추적 시스템
          </h1>
          <p className="text-gray-600 mt-2">
            4M 분석 및 8-Step Problem Solving을 통한 체계적 문제 해결
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            내보내기
          </Button>
          <Button className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4" />
            새 이슈 등록
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">전체 이슈</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
              </div>
              <FileText className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-red-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">접수 대기</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{stats.open}</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-red-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">조사/진행중</p>
                <p className="text-3xl font-bold text-purple-600 mt-1">{stats.inProgress}</p>
              </div>
              <Clock className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">해결 완료</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.resolved}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-orange-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">총 비용 영향</p>
                <p className="text-2xl font-bold text-orange-600 mt-1">
                  {(stats.totalCost / 100000000).toFixed(2)}억
                </p>
              </div>
              <TrendingUp className="w-12 h-12 text-orange-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">검색</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="이슈 번호, 제품, 제목..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">상태</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
              >
                <option value="ALL">전체</option>
                <option value="OPEN">접수</option>
                <option value="INVESTIGATING">조사중</option>
                <option value="IN_PROGRESS">진행중</option>
                <option value="RESOLVED">해결</option>
                <option value="CLOSED">종결</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">중요도</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
              >
                <option value="ALL">전체</option>
                <option value="LOW">낮음</option>
                <option value="MEDIUM">중간</option>
                <option value="HIGH">높음</option>
                <option value="CRITICAL">긴급</option>
              </select>
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setSearchTerm('');
                  setSelectedStatus('ALL');
                  setSelectedSeverity('ALL');
                }}
              >
                <Filter className="w-4 h-4 mr-2" />
                필터 초기화
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Issues List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            품질 이슈 목록 ({filteredIssues.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left p-4 font-semibold text-gray-700">이슈 번호</th>
                  <th className="text-left p-4 font-semibold text-gray-700">제목</th>
                  <th className="text-left p-4 font-semibold text-gray-700">불량 유형</th>
                  <th className="text-left p-4 font-semibold text-gray-700">제품</th>
                  <th className="text-left p-4 font-semibold text-gray-700">중요도</th>
                  <th className="text-left p-4 font-semibold text-gray-700">상태</th>
                  <th className="text-left p-4 font-semibold text-gray-700">보고일</th>
                  <th className="text-left p-4 font-semibold text-gray-700">비용 영향</th>
                  <th className="text-left p-4 font-semibold text-gray-700">작업</th>
                </tr>
              </thead>
              <tbody>
                {filteredIssues.map((issue) => (
                  <tr key={issue.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="p-4 font-medium text-purple-600">{issue.issue_number}</td>
                    <td className="p-4">
                      <div className="font-medium">{issue.title}</div>
                      <div className="text-sm text-gray-500">{issue.reporter || '미지정'} / {issue.department}</div>
                    </td>
                    <td className="p-4">
                      <Badge variant="outline">{issue.defect_type}</Badge>
                    </td>
                    <td className="p-4">
                      <div className="font-medium">{issue.product_name}</div>
                      <div className="text-sm text-gray-500">{issue.product_code}</div>
                      <div className="text-sm text-red-600">불량 {issue.defect_quantity}개</div>
                    </td>
                    <td className="p-4">{getSeverityBadge(issue.severity)}</td>
                    <td className="p-4">{getStatusBadge(issue.status)}</td>
                    <td className="p-4 text-sm">{issue.reported_date}</td>
                    <td className="p-4">
                      <div className="font-semibold text-orange-600">
                        {(issue.cost_impact / 10000).toFixed(0)}만원
                      </div>
                    </td>
                    <td className="p-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewDetail(issue)}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        상세
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Detail Modal */}
      {showDetailModal && selectedIssue && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedIssue.issue_number}</h2>
                <p className="text-gray-600">{selectedIssue.title}</p>
              </div>
              <div className="flex items-center gap-3">
                {getSeverityBadge(selectedIssue.severity)}
                {getStatusBadge(selectedIssue.status)}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowDetailModal(false)}
                >
                  ✕
                </Button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Basic Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    기본 정보
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="text-sm font-medium text-gray-500">제품</label>
                      <p className="font-semibold">{selectedIssue.product_name}</p>
                      <p className="text-sm text-gray-600">{selectedIssue.product_code}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">불량 유형</label>
                      <p className="font-semibold">{selectedIssue.defect_type}</p>
                      <p className="text-sm text-red-600">불량 {selectedIssue.defect_quantity}개</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">비용 영향</label>
                      <p className="font-semibold text-orange-600">
                        {(selectedIssue.cost_impact / 10000).toFixed(0)}만원
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">보고자</label>
                      <p className="font-semibold">{selectedIssue.reporter}</p>
                      <p className="text-sm text-gray-600">{selectedIssue.department}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">담당자</label>
                      <p className="font-semibold">{selectedIssue.responsible_person || '미배정'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">목표 해결일</label>
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <p className="font-semibold">{selectedIssue.target_resolution_date}</p>
                      </div>
                    </div>
                    <div className="md:col-span-3">
                      <label className="text-sm font-medium text-gray-500">설명</label>
                      <p className="text-gray-900">{selectedIssue.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 4M Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Search className="w-5 h-5" />
                    4M 분석 (Man, Machine, Material, Method)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {['MAN', 'MACHINE', 'MATERIAL', 'METHOD'].map((category) => {
                      const categoryAnalyses = selectedIssue.analyses_4m?.filter(a => a.category === category) || [];
                      const categoryConfig = {
                        MAN: { label: 'Man (사람)', color: 'text-blue-600', icon: User },
                        MACHINE: { label: 'Machine (설비)', color: 'text-purple-600', icon: Settings },
                        MATERIAL: { label: 'Material (자재)', color: 'text-green-600', icon: Package },
                        METHOD: { label: 'Method (방법)', color: 'text-orange-600', icon: Wrench },
                      };
                      const config = categoryConfig[category as keyof typeof categoryConfig];
                      const Icon = config.icon;

                      return (
                        <div key={category} className="space-y-3">
                          <div className={`flex items-center gap-2 font-semibold ${config.color}`}>
                            <Icon className="w-5 h-5" />
                            {config.label}
                          </div>
                          {categoryAnalyses.length > 0 ? (
                            <ul className="space-y-2 ml-7">
                              {categoryAnalyses.map((item) => (
                                <li key={item.id} className="flex items-start gap-2">
                                  <span className={config.color}>•</span>
                                  <span>{item.description}</span>
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-gray-500 ml-7">분석 항목 없음</p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* 8-Step Problem Solving */}
              <Card className="border-l-4 border-purple-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5" />
                    8-Step Problem Solving
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { stepNumber: 1, label: '1단계: 문제 정의', icon: Target },
                      { stepNumber: 2, label: '2단계: 잠시적 대책', icon: Zap },
                      { stepNumber: 3, label: '3단계: 원인 분석', icon: Search },
                      { stepNumber: 4, label: '4단계: 근본 원인', icon: Lightbulb },
                      { stepNumber: 5, label: '5단계: 영구적 대책', icon: CheckCircle },
                      { stepNumber: 6, label: '6단계: 대책 실행', icon: Settings },
                      { stepNumber: 7, label: '7단계: 효과 확인', icon: BarChart3 },
                      { stepNumber: 8, label: '8단계: 표준화', icon: FileText },
                    ].map((item) => {
                      const stepData = selectedIssue.solving_steps?.find(s => s.step_number === item.stepNumber);
                      const Icon = item.icon;
                      return (
                        <div key={item.stepNumber} className="border rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Icon className={`w-5 h-5 ${stepData?.completed ? 'text-green-600' : 'text-purple-600'}`} />
                            <span className="font-semibold text-gray-900">{item.label}</span>
                            {stepData?.completed && (
                              <CheckCircle className="w-4 h-4 text-green-600 ml-auto" />
                            )}
                          </div>
                          {stepData?.content ? (
                            <p className="text-gray-700 ml-7">{stepData.content}</p>
                          ) : (
                            <p className="text-gray-400 ml-7 italic">입력 대기중...</p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="sticky bottom-0 bg-gray-50 border-t p-6 flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                닫기
              </Button>
              <Button className="bg-purple-600 hover:bg-purple-700">
                <Edit className="w-4 h-4 mr-2" />
                편집
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QualityIssuesPage;
export { QualityIssuesPage };

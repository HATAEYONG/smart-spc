/**
 * 품질 이슈 추적 시스템
 * 불량 발생 시 원인 분석 (4M), 재발 방지 대책 관리, 8-Step Problem Solving
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
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

// 품질 이슈 인터페이스
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
  reporter: string;
  department: string;

  // 4M 분석
  analysis_4m: {
    man: string[];
    machine: string[];
    material: string[];
    method: string[];
  };

  // 8-Step Problem Solving
  problem_solving_steps: {
    step1: string; // 문제 정의
    step2: string; // 잠시적 대책
    step3: string; // 원인 분석
    step4: string; // 근본 원인
    step5: string; // 영구적 대책
    step6: string; // 대책 실행
    step7: string; // 효과 확인
    step8: string; // 표준화
  };

  // 추가 정보
  defect_quantity: number;
  cost_impact: number;
  responsible_person: string;
  target_resolution_date: string;
  actual_resolution_date?: string;
}

// Mock 데이터
const mockQualityIssues: QualityIssue[] = [
  {
    id: 1,
    issue_number: 'QI-2025-001',
    title: '프레스 금형 치수 불량',
    description: '자동차 부품 A-Type의 길이 치수가 규격 100±0.5mm를 초과하여 101.2mm 발견됨',
    product_code: 'PROD-001',
    product_name: '자동차 부품 A-Type',
    defect_type: '치수 초과',
    severity: 'HIGH',
    status: 'IN_PROGRESS',
    reported_date: '2025-01-10',
    reporter: '홍길동',
    department: '생산팀',
    defect_quantity: 150,
    cost_impact: 15000000,
    responsible_person: '김엔지니어',
    target_resolution_date: '2025-01-20',

    analysis_4m: {
      man: ['작업자 숙련도 부족', '교육 부재'],
      machine: ['프레스 기계 노후', '금형 마모'],
      material: ['원자재 두께 편차', '공급원 재질 불안정'],
      method: ['작업 표준서 미준수', '점검 주기 미준수']
    },

    problem_solving_steps: {
      step1: '프레스 금형으로 생산된 제품의 길이 치수가 101.2mm로 규격 초과',
      step2: '불량 제품 전수 검사 및 폐기, 양품만 출하',
      step3: '어시 원인: 금형 마모, 재질 편차, 온도 관리 부족',
      step4: '금형 수명 초과로 인한 마모 (설계 수명 10,000회, 현재 12,500회 사용)',
      step5: '금형 교체 및 주기적 점검 체계 도입',
      step6: '신규 금형 설치 완료, 점검 일정 수립',
      step7: '신규 금형 생산품 100개 측정 결과 전부 규격 준수 확인',
      step8: '금형 수명 기준을 8,000회로 하향 및 자동 알림 시스템 구축 중'
    }
  },
  {
    id: 2,
    issue_number: 'QI-2025-002',
    title: '표면 스크래치 불량',
    description: '전자 부품 B-Type의 표면에 미세 스크래치 다수 발견',
    product_code: 'PROD-002',
    product_name: '전자 부품 B-Type',
    defect_type: '외관 불량',
    severity: 'MEDIUM',
    status: 'INVESTIGATING',
    reported_date: '2025-01-12',
    reporter: '이검사원',
    department: '품질팀',
    defect_quantity: 80,
    cost_impact: 5000000,
    responsible_person: '박엔지니어',
    target_resolution_date: '2025-01-25',

    analysis_4m: {
      man: ['취급 주의 부족', '장갑 미착용'],
      machine: ['컨베이어 벨트 마모', '적재함 거칠음'],
      material: ['원자재 표면 민감도 증가'],
      method: ['취급 공정 미정의', '보호재 미사용']
    },

    problem_solving_steps: {
      step1: '전자 부품 표면 스크래치로 외관 불량 발생',
      step2: '불량품 발생 시점 이후 제품 전수 검사',
      step3: '원인 조사 중: 컨베이어, 취급 방법, 보호재 검토',
      step4: '',
      step5: '',
      step6: '',
      step7: '',
      step8: ''
    }
  },
  {
    id: 3,
    issue_number: 'QI-2025-003',
    title: '용접 불량 - 비드 불균형',
    description: '금속 부품 C-Type 용접부 비드 불균형 발견',
    product_code: 'PROD-003',
    product_name: '금속 부품 C-Type',
    defect_type: '용접 불량',
    severity: 'CRITICAL',
    status: 'OPEN',
    reported_date: '2025-01-14',
    reporter: '정작업자',
    department: '용접팀',
    defect_quantity: 25,
    cost_impact: 25000000,
    responsible_person: '',
    target_resolution_date: '2025-01-21',

    analysis_4m: {
      man: [],
      machine: [],
      material: [],
      method: []
    },

    problem_solving_steps: {
      step1: '',
      step2: '',
      step3: '',
      step4: '',
      step5: '',
      step6: '',
      step7: '',
      step8: ''
    }
  },
  {
    id: 4,
    issue_number: 'QI-2024-045',
    title: '조립 오차 - 치합 불량',
    description: '플라스틱 부품 D-Type 조립 시 치합 불량 발생',
    product_code: 'PROD-004',
    product_name: '플라스틱 부품 D-Type',
    defect_type: '조립 불량',
    severity: 'LOW',
    status: 'RESOLVED',
    reported_date: '2024-12-20',
    reporter: '조현장',
    department: '조립팀',
    defect_quantity: 200,
    cost_impact: 3000000,
    responsible_person: '최엔지니어',
    target_resolution_date: '2024-12-28',
    actual_resolution_date: '2024-12-27',

    analysis_4m: {
      man: ['신규 작업자 교육 부족'],
      machine: ['조립 치구 정밀도 저하'],
      material: ['사출 성형품 수축률 편차'],
      method: ['조립 순서 미준수']
    },

    problem_solving_steps: {
      step1: '조립 시 치합 불량으로 조립 불가 제품 발생',
      step2: '수리 가능품은 수리, 불가능품은 폐기 처리',
      step3: '치구 정밀도 측정, 작업자 숙련도 확인',
      step4: '조립 치구 마모로 인한 위치 정밀도 저하 (±0.3mm → ±0.8mm)',
      step5: '치구 교체 및 주기적 교정 (월 1회)',
      step6: '신규 치구 설치 및 작업자 재교육 완료',
      step7: '개선 후 불량률 2% → 0.1%로 감소 확인',
      step8: '치구 교정 주기를 작업 표준서에 반영 완료'
    }
  },
  {
    id: 5,
    issue_number: 'QI-2025-004',
    title: '열처리 경도 불균형',
    description: '정밀 부품 E-Type 열처리 후 경도 편차 발견',
    product_code: 'PROD-005',
    product_name: '정밀 부품 E-Type',
    defect_type: '열처리 불량',
    severity: 'HIGH',
    status: 'OPEN',
    reported_date: '2025-01-15',
    reporter: '한기사',
    department: '열처리팀',
    defect_quantity: 60,
    cost_impact: 12000000,
    responsible_person: '없음',
    target_resolution_date: '2025-01-22',

    analysis_4m: {
      man: ['온도 설정 오류 가능성'],
      machine: ['열처리로 온도 센서 오작동 의심'],
      material: [],
      method: ['열처리 프로파일 검증 필요']
    },

    problem_solving_steps: {
      step1: '열처리 경도가 규격 HRC 45-48 범위를 벗어남 (측정값: HRC 42-50)',
      step2: '불량품 구분 격리 및 재열처리 검토',
      step3: '온도 센서 교정, 로 내 온도 분포 측정',
      step4: '',
      step5: '',
      step6: '',
      step7: '',
      step8: ''
    }
  }
];

const QualityIssuesPage: React.FC = () => {
  const [issues, setIssues] = useState<QualityIssue[]>(mockQualityIssues);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIssue, setSelectedIssue] = useState<QualityIssue | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

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
                      <div className="text-sm text-gray-500">{issue.reporter} / {issue.department}</div>
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
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 font-semibold text-blue-600">
                        <User className="w-5 h-5" />
                        Man (사람)
                      </div>
                      {selectedIssue.analysis_4m.man.length > 0 ? (
                        <ul className="space-y-2 ml-7">
                          {selectedIssue.analysis_4m.man.map((item, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-blue-600">•</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500 ml-7">분석 항목 없음</p>
                      )}
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center gap-2 font-semibold text-purple-600">
                        <Settings className="w-5 h-5" />
                        Machine (설비)
                      </div>
                      {selectedIssue.analysis_4m.machine.length > 0 ? (
                        <ul className="space-y-2 ml-7">
                          {selectedIssue.analysis_4m.machine.map((item, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-purple-600">•</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500 ml-7">분석 항목 없음</p>
                      )}
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center gap-2 font-semibold text-green-600">
                        <Package className="w-5 h-5" />
                        Material (자재)
                      </div>
                      {selectedIssue.analysis_4m.material.length > 0 ? (
                        <ul className="space-y-2 ml-7">
                          {selectedIssue.analysis_4m.material.map((item, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-green-600">•</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500 ml-7">분석 항목 없음</p>
                      )}
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center gap-2 font-semibold text-orange-600">
                        <Wrench className="w-5 h-5" />
                        Method (방법)
                      </div>
                      {selectedIssue.analysis_4m.method.length > 0 ? (
                        <ul className="space-y-2 ml-7">
                          {selectedIssue.analysis_4m.method.map((item, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-orange-600">•</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500 ml-7">분석 항목 없음</p>
                      )}
                    </div>
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
                      { step: 'step1', label: '1단계: 문제 정의', icon: Target },
                      { step: 'step2', label: '2단계: 잠시적 대책', icon: Zap },
                      { step: 'step3', label: '3단계: 원인 분석', icon: Search },
                      { step: 'step4', label: '4단계: 근본 원인', icon: Lightbulb },
                      { step: 'step5', label: '5단계: 영구적 대책', icon: CheckCircle },
                      { step: 'step6', label: '6단계: 대책 실행', icon: Settings },
                      { step: 'step7', label: '7단계: 효과 확인', icon: BarChart3 },
                      { step: 'step8', label: '8단계: 표준화', icon: FileText },
                    ].map((item) => {
                      const content = selectedIssue.problem_solving_steps[item.step as keyof typeof selectedIssue.problem_solving_steps];
                      const Icon = item.icon;
                      return (
                        <div key={item.step} className="border rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Icon className="w-5 h-5 text-purple-600" />
                            <span className="font-semibold text-gray-900">{item.label}</span>
                          </div>
                          {content ? (
                            <p className="text-gray-700 ml-7">{content}</p>
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

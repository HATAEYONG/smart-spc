/**
 * 작업지시 관리 페이지
 * 작업지시, 설비, 치공구 연계 관리 및 수명 예측
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  ClipboardCheck,
  Wrench,
  AlertTriangle,
  Clock,
  TrendingUp,
  Calendar,
  Settings,
  Search,
  Plus,
  Eye,
  Edit,
  Trash2,
  Filter,
  Download,
  BarChart3,
  Activity,
  Target,
  Zap,
  CheckCircle,
  XCircle,
  Timer
} from 'lucide-react';

// 작업지시 인터페이스
interface WorkOrder {
  id: number;
  order_number: string;
  product_code: string;
  product_name: string;
  quantity: number;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'ON_HOLD';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  start_date: string;
  end_date: string;
  equipment: EquipmentInfo;
  tools: ToolInfo[];
  predicted_completion_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  risk_reasons: string[];
}

interface EquipmentInfo {
  id: number;
  code: string;
  name: string;
  status: string;
  health_score: number;
  predicted_failure_days?: number;
}

interface ToolInfo {
  id: number;
  code: string;
  name: string;
  current_usage: number;
  useful_life: number;
  predicted_remaining_days: number;
  replacement_urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

// Mock 데이터
const mockWorkOrders: WorkOrder[] = [
  {
    id: 1,
    order_number: 'WO-2025-001',
    product_code: 'PROD-001',
    product_name: '자동차 부품 A-Type',
    quantity: 5000,
    status: 'IN_PROGRESS',
    priority: 'HIGH',
    start_date: '2025-01-15',
    end_date: '2025-01-25',
    equipment: {
      id: 1,
      code: 'EQ-001',
      name: 'CNC 정밀 가공기 M-5000',
      status: 'OPERATIONAL',
      health_score: 85,
      predicted_failure_days: 120
    },
    tools: [
      {
        id: 1,
        code: 'TOL-001',
        name: '프레스 금형 Type-A',
        current_usage: 8500,
        useful_life: 10000,
        predicted_remaining_days: 15,
        replacement_urgency: 'MEDIUM'
      },
      {
        id: 2,
        code: 'TOL-002',
        name: '컷터 공구 10mm',
        current_usage: 9200,
        useful_life: 10000,
        predicted_remaining_days: 7,
        replacement_urgency: 'HIGH'
      }
    ],
    predicted_completion_risk: 'MEDIUM',
    risk_reasons: [
      '컷터 공구가 7일 내 교체 필요',
      '설비 상태 점검 권장'
    ]
  },
  {
    id: 2,
    order_number: 'WO-2025-002',
    product_code: 'PROD-002',
    product_name: '전자 부품 B-Type',
    quantity: 3000,
    status: 'PENDING',
    priority: 'URGENT',
    start_date: '2025-01-20',
    end_date: '2025-01-28',
    equipment: {
      id: 2,
      code: 'EQ-002',
      name: '사출 성형기 S-3000',
      status: 'MAINTENANCE',
      health_score: 72,
      predicted_failure_days: 45
    },
    tools: [
      {
        id: 3,
        code: 'TOL-003',
        name: '드릴 비트 5mm',
        current_usage: 4500,
        useful_life: 10000,
        predicted_remaining_days: 45,
        replacement_urgency: 'LOW'
      }
    ],
    predicted_completion_risk: 'HIGH',
    risk_reasons: [
      '설비 현재 정비 중',
      '작업 시작 지연 예상'
    ]
  },
  {
    id: 3,
    order_number: 'WO-2025-003',
    product_code: 'PROD-003',
    product_name: '금속 부품 C-Type',
    quantity: 8000,
    status: 'IN_PROGRESS',
    priority: 'MEDIUM',
    start_date: '2025-01-10',
    end_date: '2025-01-30',
    equipment: {
      id: 3,
      code: 'EQ-003',
      name: '레이저 절단기 L-2000',
      status: 'OPERATIONAL',
      health_score: 92,
      predicted_failure_days: 180
    },
    tools: [
      {
        id: 4,
        code: 'TOL-004',
        name: '연마 디스크 200mm',
        current_usage: 9800,
        useful_life: 10000,
        predicted_remaining_days: 3,
        replacement_urgency: 'CRITICAL'
      },
      {
        id: 5,
        code: 'TOL-005',
        name: '탭 M6',
        current_usage: 7200,
        useful_life: 10000,
        predicted_remaining_days: 22,
        replacement_urgency: 'LOW'
      }
    ],
    predicted_completion_risk: 'HIGH',
    risk_reasons: [
      '연마 디스크 긴급 교체 필요',
      '3일 내 파손 위험 높음'
    ]
  },
  {
    id: 4,
    order_number: 'WO-2025-004',
    product_code: 'PROD-004',
    product_name: '플라스틱 부품 D-Type',
    quantity: 2000,
    status: 'COMPLETED',
    priority: 'LOW',
    start_date: '2025-01-05',
    end_date: '2025-01-15',
    equipment: {
      id: 4,
      code: 'EQ-004',
      name: '프레스 기계 P-1000',
      status: 'OPERATIONAL',
      health_score: 95,
      predicted_failure_days: 200
    },
    tools: [
      {
        id: 6,
        code: 'TOL-006',
        name: '금형 Type-D',
        current_usage: 3000,
        useful_life: 10000,
        predicted_remaining_days: 70,
        replacement_urgency: 'LOW'
      }
    ],
    predicted_completion_risk: 'LOW',
    risk_reasons: []
  },
  {
    id: 5,
    order_number: 'WO-2025-005',
    product_code: 'PROD-005',
    product_name: '정밀 부품 E-Type',
    quantity: 1500,
    status: 'ON_HOLD',
    priority: 'MEDIUM',
    start_date: '2025-01-18',
    end_date: '2025-01-26',
    equipment: {
      id: 5,
      code: 'EQ-005',
      name: '선반 기계 T-4000',
      status: 'OPERATIONAL',
      health_score: 78,
      predicted_failure_days: 60
    },
    tools: [],
    predicted_completion_risk: 'MEDIUM',
    risk_reasons: [
      '치공구 미할당',
      '자재 대기 중'
    ]
  }
];

const WorkOrderManagementPage: React.FC = () => {
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>(mockWorkOrders);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedRisk, setSelectedRisk] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrder, setSelectedOrder] = useState<WorkOrder | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const getStatusBadge = (status: string) => {
    const styles = {
      PENDING: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      IN_PROGRESS: 'bg-blue-100 text-blue-800 border-blue-300',
      COMPLETED: 'bg-green-100 text-green-800 border-green-300',
      CANCELLED: 'bg-red-100 text-red-800 border-red-300',
      ON_HOLD: 'bg-gray-100 text-gray-800 border-gray-300',
    };
    const labels = {
      PENDING: '대기',
      IN_PROGRESS: '진행중',
      COMPLETED: '완료',
      CANCELLED: '취소',
      ON_HOLD: '보류',
    };
    return (
      <Badge className={styles[status as keyof typeof styles]}>
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const styles = {
      LOW: 'bg-gray-100 text-gray-800 border-gray-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
      URGENT: 'bg-red-100 text-red-800 border-red-300',
    };
    const labels = {
      LOW: '낮음',
      MEDIUM: '중간',
      HIGH: '높음',
      URGENT: '긴급',
    };
    return (
      <Badge className={styles[priority as keyof typeof styles]}>
        {labels[priority as keyof typeof labels]}
      </Badge>
    );
  };

  const getRiskBadge = (risk: string) => {
    const styles = {
      LOW: 'bg-green-100 text-green-800 border-green-300',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      HIGH: 'bg-red-100 text-red-800 border-red-300',
    };
    const labels = {
      LOW: '낮음',
      MEDIUM: '중간',
      HIGH: '높음',
    };
    const icons = {
      LOW: CheckCircle,
      MEDIUM: AlertTriangle,
      HIGH: XCircle,
    };
    const Icon = icons[risk as keyof typeof icons];
    return (
      <Badge className={styles[risk as keyof typeof styles]}>
        <Icon className="w-3 h-3 mr-1" />
        {labels[risk as keyof typeof labels]}
      </Badge>
    );
  };

  const getToolUrgencyBadge = (urgency: string) => {
    const styles = {
      LOW: 'bg-green-100 text-green-800',
      MEDIUM: 'bg-yellow-100 text-yellow-800',
      HIGH: 'bg-orange-100 text-orange-800',
      CRITICAL: 'bg-red-100 text-red-800',
    };
    const labels = {
      LOW: '정상',
      MEDIUM: '주의',
      HIGH: '긴급',
      CRITICAL: '즉시',
    };
    return (
      <Badge className={styles[urgency as keyof typeof styles]}>
        {labels[urgency as keyof typeof labels]}
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

  const filteredOrders = workOrders.filter(order => {
    const matchStatus = selectedStatus === 'ALL' || order.status === selectedStatus;
    const matchRisk = selectedRisk === 'ALL' || order.predicted_completion_risk === selectedRisk;
    const matchSearch = searchTerm === '' ||
      order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.equipment.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchStatus && matchRisk && matchSearch;
  });

  const handleViewDetail = (order: WorkOrder) => {
    setSelectedOrder(order);
    setShowDetailModal(true);
  };

  const stats = {
    total: workOrders.length,
    inProgress: workOrders.filter(o => o.status === 'IN_PROGRESS').length,
    highRisk: workOrders.filter(o => o.predicted_completion_risk === 'HIGH').length,
    urgentTools: workOrders.reduce((count, order) =>
      count + order.tools.filter(t => t.replacement_urgency === 'HIGH' || t.replacement_urgency === 'CRITICAL').length, 0
    )
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <ClipboardCheck className="w-8 h-8 text-purple-600" />
            작업지시 관리
          </h1>
          <p className="text-gray-600 mt-2">
            작업지시, 설비, 치공구 통합 관리 및 AI 기반 위험 예측
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            className="flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            내보내기
          </Button>
          <Button className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4" />
            새 작업지시
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-l-4 border-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">전체 작업지시</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
              </div>
              <ClipboardCheck className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">진행 중</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">{stats.inProgress}</p>
              </div>
              <Activity className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-red-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">높은 위험</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{stats.highRisk}</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-red-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-orange-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">긴급 치공구</p>
                <p className="text-3xl font-bold text-orange-600 mt-1">{stats.urgentTools}</p>
              </div>
              <Wrench className="w-12 h-12 text-orange-500 opacity-20" />
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
                  placeholder="작업지시 번호, 제품, 설비..."
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
                <option value="PENDING">대기</option>
                <option value="IN_PROGRESS">진행중</option>
                <option value="COMPLETED">완료</option>
                <option value="ON_HOLD">보류</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">위험도</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                value={selectedRisk}
                onChange={(e) => setSelectedRisk(e.target.value)}
              >
                <option value="ALL">전체</option>
                <option value="LOW">낮음</option>
                <option value="MEDIUM">중간</option>
                <option value="HIGH">높음</option>
              </select>
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setSearchTerm('');
                  setSelectedStatus('ALL');
                  setSelectedRisk('ALL');
                }}
              >
                <Filter className="w-4 h-4 mr-2" />
                필터 초기화
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Work Orders List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            작업지시 목록 ({filteredOrders.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left p-4 font-semibold text-gray-700">작업지시 번호</th>
                  <th className="text-left p-4 font-semibold text-gray-700">제품</th>
                  <th className="text-left p-4 font-semibold text-gray-700">설비</th>
                  <th className="text-left p-4 font-semibold text-gray-700">치공구 상태</th>
                  <th className="text-left p-4 font-semibold text-gray-700">일정</th>
                  <th className="text-left p-4 font-semibold text-gray-700">상태</th>
                  <th className="text-left p-4 font-semibold text-gray-700">우선순위</th>
                  <th className="text-left p-4 font-semibold text-gray-700">위험도</th>
                  <th className="text-left p-4 font-semibold text-gray-700">작업</th>
                </tr>
              </thead>
              <tbody>
                {filteredOrders.map((order) => (
                  <tr key={order.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="p-4">
                      <div className="font-medium text-purple-600">{order.order_number}</div>
                      <div className="text-sm text-gray-500">{order.quantity}개</div>
                    </td>
                    <td className="p-4">
                      <div className="font-medium">{order.product_name}</div>
                      <div className="text-sm text-gray-500">{order.product_code}</div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2 mb-1">
                        <Settings className="w-4 h-4 text-gray-500" />
                        <span className="font-medium">{order.equipment.name}</span>
                      </div>
                      <div className="text-sm text-gray-500">{order.equipment.code}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full ${getUsageColor(order.equipment.health_score)}`}
                            style={{ width: `${order.equipment.health_score}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">{order.equipment.health_score}%</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="space-y-2">
                        {order.tools.length > 0 ? (
                          order.tools.map((tool) => {
                            const usagePercent = getUsagePercentage(tool.current_usage, tool.useful_life);
                            return (
                              <div key={tool.id} className="text-sm">
                                <div className="flex items-center justify-between mb-1">
                                  <span className="font-medium">{tool.name}</span>
                                  {getToolUrgencyBadge(tool.replacement_urgency)}
                                </div>
                                <div className="flex items-center gap-2">
                                  <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                                    <div
                                      className={`h-1.5 rounded-full ${getUsageColor(usagePercent)}`}
                                      style={{ width: `${Math.min(usagePercent, 100)}%` }}
                                    />
                                  </div>
                                  <span className="text-xs text-gray-600">{tool.predicted_remaining_days}일</span>
                                </div>
                              </div>
                            );
                          })
                        ) : (
                          <span className="text-sm text-gray-500">미할당</span>
                        )}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2 text-sm">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <div>
                          <div>{order.start_date}</div>
                          <div className="text-gray-500">~ {order.end_date}</div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">{getStatusBadge(order.status)}</td>
                    <td className="p-4">{getPriorityBadge(order.priority)}</td>
                    <td className="p-4">{getRiskBadge(order.predicted_completion_risk)}</td>
                    <td className="p-4">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleViewDetail(order)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Detail Modal */}
      {showDetailModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedOrder.order_number}</h2>
                <p className="text-gray-600">{selectedOrder.product_name}</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDetailModal(false)}
              >
                ✕
              </Button>
            </div>

            <div className="p-6 space-y-6">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="text-sm font-medium text-gray-500">제품 코드</label>
                  <p className="text-lg font-semibold">{selectedOrder.product_code}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">생산 수량</label>
                  <p className="text-lg font-semibold">{selectedOrder.quantity.toLocaleString()}개</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">상태</label>
                  <div>{getStatusBadge(selectedOrder.status)}</div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">우선순위</label>
                  <div>{getPriorityBadge(selectedOrder.priority)}</div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">시작일</label>
                  <p className="text-lg font-semibold">{selectedOrder.start_date}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">종료일</label>
                  <p className="text-lg font-semibold">{selectedOrder.end_date}</p>
                </div>
              </div>

              {/* Equipment Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    할당 설비 정보
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="text-sm font-medium text-gray-500">설비 코드</label>
                      <p className="text-lg font-semibold">{selectedOrder.equipment.code}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">설비명</label>
                      <p className="text-lg font-semibold">{selectedOrder.equipment.name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">상태</label>
                      <Badge className="bg-blue-100 text-blue-800">{selectedOrder.equipment.status}</Badge>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">건강 점수</label>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 bg-gray-200 rounded-full h-3">
                          <div
                            className={`h-3 rounded-full ${getUsageColor(selectedOrder.equipment.health_score)}`}
                            style={{ width: `${selectedOrder.equipment.health_score}%` }}
                          />
                        </div>
                        <span className="text-lg font-bold">{selectedOrder.equipment.health_score}%</span>
                      </div>
                    </div>
                    {selectedOrder.equipment.predicted_failure_days && (
                      <div className="md:col-span-2">
                        <label className="text-sm font-medium text-gray-500">예상 잔존 수명</label>
                        <div className="flex items-center gap-2">
                          <Clock className="w-5 h-5 text-blue-500" />
                          <span className="text-lg font-semibold">
                            약 {selectedOrder.equipment.predicted_failure_days}일
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Tools Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Wrench className="w-5 h-5" />
                    할당 치공구 정보 ({selectedOrder.tools.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedOrder.tools.length > 0 ? (
                    <div className="space-y-4">
                      {selectedOrder.tools.map((tool) => {
                        const usagePercent = getUsagePercentage(tool.current_usage, tool.useful_life);
                        return (
                          <div key={tool.id} className="border rounded-lg p-4">
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-3">
                              <div>
                                <label className="text-sm font-medium text-gray-500">치공구 코드</label>
                                <p className="font-semibold">{tool.code}</p>
                              </div>
                              <div>
                                <label className="text-sm font-medium text-gray-500">치공구명</label>
                                <p className="font-semibold">{tool.name}</p>
                              </div>
                              <div>
                                <label className="text-sm font-medium text-gray-500">교체 시급성</label>
                                <div>{getToolUrgencyBadge(tool.replacement_urgency)}</div>
                              </div>
                              <div>
                                <label className="text-sm font-medium text-gray-500">잔존 수명</label>
                                <div className="flex items-center gap-2">
                                  <Clock className="w-4 h-4 text-blue-500" />
                                  <span className="font-semibold">{tool.predicted_remaining_days}일</span>
                                </div>
                              </div>
                            </div>
                            <div>
                              <div className="flex justify-between text-sm mb-2">
                                <span className="text-gray-600">사용량</span>
                                <span className="font-medium">
                                  {tool.current_usage.toLocaleString()} / {tool.useful_life.toLocaleString()}
                                </span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-3">
                                <div
                                  className={`h-3 rounded-full ${getUsageColor(usagePercent)}`}
                                  style={{ width: `${Math.min(usagePercent, 100)}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Wrench className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                      <p>할당된 치공구가 없습니다</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Risk Analysis */}
              <Card className="border-l-4 border-orange-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-orange-500" />
                    AI 위험 분석
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4 mb-4">
                    <span className="text-sm font-medium text-gray-600">완료 위험도:</span>
                    {getRiskBadge(selectedOrder.predicted_completion_risk)}
                  </div>
                  {selectedOrder.risk_reasons.length > 0 ? (
                    <div className="space-y-2">
                      {selectedOrder.risk_reasons.map((reason, index) => (
                        <div key={index} className="flex items-start gap-2 p-3 bg-orange-50 rounded-lg">
                          <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-orange-900">{reason}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-start gap-2 p-3 bg-green-50 rounded-lg">
                      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-green-900">현재 특별한 위험 요인이 없습니다.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="sticky bottom-0 bg-gray-50 border-t p-6 flex justify-end gap-3">
              <Button variant="outline" onClick={() => setShowDetailModal(false)}>
                닫기
              </Button>
              <Button className="bg-purple-600 hover:bg-purple-700">
                편집
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkOrderManagementPage;
export { WorkOrderManagementPage };

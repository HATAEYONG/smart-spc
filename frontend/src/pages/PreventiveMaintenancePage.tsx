/**
 * 예방 보전 일정 관리 페이지
 * PM(Preventive Maintenance) 스케줄링, 작업자 할당, 완료 관리
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Calendar,
  Clock,
  Settings,
  User,
  CheckCircle,
  AlertTriangle,
  Plus,
  Filter,
  Search,
  Download,
  Wrench,
  Edit,
  Eye
} from 'lucide-react';

interface PMTask {
  id: number;
  task_number: string;
  equipment_code: string;
  equipment_name: string;
  task_type: 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'QUARTERLY' | 'YEARLY' | 'CUSTOM';
  task_name: string;
  description: string;
  scheduled_date: string;
  status: 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'COMPLETED' | 'OVERDUE';
  assigned_to?: string;
  estimated_duration: number; // hours
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  last_completed?: string;
  next_due: string;
  completion_notes?: string;
}

const mockPMTasks: PMTask[] = [
  {
    id: 1,
    task_number: 'PM-2025-001',
    equipment_code: 'EQ-001',
    equipment_name: 'CNC 정밀 가공기 M-5000',
    task_type: 'DAILY',
    task_name: '일일 점검 및 청소',
    description: '설비 외부 청소, 이상 유무 확인, 윤활 상태 점검',
    scheduled_date: '2025-01-15',
    status: 'COMPLETED',
    assigned_to: '홍기사',
    estimated_duration: 1,
    priority: 'MEDIUM',
    last_completed: '2025-01-15',
    next_due: '2025-01-16',
    completion_notes: '정상, 이상 없음'
  },
  {
    id: 2,
    task_number: 'PM-2025-002',
    equipment_code: 'EQ-001',
    equipment_name: 'CNC 정밀 가공기 M-5000',
    task_type: 'WEEKLY',
    task_name: '주간 정밀 점검',
    description: '스핀들 진동 측정, 볼트 체결 확인, 필터 교환',
    scheduled_date: '2025-01-15',
    status: 'IN_PROGRESS',
    assigned_to: '김정비',
    estimated_duration: 3,
    priority: 'HIGH',
    last_completed: '2025-01-08',
    next_due: '2025-01-15'
  },
  {
    id: 3,
    task_number: 'PM-2025-003',
    equipment_code: 'EQ-002',
    equipment_name: '사출 성형기 S-3000',
    task_type: 'MONTHLY',
    task_name: '월간 완전 정비',
    description: '히터 교체, 노즐 청소, 유압계 확인, 안전 장치 점검',
    scheduled_date: '2025-01-20',
    status: 'ASSIGNED',
    assigned_to: '이엔지니어',
    estimated_duration: 8,
    priority: 'HIGH',
    last_completed: '2024-12-20',
    next_due: '2025-01-20'
  },
  {
    id: 4,
    task_number: 'PM-2025-004',
    equipment_code: 'EQ-003',
    equipment_name: '레이저 절단기 L-2000',
    task_type: 'QUARTERLY',
    task_name: '분기별 대정비',
    description: '레이저 출력 조정, 광학계 청소, 냉각수 교환',
    scheduled_date: '2025-01-10',
    status: 'OVERDUE',
    assigned_to: '박기사',
    estimated_duration: 6,
    priority: 'HIGH',
    last_completed: '2024-10-10',
    next_due: '2025-01-10'
  },
  {
    id: 5,
    task_number: 'PM-2025-005',
    equipment_code: 'EQ-004',
    equipment_name: '프레스 기계 P-1000',
    task_type: 'YEARLY',
    task_name: '연간 전면 점검',
    description: '프레임 변형 측정, 모터 교체, 유압시스템 오버홀',
    scheduled_date: '2025-03-01',
    status: 'PENDING',
    estimated_duration: 16,
    priority: 'MEDIUM',
    last_completed: '2024-03-01',
    next_due: '2025-03-01'
  },
  {
    id: 6,
    task_number: 'PM-2025-006',
    equipment_code: 'EQ-005',
    equipment_name: '선반 기계 T-4000',
    task_type: 'WEEKLY',
    task_name: '주간 윤활 관리',
    description: '급유 지점 윤활, 오일 레벨 확인, 누유 점검',
    scheduled_date: '2025-01-15',
    status: 'COMPLETED',
    assigned_to: '최기사',
    estimated_duration: 2,
    priority: 'LOW',
    last_completed: '2025-01-15',
    next_due: '2025-01-22',
    completion_notes: '윤활 완료, 오일 보충'
  },
  {
    id: 7,
    task_number: 'PM-2025-007',
    equipment_code: 'EQ-002',
    equipment_name: '사출 성형기 S-3000',
    task_type: 'DAILY',
    task_name: '일일 온도 기록',
    description: '가열 온도 기록, 냉각수 온도 확인',
    scheduled_date: '2025-01-16',
    status: 'PENDING',
    estimated_duration: 0.5,
    priority: 'LOW',
    last_completed: '2025-01-15',
    next_due: '2025-01-16'
  }
];

const PreventiveMaintenancePage: React.FC = () => {
  const [tasks, setTasks] = useState<PMTask[]>(mockPMTasks);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTask, setSelectedTask] = useState<PMTask | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const getTypeBadge = (type: string) => {
    const styles = {
      DAILY: 'bg-blue-100 text-blue-800',
      WEEKLY: 'bg-green-100 text-green-800',
      MONTHLY: 'bg-yellow-100 text-yellow-800',
      QUARTERLY: 'bg-orange-100 text-orange-800',
      YEARLY: 'bg-purple-100 text-purple-800',
      CUSTOM: 'bg-gray-100 text-gray-800',
    };
    const labels = {
      DAILY: '일일',
      WEEKLY: '주간',
      MONTHLY: '월간',
      QUARTERLY: '분기',
      YEARLY: '연간',
      CUSTOM: '사용자',
    };
    return (
      <Badge className={styles[type as keyof typeof styles]}>
        {labels[type as keyof typeof labels]}
      </Badge>
    );
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      PENDING: 'bg-gray-100 text-gray-800 border-gray-300',
      ASSIGNED: 'bg-blue-100 text-blue-800 border-blue-300',
      IN_PROGRESS: 'bg-purple-100 text-purple-800 border-purple-300',
      COMPLETED: 'bg-green-100 text-green-800 border-green-300',
      OVERDUE: 'bg-red-100 text-red-800 border-red-300',
    };
    const labels = {
      PENDING: '대기',
      ASSIGNED: '할당',
      IN_PROGRESS: '진행중',
      COMPLETED: '완료',
      OVERDUE: '지연',
    };
    const icons = {
      PENDING: Clock,
      ASSIGNED: User,
      IN_PROGRESS: Settings,
      COMPLETED: CheckCircle,
      OVERDUE: AlertTriangle,
    };
    const Icon = icons[status as keyof typeof icons];
    return (
      <Badge className={styles[status as keyof typeof styles]}>
        <Icon className="w-3 h-3 mr-1" />
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const styles = {
      LOW: 'bg-gray-100 text-gray-800',
      MEDIUM: 'bg-yellow-100 text-yellow-800',
      HIGH: 'bg-red-100 text-red-800',
    };
    const labels = {
      LOW: '낮음',
      MEDIUM: '중간',
      HIGH: '높음',
    };
    return (
      <Badge className={styles[priority as keyof typeof styles]}>
        {labels[priority as keyof typeof labels]}
      </Badge>
    );
  };

  const filteredTasks = tasks.filter(task => {
    const matchStatus = selectedStatus === 'ALL' || task.status === selectedStatus;
    const matchType = selectedType === 'ALL' || task.task_type === selectedType;
    const matchSearch = searchTerm === '' ||
      task.task_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.equipment_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.task_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchStatus && matchType && matchSearch;
  });

  const stats = {
    total: tasks.length,
    pending: tasks.filter(t => t.status === 'PENDING').length,
    inProgress: tasks.filter(t => t.status === 'IN_PROGRESS' || t.status === 'ASSIGNED').length,
    completed: tasks.filter(t => t.status === 'COMPLETED').length,
    overdue: tasks.filter(t => t.status === 'OVERDUE').length
  };

  const handleViewDetail = (task: PMTask) => {
    setSelectedTask(task);
    setShowDetailModal(true);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Calendar className="w-8 h-8 text-blue-600" />
            예방 보전 일정 관리
          </h1>
          <p className="text-gray-600 mt-2">
            PM(Preventive Maintenance) 스케줄링 및 작업 관리
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            내보내기
          </Button>
          <Button className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4" />
            새 작업 추가
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">전체 작업</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
              </div>
              <Wrench className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-gray-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">대기중</p>
                <p className="text-3xl font-bold text-gray-600 mt-1">{stats.pending}</p>
              </div>
              <Clock className="w-12 h-12 text-gray-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">진행중</p>
                <p className="text-3xl font-bold text-purple-600 mt-1">{stats.inProgress}</p>
              </div>
              <Settings className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">완료</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.completed}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-red-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">지연</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{stats.overdue}</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-red-500 opacity-20" />
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
                  placeholder="작업 번호, 설비, 작업명..."
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
                <option value="ASSIGNED">할당</option>
                <option value="IN_PROGRESS">진행중</option>
                <option value="COMPLETED">완료</option>
                <option value="OVERDUE">지연</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">주기</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
              >
                <option value="ALL">전체</option>
                <option value="DAILY">일일</option>
                <option value="WEEKLY">주간</option>
                <option value="MONTHLY">월간</option>
                <option value="QUARTERLY">분기</option>
                <option value="YEARLY">연간</option>
              </select>
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setSearchTerm('');
                  setSelectedStatus('ALL');
                  setSelectedType('ALL');
                }}
              >
                <Filter className="w-4 h-4 mr-2" />
                필터 초기화
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tasks List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wrench className="w-5 h-5" />
            PM 작업 목록 ({filteredTasks.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left p-4 font-semibold text-gray-700">작업 번호</th>
                  <th className="text-left p-4 font-semibold text-gray-700">설비</th>
                  <th className="text-left p-4 font-semibold text-gray-700">작업명</th>
                  <th className="text-left p-4 font-semibold text-gray-700">주기</th>
                  <th className="text-left p-4 font-semibold text-gray-700">예정일</th>
                  <th className="text-left p-4 font-semibold text-gray-700">담당자</th>
                  <th className="text-left p-4 font-semibold text-gray-700">상태</th>
                  <th className="text-left p-4 font-semibold text-gray-700">우선순위</th>
                  <th className="text-left p-4 font-semibold text-gray-700">작업</th>
                </tr>
              </thead>
              <tbody>
                {filteredTasks.map((task) => (
                  <tr key={task.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="p-4 font-medium text-purple-600">{task.task_number}</td>
                    <td className="p-4">
                      <div className="font-medium">{task.equipment_name}</div>
                      <div className="text-sm text-gray-500">{task.equipment_code}</div>
                    </td>
                    <td className="p-4">
                      <div className="font-medium">{task.task_name}</div>
                      <div className="text-sm text-gray-500">{task.estimated_duration}시간 예상</div>
                    </td>
                    <td className="p-4">{getTypeBadge(task.task_type)}</td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <span>{task.scheduled_date}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      {task.assigned_to ? (
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4 text-gray-500" />
                          <span>{task.assigned_to}</span>
                        </div>
                      ) : (
                        <span className="text-gray-400">미할당</span>
                      )}
                    </td>
                    <td className="p-4">{getStatusBadge(task.status)}</td>
                    <td className="p-4">{getPriorityBadge(task.priority)}</td>
                    <td className="p-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewDetail(task)}
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
      {showDetailModal && selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedTask.task_number}</h2>
                <p className="text-gray-600">{selectedTask.task_name}</p>
              </div>
              <div className="flex items-center gap-3">
                {getTypeBadge(selectedTask.task_type)}
                {getStatusBadge(selectedTask.status)}
                {getPriorityBadge(selectedTask.priority)}
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
              {/* Task Information */}
              <Card>
                <CardHeader>
                  <CardTitle>작업 정보</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="text-sm font-medium text-gray-500">설비</label>
                      <p className="font-semibold">{selectedTask.equipment_name}</p>
                      <p className="text-sm text-gray-600">{selectedTask.equipment_code}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">예상 소요시간</label>
                      <p className="font-semibold">{selectedTask.estimated_duration}시간</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">예정일</label>
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <p className="font-semibold">{selectedTask.scheduled_date}</p>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">다음 예정일</label>
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <p className="font-semibold">{selectedTask.next_due}</p>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">담당자</label>
                      <p className="font-semibold">{selectedTask.assigned_to || '미할당'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">마지막 완료일</label>
                      <p className="font-semibold">{selectedTask.last_completed || '미완료'}</p>
                    </div>
                    <div className="md:col-span-2">
                      <label className="text-sm font-medium text-gray-500">작업 설명</label>
                      <p className="text-gray-900">{selectedTask.description}</p>
                    </div>
                    {selectedTask.completion_notes && (
                      <div className="md:col-span-2">
                        <label className="text-sm font-medium text-gray-500">완료 메모</label>
                        <p className="text-gray-900 bg-green-50 p-3 rounded-lg">{selectedTask.completion_notes}</p>
                      </div>
                    )}
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

export default PreventiveMaintenancePage;
export { PreventiveMaintenancePage };

/**
 * 연계 이력 관리 페이지
 * ERP/MES 연계 데이터 동기화 이력 조회 및 모니터링
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  History,
  CheckCircle,
  XCircle,
  Clock,
  Search,
  Filter,
  Download,
  Calendar,
  Database,
  TrendingUp,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';

interface SyncHistory {
  id: number;
  sync_id: string;
  system_name: string;
  sync_type: 'FULL' | 'INCREMENTAL' | 'MANUAL';
  start_time: string;
  end_time: string;
  status: 'SUCCESS' | 'FAILED' | 'IN_PROGRESS' | 'PARTIAL';
  records_processed: number;
  records_success: number;
  records_failed: number;
  duration_seconds: number;
  error_message?: string;
  data_types: string[];
}

const mockSyncHistory: SyncHistory[] = [
  {
    id: 1,
    sync_id: 'SYNC-20250115-001',
    system_name: 'SAP ERP',
    sync_type: 'INCREMENTAL',
    start_time: '2025-01-15 14:30:00',
    end_time: '2025-01-15 14:30:45',
    status: 'SUCCESS',
    records_processed: 1520,
    records_success: 1520,
    records_failed: 0,
    duration_seconds: 45,
    data_types: ['생산주문', '자재정보']
  },
  {
    id: 2,
    sync_id: 'SYNC-20250115-002',
    system_name: 'MES 시스템',
    sync_type: 'INCREMENTAL',
    start_time: '2025-01-15 14:32:00',
    end_time: '2025-01-15 14:32:30',
    status: 'SUCCESS',
    records_processed: 850,
    records_success: 845,
    records_failed: 5,
    duration_seconds: 30,
    data_types: ['생산실적', '설비상태']
  },
  {
    id: 3,
    sync_id: 'SYNC-20250115-003',
    system_name: '창고 관리 시스템',
    sync_type: 'MANUAL',
    start_time: '2025-01-15 14:25:00',
    end_time: '2025-01-15 14:27:30',
    status: 'FAILED',
    records_processed: 320,
    records_success: 0,
    records_failed: 320,
    duration_seconds: 150,
    error_message: 'API 연결 타임아웃: 150초 경과',
    data_types: ['재고정보', '입출고']
  },
  {
    id: 4,
    sync_id: 'SYNC-20250115-004',
    system_name: 'SAP ERP',
    sync_type: 'FULL',
    start_time: '2025-01-15 10:00:00',
    end_time: '2025-01-15 10:15:30',
    status: 'SUCCESS',
    records_processed: 15840,
    records_success: 15830,
    records_failed: 10,
    duration_seconds: 930,
    data_types: ['BOM', '작업지시', '자재정보', '생산주문']
  },
  {
    id: 5,
    sync_id: 'SYNC-20250115-005',
    system_name: 'PLM 시스템',
    sync_type: 'MANUAL',
    start_time: '2025-01-15 12:00:00',
    end_time: '2025-01-15 12:05:00',
    status: 'PARTIAL',
    records_processed: 420,
    records_success: 380,
    records_failed: 40,
    duration_seconds: 300,
    error_message: '일부 도면 파일 다운로드 실패',
    data_types: ['제품설계', '도면']
  },
  {
    id: 6,
    sync_id: 'SYNC-20250114-001',
    system_name: 'MES 시스템',
    sync_type: 'INCREMENTAL',
    start_time: '2025-01-14 23:50:00',
    end_time: '2025-01-14 23:50:25',
    status: 'SUCCESS',
    records_processed: 620,
    records_success: 620,
    records_failed: 0,
    duration_seconds: 25,
    data_types: ['불량정보']
  },
  {
    id: 7,
    sync_id: 'SYNC-20250114-002',
    system_name: '창고 관리 시스템',
    sync_type: 'INCREMENTAL',
    start_time: '2025-01-14 18:00:00',
    end_time: '2025-01-14 18:01:00',
    status: 'SUCCESS',
    records_processed: 180,
    records_success: 178,
    records_failed: 2,
    duration_seconds: 60,
    data_types: ['입출고']
  }
];

const IntegrationHistoryPage: React.FC = () => {
  const [history, setHistory] = useState<SyncHistory[]>(mockSyncHistory);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedSystem, setSelectedSystem] = useState<string>('ALL');
  const [dateRange, setDateRange] = useState<string>('TODAY');

  const getStatusBadge = (status: string) => {
    const styles = {
      SUCCESS: 'bg-green-100 text-green-800 border-green-300',
      FAILED: 'bg-red-100 text-red-800 border-red-300',
      IN_PROGRESS: 'bg-blue-100 text-blue-800 border-blue-300',
      PARTIAL: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    };
    const labels = {
      SUCCESS: '성공',
      FAILED: '실패',
      IN_PROGRESS: '진행중',
      PARTIAL: '부분 성공',
    };
    const icons = {
      SUCCESS: CheckCircle,
      FAILED: XCircle,
      IN_PROGRESS: Clock,
      PARTIAL: AlertTriangle,
    };
    const Icon = icons[status as keyof typeof icons];
    return (
      <Badge className={styles[status as keyof typeof styles]}>
        <Icon className="w-3 h-3 mr-1" />
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  const getSyncTypeBadge = (type: string) => {
    const styles = {
      FULL: 'bg-purple-100 text-purple-800',
      INCREMENTAL: 'bg-blue-100 text-blue-800',
      MANUAL: 'bg-orange-100 text-orange-800',
    };
    const labels = {
      FULL: '전체',
      INCREMENTAL: '증분',
      MANUAL: '수동',
    };
    return (
      <Badge className={styles[type as keyof typeof styles]}>
        {labels[type as keyof typeof labels]}
      </Badge>
    );
  };

  const filteredHistory = history.filter(record => {
    const matchStatus = selectedStatus === 'ALL' || record.status === selectedStatus;
    const matchSystem = selectedSystem === 'ALL' || record.system_name === selectedSystem;
    return matchStatus && matchSystem;
  });

  const stats = {
    total: history.length,
    success: history.filter(h => h.status === 'SUCCESS').length,
    failed: history.filter(h => h.status === 'FAILED').length,
    partial: history.filter(h => h.status === 'PARTIAL').length,
    totalRecords: history.reduce((sum, h) => sum + h.records_processed, 0),
    successRate: history.length > 0
      ? ((history.reduce((sum, h) => sum + h.records_success, 0) / history.reduce((sum, h) => sum + h.records_processed, 0)) * 100).toFixed(1)
      : '0.0'
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}초`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}분 ${seconds % 60}초`;
    return `${Math.floor(seconds / 3600)}시간 ${Math.floor((seconds % 3600) / 60)}분`;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <History className="w-8 h-8 text-orange-600" />
            연계 이력 관리
          </h1>
          <p className="text-gray-600 mt-2">
            ERP/MES 시스템 동기화 이력 조회 및 모니터링
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            내보내기
          </Button>
          <Button className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700">
            <RefreshCw className="w-4 h-4" />
            새로고침
          </Button>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">전체 동기화</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
              </div>
              <Database className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">성공</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.success}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-red-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">실패</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{stats.failed}</p>
              </div>
              <XCircle className="w-12 h-12 text-red-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-yellow-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">부분 성공</p>
                <p className="text-3xl font-bold text-yellow-600 mt-1">{stats.partial}</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-yellow-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">성공률</p>
                <p className="text-3xl font-bold text-purple-600 mt-1">{stats.successRate}%</p>
              </div>
              <TrendingUp className="w-12 h-12 text-purple-500 opacity-20" />
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
                  placeholder="동기화 ID, 시스템명..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
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
                <option value="SUCCESS">성공</option>
                <option value="FAILED">실패</option>
                <option value="PARTIAL">부분 성공</option>
                <option value="IN_PROGRESS">진행중</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">시스템</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                value={selectedSystem}
                onChange={(e) => setSelectedSystem(e.target.value)}
              >
                <option value="ALL">전체</option>
                <option value="SAP ERP">SAP ERP</option>
                <option value="MES 시스템">MES 시스템</option>
                <option value="PLM 시스템">PLM 시스템</option>
                <option value="창고 관리 시스템">창고 관리 시스템</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">기간</label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
              >
                <option value="TODAY">오늘</option>
                <option value="WEEK">이번 주</option>
                <option value="MONTH">이번 달</option>
                <option value="CUSTOM">사용자 지정</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sync History Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            동기화 이력 ({filteredHistory.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left p-4 font-semibold text-gray-700">동기화 ID</th>
                  <th className="text-left p-4 font-semibold text-gray-700">시스템</th>
                  <th className="text-left p-4 font-semibold text-gray-700">유형</th>
                  <th className="text-left p-4 font-semibold text-gray-700">시작 시간</th>
                  <th className="text-left p-4 font-semibold text-gray-700">종료 시간</th>
                  <th className="text-left p-4 font-semibold text-gray-700">소요 시간</th>
                  <th className="text-left p-4 font-semibold text-gray-700">처리 건수</th>
                  <th className="text-left p-4 font-semibold text-gray-700">상태</th>
                  <th className="text-left p-4 font-semibold text-gray-700">데이터</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistory.map((record) => (
                  <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="p-4">
                      <div className="font-mono text-sm font-semibold text-purple-600">{record.sync_id}</div>
                    </td>
                    <td className="p-4">
                      <div className="font-medium">{record.system_name}</div>
                    </td>
                    <td className="p-4">{getSyncTypeBadge(record.sync_type)}</td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <span className="text-sm">{record.start_time}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <span className="text-sm">{record.end_time}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className="text-sm font-medium">{formatDuration(record.duration_seconds)}</span>
                    </td>
                    <td className="p-4">
                      <div className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">처리</span>
                          <span className="font-medium">{record.records_processed.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-green-600">성공</span>
                          <span className="font-medium text-green-600">{record.records_success.toLocaleString()}</span>
                        </div>
                        {record.records_failed > 0 && (
                          <div className="flex justify-between text-sm">
                            <span className="text-red-600">실패</span>
                            <span className="font-medium text-red-600">{record.records_failed.toLocaleString()}</span>
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="p-4">{getStatusBadge(record.status)}</td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1">
                        {record.data_types.map((type, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {type}
                          </Badge>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Error Details for Failed Syncs */}
      {filteredHistory.some(r => r.status === 'FAILED' || r.status === 'PARTIAL') && (
        <Card className="border-l-4 border-red-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              에러 상세
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {filteredHistory
                .filter(r => r.error_message)
                .map((record) => (
                  <div key={record.id} className="p-4 bg-red-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-red-900">{record.sync_id}</span>
                      <span className="text-sm text-red-700">{record.system_name}</span>
                    </div>
                    <p className="text-sm text-red-800">{record.error_message}</p>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default IntegrationHistoryPage;
export { IntegrationHistoryPage };

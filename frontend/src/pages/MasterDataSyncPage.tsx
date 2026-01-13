import React, { useState, useEffect } from 'react';
import { RefreshCw, Clock, CheckCircle2, XCircle, AlertCircle, Database } from 'lucide-react';
import {
  getQualitySyncLogs,
  getSyncStatistics,
  QualitySyncLog,
} from '../services/spcMasterDataApi';

interface SyncStats {
  total_syncs: number;
  by_type: Record<string, number>;
  by_source: Record<string, number>;
  by_status: Record<string, number>;
  total_records: number;
  total_success: number;
  total_failed: number;
}

const MasterDataSyncPage: React.FC = () => {
  const [logs, setLogs] = useState<QualitySyncLog[]>([]);
  const [stats, setStats] = useState<SyncStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('');
  const [filterSource, setFilterSource] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    fetchData();
  }, [filterType, filterSource, filterStatus]);

  const fetchData = async () => {
    try {
      const [logsData, statsData] = await Promise.all([
        getQualitySyncLogs({
          sync_type: filterType || undefined,
          sync_source: filterSource || undefined,
          sync_status: filterStatus || undefined,
        }),
        getSyncStatistics(),
      ]);
      setLogs(logsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch sync data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'FAILED':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'PARTIAL':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return 'bg-green-100 text-green-800';
      case 'FAILED':
        return 'bg-red-100 text-red-800';
      case 'PARTIAL':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'ERP':
        return 'bg-blue-100 text-blue-800';
      case 'MES':
        return 'bg-purple-100 text-purple-800';
      case 'LEGACY':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">데이터 동기화</h1>
        <p className="text-gray-600 mt-1">ERP/MES 시스템과의 데이터 동기화 이력 및 통계</p>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">총 동기화 횟수</p>
                <p className="text-3xl font-bold">{stats.total_syncs}</p>
              </div>
              <RefreshCw className="w-12 h-12 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">총 레코드 수</p>
                <p className="text-3xl font-bold">{stats.total_records}</p>
              </div>
              <Database className="w-12 h-12 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">성공 건수</p>
                <p className="text-3xl font-bold text-green-600">{stats.total_success}</p>
              </div>
              <CheckCircle2 className="w-12 h-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">실패 건수</p>
                <p className="text-3xl font-bold text-red-600">{stats.total_failed}</p>
              </div>
              <XCircle className="w-12 h-12 text-red-500" />
            </div>
          </div>
        </div>
      )}

      {/* Statistics Details */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">유형별 현황</h3>
            <div className="space-y-2">
              {Object.entries(stats.by_type).map(([type, count]) => (
                <div key={type} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{type}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">데이터원천별 현황</h3>
            <div className="space-y-2">
              {Object.entries(stats.by_source).map(([source, count]) => (
                <div key={source} className="flex justify-between items-center">
                  <span className={`px-2 py-1 text-xs rounded ${getSourceColor(source)}`}>
                    {source}
                  </span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">상태별 현황</h3>
            <div className="space-y-2">
              {Object.entries(stats.by_status).map(([status, count]) => (
                <div key={status} className="flex justify-between items-center">
                  <span className="flex items-center gap-2">
                    {getStatusIcon(status)}
                    <span className="text-sm">{status}</span>
                  </span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-4">
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="">전체 유형</option>
            <option value="ITEM">품목마스터</option>
            <option value="PROCESS">공정마스터</option>
            <option value="CHARACTERISTIC">특성마스터</option>
            <option value="INSTRUMENT">측정기구</option>
            <option value="STANDARD">검사기준</option>
          </select>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
          >
            <option value="">전체 원천</option>
            <option value="ERP">ERP</option>
            <option value="MES">MES</option>
            <option value="LEGACY">레거시</option>
            <option value="MANUAL">수동입력</option>
          </select>
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">전체 상태</option>
            <option value="SUCCESS">성공</option>
            <option value="FAILED">실패</option>
            <option value="PARTIAL">부분성공</option>
          </select>
        </div>
      </div>

      {/* Sync Logs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">동기화 이력</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">일시</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">유형</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">원천</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">상태</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">총건수</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">성공</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">실패</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">소요시간</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.sync_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div>{new Date(log.sync_ts).toLocaleDateString('ko-KR')}</div>
                    <div className="text-gray-500 text-xs">
                      {new Date(log.sync_ts).toLocaleTimeString('ko-KR')}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                      {log.sync_type_display || log.sync_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded ${getSourceColor(log.sync_source)}`}>
                      {log.sync_source_display || log.sync_source}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(log.sync_status)}
                      <span className="text-sm">{log.sync_status_display || log.sync_status}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {log.records_total}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-green-600">
                    {log.records_success}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-red-600">
                    {log.records_failed}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    {log.duration_seconds ? `${log.duration_seconds.toFixed(2)}초` : '-'}
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={9} className="px-6 py-12 text-center text-gray-500">
                    동기화 이력이 없습니다
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Error Details */}
      {logs.some(log => log.error_message) && (
        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="font-semibold text-red-800 mb-2">실패 내역</h3>
          <div className="space-y-2">
            {logs.filter(log => log.error_message).slice(0, 5).map((log) => (
              <div key={log.sync_id} className="text-sm text-red-700">
                <div className="font-medium">
                  {new Date(log.sync_ts).toLocaleString('ko-KR')} - {log.sync_type}
                </div>
                <div className="mt-1 text-xs">{log.error_message}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MasterDataSyncPage;

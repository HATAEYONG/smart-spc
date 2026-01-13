import React, { useState, useEffect } from 'react';
import {
  Database, Download, RefreshCw, AlertCircle, CheckCircle2,
  Package, Settings, Wrench, FileText, BarChart3
} from 'lucide-react';

const MasterDataDashboardPage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [syncStats, setSyncStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // In a real implementation, you would create a dashboard stats endpoint
      // For now, we'll show the structure
      setStats({
        total_items: 0,
        total_processes: 0,
        total_characteristics: 0,
        total_instruments: 0,
        calibration_due: 0,
        gage_rr_due: 0,
      });
      setSyncStats({
        total_syncs: 0,
        by_type: {},
        by_source: {},
        by_status: {},
        total_records: 0,
        total_success: 0,
        total_failed: 0,
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const menuItems = [
    {
      title: '품목 마스터',
      description: '품질 관리 대상 품목 정보',
      icon: Package,
      color: 'bg-blue-500',
      path: '/master-data/items',
      count: stats?.total_items || 0,
    },
    {
      title: '공정 마스터',
      description: '품질 관리 공정 정보',
      icon: Settings,
      color: 'bg-green-500',
      path: '/master-data/processes',
      count: stats?.total_processes || 0,
    },
    {
      title: '특성 마스터',
      description: '품질 측정 특성 정보',
      icon: BarChart3,
      color: 'bg-purple-500',
      path: '/master-data/characteristics',
      count: stats?.total_characteristics || 0,
    },
    {
      title: '측정기구 마스터',
      description: '측정 기구 및 장비 정보',
      icon: Wrench,
      color: 'bg-orange-500',
      path: '/master-data/instruments',
      count: stats?.total_instruments || 0,
      alert: stats?.calibration_due > 0,
      alertCount: stats?.calibration_due,
    },
    {
      title: '측정 시스템',
      description: '측정 시스템 구성 정보',
      icon: Database,
      color: 'bg-teal-500',
      path: '/master-data/systems',
    },
    {
      title: '검사 기준',
      description: '검사 기준서 정보',
      icon: FileText,
      color: 'bg-indigo-500',
      path: '/master-data/standards',
    },
    {
      title: '데이터 동기화',
      description: 'ERP/MES 데이터 연계',
      icon: RefreshCw,
      color: 'bg-pink-500',
      path: '/master-data/sync',
    },
    {
      title: '데이터 Import',
      description: '레거시 데이터 Import',
      icon: Download,
      color: 'bg-red-500',
      path: '/master-data/import',
    },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">품질 기본정보 관리</h1>
        <p className="text-gray-600 mt-2">SPC 품질 관리를 위한 마스터 데이터 및 ERP/MES 연계</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">전체 품목</p>
              <p className="text-3xl font-bold">{stats?.total_items || 0}</p>
            </div>
            <Package className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">전체 공정</p>
              <p className="text-3xl font-bold">{stats?.total_processes || 0}</p>
            </div>
            <Settings className="w-12 h-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">측정기구</p>
              <p className="text-3xl font-bold">{stats?.total_instruments || 0}</p>
            </div>
            <Wrench className="w-12 h-12 text-orange-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">보정 만료</p>
              <p className="text-3xl font-bold text-red-600">{stats?.calibration_due || 0}</p>
            </div>
            <AlertCircle className="w-12 h-12 text-red-500" />
          </div>
        </div>
      </div>

      {/* Menu Grid */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-6">마스터 데이터 관리</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {menuItems.slice(0, 6).map((item) => {
            const Icon = item.icon;
            return (
              <a
                key={item.path}
                href={item.path}
                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className={`w-12 h-12 rounded-lg ${item.color} flex items-center justify-center mb-4`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
                    <p className="text-sm text-gray-600 mb-3">{item.description}</p>
                    {item.count !== undefined && (
                      <p className="text-sm font-medium text-blue-600">
                        {item.count} 건 등록됨
                      </p>
                    )}
                    {item.alert && (
                      <div className="mt-2 flex items-center text-red-600">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        <span className="text-sm font-medium">
                          보정 만료: {item.alertCount}건
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </a>
            );
          })}
        </div>
      </div>

      {/* Data Integration Section */}
      <div>
        <h2 className="text-2xl font-bold mb-6">데이터 연계</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {menuItems.slice(6).map((item) => {
            const Icon = item.icon;
            return (
              <a
                key={item.path}
                href={item.path}
                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-center">
                  <div className={`w-16 h-16 rounded-lg ${item.color} flex items-center justify-center mr-4`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-1">{item.title}</h3>
                    <p className="text-sm text-gray-600">{item.description}</p>
                  </div>
                </div>
              </a>
            );
          })}
        </div>
      </div>

      {/* Recent Sync Logs */}
      {syncStats && (
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">동기화 통계</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-500">총 동기화 횟수</p>
              <p className="text-2xl font-bold">{syncStats.total_syncs}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">총 레코드 수</p>
              <p className="text-2xl font-bold">{syncStats.total_records}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">성공 건수</p>
              <p className="text-2xl font-bold text-green-600">{syncStats.total_success}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">실패 건수</p>
              <p className="text-2xl font-bold text-red-600">{syncStats.total_failed}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MasterDataDashboardPage;

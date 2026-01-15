/**
 * ERP/MES 연계 관리 페이지
 * ERP, MES 시스템과의 연계 설정 및 모니터링
 */
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Database,
  Link as LinkIcon,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Settings,
  Plus,
  Edit,
  Trash2,
  Activity,
  Clock,
  Server,
  TestTube
} from 'lucide-react';

interface ERPIntegration {
  id: number;
  system_name: string;
  system_type: 'ERP' | 'MES' | 'PLM' | 'WMS' | 'QMS';
  api_endpoint: string;
  status: 'CONNECTED' | 'DISCONNECTED' | 'ERROR' | 'TESTING';
  last_sync: string;
  sync_frequency: number; // minutes
  data_types: string[];
  auth_method: 'API_KEY' | 'OAUTH' | 'BASIC_AUTH';
  description: string;
}

const mockIntegrations: ERPIntegration[] = [
  {
    id: 1,
    system_name: 'SAP ERP',
    system_type: 'ERP',
    api_endpoint: 'https://sap.company.com/api/v1',
    status: 'CONNECTED',
    last_sync: '2025-01-15 14:30:00',
    sync_frequency: 30,
    data_types: ['생산주문', '자재정보', 'BOM', '작업지시'],
    auth_method: 'OAUTH',
    description: '전사 ERP 시스템'
  },
  {
    id: 2,
    system_name: 'MES 시스템',
    system_type: 'MES',
    api_endpoint: 'https://mes.company.com/api',
    status: 'CONNECTED',
    last_sync: '2025-01-15 14:32:00',
    sync_frequency: 10,
    data_types: ['생산실적', '설비상태', '불량정보'],
    auth_method: 'API_KEY',
    description: '공정 실행 시스템'
  },
  {
    id: 3,
    system_name: 'PLM 시스템',
    system_type: 'PLM',
    api_endpoint: 'https://plm.company.com/api/v2',
    status: 'DISCONNECTED',
    last_sync: '2025-01-15 10:00:00',
    sync_frequency: 60,
    data_types: ['제품설계', '도면', 'ECO'],
    auth_method: 'BASIC_AUTH',
    description: '제품 수명 주기 관리'
  },
  {
    id: 4,
    system_name: '창고 관리 시스템',
    system_type: 'WMS',
    api_endpoint: 'https://wms.company.com/api',
    status: 'ERROR',
    last_sync: '2025-01-15 12:15:00',
    sync_frequency: 15,
    data_types: ['재고정보', '입출고', '창고위치'],
    auth_method: 'API_KEY',
    description: '창고 재고 관리'
  }
];

const ERPIntegrationPage: React.FC = () => {
  const [integrations, setIntegrations] = useState<ERPIntegration[]>(mockIntegrations);
  const [isTesting, setIsTesting] = useState(false);
  const [selectedSystem, setSelectedSystem] = useState<ERPIntegration | null>(null);
  const [showModal, setShowModal] = useState(false);

  const getStatusBadge = (status: string) => {
    const styles = {
      CONNECTED: 'bg-green-100 text-green-800 border-green-300',
      DISCONNECTED: 'bg-gray-100 text-gray-800 border-gray-300',
      ERROR: 'bg-red-100 text-red-800 border-red-300',
      TESTING: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    };
    const labels = {
      CONNECTED: '연결됨',
      DISCONNECTED: '연결 안됨',
      ERROR: '에러',
      TESTING: '테스트중',
    };
    const icons = {
      CONNECTED: CheckCircle,
      DISCONNECTED: XCircle,
      ERROR: AlertTriangle,
      TESTING: RefreshCw,
    };
    const Icon = icons[status as keyof typeof icons];
    return (
      <Badge className={styles[status as keyof typeof styles]}>
        <Icon className="w-3 h-3 mr-1" />
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  const getTypeBadge = (type: string) => {
    const styles = {
      ERP: 'bg-blue-100 text-blue-800',
      MES: 'bg-purple-100 text-purple-800',
      PLM: 'bg-green-100 text-green-800',
      WMS: 'bg-orange-100 text-orange-800',
      QMS: 'bg-pink-100 text-pink-800',
    };
    return (
      <Badge className={styles[type as keyof typeof styles]}>
        {type}
      </Badge>
    );
  };

  const handleTestConnection = async (id: number) => {
    setIsTesting(true);
    // 연결 테스트 시뮬레이션
    setTimeout(() => {
      setIntegrations(prev => prev.map(integration => {
        if (integration.id === id) {
          return { ...integration, status: 'CONNECTED' as const };
        }
        return integration;
      }));
      setIsTesting(false);
      alert('연결 테스트 성공!');
    }, 2000);
  };

  const handleSyncNow = async (id: number) => {
    setIntegrations(prev => prev.map(integration => {
      if (integration.id === id) {
        return { ...integration, status: 'TESTING' as const };
      }
      return integration;
    }));

    // 동기화 시뮬레이션
    setTimeout(() => {
      const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
      setIntegrations(prev => prev.map(integration => {
        if (integration.id === id) {
          return { ...integration, status: 'CONNECTED' as const, last_sync: now };
        }
        return integration;
      }));
      alert('동기화 완료!');
    }, 3000);
  };

  const stats = {
    total: integrations.length,
    connected: integrations.filter(i => i.status === 'CONNECTED').length,
    error: integrations.filter(i => i.status === 'ERROR').length,
    disconnected: integrations.filter(i => i.status === 'DISCONNECTED').length
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Database className="w-8 h-8 text-blue-600" />
            ERP/MES 연계 관리
          </h1>
          <p className="text-gray-600 mt-2">
            외부 시스템과의 연계 설정 및 데이터 동기화 관리
          </p>
        </div>
        <Button className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700">
          <Plus className="w-4 h-4" />
          새 연계 추가
        </Button>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-l-4 border-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">전체 연계</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
              </div>
              <Server className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">연결됨</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{stats.connected}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-red-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">에러</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{stats.error}</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-red-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-gray-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">연결 안됨</p>
                <p className="text-3xl font-bold text-gray-600 mt-1">{stats.disconnected}</p>
              </div>
              <XCircle className="w-12 h-12 text-gray-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Integration List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {integrations.map((integration) => (
          <Card key={integration.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Server className="w-6 h-6 text-purple-600" />
                  <div>
                    <CardTitle className="text-lg">{integration.system_name}</CardTitle>
                    <p className="text-sm text-gray-500">{integration.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getTypeBadge(integration.system_type)}
                  {getStatusBadge(integration.status)}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Connection Info */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">API Endpoint</p>
                  <p className="font-mono text-xs bg-gray-100 p-2 rounded mt-1">{integration.api_endpoint}</p>
                </div>
                <div>
                  <p className="text-gray-500">인증 방식</p>
                  <p className="font-semibold mt-1">{integration.auth_method}</p>
                </div>
                <div>
                  <p className="text-gray-500">동기화 주기</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <span className="font-semibold">{integration.sync_frequency}분</span>
                  </div>
                </div>
                <div>
                  <p className="text-gray-500">마지막 동기화</p>
                  <p className="font-semibold mt-1">{integration.last_sync}</p>
                </div>
              </div>

              {/* Data Types */}
              <div>
                <p className="text-sm text-gray-500 mb-2">동기화 데이터</p>
                <div className="flex flex-wrap gap-2">
                  {integration.data_types.map((type, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {type}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleTestConnection(integration.id)}
                  disabled={isTesting}
                  className="flex items-center gap-2"
                >
                  <TestTube className="w-4 h-4" />
                  연결 테스트
                </Button>
                <Button
                  size="sm"
                  onClick={() => handleSyncNow(integration.id)}
                  disabled={integration.status === 'TESTING'}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
                >
                  <RefreshCw className={`w-4 h-4 ${integration.status === 'TESTING' ? 'animate-spin' : ''}`} />
                  지금 동기화
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <Settings className="w-4 h-4" />
                  설정
                </Button>
              </div>

              {/* Status Alert */}
              {integration.status === 'ERROR' && (
                <div className="flex items-start gap-2 p-3 bg-red-50 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-red-900">
                    <p className="font-semibold">연결 실패</p>
                    <p className="text-red-700">API endpoint 또는 인증 정보를 확인하세요.</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Connection Guide */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <LinkIcon className="w-5 h-5" />
            연계 가이드
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <h4 className="font-semibold flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                1. API 설정
              </h4>
              <ul className="text-sm text-gray-600 space-y-1 ml-7">
                <li>• API Endpoint URL 입력</li>
                <li>• 인증 방식 선택 (API Key, OAuth, Basic Auth)</li>
                <li>• 인증 정보 등록</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-600" />
                2. 데이터 매핑
              </h4>
              <ul className="text-sm text-gray-600 space-y-1 ml-7">
                <li>• 동기화할 데이터 유형 선택</li>
                <li>• 필드 매핑 설정</li>
                <li>• 데이터 변환 규칙 정의</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold flex items-center gap-2">
                <RefreshCw className="w-5 h-5 text-purple-600" />
                3. 동기화 실행
              </h4>
              <ul className="text-sm text-gray-600 space-y-1 ml-7">
                <li>• 동기화 주기 설정</li>
                <li>• 연결 테스트 실행</li>
                <li>• 정기 동기화 스케줄링</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ERPIntegrationPage;
export { ERPIntegrationPage };

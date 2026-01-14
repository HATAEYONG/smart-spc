import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import {
  Activity,
  AlertTriangle,
  Wrench,
  TrendingUp,
  TrendingDown,
  Settings,
  Calendar,
  Thermometer,
  Zap,
  BarChart3,
  LineChart as LineChartIcon,
  Clock,
  X,
  Info,
  GitCompare,
  Gauge,
  History,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { pmService, Equipment, SensorData, FailurePrediction, PMDashboardData } from '../services/pmService';

export const PredictiveMaintenancePage: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<PMDashboardData | null>(null);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [sensorData, setSensorData] = useState<SensorData[]>([]);
  const [upcomingMaintenance, setUpcomingMaintenance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 고도화 기능 상태
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedEquipmentForCompare, setSelectedEquipmentForCompare] = useState<number[]>([]);
  const [showOEE, setShowOEE] = useState(false);
  const [maintenanceHistory, setMaintenanceHistory] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'compare' | 'oee' | 'timeline'>('dashboard');

  useEffect(() => {
    loadDashboard();
    loadEquipment();
    loadUpcomingMaintenance();
  }, []);

  const loadDashboard = async () => {
    const data = await pmService.getDashboard();
    setDashboardData(data);
  };

  const loadEquipment = async () => {
    try {
      setLoading(true);
      const equipmentList = await pmService.getEquipment();
      setEquipment(equipmentList);
      if (equipmentList.length > 0) {
        setSelectedEquipment(equipmentList[0]);
        loadSensorData(equipmentList[0].id);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadUpcomingMaintenance = async () => {
    const data = await pmService.getUpcomingMaintenance();
    setUpcomingMaintenance(data);
  };

  const loadSensorData = async (equipmentId: number) => {
    try {
      const data = await pmService.getSensorData(equipmentId, 24);
      setSensorData(data);
    } catch (error) {
      console.error('Failed to load sensor data:', error);
    }
  };

  const handleEquipmentChange = (equipment: Equipment) => {
    setSelectedEquipment(equipment);
    loadSensorData(equipment.id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OPERATIONAL': return 'bg-green-500';
      case 'MAINTENANCE': return 'bg-yellow-500';
      case 'BREAKDOWN': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'LOW': return 'bg-green-100 text-green-800';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800';
      case 'HIGH': return 'bg-orange-100 text-orange-800';
      case 'CRITICAL': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // 설비 상세 모달 열기
  const openDetailModal = (eq: Equipment) => {
    setSelectedEquipment(eq);
    setDetailModalOpen(true);
  };

  // 비교 모드 토글
  const toggleCompareMode = (eqId: number) => {
    if (selectedEquipmentForCompare.includes(eqId)) {
      setSelectedEquipmentForCompare(selectedEquipmentForCompare.filter(id => id !== eqId));
    } else {
      if (selectedEquipmentForCompare.length < 4) {
        setSelectedEquipmentForCompare([...selectedEquipmentForCompare, eqId]);
      }
    }
  };

  // OEE 데이터 생성 (시뮬레이션)
  const generateOEEData = (eq: Equipment) => {
    const availability = 85 + Math.random() * 10;
    const performance = 90 + Math.random() * 8;
    const quality = 95 + Math.random() * 4;
    const oee = (availability * performance * quality) / 10000;

    return {
      equipment: eq.code,
      availability: availability.toFixed(1),
      performance: performance.toFixed(1),
      quality: quality.toFixed(1),
      oee: oee.toFixed(1),
    };
  };

  // 유지보수 이력 생성 (시뮬레이션)
  const generateMaintenanceHistory = () => {
    const history = [];
    const now = new Date();
    for (let i = 0; i < 10; i++) {
      const date = new Date(now);
      date.setDate(date.getDate() - i * 7);

      const types = ['예방', '예측', '고장', '개선'];
      const type = types[Math.floor(Math.random() * types.length)];
      const statuses = ['완료', '진행중', '예정'];
      const status = statuses[Math.floor(Math.random() * statuses.length)];

      history.push({
        date: date.toISOString().split('T')[0],
        type,
        status,
        description: `${type} 보전 - 정기 점검 및 부품 교체`,
        technician: ['홍길동', '김철수', '박영수', '이민지'][Math.floor(Math.random() * 4)],
        duration: Math.floor(Math.random() * 120) + 30,
      });
    }
    return history;
  };

  // 센서 데이터를 차트 포맷으로 변환
  const prepareChartData = (data: SensorData[]) => {
    const grouped = data.reduce((acc: any, curr) => {
      const timestamp = new Date(curr.timestamp).getTime();
      if (!acc[timestamp]) {
        acc[timestamp] = { timestamp };
      }
      if (curr.sensor_type === 'VIBRATION') {
        acc[timestamp].vibration = curr.value;
      } else if (curr.sensor_type === 'TEMPERATURE') {
        acc[timestamp].temperature = curr.value;
      } else if (curr.sensor_type === 'PRESSURE') {
        acc[timestamp].pressure = curr.value;
      }
      return acc;
    }, {});

    return Object.values(grouped).sort((a: any, b: any) => a.timestamp - b.timestamp);
  };

  // 건전도 트렌드 데이터 생성 (시뮬레이션)
  const generateHealthTrendData = (currentScore: number) => {
    const data = [];
    const now = new Date();
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const variation = (Math.random() - 0.5) * 10;
      const score = Math.max(0, Math.min(100, currentScore + variation - (i * 0.2)));
      data.push({
        date: date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
        healthScore: score,
      });
    }
    return data;
  };

  // 고장 확률 트렌드 데이터 생성 (시뮬레이션)
  const generateFailureTrendData = (currentProb: number) => {
    const data = [];
    const now = new Date();
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const variation = (Math.random() - 0.5) * 5;
      const prob = Math.max(0, Math.min(100, currentProb + variation + (i * 0.1)));
      data.push({
        date: date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
        failureProb: prob,
      });
    }
    return data;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex flex-col space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">설비 예지 보전</h1>
            <p className="text-sm text-gray-500 mt-1">
              AI 기반 설비 고장 예측 및 예방 보전 관리
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant={compareMode ? "default" : "outline"}
              onClick={() => setCompareMode(!compareMode)}
            >
              <GitCompare className="w-4 h-4 mr-2" />
              {compareMode ? '비교 완료' : '설비 비교'}
            </Button>
            <Button>
              <Settings className="w-4 h-4 mr-2" />
              설정
            </Button>
          </div>
        </div>

        {/* 탭 네비게이션 */}
        <div className="flex gap-2 border-b">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'dashboard'
                ? 'border-b-2 border-purple-600 text-purple-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <BarChart3 className="w-4 h-4 inline mr-2" />
            대시보드
          </button>
          <button
            onClick={() => {
              setActiveTab('compare');
              setCompareMode(true);
            }}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'compare'
                ? 'border-b-2 border-purple-600 text-purple-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <GitCompare className="w-4 h-4 inline mr-2" />
            설비 비교
          </button>
          <button
            onClick={() => setActiveTab('oee')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'oee'
                ? 'border-b-2 border-purple-600 text-purple-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Gauge className="w-4 h-4 inline mr-2" />
            OEE 분석
          </button>
          <button
            onClick={() => setActiveTab('timeline')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'timeline'
                ? 'border-b-2 border-purple-600 text-purple-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <History className="w-4 h-4 inline mr-2" />
            유지보수 이력
          </button>
        </div>
      </div>

      {/* 대시보드 카드 */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">전체 설비</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">
                    {dashboardData?.total_equipment || 0}
                  </p>
                </div>
                <div className="bg-blue-100 p-3 rounded-full">
                  <Settings className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">가동 중</p>
                  <p className="text-3xl font-bold text-green-600 mt-1">
                    {dashboardData?.operational || 0}
                  </p>
                </div>
                <div className="bg-green-100 p-3 rounded-full">
                  <Activity className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">점검 중</p>
                  <p className="text-3xl font-bold text-yellow-600 mt-1">
                    {dashboardData?.maintenance || 0}
                  </p>
                </div>
                <div className="bg-yellow-100 p-3 rounded-full">
                  <Wrench className="w-6 h-6 text-yellow-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">고장 위험</p>
                  <p className="text-3xl font-bold text-red-600 mt-1">
                    {dashboardData?.high_risk || 0}
                  </p>
                </div>
                <div className="bg-red-100 p-3 rounded-full">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 설비 건전도 히트맵 */}
      {equipment && equipment.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-purple-600" />
              설비 건전도 현황
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {equipment.map((eq) => (
                <div
                  key={eq.id}
                  className={`relative p-4 rounded-lg border-2 transition-all ${
                    eq.health_score >= 80
                      ? 'border-green-200 bg-green-50'
                      : eq.health_score >= 60
                      ? 'border-yellow-200 bg-yellow-50'
                      : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-gray-900">{eq.code}</h4>
                      <p className="text-sm text-gray-600">{eq.name}</p>
                    </div>
                    <Badge
                      variant="outline"
                      className={
                        eq.health_score >= 80
                          ? 'bg-green-100 text-green-800'
                          : eq.health_score >= 60
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }
                    >
                      {eq.status_display}
                    </Badge>
                  </div>

                  {/* 건전도 바 */}
                  <div className="mb-2">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-gray-600">건전도</span>
                      <span className={`font-semibold ${
                        eq.health_score >= 80 ? 'text-green-600' : eq.health_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {eq.health_score.toFixed(1)}점
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          eq.health_score >= 80 ? 'bg-green-500' : eq.health_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${eq.health_score}%` }}
                      />
                    </div>
                  </div>

                  {/* 고장 확률 바 */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-gray-600">고장 확률</span>
                      <span className="font-semibold text-orange-600">
                        {eq.failure_probability.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 rounded-full transition-all bg-orange-500"
                        style={{ width: `${eq.failure_probability}%` }}
                      />
                    </div>
                  </div>

                  {/* 상태 아이콘 */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>가동률: {eq.availability_current.toFixed(1)}%</span>
                    <span>{eq.location}</span>
                  </div>

                  {/* 액션 버튼 */}
                  <div className="flex gap-2 mt-3 pt-3 border-t">
                    {compareMode && (
                      <button
                        onClick={() => toggleCompareMode(eq.id)}
                        className={`flex-1 px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                          selectedEquipmentForCompare.includes(eq.id)
                            ? 'bg-purple-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {selectedEquipmentForCompare.includes(eq.id) ? '선택됨' : '비교 추가'}
                      </button>
                    )}
                    <button
                      onClick={() => openDetailModal(eq)}
                      className="flex-1 px-3 py-1.5 text-xs font-medium rounded bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors"
                    >
                      <Info className="w-3 h-3 inline mr-1" />
                      상세
                    </button>
                  </div>
                  {eq.maintenance_overdue && (
                    <div className="mt-2 text-center">
                      <span className="text-red-600 font-semibold">점검 지연</span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* 범례 */}
            <div className="mt-4 flex items-center justify-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span className="text-gray-600">양호 (80점 이상)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                <span className="text-gray-600">주의 (60-79점)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span className="text-gray-600">위험 (60점 미만)</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 주요 내용 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 설비 목록 */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>설비 목록</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {equipment && equipment.length > 0 ? equipment.map((eq) => (
                  <div
                    key={eq.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedEquipment?.id === eq.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleEquipmentChange(eq)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-gray-900">{eq.code}</h4>
                          <div className={`w-2 h-2 rounded-full ${getStatusColor(eq.status)}`} />
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{eq.name}</p>
                        <p className="text-xs text-gray-500 mt-1">{eq.location}</p>
                      </div>
                    </div>
                    <div className="mt-3 flex items-center justify-between text-sm">
                      <span className={getHealthScoreColor(eq.health_score)}>
                        건전도: {eq.health_score}점
                      </span>
                      <span className="text-orange-600">
                        위험도: {eq.failure_probability}%
                      </span>
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-8 text-gray-500">
                    <Settings className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                    <p>설비 데이터가 없습니다.</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 설비 상세 및 센서 데이터 */}
        <div className="lg:col-span-2 space-y-6">
          {selectedEquipment && (
            <>
              {/* 설비 상세 정보 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Settings className="w-5 h-5 text-blue-600" />
                      {selectedEquipment.code} - {selectedEquipment.name}
                    </div>
                    <Badge variant="outline">{selectedEquipment.category_display}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">상태</p>
                      <p className="font-semibold text-gray-900">{selectedEquipment.status_display}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">위치</p>
                      <p className="font-semibold text-gray-900">{selectedEquipment.location}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">제조사</p>
                      <p className="font-semibold text-gray-900">{selectedEquipment.manufacturer}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">모델</p>
                      <p className="font-semibold text-gray-900">{selectedEquipment.model_number}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">건전도</p>
                      <p className={`font-semibold ${getHealthScoreColor(selectedEquipment.health_score)}`}>
                        {selectedEquipment.health_score}점
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">고장 확률</p>
                      <p className="font-semibold text-orange-600">{selectedEquipment.failure_probability}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">가동률</p>
                      <p className="font-semibold text-gray-900">{selectedEquipment.availability_current}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">다음 점검</p>
                      <p className="font-semibold text-gray-900">
                        {selectedEquipment.next_maintenance_date || '예정됨'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 최신 센서 데이터 */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-green-600" />
                    최신 센서 데이터 (24시간)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {sensorData && ['VIBRATION', 'TEMPERATURE', 'PRESSURE'].map((sensorType) => {
                      const typeData = sensorData.filter((d: any) => d.sensor_type === sensorType);
                      const latest = typeData && typeData[0];
                      if (!latest) return null;

                      const getIcon = (type: string) => {
                        switch (type) {
                          case 'VIBRATION': return <Activity className="w-5 h-5" />;
                          case 'TEMPERATURE': return <Thermometer className="w-5 h-5" />;
                          case 'PRESSURE': return <Zap className="w-5 h-5" />;
                          default: return <Activity className="w-5 h-5" />;
                        }
                      };

                      return (
                        <div key={sensorType} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                              {getIcon(sensorType)}
                              <h4 className="font-semibold text-gray-900">
                                {latest.sensor_type_display}
                              </h4>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-2xl font-bold text-gray-900">
                                {latest.value.toFixed(2)}
                              </span>
                              <span className="text-sm text-gray-500">{latest.unit}</span>
                              <Badge
                                variant={latest.is_normal ? 'outline' : 'destructive'}
                                className={latest.is_normal ? 'bg-green-100 text-green-800' : ''}
                              >
                                {latest.is_normal ? '정상' : '이상'}
                              </Badge>
                            </div>
                          </div>
                          {!latest.is_normal && (
                            <div className="bg-red-50 border border-red-200 rounded p-2 text-sm text-red-800">
                              ⚠️ 이상 감지: 이상 점수 {latest.anomaly_score.toFixed(1)}점
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* 센서 데이터 추이 차트 */}
              {sensorData && sensorData.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <LineChartIcon className="w-5 h-5 text-blue-600" />
                      센서 데이터 추이 (24시간)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={prepareChartData(sensorData)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            dataKey="timestamp"
                            tickFormatter={(value) => new Date(value).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                          />
                          <YAxis />
                          <Tooltip
                            labelFormatter={(value) => new Date(value).toLocaleString('ko-KR')}
                          />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="vibration"
                            stroke="#3b82f6"
                            name="진동 (mm/s)"
                            dot={false}
                            connectNulls={false}
                          />
                          <Line
                            type="monotone"
                            dataKey="temperature"
                            stroke="#ef4444"
                            name="온도 (°C)"
                            dot={false}
                            connectNulls={false}
                          />
                          <Line
                            type="monotone"
                            dataKey="pressure"
                            stroke="#10b981"
                            name="압력 (bar)"
                            dot={false}
                            connectNulls={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* 설비 건전도 추이 */}
              {selectedEquipment && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-purple-600" />
                      건전도 및 고장 확률 추세
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* 건전도 차트 */}
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-4">건전도 점수 (최근 30일)</h4>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={generateHealthTrendData(selectedEquipment.health_score)}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis domain={[0, 100]} />
                              <Tooltip />
                              <Area
                                type="monotone"
                                dataKey="healthScore"
                                stroke="#8b5cf6"
                                fill="#8b5cf6"
                                fillOpacity={0.3}
                              />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* 고장 확률 차트 */}
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-4">고장 확률 (최근 30일)</h4>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={generateFailureTrendData(selectedEquipment.failure_probability)}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="date" />
                              <YAxis domain={[0, 100]} />
                              <Tooltip />
                              <Area
                                type="monotone"
                                dataKey="failureProb"
                                stroke="#f97316"
                                fill="#f97316"
                                fillOpacity={0.3}
                              />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>

                    {/* 현재 지표 요약 */}
                    <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-orange-50 rounded-lg">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <p className="text-sm text-gray-600">현재 건전도</p>
                          <p className={`text-3xl font-bold ${getHealthScoreColor(selectedEquipment.health_score)}`}>
                            {selectedEquipment.health_score.toFixed(1)}점
                          </p>
                          <div className="flex items-center justify-center gap-1 mt-1">
                            {selectedEquipment.health_score > 80 ? (
                              <TrendingUp className="w-4 h-4 text-green-600" />
                            ) : (
                              <TrendingDown className="w-4 h-4 text-red-600" />
                            )}
                            <span className="text-xs text-gray-500">
                              {selectedEquipment.health_score > 80 ? '양호' : '주의 필요'}
                            </span>
                          </div>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-600">고장 확률</p>
                          <p className="text-3xl font-bold text-orange-600">
                            {selectedEquipment.failure_probability.toFixed(1)}%
                          </p>
                          <div className="flex items-center justify-center gap-1 mt-1">
                            <Clock className="w-4 h-4 text-orange-600" />
                            <span className="text-xs text-gray-500">
                              {selectedEquipment.failure_probability < 20 ? '안정' : selectedEquipment.failure_probability < 50 ? '관찰' : '위험'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>

      {/* 긴급 예측 알림 */}
      {dashboardData && dashboardData.critical_predictions && dashboardData.critical_predictions.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-800">
              <AlertTriangle className="w-5 h-5" />
              긴급 고장 예측 알림
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboardData.critical_predictions.map((prediction) => (
                <div
                  key={prediction.id}
                  className="bg-white border border-red-200 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-semibold text-gray-900">{prediction.equipment_code}</h4>
                        <Badge className={getSeverityColor(prediction.severity)}>
                          {prediction.severity_display}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-1">
                        예상 고장일: {new Date(prediction.predicted_failure_date).toLocaleDateString('ko-KR')}
                      </p>
                      <p className="text-sm text-gray-600 mb-2">
                        고장 확률: {prediction.failure_probability}%
                      </p>
                      <p className="text-sm text-gray-700">
                        <strong>원인:</strong> {prediction.potential_causes}
                      </p>
                      <p className="text-sm text-gray-700 mt-1">
                        <strong>권장 조치:</strong> {prediction.recommended_actions}
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      확인
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 다가오는 예방 보전 일정 */}
      {upcomingMaintenance && upcomingMaintenance.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              다가오는 예방 보전 일정 (7일 이내)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {upcomingMaintenance.map((plan) => {
                const daysUntil = Math.ceil((new Date(plan.next_due_date) - new Date()).getTime() / (1000 * 60 * 60 * 24));
                const isUrgent = daysUntil <= 3;

                return (
                  <div
                    key={plan.id}
                    className={`border rounded-lg p-4 transition-all ${
                      isUrgent ? 'border-red-200 bg-red-50' : 'border-blue-200 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold text-gray-900">{plan.equipment_code} - {plan.name}</h4>
                          <Badge className={isUrgent ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'}>
                            {isUrgent ? '긴급' : '예정'}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500">예정일</p>
                            <p className="font-semibold text-gray-900">
                              {new Date(plan.next_due_date).toLocaleDateString('ko-KR')}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500">남은 기간</p>
                            <p className={`font-semibold ${daysUntil <= 3 ? 'text-red-600' : daysUntil <= 7 ? 'text-yellow-600' : 'text-blue-600'}`}>
                              {daysUntil > 0 ? `D-${daysUntil}` : '오늘'}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500">주기</p>
                            <p className="font-semibold text-gray-900">{plan.frequency_display}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">담당자</p>
                            <p className="font-semibold text-gray-900">
                              {plan.assigned_to_name || '미지정'}
                            </p>
                          </div>
                        </div>

                        {plan.tasks && (
                          <div className="mt-3">
                            <p className="text-sm text-gray-500 mb-1">작업 내용</p>
                            <p className="text-sm text-gray-700 line-clamp-2">{plan.tasks}</p>
                          </div>
                        )}
                      </div>

                      <Button variant="outline" size="sm" className="ml-4">
                        <Wrench className="w-4 h-4 mr-1" />
                        완료
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* 일정 요약 */}
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">총 {upcomingMaintenance.length}건의 예정된 점검이 있습니다</span>
                <span className="text-gray-600">
                  긴급: {upcomingMaintenance.filter((p) => {
                    const days = Math.ceil((new Date(p.next_due_date) - new Date()).getTime() / (1000 * 60 * 60 * 24));
                    return days <= 3;
                  }).length}건
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 설비 비교 탭 */}
      {activeTab === 'compare' && selectedEquipmentForCompare.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitCompare className="w-5 h-5 text-purple-600" />
              설비 비교 분석 ({selectedEquipmentForCompare.length}개 선택)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* 비교 테이블 */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3 font-semibold">항목</th>
                      {selectedEquipmentForCompare.map(id => {
                        const eq = equipment.find(e => e.id === id);
                        return eq && <th key={id} className="text-center p-3 font-semibold">{eq.code}</th>;
                      })}
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="p-3 font-medium">건전도 점수</td>
                      {selectedEquipmentForCompare.map(id => {
                        const eq = equipment.find(e => e.id === id);
                        return eq && (
                          <td key={id} className={`text-center p-3 font-semibold ${getHealthScoreColor(eq.health_score)}`}>
                            {eq.health_score.toFixed(1)}점
                          </td>
                        );
                      })}
                    </tr>
                    <tr className="border-b">
                      <td className="p-3 font-medium">고장 확률</td>
                      {selectedEquipmentForCompare.map(id => {
                        const eq = equipment.find(e => e.id === id);
                        return eq && (
                          <td key={id} className="text-center p-3 font-semibold text-orange-600">
                            {eq.failure_probability.toFixed(1)}%
                          </td>
                        );
                      })}
                    </tr>
                    <tr className="border-b">
                      <td className="p-3 font-medium">가동률</td>
                      {selectedEquipmentForCompare.map(id => {
                        const eq = equipment.find(e => e.id === id);
                        return eq && (
                          <td key={id} className="text-center p-3 font-semibold text-blue-600">
                            {eq.availability_current.toFixed(1)}%
                          </td>
                        );
                      })}
                    </tr>
                    <tr className="border-b">
                      <td className="p-3 font-medium">성능률</td>
                      {selectedEquipmentForCompare.map(id => {
                        const eq = equipment.find(e => e.id === id);
                        return eq && (
                          <td key={id} className="text-center p-3 font-semibold text-green-600">
                            {eq.performance_current.toFixed(1)}%
                          </td>
                        );
                      })}
                    </tr>
                    <tr className="border-b">
                      <td className="p-3 font-medium">위치</td>
                      {selectedEquipmentForCompare.map(id => {
                        const eq = equipment.find(e => e.id === id);
                        return eq && <td key={id} className="text-center p-3">{eq.location}</td>;
                      })}
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* 비교 차트 */}
              <div>
                <h4 className="font-semibold mb-4">건전도 트렌드 비교</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={selectedEquipmentForCompare.map(id => {
                    const eq = equipment.find(e => e.id === id);
                    return eq ? generateHealthTrendData(eq.health_score)[0] : {};
                  })}>
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    {selectedEquipmentForCompare.map((id, index) => {
                      const eq = equipment.find(e => e.id === id);
                      if (!eq) return null;
                      const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b'];
                      const data = generateHealthTrendData(eq.health_score);
                      return (
                        <Line
                          key={id}
                          type="monotone"
                          dataKey="healthScore"
                          data={data}
                          stroke={colors[index % colors.length]}
                          name={eq.code}
                        />
                      );
                    })}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* OEE 분석 탭 */}
      {activeTab === 'oee' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Gauge className="w-5 h-5 text-purple-600" />
              종합설비효율 (OEE) 분석
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* OEE 요약 카드 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm text-blue-600 font-medium mb-2">가동율 (Availability)</div>
                  <div className="text-3xl font-bold text-blue-700">
                    {(equipment.reduce((sum, eq) => sum + parseFloat(generateOEEData(eq).availability), 0) / equipment.length).toFixed(1)}%
                  </div>
                  <div className="text-xs text-blue-500 mt-1">목표: 90%</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm text-green-600 font-medium mb-2">성능율 (Performance)</div>
                  <div className="text-3xl font-bold text-green-700">
                    {(equipment.reduce((sum, eq) => sum + parseFloat(generateOEEData(eq).performance), 0) / equipment.length).toFixed(1)}%
                  </div>
                  <div className="text-xs text-green-500 mt-1">목표: 95%</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-sm text-purple-600 font-medium mb-2">양품률 (Quality)</div>
                  <div className="text-3xl font-bold text-purple-700">
                    {(equipment.reduce((sum, eq) => sum + parseFloat(generateOEEData(eq).quality), 0) / equipment.length).toFixed(1)}%
                  </div>
                  <div className="text-xs text-purple-500 mt-1">목표: 99%</div>
                </div>
              </div>

              {/* OEE 상세 테이블 */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-gray-50">
                      <th className="text-left p-3 font-semibold">설비</th>
                      <th className="text-center p-3 font-semibold">가동율</th>
                      <th className="text-center p-3 font-semibold">성능율</th>
                      <th className="text-center p-3 font-semibold">양품률</th>
                      <th className="text-center p-3 font-semibold">OEE</th>
                      <th className="text-center p-3 font-semibold">등급</th>
                    </tr>
                  </thead>
                  <tbody>
                    {equipment.map(eq => {
                      const oeeData = generateOEEData(eq);
                      const oeeValue = parseFloat(oeeData.oee);
                      const grade = oeeValue >= 85 ? 'A' : oeeValue >= 70 ? 'B' : oeeValue >= 50 ? 'C' : 'D';
                      const gradeColor = grade === 'A' ? 'bg-green-100 text-green-800' :
                                        grade === 'B' ? 'bg-blue-100 text-blue-800' :
                                        grade === 'C' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-red-100 text-red-800';
                      return (
                        <tr key={eq.id} className="border-b hover:bg-gray-50">
                          <td className="p-3 font-medium">{eq.code} - {eq.name}</td>
                          <td className="text-center p-3">{oeeData.availability}%</td>
                          <td className="text-center p-3">{oeeData.performance}%</td>
                          <td className="text-center p-3">{oeeData.quality}%</td>
                          <td className="text-center p-3 font-bold">{oeeData.oee}%</td>
                          <td className="text-center p-3">
                            <Badge className={gradeColor}>{grade}급</Badge>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 유지보수 이력 탭 */}
      {activeTab === 'timeline' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="w-5 h-5 text-purple-600" />
              유지보수 이력 타임라인
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {selectedEquipment ? (
                <>
                  <div className="mb-4 p-3 bg-purple-50 rounded-lg">
                    <span className="font-semibold text-purple-900">{selectedEquipment.code} - {selectedEquipment.name}</span>의 유지보수 이력
                  </div>
                  <div className="relative">
                    {/* 타임라인 라인 */}
                    <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

                    {/* 타임라인 아이템 */}
                    {generateMaintenanceHistory().map((item, index) => (
                      <div key={index} className="relative pl-10 pb-6">
                        {/* 타임라인 도트 */}
                        <div className={`absolute left-2 w-5 h-5 rounded-full border-2 ${
                          item.type === '예방' ? 'bg-green-500 border-green-200' :
                          item.type === '예측' ? 'bg-blue-500 border-blue-200' :
                          item.type === '고장' ? 'bg-red-500 border-red-200' :
                          'bg-purple-500 border-purple-200'
                        }`}></div>

                        {/* 이력 카드 */}
                        <div className="bg-white border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-semibold text-gray-900">{item.date}</span>
                                <Badge variant="outline" className={
                                  item.type === '예방' ? 'bg-green-100 text-green-800' :
                                  item.type === '예측' ? 'bg-blue-100 text-blue-800' :
                                  item.type === '고장' ? 'bg-red-100 text-red-800' :
                                  'bg-purple-100 text-purple-800'
                                }>{item.type}</Badge>
                                <Badge variant="outline" className={
                                  item.status === '완료' ? 'bg-gray-100 text-gray-800' :
                                  item.status === '진행중' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-blue-100 text-blue-800'
                                }>{item.status}</Badge>
                              </div>
                              <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span>담당자: {item.technician}</span>
                            <span>소요시간: {item.duration}분</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  설비를 선택해주세요
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 설비 상세 모달 */}
      <Modal
        isOpen={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        title="설비 상세 정보"
        size="lg"
      >
        {selectedEquipment && (
          <div className="space-y-6">
            {/* 기본 정보 */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">설비 코드</label>
                <p className="text-lg font-semibold text-gray-900">{selectedEquipment.code}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">설비명</label>
                <p className="text-lg font-semibold text-gray-900">{selectedEquipment.name}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">위치</label>
                <p className="text-gray-900">{selectedEquipment.location}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">상태</label>
                <Badge className={selectedEquipment.status === 'OPERATIONAL' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                  {selectedEquipment.status_display}
                </Badge>
              </div>
            </div>

            {/* 건전도 및 고장 확률 */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-green-600 font-medium mb-2">건전도 점수</div>
                <div className={`text-4xl font-bold ${getHealthScoreColor(selectedEquipment.health_score)}`}>
                  {selectedEquipment.health_score.toFixed(1)}
                </div>
                <div className="text-xs text-green-500 mt-1">/ 100점</div>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <div className="text-sm text-orange-600 font-medium mb-2">고장 확률</div>
                <div className="text-4xl font-bold text-orange-600">
                  {selectedEquipment.failure_probability.toFixed(1)}%
                </div>
                <div className="text-xs text-orange-500 mt-1">향후 30일</div>
              </div>
            </div>

            {/* 가동율 및 성능률 */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">가동률</label>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${selectedEquipment.availability_current}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-blue-600 w-16 text-right">
                    {selectedEquipment.availability_current.toFixed(1)}%
                  </span>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">성능률</label>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${selectedEquipment.performance_current}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-green-600 w-16 text-right">
                    {selectedEquipment.performance_current.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            {/* 건전도 트렌드 */}
            <div>
              <h4 className="font-semibold mb-4">건전도 트렌드 (최근 30일)</h4>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={generateHealthTrendData(selectedEquipment.health_score)}>
                  <defs>
                    <linearGradient id="colorHealth" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="healthScore" stroke="#10b981" fillOpacity={1} fill="url(#colorHealth)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* 예측 고장 확률 */}
            <div>
              <h4 className="font-semibold mb-4">고장 확률 예측 (향후 30일)</h4>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={generateFailureTrendData(selectedEquipment.failure_probability)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="failureProb" stroke="#ef4444" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* 액션 버튼 */}
            <div className="flex gap-2 pt-4 border-t">
              <Button className="flex-1">
                <Wrench className="w-4 h-4 mr-2" />
                보전 일정 추가
              </Button>
              <Button variant="outline" className="flex-1" onClick={() => {
                setActiveTab('timeline');
                setDetailModalOpen(false);
              }}>
                <History className="w-4 h-4 mr-2" />
                이력 보기
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">설비 예지 보전</h1>
          <p className="text-sm text-gray-500 mt-1">
            AI 기반 설비 고장 예측 및 예방 보전 관리
          </p>
        </div>
        <Button>
          <Settings className="w-4 h-4 mr-2" />
          설정
        </Button>
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
                    {eq.maintenance_overdue && (
                      <span className="text-red-600 font-semibold">점검 지연</span>
                    )}
                  </div>
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
    </div>
  );
};

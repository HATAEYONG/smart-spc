import React, { useState, useEffect } from 'react';
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
  Settings,
  Calendar,
  Thermometer,
  Zap,
} from 'lucide-react';
import { pmService, Equipment, SensorData, FailurePrediction, PMDashboardData } from '../services/pmService';

export const PredictiveMaintenancePage: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<PMDashboardData | null>(null);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [sensorData, setSensorData] = useState<SensorData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
    loadEquipment();
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
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TimeSeries3DChart } from '../components/TimeSeries3DChart';
import { Heatmap3D } from '../components/Heatmap3D';
import { Scatter3D } from '../components/Scatter3D';
import { ForecastChart } from '../components/ForecastChart';
import { Spinner, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface TimeSeriesAnalysisProps {
  productId?: number;
}

export const TimeSeriesAnalysisPage: React.FC<TimeSeriesAnalysisProps> = ({ productId = 1 }) => {
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [forecastData, setForecastData] = useState<any>(null);
  const [anomalyData, setAnomalyData] = useState<any>(null);
  const [days, setDays] = useState(30);
  const [forecastSteps, setForecastSteps] = useState(5);
  const [forecastMethod, setForecastMethod] = useState('COMBINED');
  const [activeTab, setActiveTab] = useState<'analyze' | 'forecast' | 'anomalies'>('analyze');

  const fetchAnalysis = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/spc/time-series/analyze/', {
        product_id: productId,
        days,
        forecast_steps: forecastSteps
      });
      setAnalysisData(response.data);
      toast.success('시계열 분석 완료');
    } catch (error: any) {
      toast.error(`분석 실패: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchForecast = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/spc/time-series/forecast/', {
        product_id: productId,
        days,
        forecast_steps: forecastSteps,
        method: forecastMethod
      });
      setForecastData(response.data);
      toast.success('예측 완료');
    } catch (error: any) {
      toast.error(`예측 실패: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnomalies = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/spc/time-series/detect_anomalies/', {
        product_id: productId,
        days,
        threshold: 3.0
      });
      setAnomalyData(response.data);
      toast.success('이상 감지 완료');
    } catch (error: any) {
      toast.error(`이상 감지 실패: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, [productId]);

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-4">
          시계열 분석
        </h1>

        {/* 컨트롤 패널 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              분석 기간 (일)
            </label>
            <input
              type="number"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              min="7"
              max="365"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              예측 스텝 수
            </label>
            <input
              type="number"
              value={forecastSteps}
              onChange={(e) => setForecastSteps(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              min="1"
              max="20"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              예측 방법
            </label>
            <select
              value={forecastMethod}
              onChange={(e) => setForecastMethod(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
            >
              <option value="MA">이동평균 (MA)</option>
              <option value="ES">지수평활 (ES)</option>
              <option value="LT">선형추세 (LT)</option>
              <option value="COMBINED">앙상블 (COMBINED)</option>
            </select>
          </div>

          <div className="flex items-end gap-2">
            <button
              onClick={fetchAnalysis}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? <Spinner className="animate-spin h-5 w-5 mx-auto" /> : '분석 실행'}
            </button>
          </div>
        </div>

        {/* 탭 */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('analyze')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'analyze'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            종합 분석
          </button>
          <button
            onClick={() => setActiveTab('forecast')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'forecast'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            예측
          </button>
          <button
            onClick={() => setActiveTab('anomalies')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'anomalies'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 dark:text-gray-400'
            }`}
          >
            이상 감지
          </button>
        </div>
      </div>

      {/* 종합 분석 탭 */}
      {activeTab === 'analyze' && analysisData && (
        <div className="space-y-6">
          {/* 추세 분석 요약 */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
              추세 분석
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">추세</p>
                <p className="text-2xl font-bold text-gray-800 dark:text-white">
                  {analysisData.trend_analysis?.trend || 'N/A'}
                </p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">기울기</p>
                <p className="text-2xl font-bold text-gray-800 dark:text-white">
                  {analysisData.trend_analysis?.slope?.toFixed(6) || 'N/A'}
                </p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">R²</p>
                <p className="text-2xl font-bold text-gray-800 dark:text-white">
                  {analysisData.trend_analysis?.r_squared?.toFixed(4) || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* 3D 시계열 차트 */}
          <TimeSeries3DChart
            data={analysisData.historical_data || []}
            title="3D 시계열 분석"
          />

          {/* 다변량 히트맵 */}
          {analysisData.multivariate_data && (
            <Heatmap3D
              data={analysisData.multivariate_data}
              title="다변량 히트맵"
            />
          )}
        </div>
      )}

      {/* 예측 탭 */}
      {activeTab === 'forecast' && (
        <div className="space-y-6">
          <div className="flex justify-end">
            <button
              onClick={fetchForecast}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? <Spinner className="animate-spin h-5 w-5 mx-auto" /> : '예측 실행'}
            </button>
          </div>

          {forecastData && (
            <>
              {/* 예측 결과 요약 */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
                  예측 결과 ({forecastData.method})
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {forecastData.forecast_values?.map((value: number, idx: number) => (
                    <div key={idx} className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {forecastData.forecast_dates?.[idx] || `스텝 ${idx + 1}`}
                      </p>
                      <p className="text-2xl font-bold text-gray-800 dark:text-white">
                        {value?.toFixed(4)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 예측 차트 */}
              <ForecastChart
                data={[
                  ...forecastData.historical_data || [],
                  ...forecastData.forecast_values?.map((v: number, i: number) => ({
                    timestamp: forecastData.forecast_dates?.[i] || '',
                    value: v,
                    is_forecast: true,
                    upper_bound: forecastData.confidence_interval?.upper?.[i],
                    lower_bound: forecastData.confidence_interval?.lower?.[i]
                  })) || []
                ]}
                title="시계열 예측"
              />
            </>
          )}
        </div>
      )}

      {/* 이상 감지 탭 */}
      {activeTab === 'anomalies' && (
        <div className="space-y-6">
          <div className="flex justify-end">
            <button
              onClick={fetchAnomalies}
              disabled={loading}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {loading ? <Spinner className="animate-spin h-5 w-5 mx-auto" /> : '이상 감지 실행'}
            </button>
          </div>

          {anomalyData && (
            <>
              {/* 이상 감지 요약 */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
                  이상 감지 결과
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400">총 데이터 포인트</p>
                    <p className="text-2xl font-bold text-gray-800 dark:text-white">
                      {anomalyData.total_data_points}
                    </p>
                  </div>
                  <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400">이상 데이터 개수</p>
                    <p className="text-2xl font-bold text-gray-800 dark:text-white">
                      {anomalyData.anomaly_count}
                    </p>
                  </div>
                  <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400">이상율</p>
                    <p className="text-2xl font-bold text-gray-800 dark:text-white">
                      {anomalyData.anomaly_rate}%
                    </p>
                  </div>
                </div>
              </div>

              {/* 이상 데이터 목록 */}
              {anomalyData.anomalies?.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                  <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
                    이상 데이터 상세
                  </h3>
                  <div className="space-y-2">
                    {anomalyData.anomalies.map((anomaly: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-4 border border-red-200 dark:border-red-800 rounded-lg bg-red-50 dark:bg-red-900/10"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-semibold text-gray-800 dark:text-white">
                              값: {anomaly.value?.toFixed(4)}
                            </p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {anomaly.measured_at}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-semibold text-red-600 dark:text-red-400">
                              이상 점수: {anomaly.anomaly_score?.toFixed(1)}
                            </p>
                            {anomaly.statistical && (
                              <p className="text-xs text-gray-600 dark:text-gray-400">
                                Z-score: {anomaly.statistical.z_score?.toFixed(2)}
                              </p>
                            )}
                            {anomaly.pattern && (
                              <p className="text-xs text-gray-600 dark:text-gray-400">
                                패턴: {anomaly.pattern.description}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {anomalyData.anomalies?.length === 0 && (
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-8 text-center">
                  <AlertCircle className="h-12 w-12 text-green-600 dark:text-green-400 mx-auto mb-4" />
                  <p className="text-lg font-semibold text-green-800 dark:text-green-200">
                    감지된 이상 데이터가 없습니다
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

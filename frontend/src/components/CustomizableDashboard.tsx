import React, { useState } from 'react';
import { useDashboardStore, DashboardWidget } from '../store/dashboardStore';
import { X, Plus, Settings, RefreshCw, Moon, Sun } from 'lucide-react';
import { XBarRChart } from './XBarRChart';
import { ProcessCapabilityPage } from '../pages/ProcessCapabilityPage';
import { RunRuleViolationsChart } from './RunRuleViolationsChart';
import { RealtimeNotifications } from './RealtimeNotifications';
import { TimeSeries3DChart } from './TimeSeries3DChart';
import { Heatmap3D } from './Heatmap3D';
import { Scatter3D } from './Scatter3D';
import { ForecastChart } from './ForecastChart';

interface CustomizableDashboardProps {
  productId?: number;
}

export const CustomizableDashboard: React.FC<CustomizableDashboardProps> = ({ productId = 1 }) => {
  const { widgets, theme, addWidget, removeWidget, toggleWidgetVisibility, resetDashboard, setTheme } = useDashboardStore();
  const [editMode, setEditMode] = useState(false);
  const [showWidgetMenu, setShowWidgetMenu] = useState(false);

  const availableWidgets = [
    { type: 'xbar-r-chart', title: 'X-bar R 관리도' },
    { type: 'process-capability', title: '공정능력 지수' },
    { type: 'run-rule-violations', title: 'Run Rule 위반' },
    { type: 'quality-alerts', title: '품질 경고' },
    { type: 'time-series-3d', title: '3D 시계열 분석' },
    { type: 'heatmap-3d', title: '3D 다변량 히트맵' },
    { type: 'scatter-3d', title: '3D 산점도' },
    { type: 'forecast-chart', title: '예측 차트' },
    { type: 'realtime-notifications', title: '실시간 알림' }
  ];

  const renderWidget = (widget: DashboardWidget) => {
    const widgetStyle = {
      gridColumn: `span ${widget.position.w}`,
      gridRow: `span ${widget.position.h}`
    };

    return (
      <div
        key={widget.id}
        className={`relative bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 ${!widget.visible ? 'hidden' : ''}`}
        style={widgetStyle}
      >
        {editMode && (
          <div className="absolute top-2 right-2 z-10 flex gap-2">
            <button
              onClick={() => toggleWidgetVisibility(widget.id)}
              className="p-1 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
              aria-label={widget.visible ? '위젯 숨기기' : '위젯 표시'}
            >
              {widget.visible ? '👁️' : '🙈'}
            </button>
            <button
              onClick={() => removeWidget(widget.id)}
              className="p-1 bg-red-500 text-white rounded hover:bg-red-600"
              aria-label="위젯 제거"
            >
              <X size={16} />
            </button>
          </div>
        )}

        <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white pr-16">
          {widget.title}
        </h3>

        {widget.visible && (
          <>
            {widget.type === 'xbar-r-chart' && <XBarRChart data={[]} limits={{}} />}
            {widget.type === 'process-capability' && <ProcessCapabilityPage />}
            {widget.type === 'run-rule-violations' && <RunRuleViolationsChart measurements={[]} violations={[]} limits={{ucl: 0, cl: 0, lcl: 0}} />}
            {widget.type === 'quality-alerts' && (
              <div className="text-gray-600 dark:text-gray-300">
                품질 경고 위젯 (개발 중)
              </div>
            )}
            {widget.type === 'time-series-3d' && (
              <TimeSeries3DChart
                data={[]}
                title="3D 시계열 분석"
              />
            )}
            {widget.type === 'heatmap-3d' && (
              <Heatmap3D
                data={[]}
                title="3D 다변량 히트맵"
              />
            )}
            {widget.type === 'scatter-3d' && (
              <Scatter3D
                data={[]}
                title="3D 산점도"
              />
            )}
            {widget.type === 'forecast-chart' && (
              <ForecastChart
                data={[]}
                title="시계열 예측"
              />
            )}
            {widget.type === 'realtime-notifications' && <RealtimeNotifications />}
          </>
        )}
      </div>
    );
  };

  return (
    <div className={theme === 'dark' ? 'dark' : ''}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
        {/* 헤더 컨트롤 */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
              SPC 품질 관리 대시보드
            </h1>
            <button
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
              className="p-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>
          </div>

          <div className="flex items-center gap-2">
            {!editMode && (
              <button
                onClick={() => setShowWidgetMenu(!showWidgetMenu)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus size={20} />
                위젯 추가
              </button>
            )}

            <button
              onClick={() => setEditMode(!editMode)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                editMode
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : 'bg-gray-600 text-white hover:bg-gray-700'
              }`}
            >
              <Settings size={20} />
              {editMode ? '편집 완료' : '편집'}
            </button>

            <button
              onClick={resetDashboard}
              className="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              aria-label="대시보드 초기화"
            >
              <RefreshCw size={20} />
              초기화
            </button>
          </div>
        </div>

        {/* 위젯 추가 메뉴 */}
        {showWidgetMenu && (
          <div className="mb-6 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
            <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-white">
              위젯 추가
            </h3>
            <div className="grid grid-cols-3 gap-3">
              {availableWidgets.map((widget) => (
                <button
                  key={widget.type}
                  onClick={() => {
                    addWidget({
                      type: widget.type as any,
                      title: widget.title,
                      position: { x: 0, y: 0, w: 6, h: 4 },
                      visible: true
                    });
                    setShowWidgetMenu(false);
                  }}
                  className="px-4 py-3 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-gray-800 dark:text-white"
                >
                  {widget.title}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 대시보드 그리드 */}
        <div className="grid grid-cols-12 gap-6 auto-rows-auto">
          {widgets.map(renderWidget)}
        </div>

        {/* 편집 모드 안내 */}
        {editMode && (
          <div className="fixed bottom-4 right-4 p-4 bg-yellow-100 dark:bg-yellow-900 border border-yellow-400 dark:border-yellow-600 rounded-lg shadow-lg">
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              <strong>편집 모드</strong>: 위젯을 숨기거나 제거할 수 있습니다.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

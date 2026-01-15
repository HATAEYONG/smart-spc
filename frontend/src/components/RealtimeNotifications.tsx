import React, { useEffect, useState, useRef } from 'react';
import { Bell, X, AlertTriangle, CheckCircle, Info, AlertCircle } from 'lucide-react';

interface Toast {
  id: string;
  type: 'alert' | 'measurement' | 'capability' | 'info' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  data?: any;
}

const RealtimeNotifications: React.FC = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [showPanel, setShowPanel] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [wsEnabled, setWsEnabled] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket 백엔드 미구현으로 알림 기능 비활성화
  const isWebSocketImplemented = false;

  // WebSocket 연결 설정
  useEffect(() => {
    // WebSocket 연결 시도를 완전히 비활성화 (백엔드에서 WebSocket 지원 안 함)
    // 추후 Redis + channels 설치 후 활성화 필요
    const suppressErrors = () => {
      // 빈 함수로 에러 억제
    };

    // Cleanup
    return () => {
      suppressErrors();
    };
  }, []);

  // WebSocket 메시지 처리
  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'connection':
        addToast({
          type: 'info',
          title: '연결 성공',
          message: data.message || '실시간 알림에 연결되었습니다',
        });
        break;

      case 'alert':
        addToast({
          type: 'alert',
          title: `품질 경고: ${data.alert?.product_code || '알 수 없음'}`,
          message: data.alert?.message || '규격 이탈이 감지되었습니다',
          data: data.alert,
        });
        break;

      case 'measurement':
        addToast({
          type: 'measurement',
          title: `측정 데이터: ${data.measurement?.product_code || '알 수 없음'}`,
          message: `새로운 측정값: ${data.measurement?.measurement_value}`,
          data: data.measurement,
        });
        break;

      case 'capability':
        addToast({
          type: 'capability',
          title: `공정능력 업데이트: ${data.capability?.product_code || '알 수 없음'}`,
          message: `Cpk: ${data.capability?.cpk?.toFixed(3)}`,
          data: data.capability,
        });
        break;

      case 'subscription':
        addToast({
          type: 'info',
          title: '구독 완료',
          message: data.message || '제품 알림을 구독했습니다',
        });
        break;

      case 'error':
        addToast({
          type: 'error',
          title: '오류',
          message: data.message || '알 수 없는 오류가 발생했습니다',
        });
        break;

      default:
        console.log('Unhandled WebSocket message type:', data.type);
    }
  };

  const addToast = (toast: Omit<Toast, 'id' | 'timestamp'>) => {
    const id = Date.now().toString();
    const newToast: Toast = {
      ...toast,
      id,
      timestamp: new Date(),
    };

    setToasts(prev => [newToast, ...prev].slice(0, 50));
    setUnreadCount(prev => prev + 1);

    if (toast.type !== 'alert') {
      setTimeout(() => {
        removeToast(id);
      }, 5000);
    }
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const clearAll = () => {
    setToasts([]);
    setUnreadCount(0);
  };

  const getToastIcon = (type: Toast['type']) => {
    switch (type) {
      case 'alert':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'measurement':
        return <AlertCircle className="w-5 h-5 text-orange-500" />;
      case 'capability':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <X className="w-5 h-5 text-red-600" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getToastStyle = (type: Toast['type']) => {
    switch (type) {
      case 'alert':
        return 'bg-red-50 border-red-200';
      case 'measurement':
        return 'bg-orange-50 border-orange-200';
      case 'capability':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-100 border-red-300';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  return (
    <>
      {/* Bell Icon Button - WebSocket 미구현으로 숨김 */}
      {isWebSocketImplemented && (
        <div className="fixed top-20 right-4 z-50">
          <button
            onClick={() => {
              setShowPanel(!showPanel);
              setUnreadCount(0);
            }}
            className="relative p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow"
          >
            <Bell className="w-6 h-6 text-gray-600" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          <div className={`mt-2 text-xs text-center ${wsEnabled ? 'text-green-600' : 'text-gray-400'}`}>
            {wsEnabled ? '● 실시간' : '○ 연결안됨'}
          </div>
        </div>
      )}

      {/* Notification Panel */}
      {isWebSocketImplemented && showPanel && (
        <div className="fixed top-20 right-16 w-96 max-h-[600px] bg-white rounded-lg shadow-2xl z-50 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">알림</h3>
              <p className="text-xs text-gray-500">{toasts.length}개의 알림</p>
            </div>
            <button
              onClick={clearAll}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              모두 지우기
            </button>
          </div>

          {/* Toasts */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {toasts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Bell className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>알림이 없습니다</p>
              </div>
            ) : (
              toasts.map((toast) => (
                <div
                  key={toast.id}
                  className={`p-3 border rounded-lg ${getToastStyle(toast.type)} relative`}
                >
                  <button
                    onClick={() => removeToast(toast.id)}
                    className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-4 h-4" />
                  </button>

                  <div className="flex items-start gap-2">
                    <div className="flex-shrink-0 mt-0.5">
                      {getToastIcon(toast.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm text-gray-900">{toast.title}</p>
                      <p className="text-sm text-gray-600 mt-1">{toast.message}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {toast.timestamp.toLocaleTimeString('ko-KR')}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default RealtimeNotifications;
export { RealtimeNotifications };

/**
 * WebSocket React Hook
 * 실시간 데이터 업데이트를 위한 React Hook
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { spcWebSocket, WebSocketMessage } from '../services/websocket';

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoConnect?: boolean;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  messages: WebSocketMessage[];
  sendMessage: (data: any) => void;
  connect: () => void;
  disconnect: () => void;
  subscribe: (eventType: string, handler: (message: WebSocketMessage) => void) => () => void;
}

/**
 * WebSocket 연결을 위한 React Hook
 *
 * @param url - WebSocket URL (선택 사항, 기본값은 환경 변수 사용)
 * @param options - 추가 옵션
 */
export function useWebSocket(url?: string, options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const optionsRef = useRef(options);
  const wsUrlRef = useRef(url);

  // 옵션 및 URL 업데이트
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  useEffect(() => {
    wsUrlRef.current = url;
  }, [url]);

  // 메시지 핸들러
  useEffect(() => {
    const handleMessage = (message: WebSocketMessage) => {
      setMessages(prev => [...prev, message].slice(-100)); // 최근 100개 메시지만 유지
      optionsRef.current.onMessage?.(message);
    };

    const handleConnect = () => {
      setIsConnected(true);
      optionsRef.current.onConnect?.();
    };

    const handleDisconnect = () => {
      setIsConnected(false);
      optionsRef.current.onDisconnect?.();
    };

    const handleError = (error: Event) => {
      optionsRef.current.onError?.(error);
    };

    // 이벤트 핸들러 등록
    const unsubscribeMessage = spcWebSocket.on('*', handleMessage);
    const unsubscribeConnect = spcWebSocket.onConnect(handleConnect);
    const unsubscribeDisconnect = spcWebSocket.onDisconnect(handleDisconnect);
    const unsubscribeError = spcWebSocket.onError(handleError);

    // 정리 함수
    return () => {
      unsubscribeMessage();
      unsubscribeConnect();
      unsubscribeDisconnect();
      unsubscribeError();
    };
  }, []);

  // 자동 연결
  useEffect(() => {
    if (optionsRef.current.autoConnect && !spcWebSocket.isConnected()) {
      const connectUrl = wsUrlRef.current || `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}/spc/`;
      spcWebSocket.connect(connectUrl);
    }

    return () => {
      if (optionsRef.current.autoConnect) {
        spcWebSocket.disconnect();
      }
    };
  }, []);

  // 메시지 전송
  const sendMessage = useCallback((data: any) => {
    spcWebSocket.send(data);
  }, []);

  // 연결
  const connect = useCallback(() => {
    const connectUrl = wsUrlRef.current || `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}/spc/`;
    spcWebSocket.connect(connectUrl);
  }, []);

  // 연결 해제
  const disconnect = useCallback(() => {
    spcWebSocket.disconnect();
  }, []);

  // 이벤트 구독
  const subscribe = useCallback((eventType: string, handler: (message: WebSocketMessage) => void) => {
    return spcWebSocket.on(eventType, handler);
  }, []);

  return {
    isConnected,
    messages,
    sendMessage,
    connect,
    disconnect,
    subscribe,
  };
}

/**
 * 특정 이벤트 타입만 구독하는 Hook
 */
export function useWebSocketEvent(
  eventType: string,
  handler: (message: WebSocketMessage) => void,
  url?: string
) {
  const { isConnected } = useWebSocket(url, {
    autoConnect: true,
  });

  useEffect(() => {
    const unsubscribe = spcWebSocket.on(eventType, handler);
    return () => {
      unsubscribe();
    };
  }, [eventType, handler]);

  return { isConnected };
}

/**
 * SPC 알림 실시간 수신 Hook
 */
export function useSPCAlerts(onAlert: (alert: any) => void) {
  return useWebSocketEvent('spc_alert', (message) => {
    onAlert(message.data);
  });
}

/**
 * APS 이벤트 실시간 수신 Hook
 */
export function useAPSEvents(onEvent: (event: any) => void) {
  return useWebSocketEvent('aps_event', (message) => {
    onEvent(message.data);
  });
}

/**
 * KPI 업데이트 실시간 수신 Hook
 */
export function useKPIUpdates(onUpdate: (kpi: any) => void) {
  return useWebSocketEvent('kpi_update', (message) => {
    onUpdate(message.data);
  });
}

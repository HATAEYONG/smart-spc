/**
 * WebSocket 서비스
 * SPC 실시간 알림 및 데이터 업데이트
 */

export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface AlertData {
  id: number;
  product_code: string;
  product_name: string;
  alert_type: string;
  priority: number;
  title: string;
  message: string;
  status: string;
  created_at: string;
}

export interface MeasurementData {
  id: number;
  product_id: number;
  product_code: string;
  measurement_value: number;
  sample_number: number;
  subgroup_number: number;
  is_within_spec: boolean;
  is_within_control: boolean;
  measured_at: string;
}

export interface CapabilityData {
  id: number;
  product_id: number;
  product_code: string;
  cp: number;
  cpk: number;
  pp?: number;
  ppk?: number;
  analyzed_at: string;
}

type MessageHandler = (data: any) => void;
type ConnectionHandler = () => void;
type ErrorHandler = (error: Event) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimeout: number = 5000;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private isManualClose: boolean = false;
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map();
  private onConnectCallbacks: Set<ConnectionHandler> = new Set();
  private onDisconnectCallbacks: Set<ConnectionHandler> = new Set();
  private onErrorCallbacks: Set<ErrorHandler> = new Set();

  /**
   * WebSocket 연결
   */
  connect(url: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      this.isManualClose = false;
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.onConnectCallbacks.forEach(cb => cb());
      };

      this.ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.onDisconnectCallbacks.forEach(cb => cb());

        if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          setTimeout(() => this.connect(url), this.reconnectTimeout);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.onErrorCallbacks.forEach(cb => cb(error));
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }

  /**
   * WebSocket 연결 해제
   */
  disconnect(): void {
    this.isManualClose = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * 메시지 핸들러 등록
   */
  on(type: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }
    this.messageHandlers.get(type)!.add(handler);

    // 핸들러 제거 함수 반환
    return () => {
      this.off(type, handler);
    };
  }

  /**
   * 메시지 핸들러 해제
   */
  off(type: string, handler: MessageHandler): void {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  /**
   * 연결 핸들러 등록
   */
  onConnect(handler: ConnectionHandler): () => void {
    this.onConnectCallbacks.add(handler);
    return () => {
      this.onConnectCallbacks.delete(handler);
    };
  }

  /**
   * 연결 해제 핸들러 등록
   */
  onDisconnect(handler: ConnectionHandler): () => void {
    this.onDisconnectCallbacks.add(handler);
    return () => {
      this.onDisconnectCallbacks.delete(handler);
    };
  }

  /**
   * 에러 핸들러 등록
   */
  onError(handler: ErrorHandler): () => void {
    this.onErrorCallbacks.add(handler);
    return () => {
      this.onErrorCallbacks.delete(handler);
    };
  }

  /**
   * 메시지 전송
   */
  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', data);
    }
  }

  /**
   * 특정 제품 구독
   */
  subscribeProduct(productId: number): void {
    this.send({
      type: 'subscribe_product',
      product_id: productId,
    });
  }

  /**
   * 특정 제품 구독 해지
   */
  unsubscribeProduct(productId: number): void {
    this.send({
      type: 'unsubscribe_product',
      product_id: productId,
    });
  }

  /**
   * 최근 알림 요청
   */
  getAlerts(limit: number = 10): void {
    this.send({
      type: 'get_alerts',
      limit,
    });
  }

  /**
   * 최신 데이터 요청
   */
  getLatestData(limit: number = 20): void {
    this.send({
      type: 'get_latest_data',
      limit,
    });
  }

  /**
   * 연결 상태 확인
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * 메시지 타입별로 핸들러 호출
   */
  private handleMessage(data: WebSocketMessage): void {
    const handlers = this.messageHandlers.get(data.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in ${data.type} handler:`, error);
        }
      });
    }

    // 전체 메시지 핸들러 (*)
    const allHandlers = this.messageHandlers.get('*');
    if (allHandlers) {
      allHandlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error('Error in * handler:', error);
        }
      });
    }
  }
}

// SPC WebSocket 서비스 인스턴스 생성
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsHost = window.location.hostname;
const wsPort = '8000';

export const spcWebSocket = new WebSocketService();

/**
 * 알림 WebSocket 연결
 */
export const connectNotifications = () => {
  const url = `${wsProtocol}//${wsHost}:${wsPort}/ws/spc/notifications/`;
  spcWebSocket.connect(url);
  return spcWebSocket;
};

/**
 * 제품 데이터 WebSocket 연결
 */
export const connectProductData = (productId: number) => {
  const url = `${wsProtocol}//${wsHost}:${wsPort}/ws/spc/product/${productId}/`;
  spcWebSocket.connect(url);
  return spcWebSocket;
};

export default spcWebSocket;

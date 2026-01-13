/**
 * PWA (Progressive Web App) 유틸리티
 */

// 서비스 워커 등록
export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('Service Worker 등록 성공:', registration.scope);

          // 업데이트 확인
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  // 새로운 버전 사용 가능
                  if (window.confirm('새로운 버전이 있습니다. 업데이트하시겠습니까?')) {
                    newWorker.postMessage({ type: 'SKIP_WAITING' });
                  }
                }
              });
            }
          });
        })
        .catch((error) => {
          console.error('Service Worker 등록 실패:', error);
        });
    });
  }
}

// 서비스 워커 업데이트 스킵
export function skipWaiting() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.waiting?.postMessage({ type: 'SKIP_WAITING' });
    });
  }
}

// PWA 설치 상태 확인
export function isPWAInstalled(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as any).standalone === true;
}

// 앱 설치 프롬프트 (사용자 정의 설치 UI)
export function setupInstallPrompt() {
  let deferredPrompt: any = null;

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
  });

  return {
    canInstall: () => deferredPrompt !== null,
    prompt: async () => {
      if (!deferredPrompt) return false;

      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      deferredPrompt = null;

      return outcome === 'accepted';
    }
  };
}

// 오프라인 상태 감지
export function setupOfflineDetection(
  onOnline: () => void,
  onOffline: () => void
) {
  window.addEventListener('online', onOnline);
  window.addEventListener('offline', onOffline);

  return () => {
    window.removeEventListener('online', onOnline);
    window.removeEventListener('offline', onOffline);
  };
}

// 온라인/오프라인 상태 확인
export function isOnline(): boolean {
  return navigator.onLine;
}

// 캐시 관리
export const cacheManager = {
  async clearCache() {
    if ('serviceWorker' in navigator) {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map((cacheName) => caches.delete(cacheName))
      );
    }
  },

  async getCacheSize(): Promise<number> {
    if ('serviceWorker' in navigator) {
      const cacheNames = await caches.keys();
      let totalSize = 0;

      for (const cacheName of cacheNames) {
        const cache = await caches.open(cacheName);
        const keys = await cache.keys();

        for (const request of keys) {
          const response = await cache.match(request);
          if (response) {
            const blob = await response.blob();
            totalSize += blob.size;
          }
        }
      }

      return totalSize;
    }
    return 0;
  },

  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }
};

// 푸시 알림 요청
export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!('Notification' in window)) {
    console.warn('이 브라우저는 알림을 지원하지 않습니다');
    return 'denied';
  }

  if (Notification.permission === 'granted') {
    return 'granted';
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission;
  }

  return 'denied';
}

// 푸시 알림 표시
export async function showNotification(
  title: string,
  options?: NotificationOptions
): Promise<void> {
  const permission = await requestNotificationPermission();

  if (permission === 'granted') {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'SHOW_NOTIFICATION',
        title,
        options
      });
    } else {
      new Notification(title, options);
    }
  }
}

// 앱 배지 설정 (모바일 홈 화면 아이콘 위 숫자)
export function setAppBadge(count: number | undefined) {
  if ('setAppBadge' in navigator) {
    (navigator as any).setAppBadge(count);
  } else if ('setAppBadge' in (window.navigator as any)) {
    // Safari fallback
    // Safari에서는 지원하지 않음
    console.warn('App badge not supported');
  }
}

// 앱 배지 제거
export function clearAppBadge() {
  if ('clearAppBadge' in navigator) {
    (navigator as any).clearAppBadge();
  }
}

// PWA 정보 가져오기
export async function getPWAInfo(): Promise<{
  isInstalled: boolean;
  isOnline: boolean;
  cacheSize: string;
  notificationPermission: NotificationPermission;
}> {
  const cacheSize = await cacheManager.getCacheSize();

  return {
    isInstalled: isPWAInstalled(),
    isOnline: isOnline(),
    cacheSize: cacheManager.formatBytes(cacheSize),
    notificationPermission: Notification.permission
  };
}

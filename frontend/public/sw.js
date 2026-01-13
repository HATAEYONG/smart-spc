const CACHE_NAME = 'spc-qc-v1';
const urlsToCache = [
  '/',
  '/dashboard',
  '/data-entry',
  '/process-capability',
  '/reports',
  '/chatbot',
  '/time-series',
  '/manifest.json'
];

const STATIC_CACHE = 'spc-static-v1';
const DYNAMIC_CACHE = 'spc-dynamic-v1';

// 설치 이벤트
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

// 활성화 이벤트
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// 페치 이벤트 (Network First, Fall Back to Cache)
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API 요청은 Network First
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // 성공적인 응답 캐시
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // 네트워크 실패 시 캐시 사용
          return caches.match(request);
        })
    );
    return;
  }

  // 정적 리소스는 Cache First
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(request).then((response) => {
        // 정적 리소스만 캐시
        if (response.status === 200 && request.method === 'GET') {
          const responseClone = response.clone();
          caches.open(STATIC_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      });
    })
  );
});

// 백그라운드 동기화 (옵션)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-quality-data') {
    event.waitUntil(
      // 오프라인 동안 저장된 품질 데이터 동기화
      caches.open(DYNAMIC_CACHE).then((cache) => {
        return cache.keys().then((keys) => {
          return Promise.all(
            keys.map((request) => {
              return fetch(request.url).then((response) => {
                if (response.status === 200) {
                  return cache.put(request, response.clone());
                }
              });
            })
          );
        });
      })
    );
  }
});

// 푸시 알림 (옵션)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : '새로운 품질 알림이 있습니다',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: '알림 보기',
        icon: '/icons/icon-96x96.png'
      },
      {
        action: 'close',
        title: '닫기',
        icon: '/icons/icon-96x96.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('SPC 품질관리 시스템', options)
  );
});

// 알림 클릭 처리
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/alerts')
    );
  }
});

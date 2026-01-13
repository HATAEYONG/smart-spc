/**
 * WCAG 2.1 접근성 유틸리티
 */

// 색상 대비율 계산 (WCAG 2.1)
export function getContrastRatio(foreground: string, background: string): number {
  const getLuminance = (hex: string): number => {
    const rgb = hexToRgb(hex);
    if (!rgb) return 0;

    const [r, g, b] = [rgb.r, rgb.g, rgb.b].map((val) => {
      val = val / 255;
      return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const lum1 = getLuminance(foreground);
  const lum2 = getLuminance(background);

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
}

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      }
    : null;
}

// WCAG 2.1 준수 여부 확인
export function checkWCAGCompliance(foreground: string, background: string): {
  aaNormal: boolean;
  aaLarge: boolean;
  aaaNormal: boolean;
  aaaLarge: boolean;
  ratio: number;
} {
  const ratio = getContrastRatio(foreground, background);

  return {
    ratio,
    aaNormal: ratio >= 4.5,
    aaLarge: ratio >= 3,
    aaaNormal: ratio >= 7,
    aaaLarge: ratio >= 4.5
  };
}

// 키보드 네비게이션 가능한 요소 확인
export function isKeyboardNavigable(element: HTMLElement): boolean {
  const tagName = element.tagName.toLowerCase();
  const hasTabIndex = element.tabIndex >= 0;

  return (
    tagName === 'a' ||
    tagName === 'button' ||
    tagName === 'input' ||
    tagName === 'select' ||
    tagName === 'textarea' ||
    hasTabIndex
  );
}

// 포커스 트랩 확인 (모달/다이얼로그용)
export function setupFocusTrap(container: HTMLElement): () => void {
  const focusableElements = container.querySelectorAll(
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  ) as NodeListOf<HTMLElement>;

  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  const handleTabKey = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
    } else {
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  };

  container.addEventListener('keydown', handleTabKey);

  // 초기 포커스
  setTimeout(() => firstElement?.focus(), 100);

  // 정리 함수
  return () => {
    container.removeEventListener('keydown', handleTabKey);
  };
}

// ARIA 라벨 생성
export function generateAriaLabel(component: string, props: Record<string, any>): string {
  const labels: Record<string, string> = {
    'button': props['aria-label'] || props.title || props.children || 'Button',
    'link': props['aria-label'] || props.title || props.children || 'Link',
    'input': props['aria-label'] || props.placeholder || props.label || 'Input',
    'select': props['aria-label'] || props.placeholder || props.label || 'Select',
    'chart': props['aria-label'] || props.title || `${component} Chart`,
  };

  return labels[component] || component;
}

// 스크린 리더 전용 텍스트 생성
export function getScreenReaderText(
  type: 'loading' | 'error' | 'success' | 'info',
  message?: string
): string {
  const baseMessages = {
    loading: '로딩 중입니다',
    error: '오류가 발생했습니다',
    success: '작업이 완료되었습니다',
    info: '정보'
  };

  return message ? `${baseMessages[type]}: ${message}` : baseMessages[type];
}

// 포커스 관리
export class FocusManager {
  private previousFocus: HTMLElement | null = null;

  saveFocus() {
    this.previousFocus = document.activeElement as HTMLElement;
  }

  restoreFocus() {
    if (this.previousFocus) {
      this.previousFocus.focus();
    }
  }

  setFocus(element: HTMLElement) {
    this.saveFocus();
    element.focus();
  }
}

// 토스트 announcements (스크린 리더용)
export function announceToScreenReader(message: string, priority: 'polite' | 'assertive' = 'polite') {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

// 키보드 단축키 설명 생성
export function getKeyboardShortcutHelp(): Array<{
  key: string;
  description: string;
}> {
  return [
    { key: 'Tab', description: '다음 요소로 이동' },
    { key: 'Shift + Tab', description: '이전 요소로 이동' },
    { key: 'Enter / Space', description: '선택 또는 활성화' },
    { key: 'Esc', description: '모달/다이얼로그 닫기' },
    { key: 'Arrow Keys', description: '목록/메뉴 탐색' },
    { key: 'Home / End', description: '첫 번째/마지막 요소로 이동' }
  ];
}

// 시각적 숨김 클래스 (스크린 리더용)
export const srOnlyStyles = `
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
`;

// 텍스트 크기 조절 가능 여부 확인 (WCAG 1.4.4)
export function checkTextResizability(): boolean {
  const body = document.body;
  const computedStyle = window.getComputedStyle(body);
  const fontSize = parseFloat(computedStyle.fontSize);

  // 브라우저 기본 zoom 테스트
  const originalZoom = (document.documentElement as any).style.zoom || 1;
  (document.documentElement as any).style.zoom = 2;

  const newFontSize = parseFloat(window.getComputedStyle(body).fontSize);
  const isResizable = newFontSize > fontSize;

  (document.documentElement as any).style.zoom = originalZoom;

  return isResizable;
}

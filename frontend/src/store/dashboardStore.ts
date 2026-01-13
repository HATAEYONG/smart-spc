import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type WidgetType =
  | 'xbar-r-chart'
  | 'process-capability'
  | 'run-rule-violations'
  | 'quality-alerts'
  | 'time-series-3d'
  | 'heatmap-3d'
  | 'scatter-3d'
  | 'forecast-chart'
  | 'realtime-notifications';

export interface DashboardWidget {
  id: string;
  type: WidgetType;
  title: string;
  position: { x: number; y: number; w: number; h: number };
  visible: boolean;
  config?: Record<string, any>;
}

interface DashboardState {
  widgets: DashboardWidget[];
  theme: 'light' | 'dark';
  addWidget: (widget: Omit<DashboardWidget, 'id'>) => void;
  removeWidget: (id: string) => void;
  updateWidget: (id: string, updates: Partial<DashboardWidget>) => void;
  toggleWidgetVisibility: (id: string) => void;
  updateWidgetPosition: (id: string, position: { x: number; y: number; w: number; h: number }) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  resetDashboard: () => void;
}

const defaultWidgets: DashboardWidget[] = [
  {
    id: '1',
    type: 'xbar-r-chart',
    title: 'X-bar R 관리도',
    position: { x: 0, y: 0, w: 6, h: 4 },
    visible: true
  },
  {
    id: '2',
    type: 'process-capability',
    title: '공정능력 지수',
    position: { x: 6, y: 0, w: 6, h: 4 },
    visible: true
  },
  {
    id: '3',
    type: 'run-rule-violations',
    title: 'Run Rule 위반',
    position: { x: 0, y: 4, w: 6, h: 4 },
    visible: true
  },
  {
    id: '4',
    type: 'quality-alerts',
    title: '품질 경고',
    position: { x: 6, y: 4, w: 6, h: 4 },
    visible: true
  },
  {
    id: '5',
    type: 'realtime-notifications',
    title: '실시간 알림',
    position: { x: 0, y: 8, w: 12, h: 2 },
    visible: true
  }
];

export const useDashboardStore = create<DashboardState>()(
  persist(
    (set) => ({
      widgets: defaultWidgets,
      theme: 'light',

      addWidget: (widget) =>
        set((state) => ({
          widgets: [
            ...state.widgets,
            { ...widget, id: Date.now().toString() }
          ]
        })),

      removeWidget: (id) =>
        set((state) => ({
          widgets: state.widgets.filter((w) => w.id !== id)
        })),

      updateWidget: (id, updates) =>
        set((state) => ({
          widgets: state.widgets.map((w) =>
            w.id === id ? { ...w, ...updates } : w
          )
        })),

      toggleWidgetVisibility: (id) =>
        set((state) => ({
          widgets: state.widgets.map((w) =>
            w.id === id ? { ...w, visible: !w.visible } : w
          )
        })),

      updateWidgetPosition: (id, position) =>
        set((state) => ({
          widgets: state.widgets.map((w) =>
            w.id === id ? { ...w, position } : w
          )
        })),

      setTheme: (theme) => set({ theme }),

      resetDashboard: () => set({ widgets: defaultWidgets, theme: 'light' })
    })),
    {
      name: 'spc-dashboard-storage'
    }
  )
);

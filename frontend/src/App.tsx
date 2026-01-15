/**
 * Main App Component
 * 스마트 품질예측 시스템 메인 앱
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Activity, FileText, Database, Brain, MessageSquare,
  BarChart3, Sigma, Wrench, Settings, DollarSign, ClipboardCheck,
  ListChecks, Search, Shield, TrendingUp, Lightbulb, AlertTriangle,
  Package, BookOpen, AlertCircle
} from 'lucide-react';
import { DashboardPage } from './pages/DashboardPage';
import { QCostClassificationPage } from './pages/QCostClassificationPage';
import { QCostDashboardPage } from './pages/QCostDashboardPage';
import { QCostCollectionPage } from './pages/QCostCollectionPage';
import { COPQAnalysisPage } from './pages/COPQAnalysisPage';
import { InspectionProcessDesignPage } from './pages/InspectionProcessDesignPage';
import { InspectionStandardsPage } from './pages/InspectionStandardsPage';
import { InspectionMethodsPage } from './pages/InspectionMethodsPage';
import { SPCChartPage } from './pages/SPCChartPage';
import ProcessCapabilityPage from './pages/ProcessCapabilityPage';
import DataEntryPage from './pages/DataEntryPage';
import RunRuleAnalysisPage from './pages/RunRuleAnalysisPage';
import ChatbotPage from './pages/ChatbotPage';
import ReportsPage from './pages/ReportsPage';
import AdvancedChartsPage from './pages/AdvancedChartsPage';
import SixSigmaDashboardPage from './pages/SixSigmaDashboardPage';
import SixSigmaToolsPage from './pages/SixSigmaToolsPage';
import MasterDataDashboardPage from './pages/MasterDataDashboardPage';
import MasterDataItemsPage from './pages/MasterDataItemsPage';
import MasterDataInstrumentsPage from './pages/MasterDataInstrumentsPage';
import MasterDataSyncPage from './pages/MasterDataSyncPage';
import MasterDataProcessesPage from './pages/MasterDataProcessesPage';
import MasterDataCharacteristicsPage from './pages/MasterDataCharacteristicsPage';
import MasterDataSystemsPage from './pages/MasterDataSystemsPage';
import MasterDataStandardsPage from './pages/MasterDataStandardsPage';
import { QASystemPage } from './pages/QASystemPage';
import { AIAnalysisPage } from './pages/AIAnalysisPage';
import { BenchmarksPage } from './pages/BenchmarksPage';
import { RealtimeNotifications } from './components/RealtimeNotifications';
import { PredictiveMaintenancePage } from './pages/PredictiveMaintenancePage';
import { EquipmentMasterPage } from './pages/EquipmentMasterPage';
import { EquipmentPartsPage } from './pages/EquipmentPartsPage';
import { EquipmentManualPage } from './pages/EquipmentManualPage';
import { EquipmentRepairHistoryPage } from './pages/EquipmentRepairHistoryPage';
import { ToolMasterPage } from './pages/ToolMasterPage';
import { ToolRepairHistoryPage } from './pages/ToolRepairHistoryPage';
import { ToolPredictionPage } from './pages/ToolPredictionPage';
import { WorkOrderManagementPage } from './pages/WorkOrderManagementPage';
import { QualityIssuesPage } from './pages/QualityIssuesPage';
import { PreventiveMaintenancePage } from './pages/PreventiveMaintenancePage';
import { ProductionMonitoringPage } from './pages/ProductionMonitoringPage';

// Placeholder pages for new features
const PlaceholderPage = ({ title }: { title: string }) => (
  <div className="p-6">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
    <div className="bg-white rounded-lg shadow p-6">
      <p className="text-gray-600">이 페이지는 준비 중입니다.</p>
      <p className="text-sm text-gray-500 mt-2">곧 새로운 기능이 추가될 예정입니다.</p>
    </div>
  </div>
);

const QCostReport = () => <PlaceholderPage title="결과보고서 생성" />;

const menuItems = [
  {
    category: '기본 기능',
    items: [
      { path: '/', label: '통합대시보드', icon: LayoutDashboard },
      { path: '/production-monitoring', label: '생산 모니터링', icon: Activity },
      { path: '/qcost-dashboard', label: 'Q-COST 대시보드', icon: TrendingUp },
    ]
  },
  {
    category: '품질코스트 관리',
    items: [
      { path: '/qcost-classification', label: 'Q-COST 분류체계', icon: Settings },
      { path: '/qcost-collection', label: 'Q-COST 수집', icon: Database },
      { path: '/copq-analysis', label: 'COPQ 분석', icon: DollarSign },
      { path: '/qcost-report', label: '결과보고서', icon: FileText },
    ]
  },
  {
    category: '검수 관리',
    items: [
      { path: '/inspection-process', label: '검수 프로세스', icon: ClipboardCheck },
      { path: '/inspection-standards', label: '검수 기준', icon: ListChecks },
      { path: '/inspection-methods', label: '검사 기법', icon: Search },
    ]
  },
  {
    category: 'SPC & 분석',
    items: [
      { path: '/capability', label: '공정능력 분석', icon: Activity },
      { path: '/data-entry', label: '데이터 입력', icon: Database },
      { path: '/run-rules', label: 'AI Run Rule 분석', icon: Brain },
      { path: '/advanced-charts', label: '고급 관리도', icon: BarChart3 },
      { path: '/quality-issues', label: '품질 이슈 추적', icon: AlertTriangle },
    ]
  },
  {
    category: '품질보증 & AI',
    items: [
      { path: '/qa-system', label: '품질보증 시스템', icon: Shield },
      { path: '/ai-analysis', label: 'AI 분석·추천', icon: Lightbulb },
      { path: '/chatbot', label: 'AI 챗봇', icon: MessageSquare },
    ]
  },
  {
    category: '고급 기능',
    items: [
      { path: '/work-orders', label: '작업지시 관리', icon: ClipboardCheck },
      { path: '/six-sigma', label: 'Six Sigma', icon: Sigma },
      { path: '/six-sigma/tools', label: '통계 도구', icon: Wrench },
      { path: '/benchmarks', label: '사례·벤치마킹', icon: TrendingUp },
      { path: '/reports', label: '보고서', icon: FileText },
      { path: '/master-data', label: '기본정보', icon: Settings },
    ]
  },
  {
    category: '설비 관리',
    items: [
      { path: '/equipment-master', label: '설비 마스터', icon: Wrench },
      { path: '/equipment-parts', label: '설비 부품', icon: Package },
      { path: '/equipment-manual', label: '설비 매뉴얼', icon: BookOpen },
      { path: '/equipment-repair', label: '수리 이력', icon: AlertCircle },
      { path: '/preventive-maintenance', label: '예방 보전 일정', icon: Calendar },
      { path: '/predictive-maintenance', label: '설비 예지 보전', icon: AlertTriangle },
    ]
  },
  {
    category: '치공구 관리',
    items: [
      { path: '/tool-master', label: '치공구 마스터', icon: Wrench },
      { path: '/tool-repair', label: '수리 이력', icon: AlertCircle },
      { path: '/tool-prediction', label: '예측 고도화', icon: Brain },
    ]
  },
];

function Sidebar() {
  const location = useLocation();

  return (
    <div className="w-80 bg-gradient-to-b from-white to-purple-50 max-h-screen shadow-2xl border-r-2 border-purple-100 flex flex-col fixed left-0 top-0 bottom-0">
      {/* Logo Section */}
      <div className="p-6 border-b-2 border-purple-200 bg-gradient-to-r from-purple-600 to-pink-600 flex-shrink-0">
        <h1 className="text-3xl font-black text-white flex items-center gap-2">
          <Brain className="w-9 h-9" />
          스마트 품질예측
        </h1>
        <p className="text-purple-100 text-sm mt-2 font-medium">AI 기반 통합 품질관리 시스템</p>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4 space-y-4 overflow-y-auto overflow-x-hidden" style={{ maxHeight: 'calc(100vh - 200px)' }}>
        {menuItems.map((section) => (
          <div key={section.category}>
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 px-3">
              {section.category}
            </h3>
            <div className="space-y-1">
              {section.items.map((item) => {
                const isActive = location.pathname === item.path ||
                  (item.path !== '/' && location.pathname.startsWith(item.path));
                const Icon = item.icon;

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                      isActive
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg scale-105'
                        : 'text-gray-700 hover:bg-purple-100 hover:scale-102'
                    }`}
                  >
                    <Icon className={`w-6 h-6 flex-shrink-0 ${isActive ? 'text-white' : 'text-purple-600 group-hover:scale-110 transition-transform'}`} />
                    <span className={`font-semibold ${isActive ? 'text-white' : 'text-sm group-hover:text-purple-700'}`}>
                      {item.label}
                    </span>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t-2 border-purple-200 bg-white flex-shrink-0">
        <div className="text-center text-xs text-gray-500">
          <p className="font-semibold text-purple-600">Smart Quality Prediction System</p>
          <p className="mt-1">© 2025 SPC Solution</p>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-gray-100">
        <Sidebar />

        {/* Main Content */}
        <div className="flex-1 overflow-auto ml-80">
          <Routes>
            {/* 기본 기능 */}
            <Route path="/" element={<DashboardPage />} />
            <Route path="/production-monitoring" element={<ProductionMonitoringPage />} />
            <Route path="/qcost-dashboard" element={<QCostDashboardPage />} />

            {/* 품질코스트 관리 */}
            <Route path="/qcost-classification" element={<QCostClassificationPage />} />
            <Route path="/qcost-collection" element={<QCostCollectionPage />} />
            <Route path="/copq-analysis" element={<COPQAnalysisPage />} />
            <Route path="/qcost-report" element={<QCostReport />} />

            {/* 검수 관리 */}
            <Route path="/inspection-process" element={<InspectionProcessDesignPage />} />
            <Route path="/inspection-standards" element={<InspectionStandardsPage />} />
            <Route path="/inspection-methods" element={<InspectionMethodsPage />} />

            {/* SPC & 분석 */}
            <Route path="/spc-chart" element={<SPCChartPage />} />
            <Route path="/capability" element={<ProcessCapabilityPage />} />
            <Route path="/data-entry" element={<DataEntryPage />} />
            <Route path="/run-rules" element={<RunRuleAnalysisPage />} />
            <Route path="/advanced-charts" element={<AdvancedChartsPage />} />
            <Route path="/quality-issues" element={<QualityIssuesPage />} />

            {/* 품질보증 & AI */}
            <Route path="/qa-system" element={<QASystemPage />} />
            <Route path="/ai-analysis" element={<AIAnalysisPage />} />
            <Route path="/chatbot" element={<ChatbotPage />} />

            {/* 고급 기능 */}
            <Route path="/work-orders" element={<WorkOrderManagementPage />} />
            <Route path="/six-sigma" element={<SixSigmaDashboardPage />} />
            <Route path="/six-sigma/tools" element={<SixSigmaToolsPage />} />
            <Route path="/benchmarks" element={<BenchmarksPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/master-data" element={<MasterDataDashboardPage />} />
            <Route path="/master-data/items" element={<MasterDataItemsPage />} />
            <Route path="/master-data/processes" element={<MasterDataProcessesPage />} />
            <Route path="/master-data/characteristics" element={<MasterDataCharacteristicsPage />} />
            <Route path="/master-data/instruments" element={<MasterDataInstrumentsPage />} />
            <Route path="/master-data/systems" element={<MasterDataSystemsPage />} />
            <Route path="/master-data/standards" element={<MasterDataStandardsPage />} />
            <Route path="/master-data/sync" element={<MasterDataSyncPage />} />

            {/* 설비 관리 */}
            <Route path="/equipment-master" element={<EquipmentMasterPage />} />
            <Route path="/equipment-parts" element={<EquipmentPartsPage />} />
            <Route path="/equipment-manual" element={<EquipmentManualPage />} />
            <Route path="/equipment-repair" element={<EquipmentRepairHistoryPage />} />
            <Route path="/preventive-maintenance" element={<PreventiveMaintenancePage />} />
            <Route path="/predictive-maintenance" element={<PredictiveMaintenancePage />} />

            {/* 치공구 관리 */}
            <Route path="/tool-master" element={<ToolMasterPage />} />
            <Route path="/tool-repair" element={<ToolRepairHistoryPage />} />
            <Route path="/tool-prediction" element={<ToolPredictionPage />} />
          </Routes>
        </div>

        {/* 실시간 알림 컴포넌트 - WebSocket 미구현으로 비활성화 */}
        {/* <RealtimeNotifications /> */}
      </div>
    </Router>
  );
}

export default App;

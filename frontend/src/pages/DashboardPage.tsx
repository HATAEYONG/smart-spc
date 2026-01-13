import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/Tabs';
import {
  DollarSign,
  TrendingUp,
  AlertTriangle,
  FileText,
  Sparkles,
  BarChart3,
  AlertCircle,
  Download,
  Eye,
  Plus
} from 'lucide-react';
import { AIResultPanel } from '../components/common';
import {
  BarChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { dashboardService } from '../services/dashboardService';
import { DashboardSummaryDTO } from '../types/dashboard';

interface DashboardData {
  copq: {
    total: number;
    rate: number;
    change: number;
  };
  oosCount: {
    total: number;
    change: number;
  };
  topDefects: Array<{
    defect: string;
    count: number;
    cost: number;
  }>;
  aiInsights: Array<{
    id: string;
    title: string;
    summary: string;
    priority: 'high' | 'medium' | 'low';
    confidence: number;
    rationale: string[];
    assumptions: string[];
    risks: Array<{
      risk: string;
      probability: string;
      mitigation: string;
    }>;
  }>;
  spcAlerts: Array<{
    id: string;
    date: string;
    type: string;
    severity: 'high' | 'medium' | 'low';
    description: string;
  }>;
}

interface AlertDTO {
  event_id: string;
  type: string;
  severity: number;
  title: string;
  description: string;
  created_at?: string;
}

interface AIInsightDTO {
  ai_id: string;
  period: string;
  title: string;
  summary: string;
  confidence: number;
  insight_type: string;
  actionable: boolean;
}

interface DashboardSummaryDTO {
  period: string;
  kpis: {
    copq_rate: number;
    total_copq: number;
    total_qcost: number;
    oos_count: number;
    spc_open_events: number;
  };
  top_defects: Array<{
    defect: string;
    count: number;
    cost: number;
  }>;
  alerts: AlertDTO[];
  ai_insights: AIInsightDTO[];
}

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPeriod, setCurrentPeriod] = useState(
    new Date().toISOString().slice(0, 7) // YYYY-MM format
  );

  useEffect(() => {
    fetchDashboardData();
  }, [currentPeriod]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await dashboardService.getSummary(currentPeriod);

      if (!response.ok || !response.data) {
        throw new Error(response.error || '대시보드 데이터를 불러오는데 실패했습니다.');
      }

      const apiData = response.data;

      // API 데이터를 UI 형식으로 변환
      const transformedData: DashboardData = {
        copq: {
          total: apiData.kpis.total_copq,
          rate: apiData.kpis.copq_rate * 100, // 소수를 퍼센트로 변환
          change: 0, // API에 없으면 0으로 처리
        },
        oosCount: {
          total: apiData.kpis.oos_count,
          change: 0,
        },
        topDefects: apiData.top_defects.map(d => ({
          defect: d.defect,
          count: d.count,
          cost: d.cost,
        })),
        aiInsights: apiData.ai_insights.map(insight => ({
          id: insight.ai_id,
          title: insight.title,
          summary: insight.summary,
          priority: insight.insight_type === 'OPTIMIZATION' ? 'high' : 'medium',
          confidence: insight.confidence,
          rationale: [insight.summary], // 요약을 근거로 사용
          assumptions: [],
          risks: [],
        })),
        spcAlerts: apiData.alerts.map(alert => {
          // 심각도 변환 (1-5 -> low/medium/high)
          let severity: 'high' | 'medium' | 'low' = 'low';
          if (alert.severity >= 4) severity = 'high';
          else if (alert.severity >= 3) severity = 'medium';

          return {
            id: alert.event_id,
            date: alert.created_at || new Date().toISOString().split('T')[0],
            type: alert.type,
            severity,
            description: alert.title || alert.description,
          };
        }),
      };

      setData(transformedData);
    } catch (err: any) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err.message || '데이터를 불러오는데 실패했습니다.');

      // API 실패시 샘플 데이터 표시 (개발용)
      setData({
        copq: {
          total: 41000000,
          rate: 3.42,
          change: 0,
        },
        oosCount: {
          total: 18,
          change: 0,
        },
        topDefects: [
          { defect: '스크래치', count: 61, cost: 8000000 },
          { defect: '치수불량', count: 45, cost: 5000000 },
          { defect: '이물', count: 28, cost: 2000000 },
          { defect: '색상불량', count: 15, cost: 1000000 },
          { defect: '기타', count: 12, cost: 500000 },
        ],
        aiInsights: [
          {
            id: 'ai-001',
            title: 'COPQ 주요 원인 분석',
            summary: '치수불량이 전체 COPQ의 40% 차지. CNC 가공 공정에서 온도 보정 주기를 단축할 것을 권장합니다.',
            priority: 'high',
            confidence: 0.86,
            rationale: ['치수불량이 전체 COPQ의 40% 차지', 'CNC 가공 공정 개선 필요'],
            assumptions: ['온도 보정 효과 가정'],
            risks: [],
          },
          {
            id: 'ai-002',
            title: '세척 공정 개선 효과',
            summary: '세척 시간 연장으로 이물 부착률이 15% 감소했습니다.',
            priority: 'medium',
            confidence: 0.92,
            rationale: ['이물 부착률 15% 감소'],
            assumptions: [],
            risks: [],
          },
        ],
        spcAlerts: [
          { id: 'evt-001', date: '2026-01-14', type: 'TREND', severity: 'high', description: '내경 추세 발생' },
          { id: 'evt-002', date: '2026-01-14', type: 'OOS', severity: 'high', description: '외경 규격 이탈' },
          { id: 'evt-003', date: '2026-01-14', type: 'RULE_1', severity: 'medium', description: '3σ 벗어남' },
        ],
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg">로딩 중...</div>
      </div>
    );
  }

  if (!data) return null;

  // Pareto 데이터 준비
  const totalCost = data.topDefects.reduce((sum, d) => sum + d.cost, 0);
  let cumulativeCost = 0;
  const paretoData = data.topDefects.map((defect, idx) => {
    cumulativeCost += defect.cost;
    return {
      name: defect.defect,
      cost: defect.cost,
      count: defect.count,
      cumulative: Number(((cumulativeCost / totalCost) * 100).toFixed(1)),
    };
  });

  const colors = ['#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e'];

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">통합 대시보드</h1>
          <p className="text-sm text-gray-500 mt-1">
            {new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' })}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
           월간 리포트 생성
          </Button>
          <Button variant="outline">
            <Eye className="w-4 h-4 mr-2" />
            경보 상세
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4 mr-2" />
            CAPA 생성
          </Button>
        </div>
      </div>

      {/* 위젯 영역 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* COPQ 금액 */}
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-purple-100">
              COPQ (월간)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline justify-between">
              <div className="text-3xl font-bold">
                ₩{(data.copq.total / 10000).toFixed(0)}만
              </div>
              <Badge
                variant={data.copq.change < 0 ? 'default' : 'destructive'}
                className={
                  data.copq.change < 0
                    ? 'bg-white/20 text-white hover:bg-white/30'
                    : 'bg-red-500 text-white hover:bg-red-600'
                }
              >
                {data.copq.change > 0 ? '+' : ''}
                {data.copq.change}%
              </Badge>
            </div>
            <p className="text-xs text-purple-100 mt-2">전월 대비</p>
          </CardContent>
        </Card>

        {/* COPQ Rate */}
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-blue-100">
              COPQ Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline justify-between">
              <div className="text-3xl font-bold">{data.copq.rate}%</div>
              <Badge className="bg-white/20 text-white hover:bg-white/30">
                목표: 3.0%
              </Badge>
            </div>
            <p className="text-xs text-blue-100 mt-2">대 매출액</p>
          </CardContent>
        </Card>

        {/* OOS 건수 */}
        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-orange-100">
              OOS 건수
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline justify-between">
              <div className="text-3xl font-bold">{data.oosCount.total}건</div>
              <Badge
                variant={data.oosCount.change < 0 ? 'default' : 'destructive'}
                className={
                  data.oosCount.change < 0
                    ? 'bg-white/20 text-white hover:bg-white/30'
                    : 'bg-red-500 text-white hover:bg-red-600'
                }
              >
                {data.oosCount.change > 0 ? '+' : ''}
                {data.oosCount.change}건
              </Badge>
            </div>
            <p className="text-xs text-orange-100 mt-2">전월 대비</p>
          </CardContent>
        </Card>

        {/* 주요 불량 TOP3 */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-600" />
              주요 불량 TOP3
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.topDefects.map((defect, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">{defect.defect}</span>
                  <Badge variant="secondary">{defect.count}건</Badge>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">불량 건수 기준</p>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 영역 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 왼쪽: Pareto + SPC 경보 타임라인 */}
        <div className="lg:col-span-2 space-y-6">
          {/* Pareto 차트 미리보기 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-600" />
                불량/코스트 Pareto 분석
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={paretoData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="name"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    interval={0}
                  />
                  <YAxis yAxisId="left" orientation="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip
                    formatter={(value: number, name: string) => {
                      if (name === '누적 비율') {
                        return [`${value}%`, name];
                      }
                      return [`₩${value.toLocaleString()}`, name];
                    }}
                  />
                  <Legend />
                  <Bar
                    yAxisId="left"
                    dataKey="cost"
                    name="불량 코스트"
                    fill="#8b5cf6"
                  >
                    {paretoData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                    ))}
                  </Bar>
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="cumulative"
                    name="누적 비율"
                    stroke="#ef4444"
                    strokeWidth={3}
                    dot={{ fill: '#ef4444', r: 4 }}
                  />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-5 gap-2 text-xs">
                {paretoData.map((item, idx) => (
                  <div key={item.name} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                    <div
                      className="w-3 h-3 rounded"
                      style={{ backgroundColor: colors[idx] }}
                    ></div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{item.name}</div>
                      <div className="text-gray-500">
                        {item.count}건 · {item.cumulative}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* SPC 경보 타임라인 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-600" />
                SPC 경보 타임라인 (최근 7일)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {data.spcAlerts.map((alert) => (
                  <div
                    key={alert.id}
                    className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
                  >
                    <div className="text-xs text-gray-500 w-24">
                      {new Date(alert.date).toLocaleDateString('ko-KR', {
                        month: '2-digit',
                        day: '2-digit',
                      })}
                    </div>
                    <Badge
                      variant={
                        alert.severity === 'high'
                          ? 'destructive'
                          : alert.severity === 'medium'
                          ? 'default'
                          : 'secondary'
                      }
                      className="shrink-0"
                    >
                      {alert.type}
                    </Badge>
                    <span className="text-sm text-gray-700 flex-1">
                      {alert.description}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 오른쪽: AI 인사이트 카드 */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-purple-600" />
            <h2 className="text-lg font-bold text-gray-900">AI 인사이트</h2>
            <Badge variant="outline">{data.aiInsights.length}개</Badge>
          </div>

          {data.aiInsights.map((insight) => (
            <AIResultPanel
              key={insight.id}
              rationale={insight.rationale}
              assumptions={insight.assumptions}
              risks={insight.risks}
              confidence={insight.confidence}
              className="cursor-pointer hover:shadow-md transition-shadow"
            />
          ))}

          {data.aiInsights.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center text-gray-500">
                <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>AI 인사이트가 없습니다</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

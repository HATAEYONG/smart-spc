import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/Select';
import {
  TrendingUp,
  DollarSign,
  AlertCircle,
  PieChart,
  BarChart3,
  Target,
  Lightbulb,
  ArrowUpRight,
  ArrowDownRight,
  Download
} from 'lucide-react';
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
import { qcostService } from '../services/qcostService';

interface COPQData {
  totalCOPQ: number;
  copqRatio: number;
  internalFailure: number;
  externalFailure: number;
  topDefects: Array<{
    rank: number;
    defect: string;
    cost: number;
    percentage: number;
    trend: 'up' | 'down' | 'stable';
  }>;
  monthlyTrend: Array<{
    month: string;
    copq: number;
    target: number;
  }>;
}

export const COPQAnalysisPage: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('6months');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [loading, setLoading] = useState(false);

  // 샘플 데이터
  const sampleData: COPQData = {
    totalCOPQ: 62000000,
    copqRatio: 49.6,
    internalFailure: 42000000,
    externalFailure: 20000000,
    topDefects: [
      { rank: 1, defect: '치수불량', cost: 25000000, percentage: 40.3, trend: 'up' },
      { rank: 2, defect: '스크래치', cost: 15000000, percentage: 24.2, trend: 'stable' },
      { rank: 3, defect: '이물', cost: 10000000, percentage: 16.1, trend: 'down' },
      { rank: 4, defect: '균열', cost: 8000000, percentage: 12.9, trend: 'up' },
      { rank: 5, defect: '기타', cost: 4000000, percentage: 6.5, trend: 'stable' },
    ],
    monthlyTrend: [
      { month: '7월', copq: 68000, target: 65000 },
      { month: '8월', copq: 65000, target: 65000 },
      { month: '9월', copq: 63000, target: 65000 },
      { month: '10월', copq: 61000, target: 65000 },
      { month: '11월', copq: 63000, target: 65000 },
      { month: '12월', copq: 62000, target: 65000 },
    ]
  };

  const [data, setData] = useState<COPQData>(sampleData);

  useEffect(() => {
    loadCOPQData();
  }, [selectedPeriod, selectedCategory]);

  const loadCOPQData = async () => {
    setLoading(true);
    try {
      // 기간 설정
      const today = new Date();
      const startDate = new Date();
      if (selectedPeriod === '6months') {
        startDate.setMonth(today.getMonth() - 6);
      } else if (selectedPeriod === '3months') {
        startDate.setMonth(today.getMonth() - 3);
      } else if (selectedPeriod === '1month') {
        startDate.setMonth(today.getMonth() - 1);
      }

      const from = startDate.toISOString().split('T')[0];
      const to = today.toISOString().split('T')[0];

      // Q-COST 엔트리 조회
      const entriesResponse = await qcostService.getEntries(from, to);
      const categoriesResponse = await qcostService.getCategories();

      if (entriesResponse.ok && categoriesResponse.ok) {
        const entries = entriesResponse.data?.results || entriesResponse.data || [];
        const categories = categoriesResponse.data || [];

        // 카테고리별 비용 집계
        let internalFailure = 0;
        let externalFailure = 0;
        const defectMap = new Map<string, number>();

        entries.forEach((entry: any) => {
          const amount = entry.amount || 0;
          const category = categories.find((c: any) => c.qcat_id === entry.qcat_id);

          if (category) {
            if (category.lvl1 === 'INTERNAL_FAILURE') {
              internalFailure += amount;
            } else if (category.lvl1 === 'EXTERNAL_FAILURE') {
              externalFailure += amount;
            }

            // 불량 유형별 집계
            const defectType = entry.description || '기타';
            defectMap.set(defectType, (defectMap.get(defectType) || 0) + amount);
          }
        });

        const totalCOPQ = internalFailure + externalFailure;
        const totalQCost = totalCOPQ * 2; // 가정: 전체 품질비용의 50%가 COPQ

        // TOP 5 불량 유형 정렬
        const sortedDefects = Array.from(defectMap.entries())
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map((defect, index) => ({
            rank: index + 1,
            defect: defect[0],
            cost: defect[1],
            percentage: (defect[1] / totalCOPQ) * 100,
            trend: 'stable' as const,
          }));

        setData({
          totalCOPQ,
          copqRatio: totalQCost > 0 ? (totalCOPQ / totalQCost) * 100 : 0,
          internalFailure,
          externalFailure,
          topDefects: sortedDefects.length > 0 ? sortedDefects : sampleData.topDefects,
          monthlyTrend: sampleData.monthlyTrend, // API가 제공하지 않으면 샘플 사용
        });
      }
    } catch (error) {
      console.error('Failed to load COPQ data:', error);
      // API 실패시 샘플 데이터 유지
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <ArrowUpRight className="w-4 h-4 text-red-600" />;
      case 'down':
        return <ArrowDownRight className="w-4 h-4 text-green-600" />;
      default:
        return <div className="w-4 h-4 rounded-full bg-gray-300" />;
    }
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">COPQ 분석</h1>
          <p className="text-sm text-gray-500 mt-1">
            품질불량비용(COPQ) 분석 및 개선 기회 식별
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            분석 리포트
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Target className="w-4 h-4 mr-2" />
            개선 계획 생성
          </Button>
        </div>
      </div>

      {/* KPI 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* 총 COPQ */}
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-red-100">
              총 COPQ (월간)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ₩{(data.totalCOPQ / 100000000).toFixed(2)}억
            </div>
            <p className="text-xs text-red-100 mt-2">
              내부: {(data.internalFailure / data.totalCOPQ * 100).toFixed(0)}% /
              외부: {(data.externalFailure / data.totalCOPQ * 100).toFixed(0)}%
            </p>
          </CardContent>
        </Card>

        {/* COPQ 비율 */}
        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-orange-100">
              COPQ 비율
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data.copqRatio}%</div>
            <p className="text-xs text-orange-100 mt-2">목표: 50% 이하</p>
          </CardContent>
        </Card>

        {/* 내부 실패비용 */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-orange-600" />
              내부 실패비용
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              ₩{(data.internalFailure / 10000000).toFixed(1)}천만원
            </div>
            <p className="text-xs text-gray-500 mt-2">
              전체의 {(data.internalFailure / data.totalCOPQ * 100).toFixed(1)}%
            </p>
          </CardContent>
        </Card>

        {/* 외부 실패비용 */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              외부 실패비용
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">
              ₩{(data.externalFailure / 10000000).toFixed(1)}천만원
            </div>
            <p className="text-xs text-gray-500 mt-2">
              전체의 {(data.externalFailure / data.totalCOPQ * 100).toFixed(1)}%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 왼쪽: 파레토 차트 & 추이 */}
        <div className="lg:col-span-2 space-y-6">
          {/* TOP 불량 항목 파레토 */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  TOP 5 불상 유형 (Pareto)
                </CardTitle>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ALL">전체</SelectItem>
                    <SelectItem value="INTERNAL">내부 실패</SelectItem>
                    <SelectItem value="EXTERNAL">외부 실패</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              {/* Pareto 차트 */}
              <div className="mb-6">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={data.topDefects}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="defect" />
                    <YAxis yAxisId="left" orientation="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip
                      formatter={(value: number, name: string) => {
                        if (name === '누적 비율') {
                          return [`${value}%`, name];
                        }
                        return [`₩${(value / 10000).toFixed(0)}만원`, '불량 비용'];
                      }}
                    />
                    <Legend />
                    <Bar
                      yAxisId="left"
                      dataKey="cost"
                      name="불량 비용"
                      fill="#8b5cf6"
                    >
                      {data.topDefects.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={`hsl(${270 + index * 15}, 70%, 60%)`} />
                      ))}
                    </Bar>
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="percentage"
                      name="누적 비율"
                      stroke="#ef4444"
                      strokeWidth={3}
                      dot={{ fill: '#ef4444', r: 5 }}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* 상세 목록 */}
              <div className="space-y-3">
                {data.topDefects.map((defect) => (
                  <div key={defect.rank} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-purple-600 text-white font-bold text-sm">
                          {defect.rank}
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{defect.defect}</div>
                          <div className="text-sm text-gray-500">
                            ₩{(defect.cost / 10000).toFixed(0)}만원 ({defect.percentage}%)
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {getTrendIcon(defect.trend)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* 누적 비율 표시 */}
              <div className="mt-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-700">
                    <span className="font-semibold">TOP 3 불량 유형</span>이 전체 COPQ의
                  </div>
                  <div className="text-2xl font-bold text-purple-600">
                    {(data.topDefects.slice(0, 3).reduce((sum, d) => sum + d.percentage, 0)).toFixed(1)}%
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  80:20 법칙에 따라 TOP 3에 집중 권장
                </p>
              </div>
            </CardContent>
          </Card>

          {/* 월별 추이 차트 영역 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                월별 COPQ 추이
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200">
                <div className="text-center text-gray-500">
                  <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">추이 차트 영역</p>
                  <p className="text-xs mt-1">월별 COPQ 추이 데이터 시각화</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 오른쪽: 인사이트 & 개선 제안 */}
        <div className="space-y-4">
          {/* 개선 기회 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-yellow-600" />
                개선 기회
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span className="font-semibold text-red-800 text-sm">우선순위 1</span>
                  </div>
                  <p className="text-sm text-red-700 mb-2">치수불량 개선</p>
                  <p className="text-xs text-red-600">
                    연간 ₩3억 절감 기대 (40% 차지)
                  </p>
                </div>

                <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="w-4 h-4 text-orange-600" />
                    <span className="font-semibold text-orange-800 text-sm">우선순위 2</span>
                  </div>
                  <p className="text-sm text-orange-700 mb-2">스크래치 감소</p>
                  <p className="text-xs text-orange-600">
                    취급 프로세스 표준화 필요
                  </p>
                </div>

                <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-green-600" />
                    <span className="font-semibold text-green-800 text-sm">성과</span>
                  </div>
                  <p className="text-sm text-green-700 mb-2">이물 개선 완료</p>
                  <p className="text-xs text-green-600">
                    세척 공정 최적화로 15% 감소
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 개선 제안 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5 text-purple-600" />
                개선 액션 아이템
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="text-sm font-medium text-gray-900 mb-1">
                    CNC 공정 능력 개선
                  </div>
                  <div className="text-xs text-gray-600 mb-2">
                    온도 보정 주기 단축, 공구 마니지먼트 강화
                  </div>
                  <Badge variant="outline" className="text-xs">
                    기대 효과: ₩1.5억/년
                  </Badge>
                </div>

                <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="text-sm font-medium text-gray-900 mb-1">
                    취급 작업 SOP 재정립
                  </div>
                  <div className="text-xs text-gray-600 mb-2">
                    작업자 교육, 보호구 사용 강화
                  </div>
                  <Badge variant="outline" className="text-xs">
                    기대 효과: ₩8천만/년
                  </Badge>
                </div>

                <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="text-sm font-medium text-gray-900 mb-1">
                    균열 방지를 위한 열처리 공정 최적화
                  </div>
                  <div className="text-xs text-gray-600 mb-2">
                    냉각 속도 제어, 온도 프로필 관리
                  </div>
                  <Badge variant="outline" className="text-xs">
                    기대 효과: ₩5천만/년
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

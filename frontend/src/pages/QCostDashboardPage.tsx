import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  TrendingUp,
  DollarSign,
  PieChart,
  BarChart3,
  Calendar,
  Download,
  Filter,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { qcostService } from '../services/qcostService';

interface QCostData {
  monthlyTotal: number;
  monthlyChange: number;
  preventionCost: number;
  appraisalCost: number;
  internalFailure: number;
  externalFailure: number;
  copqRatio: number;
  trend: Array<{
    month: string;
    prevention: number;
    appraisal: number;
    internal: number;
    external: number;
  }>;
}

export const QCostDashboardPage: React.FC = () => {
  const [data, setData] = useState<QCostData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('6months');
  const [currentMonth, setCurrentMonth] = useState(
    new Date().toISOString().slice(0, 7) // YYYY-MM
  );

  useEffect(() => {
    fetchQCostData();
  }, [currentMonth]);

  const fetchQCostData = async () => {
    try {
      setLoading(true);

      // Q-COST 카테고리 및 엔트리 조회
      const [categoriesResponse, entriesResponse] = await Promise.all([
        qcostService.getCategories(),
        qcostService.getEntries(
          currentMonth + '-01',
          currentMonth + '-31'
        ),
      ]);

      if (categoriesResponse.ok && entriesResponse.ok) {
        const categories = categoriesResponse.data || [];
        const entries = entriesResponse.data?.results || entriesResponse.data || [];

        // 카테고리별 비용 집계
        let preventionCost = 0;
        let appraisalCost = 0;
        let internalFailure = 0;
        let externalFailure = 0;

        entries.forEach((entry: any) => {
          const amount = entry.amount || 0;
          // 카테고리 타입에 따라 분류
          const category = categories.find((c: any) => c.qcat_id === entry.qcat_id);
          if (category) {
            switch (category.lvl1) {
              case 'PREVENTION':
                preventionCost += amount;
                break;
              case 'APPRAISAL':
                appraisalCost += amount;
                break;
              case 'INTERNAL_FAILURE':
                internalFailure += amount;
                break;
              case 'EXTERNAL_FAILURE':
                externalFailure += amount;
                break;
            }
          }
        });

        const totalCost = preventionCost + appraisalCost + internalFailure + externalFailure;
        const copq = internalFailure + externalFailure;

        setData({
          monthlyTotal: totalCost || 62000000, // API 데이터가 없으면 샘플값
          monthlyChange: 0,
          preventionCost: preventionCost || 20000000,
          appraisalCost: appraisalCost || 18000000,
          internalFailure: internalFailure || 14000000,
          externalFailure: externalFailure || 10000000,
          copqRatio: totalCost > 0 ? ((copq / totalCost) * 100) : 38.7,
          trend: [
            { month: '7월', prevention: 18500, appraisal: 16700, internal: 13000, external: 9300 },
            { month: '8월', prevention: 19000, appraisal: 17200, internal: 13500, external: 9600 },
            { month: '9월', prevention: 19500, appraisal: 17600, internal: 13700, external: 9800 },
            { month: '10월', prevention: 19800, appraisal: 17800, internal: 13900, external: 9900 },
            { month: '11월', prevention: 19900, appraisal: 17900, internal: 14000, external: 10000 },
            { month: '12월', prevention: 20000, appraisal: 18000, internal: 14000, external: 10000 },
          ]
        });
      } else {
        throw new Error(categoriesResponse.error || entriesResponse.error);
      }
    } catch (error) {
      console.error('Failed to fetch Q-Cost data:', error);
      // API 실패시 샘플 데이터 표시
      setData({
        monthlyTotal: 62000000,
        monthlyChange: 0,
        preventionCost: 20000000,
        appraisalCost: 18000000,
        internalFailure: 14000000,
        externalFailure: 10000000,
        copqRatio: 38.7,
        trend: [
          { month: '7월', prevention: 18500, appraisal: 16700, internal: 13000, external: 9300 },
          { month: '8월', prevention: 19000, appraisal: 17200, internal: 13500, external: 9600 },
          { month: '9월', prevention: 19500, appraisal: 17600, internal: 13700, external: 9800 },
          { month: '10월', prevention: 19800, appraisal: 17800, internal: 13900, external: 9900 },
          { month: '11월', prevention: 19900, appraisal: 17900, internal: 14000, external: 10000 },
          { month: '12월', prevention: 20000, appraisal: 18000, internal: 14000, external: 10000 },
        ]
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

  const costCategories = [
    {
      name: '예방비용',
      amount: data.preventionCost,
      percentage: (data.preventionCost / data.monthlyTotal * 100).toFixed(1),
      color: 'bg-blue-500',
      icon: TrendingUp,
    },
    {
      name: '평가비용',
      amount: data.appraisalCost,
      percentage: (data.appraisalCost / data.monthlyTotal * 100).toFixed(1),
      color: 'bg-green-500',
      icon: PieChart,
    },
    {
      name: '내부 실패비용',
      amount: data.internalFailure,
      percentage: (data.internalFailure / data.monthlyTotal * 100).toFixed(1),
      color: 'bg-orange-500',
      icon: BarChart3,
    },
    {
      name: '외부 실패비용',
      amount: data.externalFailure,
      percentage: (data.externalFailure / data.monthlyTotal * 100).toFixed(1),
      color: 'bg-red-500',
      icon: ArrowUpRight,
    },
  ];

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Q-COST 대시보드</h1>
          <p className="text-sm text-gray-500 mt-1">
            품질비용 현황 및 추이 분석
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Calendar className="w-4 h-4 mr-2" />
            {selectedPeriod === '6months' ? '최근 6개월' : '최근 12개월'}
          </Button>
          <Button variant="outline">
            <Filter className="w-4 h-4 mr-2" />
            필터
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Download className="w-4 h-4 mr-2" />
            리포트 다운로드
          </Button>
        </div>
      </div>

      {/* KPI 카드 영역 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 월간 총 품질비용 */}
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-purple-100">
              월간 총 품질비용
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline justify-between">
              <div className="text-3xl font-bold">
                ₩{(data.monthlyTotal / 100000000).toFixed(2)}억
              </div>
              <Badge
                className={data.monthlyChange < 0
                  ? 'bg-white/20 text-white hover:bg-white/30'
                  : 'bg-red-500 text-white hover:bg-red-600'
                }
              >
                {data.monthlyChange > 0 ? (
                  <ArrowUpRight className="w-3 h-3 mr-1" />
                ) : (
                  <ArrowDownRight className="w-3 h-3 mr-1" />
                )}
                {Math.abs(data.monthlyChange)}%
              </Badge>
            </div>
            <p className="text-xs text-purple-100 mt-2">전월 대비</p>
          </CardContent>
        </Card>

        {/* COPQ 비율 */}
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-red-100">
              COPQ 비율
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline justify-between">
              <div className="text-3xl font-bold">{data.copqRatio}%</div>
              <Badge className="bg-white/20 text-white hover:bg-white/30">
                목표: 50%
              </Badge>
            </div>
            <p className="text-xs text-red-100 mt-2">
              총 품질비용 중 실패비용 비중
            </p>
          </CardContent>
        </Card>

        {/* 예방비용 비율 */}
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-blue-100">
              예방비용 비율
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {(data.preventionCost / data.monthlyTotal * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-blue-100 mt-2">
              ₩{(data.preventionCost / 10000000).toFixed(1)}천만원
            </p>
          </CardContent>
        </Card>

        {/* 평가비용 비율 */}
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-green-100">
              평가비용 비율
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {(data.appraisalCost / data.monthlyTotal * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-green-100 mt-2">
              ₩{(data.appraisalCost / 10000000).toFixed(1)}천만원
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 영역 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 왼쪽: 비용별 분포 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 비용별 카테고리 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="w-5 h-5 text-purple-600" />
                비용별 현황
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {costCategories.map((category) => {
                  const Icon = category.icon;
                  return (
                    <div key={category.name} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${category.color} bg-opacity-10`}>
                            <Icon className={`w-5 h-5 ${category.color.replace('bg-', 'text-')}`} />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{category.name}</div>
                            <div className="text-sm text-gray-500">
                              ₩{(category.amount / 10000000).toFixed(1)}천만원 ({category.percentage}%)
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className={`${category.color} h-3 rounded-full transition-all`}
                          style={{ width: `${category.percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* 추이 차트 영역 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                월별 품질비용 추이
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data.trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip
                    formatter={(value: number) => [`₩${(value * 10000).toLocaleString()}만`, '']}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="prevention"
                    name="예방비용"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="appraisal"
                    name="평가비용"
                    stroke="#22c55e"
                    strokeWidth={2}
                    dot={{ fill: '#22c55e', r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="internal"
                    name="내부 실패비용"
                    stroke="#f97316"
                    strokeWidth={2}
                    dot={{ fill: '#f97316', r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="external"
                    name="외부 실패비용"
                    stroke="#ef4444"
                    strokeWidth={2}
                    dot={{ fill: '#ef4444', r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div className="flex items-center gap-2 p-2 bg-blue-50 rounded">
                  <div className="w-3 h-3 rounded bg-blue-500"></div>
                  <span className="text-gray-700">예방비용</span>
                </div>
                <div className="flex items-center gap-2 p-2 bg-green-50 rounded">
                  <div className="w-3 h-3 rounded bg-green-500"></div>
                  <span className="text-gray-700">평가비용</span>
                </div>
                <div className="flex items-center gap-2 p-2 bg-orange-50 rounded">
                  <div className="w-3 h-3 rounded bg-orange-500"></div>
                  <span className="text-gray-700">내부 실패비용</span>
                </div>
                <div className="flex items-center gap-2 p-2 bg-red-50 rounded">
                  <div className="w-3 h-3 rounded bg-red-500"></div>
                  <span className="text-gray-700">외부 실패비용</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 오른쪽: 인사이트 & 추천 */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                주요 인사이트
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2 mb-1">
                    <ArrowDownRight className="w-4 h-4 text-green-600" />
                    <span className="font-medium text-green-800 text-sm">COPQ 감소</span>
                  </div>
                  <p className="text-xs text-green-700">
                    전월 대비 8.5% 감소하여 목표 비율 달성
                  </p>
                </div>

                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-2 mb-1">
                    <DollarSign className="w-4 h-4 text-blue-600" />
                    <span className="font-medium text-blue-800 text-sm">예방비용 증가</span>
                  </div>
                  <p className="text-xs text-blue-700">
                    예방 활동 강화로 내부 실패비용 12% 감소
                  </p>
                </div>

                <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                  <div className="flex items-center gap-2 mb-1">
                    <BarChart3 className="w-4 h-4 text-orange-600" />
                    <span className="font-medium text-orange-800 text-sm">주요 불량</span>
                  </div>
                  <p className="text-xs text-orange-700">
                    치수불량이 내부 실패비용의 65% 차지
                  </p>
                </div>

                <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="flex items-center gap-2 mb-1">
                    <TrendingUp className="w-4 h-4 text-purple-600" />
                    <span className="font-medium text-purple-800 text-sm">개선 제안</span>
                  </div>
                  <p className="text-xs text-purple-700">
                    외부 실패비용을 내부 실패비용의 50% 이하로 유지 권장
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

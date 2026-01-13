import React, { useState } from 'react';
import { FileText, Calendar, Download, Filter, BarChart3, AlertTriangle, CheckCircle } from 'lucide-react';
import { api } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface ReportSummary {
  total_products: number;
  total_measurements: number;
  out_of_spec_rate: number;
  out_of_control_rate: number;
  total_alerts: number;
  critical_alerts: number;
  resolution_rate: number;
}

interface ProductDetail {
  product_code: string;
  product_name: string;
  statistics: {
    total_measurements: number;
    average: number;
    std_dev: number;
    out_of_spec_rate: number;
  };
  capability: {
    cp?: number;
    cpk?: number;
    analyzed_at?: string;
  };
}

interface ReportData {
  report_type: string;
  period: {
    start: string;
    end: string;
    formatted: string;
  };
  generated_at: string;
  summary: ReportSummary;
  product_details: ProductDetail[];
  alerts_summary: any;
  capability_analysis: any;
  recommendations: any[];
}

const ReportsPage: React.FC = () => {
  const [reportType, setReportType] = useState<'DAILY' | 'WEEKLY' | 'MONTHLY' | 'CUSTOM'>('DAILY');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [format, setFormat] = useState<'json' | 'markdown'>('json');
  const [selectedProducts, setSelectedProducts] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [markdownContent, setMarkdownContent] = useState('');

  // 제품 목록 로드
  const [products, setProducts] = useState<any[]>([]);
  const [productsLoaded, setProductsLoaded] = useState(false);

  React.useEffect(() => {
    const loadProducts = async () => {
      try {
        const response = await api.get('/products/');
        setProducts(response.data.results || response.data);
        setProductsLoaded(true);
      } catch (error) {
        console.error('Failed to load products:', error);
      }
    };
    loadProducts();
  }, []);

  const handleGenerateReport = async () => {
    setIsLoading(true);
    try {
      const payload: any = {
        report_type: reportType,
        format: format,
      };

      if (reportType === 'CUSTOM') {
        payload.start_date = new Date(startDate).toISOString();
        payload.end_date = new Date(endDate).toISOString();
        if (selectedProducts.length > 0) {
          payload.product_ids = selectedProducts;
        }
      } else {
        payload.start_date = new Date(startDate).toISOString();
      }

      const response = await api.post('/reports/generate/', payload);
      setReportData(response.data.data || response.data);

      if (format === 'markdown' && response.data.content) {
        setMarkdownContent(response.data.content);
      }

      setShowPreview(true);
    } catch (error: any) {
      console.error('Report generation failed:', error);
      alert('보고서 생성에 실패했습니다: ' + (error.response?.data?.error || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadMarkdown = () => {
    if (!markdownContent) return;

    const blob = new Blob([markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SPC_${reportType}_Report_${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadJSON = () => {
    if (!reportData) return;

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SPC_${reportType}_Report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getCpkGrade = (cpk: number) => {
    if (cpk >= 2.0) return { grade: 'Superior', color: 'text-green-600 bg-green-50' };
    if (cpk >= 1.67) return { grade: 'Excellent', color: 'text-blue-600 bg-blue-50' };
    if (cpk >= 1.33) return { grade: 'Good', color: 'text-indigo-600 bg-indigo-50' };
    if (cpk >= 1.0) return { grade: 'Adequate', color: 'text-amber-600 bg-amber-50' };
    return { grade: 'Inadequate', color: 'text-red-600 bg-red-50' };
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <FileText className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">품질 보고서</h1>
                <p className="text-sm text-gray-600">일일/주간/월간 품질 리포트 생성</p>
              </div>
            </div>
          </div>
        </div>

        {/* Report Configuration */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Filter className="w-5 h-5" />
            보고서 설정
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Report Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                보고서 유형
              </label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="DAILY">일일 보고서</option>
                <option value="WEEKLY">주간 보고서</option>
                <option value="MONTHLY">월간 보고서</option>
                <option value="CUSTOM">사용자 정의</option>
              </select>
            </div>

            {/* Start Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                시작일
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            {/* End Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {reportType === 'CUSTOM' ? '종료일' : '기준일'}
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                disabled={reportType !== 'CUSTOM'}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
            </div>

            {/* Format */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                내보내기 형식
              </label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="json">JSON</option>
                <option value="markdown">Markdown</option>
              </select>
            </div>
          </div>

          {/* Product Selection (for Custom reports) */}
          {reportType === 'CUSTOM' && productsLoaded && (
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                대상 제품 (선택사항, 미선택시 전체)
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                {products.map((product) => (
                  <label key={product.id} className="flex items-center space-x-2 text-sm">
                    <input
                      type="checkbox"
                      checked={selectedProducts.includes(product.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedProducts([...selectedProducts, product.id]);
                        } else {
                          setSelectedProducts(selectedProducts.filter(id => id !== product.id));
                        }
                      }}
                      className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                    />
                    <span className="text-gray-700">{product.product_code}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Generate Button */}
          <div className="mt-6 flex justify-end space-x-3">
            <button
              onClick={handleGenerateReport}
              disabled={isLoading}
              className="px-6 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <BarChart3 className="w-5 h-5" />
              <span>{isLoading ? '생성 중...' : '보고서 생성'}</span>
            </button>
          </div>
        </div>

        {/* Report Preview */}
        {showPreview && reportData && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">보고서 미리보기</h2>
                <p className="text-sm text-gray-600">{reportData.period.formatted}</p>
              </div>
              <div className="flex space-x-2">
                {format === 'markdown' && (
                  <button
                    onClick={handleDownloadMarkdown}
                    className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>Markdown 다운로드</span>
                  </button>
                )}
                <button
                  onClick={handleDownloadJSON}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>JSON 다운로드</span>
                </button>
              </div>
            </div>

            {/* Summary Statistics - KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-blue-100">
                    전체 제품
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {reportData.summary.total_products}
                  </div>
                  <p className="text-xs text-blue-100 mt-2">분석 대상</p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-purple-100">
                    전체 측정값
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {reportData.summary.total_measurements.toLocaleString()}
                  </div>
                  <p className="text-xs text-purple-100 mt-2">데이터 포인트</p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-amber-100">
                    규격 외률
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {reportData.summary.out_of_spec_rate}%
                  </div>
                  <p className="text-xs text-amber-100 mt-2">
                    {reportData.summary.out_of_spec_rate < 2 ? '양호' : '개선 필요'}
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-red-100">
                    총 경고
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-baseline justify-between">
                    <div className="text-3xl font-bold">
                      {reportData.summary.total_alerts}
                    </div>
                    <Badge className="bg-white/20 text-white hover:bg-white/30">
                      긴급: {reportData.summary.critical_alerts}
                    </Badge>
                  </div>
                  <p className="text-xs text-red-100 mt-2">
                    해결률: {reportData.summary.resolution_rate}%
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Cpk Distribution Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-purple-600" />
                    제품별 Cpk 분포
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={reportData.product_details.map(p => ({
                      name: p.product_code,
                      cpk: p.capability.cpk || 0,
                      target: 1.33,
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <ReferenceLine y={1.33} stroke="#22c55e" strokeDasharray="5 5" label="목표 (1.33)" />
                      <Bar dataKey="cpk" fill="#8b5cf6" name="Cpk" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Alert Status Pie Chart */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-orange-600" />
                    경고 상태 분포
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: '긴급', value: reportData.summary.critical_alerts },
                          { name: '일반', value: reportData.summary.total_alerts - reportData.summary.critical_alerts },
                          { name: '해결됨', value: Math.floor(reportData.summary.total_alerts * (reportData.summary.resolution_rate / 100)) },
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        <Cell fill="#ef4444" />
                        <Cell fill="#f97316" />
                        <Cell fill="#22c55e" />
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Out of Spec Rate Trend */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  제품별 불량률 현황
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={reportData.product_details.map(p => ({
                    name: p.product_code,
                    oos: p.statistics.out_of_spec_rate,
                    target: 2.0,
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis label={{ value: '불량률 (%)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip formatter={(value: number) => [`${value}%`, '불량률']} />
                    <Legend />
                    <ReferenceLine y={2.0} stroke="#ef4444" strokeDasharray="5 5" label="목표 (2%)" />
                    <Bar dataKey="oos" fill="#f97316" name="불량률" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Product Details Table */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>제품별 상세 분석</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">제품</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">측정 개수</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">평균</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">표준편차</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">불량률</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Cpk</th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">등급</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {reportData.product_details.map((product, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{product.product_name}</div>
                            <div className="text-sm text-gray-500">{product.product_code}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                            {product.statistics.total_measurements.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                            {product.statistics.average?.toFixed(4)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                            {product.statistics.std_dev?.toFixed(4)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                            <span className={product.statistics.out_of_spec_rate > 1 ? 'text-red-600 font-medium' : 'text-gray-900'}>
                              {product.statistics.out_of_spec_rate.toFixed(2)}%
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                            {product.capability.cpk?.toFixed(3) || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            {product.capability.cpk ? (
                              <Badge className={getCpkGrade(product.capability.cpk).color}>
                                {getCpkGrade(product.capability.cpk).grade}
                              </Badge>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Recommendations */}
            {reportData.recommendations.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-amber-500" />
                    개선 권장사항
                  </CardTitle>
                </CardHeader>
                <CardContent>
                <div className="space-y-4">
                  {reportData.recommendations.map((rec, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">{rec.product_name}</h4>
                      <div className="space-y-2">
                        {rec.recommendations.map((item: any, itemIdx: number) => (
                          <div key={itemIdx} className="bg-amber-50 rounded p-3">
                            <div className="flex items-start gap-2">
                              {item.priority === 'urgent' && <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5" />}
                              {item.priority === 'high' && <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5" />}
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900">{item.message}</p>
                                <ul className="mt-2 space-y-1">
                                  {item.actions.map((action: string, actionIdx: number) => (
                                    <li key={actionIdx} className="text-sm text-gray-600 flex items-center gap-2">
                                      <CheckCircle className="w-3 h-3 text-green-500" />
                                      {action}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
export { ReportsPage };

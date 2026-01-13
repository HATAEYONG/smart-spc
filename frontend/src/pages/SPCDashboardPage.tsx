import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, TrendingUp, CheckCircle } from 'lucide-react';
import api from '../services/apiSimple';

interface Product {
  id: number;
  product_code: string;
  product_name: string;
  usl: number;
  lsl: number;
  target_value: number;
  unit: string;
}

interface QualityAlert {
  id: number;
  product_code: string;
  alert_type: string;
  priority: number;
  status: string;
  message: string;
  created_at: string;
}

const SPCDashboardPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [productSummary, setProductSummary] = useState<any>(null);
  const [alerts, setAlerts] = useState<QualityAlert[]>([]);
  const [alertStats, setAlertStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProducts();
    loadAlerts();
  }, []);

  useEffect(() => {
    if (selectedProduct) {
      loadProductSummary(selectedProduct);
    }
  }, [selectedProduct]);

  const loadProducts = async () => {
    try {
      const response = await api.get('/spc/products/');
      setProducts(response.data.results || response.data);
      if (response.data.results?.length > 0) {
        setSelectedProduct(response.data.results[0].id);
      }
    } catch (error) {
      console.error('Failed to load products:', error);
    }
  };

  const loadProductSummary = async (productId: number) => {
    try {
      const response = await api.get(`/spc/products/${productId}/summary/`);
      setProductSummary(response.data);
    } catch (error) {
      console.error('Failed to load product summary:', error);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await api.get('/spc/alerts/dashboard/');
      setAlertStats(response.data);

      const alertsResponse = await api.get('/spc/alerts/?page_size=10');
      setAlerts(alertsResponse.data.results || []);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    }
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 4: return 'bg-red-100 text-red-800 border-red-300';
      case 3: return 'bg-orange-100 text-orange-800 border-orange-300';
      case 2: return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">SPC 품질관리 대시보드</h1>
          <p className="text-gray-600 mt-2">실시간 품질 모니터링 및 통계적 공정 관리</p>
        </div>

        {/* Product Selection */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">제품 선택</label>
          <select
            value={selectedProduct || ''}
            onChange={(e) => setSelectedProduct(Number(e.target.value))}
            className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">제품을 선택하세요</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.product_code} - {product.product_name}
              </option>
            ))}
          </select>
        </div>

        {/* Summary Cards */}
        {alertStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm">전체 제품</p>
                  <p className="text-2xl font-bold text-gray-900">{products.length}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Activity className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm">총 경고</p>
                  <p className="text-2xl font-bold text-gray-900">{alertStats.total || 0}</p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm">긴급 경고</p>
                  <p className="text-2xl font-bold text-gray-900">{alertStats.by_priority?.urgent || 0}</p>
                </div>
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm">해결됨</p>
                  <p className="text-2xl font-bold text-gray-900">{alertStats.by_status?.resolved || 0}</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Product Summary & Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Product Summary */}
          {productSummary && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">제품 품질 요약</h2>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">제품 코드</p>
                  <p className="text-lg font-semibold">{productSummary.product_code}</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-gray-600">제품명</p>
                  <p className="text-lg font-semibold">{productSummary.product_name}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-gray-600">총 측정값</p>
                    <p className="text-lg font-semibold">{productSummary.statistics?.total_measurements || 0}</p>
                  </div>
                  <div className="p-4 bg-amber-50 rounded-lg">
                    <p className="text-sm text-gray-600">규격 이탈률</p>
                    <p className="text-lg font-semibold">{productSummary.statistics?.out_of_spec_rate?.toFixed(2) || 0}%</p>
                  </div>
                </div>
                {productSummary.capability?.cpk && (
                  <div className="p-4 bg-indigo-50 rounded-lg">
                    <p className="text-sm text-gray-600">공정능력 지수 (Cpk)</p>
                    <p className="text-lg font-semibold">{productSummary.capability.cpk.toFixed(3)}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Recent Alerts */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">최근 경고</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {alerts.length > 0 ? (
                alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-3 border rounded-lg ${getPriorityColor(alert.priority)}`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-semibold text-sm">{alert.alert_type}</span>
                      <span className="text-xs px-2 py-1 bg-white rounded">
                        {alert.priority === 4 ? '긴급' : alert.priority === 3 ? '높음' : alert.priority === 2 ? '보통' : '낮음'}
                      </span>
                    </div>
                    <p className="text-sm mb-2">{alert.message}</p>
                    <div className="flex justify-between items-center text-xs text-gray-600">
                      <span>{alert.product_code}</span>
                      <span>{new Date(alert.created_at).toLocaleString('ko-KR')}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
                  <p>경고가 없습니다</p>
                  <p className="text-sm mt-1">품질 상태가 양호합니다</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Products List */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">전체 제품 목록</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">제품 코드</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">제품명</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">목표값</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">USL</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">LSL</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">단위</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{product.product_code}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{product.product_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">{product.target_value}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">{product.usl}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">{product.lsl}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">{product.unit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SPCDashboardPage;
export { SPCDashboardPage };

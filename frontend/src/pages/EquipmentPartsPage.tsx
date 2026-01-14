import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import {
  Select,
  SelectItem,
} from '../components/ui/Select';
import {
  Plus,
  Edit,
  Trash2,
  Search,
  Package,
  AlertTriangle,
  Box,
  Wrench,
} from 'lucide-react';

interface Part {
  id: number;
  code: string;
  name: string;
  equipment_id: number;
  equipment_name: string;
  category: string;
  manufacturer: string;
  part_number: string;
  unit_price: number;
  stock_quantity: number;
  min_stock: number;
  max_stock: number;
  location: string;
  supplier: string;
  lead_time_days: number;
  last_restocked_date: string;
}

const MOCK_PARTS: Part[] = [
  {
    id: 1,
    code: 'PART-001',
    name: '베어링 6205',
    equipment_id: 1,
    equipment_name: 'CNC 머신 A',
    category: '회전부품',
    manufacturer: 'SKF',
    part_number: '6205-2RS',
    unit_price: 25000,
    stock_quantity: 5,
    min_stock: 10,
    max_stock: 50,
    location: '창고 A-1',
    supplier: 'SKF Korea',
    lead_time_days: 7,
    last_restocked_date: '2026-01-10',
  },
  {
    id: 2,
    code: 'PART-002',
    name: '오일 필터',
    equipment_id: 1,
    equipment_name: 'CNC 머신 A',
    category: '소모품',
    manufacturer: 'HYDAC',
    part_number: 'OF-100',
    unit_price: 45000,
    stock_quantity: 20,
    min_stock: 15,
    max_stock: 100,
    location: '창고 A-2',
    supplier: 'HYDAC Korea',
    lead_time_days: 5,
    last_restocked_date: '2026-01-12',
  },
  {
    id: 3,
    code: 'PART-003',
    name: '벨트 V-300',
    equipment_id: 4,
    equipment_name: '컨베이어 벨트 C-1',
    category: '구동부품',
    manufacturer: 'Gates',
    part_number: 'V-BELT-300',
    unit_price: 85000,
    stock_quantity: 3,
    min_stock: 8,
    max_stock: 40,
    location: '창고 B-1',
    supplier: 'Gates Korea',
    lead_time_days: 10,
    last_restocked_date: '2026-01-05',
  },
  {
    id: 4,
    code: 'PART-004',
    name: '모터 2kW',
    equipment_id: 4,
    equipment_name: '컨베이어 벨트 C-1',
    category: '전장부품',
    manufacturer: 'Siemens',
    part_number: 'MOT-2K-IND',
    unit_price: 450000,
    stock_quantity: 1,
    min_stock: 2,
    max_stock: 5,
    location: '창고 C-1',
    supplier: 'Siemens Korea',
    lead_time_days: 14,
    last_restocked_date: '2025-12-20',
  },
];

export const EquipmentPartsPage: React.FC = () => {
  const [parts, setParts] = useState<Part[]>(MOCK_PARTS);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedEquipment, setSelectedEquipment] = useState('ALL');
  const [stockStatus, setStockStatus] = useState('ALL');
  const [selectedPart, setSelectedPart] = useState<Part | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredParts = parts.filter(part => {
    const matchesSearch =
      part.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      part.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      part.part_number.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCategory = selectedCategory === 'ALL' || part.category === selectedCategory;
    const matchesEquipment = selectedEquipment === 'ALL' || part.equipment_id.toString() === selectedEquipment;

    let matchesStock = true;
    if (stockStatus === 'LOW') {
      matchesStock = part.stock_quantity <= part.min_stock;
    } else if (stockStatus === 'NORMAL') {
      matchesStock = part.stock_quantity > part.min_stock && part.stock_quantity < part.max_stock;
    } else if (stockStatus === 'OVERSTOCK') {
      matchesStock = part.stock_quantity >= part.max_stock;
    }

    return matchesSearch && matchesCategory && matchesEquipment && matchesStock;
  });

  const categories = Array.from(new Set(parts.map(p => p.category)));
  const equipments = Array.from(new Set(parts.map(p => ({ id: p.equipment_id, name: p.equipment_name }))));

  const getStockStatus = (part: Part) => {
    if (part.stock_quantity <= part.min_stock) {
      return {
        label: '부족',
        color: 'bg-red-100 text-red-800',
        icon: AlertTriangle,
      };
    } else if (part.stock_quantity >= part.max_stock) {
      return {
        label: '과잉',
        color: 'bg-blue-100 text-blue-800',
        icon: Box,
      };
    }
    return {
      label: '정상',
      color: 'bg-green-100 text-green-800',
      icon: Package,
    };
  };

  const lowStockCount = parts.filter(p => p.stock_quantity <= p.min_stock).length;
  const totalValue = parts.reduce((sum, p) => sum + (p.unit_price * p.stock_quantity), 0);

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">설비 부품 관리</h1>
          <p className="text-sm text-gray-500 mt-1">
            부품 재고 및 발주 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Package className="w-4 h-4 mr-2" />
            재고 실사
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4 mr-2" />
            신규 부품 등록
          </Button>
        </div>
      </div>

      {/* 필터 영역 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="부품명, 코드, 번호 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory} className="w-48">
              <SelectItem value="ALL">전체 카테고리</SelectItem>
              {categories.map(cat => (
                <SelectItem key={cat} value={cat}>{cat}</SelectItem>
              ))}
            </Select>
            <Select value={selectedEquipment} onValueChange={setSelectedEquipment} className="w-48">
              <SelectItem value="ALL">전체 설비</SelectItem>
              {equipments.map(eq => (
                <SelectItem key={eq.id} value={eq.id.toString()}>{eq.name}</SelectItem>
              ))}
            </Select>
            <Select value={stockStatus} onValueChange={setStockStatus} className="w-40">
              <SelectItem value="ALL">전체 재고</SelectItem>
              <SelectItem value="LOW">부족</SelectItem>
              <SelectItem value="NORMAL">정상</SelectItem>
              <SelectItem value="OVERSTOCK">과잉</SelectItem>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 요약 정보 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-purple-100 mb-1">총 부품 수</div>
            <div className="text-2xl font-bold">{parts.length}종</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-green-100 mb-1">총 재고 가치</div>
            <div className="text-2xl font-bold">₩{(totalValue / 1000000).toFixed(1)}M</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <Package className="w-4 h-4" />
              <div className="text-sm font-medium text-yellow-100">정상 재고</div>
            </div>
            <div className="text-2xl font-bold">
              {parts.filter(p => p.stock_quantity > p.min_stock && p.stock_quantity < p.max_stock).length}종
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <AlertTriangle className="w-4 h-4" />
              <div className="text-sm font-medium text-red-100">재고 부족</div>
            </div>
            <div className="text-2xl font-bold">{lowStockCount}종</div>
          </CardContent>
        </Card>
      </div>

      {/* 재고 부족 알림 */}
      {lowStockCount > 0 && (
        <Card className="border-l-4 border-red-500 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <h3 className="text-lg font-semibold text-red-900">재고 부족 부품</h3>
              <Badge className="bg-red-100 text-red-800">{lowStockCount}종</Badge>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {parts.filter(p => p.stock_quantity <= p.min_stock).map(part => (
                <div key={part.id} className="bg-white p-3 rounded-lg border border-red-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{part.name}</div>
                      <div className="text-sm text-gray-500">{part.equipment_name}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-red-600">{part.stock_quantity}</div>
                      <div className="text-xs text-gray-500">/ 최소: {part.min_stock}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 부품 목록 테이블 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="w-5 h-5 text-purple-600" />
            부품 목록
            <Badge variant="outline" className="ml-2">
              {filteredParts.length}종
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">코드</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">부품명</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">설비</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">제조사</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">재고</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">단가</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">공급사</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">관리</th>
                </tr>
              </thead>
              <tbody>
                {filteredParts.map((part) => {
                  const stockStatus = getStockStatus(part);
                  const StockIcon = stockStatus.icon;
                  return (
                    <tr
                      key={part.id}
                      className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedPart(part);
                        setIsModalOpen(true);
                      }}
                    >
                      <td className="py-3 px-4 text-sm font-mono text-gray-700">
                        {part.code}
                      </td>
                      <td className="py-3 px-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{part.name}</div>
                          <div className="text-xs text-gray-500">{part.part_number}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div>{part.equipment_name}</div>
                        <div className="text-xs text-gray-500">{part.category}</div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {part.manufacturer}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${stockStatus.color}`}>
                          <StockIcon className="w-3 h-3" />
                          {part.stock_quantity} / {part.max_stock}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm font-semibold text-gray-900">
                        ₩{part.unit_price.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div>{part.supplier}</div>
                        <div className="text-xs text-gray-500">{part.lead_time_days}일</div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedPart(part);
                              setIsModalOpen(true);
                            }}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {filteredParts.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Package className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>검색 결과가 없습니다</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 상세 모달 */}
      {isModalOpen && selectedPart && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setIsModalOpen(false)} />
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-xl font-semibold">부품 상세 정보</h3>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">부품 코드</label>
                    <p className="text-lg font-semibold text-gray-900 font-mono">{selectedPart.code}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">부품명</label>
                    <p className="text-lg font-semibold text-gray-900">{selectedPart.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">제조사</label>
                    <p className="text-gray-900">{selectedPart.manufacturer}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">부품 번호</label>
                    <p className="text-gray-900 font-mono">{selectedPart.part_number}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">카테고리</label>
                    <p className="text-gray-900">{selectedPart.category}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">적용 설비</label>
                    <p className="text-gray-900">{selectedPart.equipment_name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">현재 재고</label>
                    <p className="text-gray-900">{selectedPart.stock_quantity}개</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">단가</label>
                    <p className="text-gray-900">₩{selectedPart.unit_price.toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">보관 위치</label>
                    <p className="text-gray-900">{selectedPart.location}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">공급사</label>
                    <p className="text-gray-900">{selectedPart.supplier}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">리드타임</label>
                    <p className="text-gray-900">{selectedPart.lead_time_days}일</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">최근 입고일</label>
                    <p className="text-gray-900">{selectedPart.last_restocked_date}</p>
                  </div>
                </div>

                <div className="mt-6 flex gap-2">
                  <Button className="flex-1 bg-blue-600 hover:bg-blue-700">
                    <Wrench className="w-4 h-4 mr-2" />
                    발주 요청
                  </Button>
                  <Button variant="outline" className="flex-1">
                    <Package className="w-4 h-4 mr-2" />
                    입고 처리
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/Select';
import {
  Plus,
  Upload,
  Download,
  Search,
  Filter,
  Edit,
  Trash2,
  Calendar,
  DollarSign,
  FileText,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';
import { StatusBadge } from '../components/common';
import { qcostService } from '../services/qcostService';
import { QCostEntryDTO } from '../types/qcost';

interface QCostRecord {
  id: string;
  date: string;
  category: string; // 예방/평가/내부실패/외부실패
  subCategory: string;
  itemCode: string;
  itemName: string;
  amount: number;
  department: string;
  status: 'PENDING' | 'VERIFIED' | 'APPROVED';
  description: string;
  attachment?: string;
}

const MOCK_DATA: QCostRecord[] = [
  {
    id: '1',
    date: '2026-01-12',
    category: '내부 실패비용',
    subCategory: '재작업비',
    itemCode: 'INT-001',
    itemName: '재세척 인건비',
    amount: 1500000,
    department: '생산팀',
    status: 'APPROVED',
    description: 'CNC 가공 후 치수 불량으로 인한 재세척',
  },
  {
    id: '2',
    date: '2026-01-11',
    category: '예방비용',
    subCategory: '품질기획',
    itemCode: 'PREV-001',
    itemName: '품질시스템 설계비',
    amount: 5000000,
    department: '품질팀',
    status: 'APPROVED',
    description: 'QMS 개선 프로젝트',
  },
  {
    id: '3',
    date: '2026-01-10',
    category: '외부 실패비용',
    subCategory: '보증비용',
    itemCode: 'EXT-001',
    itemName: '고객 클레임 비용',
    amount: 3500000,
    department: '고객지원팀',
    status: 'VERIFIED',
    description: '외경 치수 불량으로 인한 클레임',
  }
];

export const QCostCollectionPage: React.FC = () => {
  const [records, setRecords] = useState<QCostRecord[]>(MOCK_DATA);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [currentMonth, setCurrentMonth] = useState(
    new Date().toISOString().slice(0, 7) // YYYY-MM
  );

  useEffect(() => {
    fetchEntries();
  }, [currentMonth]);

  const fetchEntries = async () => {
    try {
      setLoading(true);
      const response = await qcostService.getEntries(
        currentMonth + '-01',
        currentMonth + '-31'
      );

      if (response.ok && response.data) {
        const entries = response.data.results || response.data;

        // API 데이터를 UI 형식으로 변환
        const transformedRecords: QCostRecord[] = entries.map((entry: QCostEntryDTO) => ({
          id: entry.entry_id,
          date: entry.occur_dt,
          category: '-', // 카테고리 정보를 별도로 가져와야 함
          subCategory: '-',
          itemCode: '-',
          itemName: '-',
          amount: entry.amount,
          department: entry.dept_id || '-',
          status: 'APPROVED',
          description: entry.memo || '-',
          attachment: entry.evidence_file_id || undefined,
        }));

        setRecords(transformedRecords.length > 0 ? transformedRecords : MOCK_DATA);
      } else {
        throw new Error(response.error || '데이터를 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to fetch entries:', error);
      setRecords(MOCK_DATA);
    } finally {
      setLoading(false);
    }
  };

  const filteredRecords = records.filter(record => {
    const matchesSearch = searchTerm === '' ||
      record.itemName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.itemCode.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCategory = selectedCategory === 'ALL' || record.category === selectedCategory;
    const matchesStatus = selectedStatus === 'ALL' || record.status === selectedStatus;

    return matchesSearch && matchesCategory && matchesStatus;
  });

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return { label: '승인 완료', color: 'text-green-600', bgColor: 'bg-green-50' };
      case 'VERIFIED':
        return { label: '검증 완료', color: 'text-blue-600', bgColor: 'bg-blue-50' };
      case 'PENDING':
        return { label: '대기 중', color: 'text-yellow-600', bgColor: 'bg-yellow-50' };
      default:
        return { label: status, color: 'text-gray-600', bgColor: 'bg-gray-50' };
    }
  };

  const totalAmount = filteredRecords.reduce((sum, record) => sum + record.amount, 0);

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Q-COST 수집 관리</h1>
          <p className="text-sm text-gray-500 mt-1">
            품질비용 데이터 수집 및 검증
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Upload className="w-4 h-4 mr-2" />
            일괄 업로드
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            엑셀 다운로드
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4 mr-2" />
            신규 등록
          </Button>
        </div>
      </div>

      {/* 필터 영역 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="항목명 또는 코드 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="비용 카테고리" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">전체</SelectItem>
                <SelectItem value="예방비용">예방비용</SelectItem>
                <SelectItem value="평가비용">평가비용</SelectItem>
                <SelectItem value="내부 실패비용">내부 실패비용</SelectItem>
                <SelectItem value="외부 실패비용">외부 실패비용</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="상태" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">전체</SelectItem>
                <SelectItem value="PENDING">대기 중</SelectItem>
                <SelectItem value="VERIFIED">검증 완료</SelectItem>
                <SelectItem value="APPROVED">승인 완료</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline">
              <Filter className="w-4 h-4 mr-2" />
              상세 필터
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 요약 정보 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="text-sm font-medium text-purple-100 mb-1">총 금액</div>
            <div className="text-2xl font-bold">₩{(totalAmount / 100000000).toFixed(2)}억</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-500 mb-1">총 건수</div>
            <div className="text-2xl font-bold text-gray-900">{filteredRecords.length}건</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4 text-yellow-600" />
              <div className="text-sm text-gray-500">대기 중</div>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {filteredRecords.filter(r => r.status === 'PENDING').length}건
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-1">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <div className="text-sm text-gray-500">승인 완료</div>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {filteredRecords.filter(r => r.status === 'APPROVED').length}건
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 데이터 테이블 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-600" />
            품질비용 데이터 목록
            <Badge variant="outline" className="ml-2">
              {filteredRecords.length}건
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">날짜</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">카테고리</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">항목 코드</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">항목명</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">부서</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">금액</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">상태</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">관리</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((record) => {
                  const statusConfig = getStatusConfig(record.status);
                  return (
                    <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {new Date(record.date).toLocaleDateString('ko-KR')}
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="text-xs">
                          {record.category}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm font-mono text-gray-700">
                        {record.itemCode}
                      </td>
                      <td className="py-3 px-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{record.itemName}</div>
                          <div className="text-xs text-gray-500">{record.description}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{record.department}</td>
                      <td className="py-3 px-4 text-sm font-semibold text-gray-900">
                        ₩{(record.amount / 10000).toFixed(0)}만원
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusConfig.bgColor} ${statusConfig.color}`}>
                          {statusConfig.label}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-red-600 hover:text-red-700">
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

          {filteredRecords.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>데이터가 없습니다</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

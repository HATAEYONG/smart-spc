import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Dialog } from '../components/ui/Dialog';
import {
  Folder,
  FolderOpen,
  ChevronRight,
  Plus,
  Edit,
  Trash2,
  Search,
  DollarSign
} from 'lucide-react';
import { StatusBadge, VersionTag, AuditLogButton, type AuditLogEntry } from '../components/common';
import { qcostService } from '../services/qcostService';
import { QCostCategoryDTO } from '../types/qcost';

interface QCostCategory {
  id: string;
  lvl1: string;      // 예방/평가/내부실패/외부실패
  lvl2: string;      // 2단계 분류
  lvl3: string;      // 3단계 항목
  itemCode: string;
  itemName: string;
  department: string;
  glAccount: string;
  isCopq: boolean;
  unitCost?: number;
  children?: QCostCategory[];
}

const MOCK_DATA: QCostCategory[] = [
  {
    id: '1',
    lvl1: '예방비용',
    lvl2: '품질기획',
    lvl3: '품질시스템 설계',
    itemCode: 'PREV-001',
    itemName: '품질시스템 설계비',
    department: '품질팀',
    glAccount: 'GL-001',
    isCopq: false,
    unitCost: 500000,
    children: [
      {
        id: '1-1',
        lvl1: '예방비용',
        lvl2: '품질기획',
        lvl3: '공정설계',
        itemCode: 'PREV-001-01',
        itemName: '공정설계비',
        department: '생산기술팀',
        glAccount: 'GL-001-01',
        isCopq: false,
      }
    ]
  },
  {
    id: '2',
    lvl1: '평가비용',
    lvl2: '검사비용',
    lvl3: '검사인건비',
    itemCode: 'APP-001',
    itemName: '검사원 인건비',
    department: '검사팀',
    glAccount: 'GL-101',
    isCopq: false,
    unitCost: 300000,
  },
  {
    id: '3',
    lvl1: '내부 실패비용',
    lvl2: '재작업비',
    lvl3: '재세척비',
    itemCode: 'INT-001',
    itemName: '재세척 인건비',
    department: '생산팀',
    glAccount: 'GL-201',
    isCopq: true,
    unitCost: 150000,
  },
  {
    id: '4',
    lvl1: '외부 실패비용',
    lvl2: '보증비용',
    lvl3: '클레임 처리비',
    itemCode: 'EXT-001',
    itemName: '고객 클레임 비용',
    department: '고객지원팀',
    glAccount: 'GL-301',
    isCopq: true,
  }
];

export const QCostClassificationPage: React.FC = () => {
  const [categories, setCategories] = useState<QCostCategory[]>(MOCK_DATA);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<QCostCategory | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['1']));

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await qcostService.getCategories();

      if (response.ok && response.data) {
        // API 데이터를 UI 형식으로 변환
        const transformedCategories: QCostCategory[] = response.data.map((cat: QCostCategoryDTO) => ({
          id: cat.qcat_id,
          lvl1: cat.lvl1 === 'PREVENTION' ? '예방비용' :
                cat.lvl1 === 'APPRAISAL' ? '평가비용' :
                cat.lvl1 === 'INTERNAL_FAILURE' ? '내부 실패비용' :
                cat.lvl1 === 'EXTERNAL_FAILURE' ? '외부 실패비용' : cat.lvl1,
          lvl2: cat.lvl2 || '-',
          lvl3: cat.lvl3 || '-',
          itemCode: cat.code,
          itemName: cat.name,
          department: '-',
          glAccount: cat.gl_account || '-',
          isCopq: false, // API에 해당 필드가 없으면 기본값
          unitCost: undefined,
        }));

        setCategories(transformedCategories.length > 0 ? transformedCategories : MOCK_DATA);
      } else {
        throw new Error(response.error || '카테고리를 불러오는데 실패했습니다.');
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      // API 실패시 샘플 데이터 유지
      setCategories(MOCK_DATA);
    } finally {
      setLoading(false);
    }
  };

  const toggleNode = (id: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedNodes(newExpanded);
  };

  const filteredCategories = categories.filter(cat =>
    cat.itemName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cat.itemCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cat.lvl1.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderTree = (nodes: QCostCategory[], level: number = 0): React.ReactNode => {
    return nodes.map((node, index) => (
      <div key={`${node.id}-${level}-${index}`} style={{ marginLeft: `${level * 20}px` }}>
        <div
          className={`flex items-center gap-2 p-2 hover:bg-purple-50 rounded-lg cursor-pointer transition-colors ${
            selectedCategory?.id === node.id ? 'bg-purple-100 border-l-4 border-purple-600' : ''
          }`}
          onClick={() => setSelectedCategory(node)}
        >
          {node.children && node.children.length > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleNode(node.id);
              }}
              className="p-1 hover:bg-gray-200 rounded"
            >
              {expandedNodes.has(node.id) ? (
                <FolderOpen className="w-4 h-4 text-purple-600" />
              ) : (
                <Folder className="w-4 h-4 text-gray-600" />
              )}
            </button>
          )}
          {!node.children && (
            <ChevronRight className="w-4 h-4 text-gray-400" />
          )}

          <div className="flex-1">
            <div className="font-medium text-sm text-gray-800">{node.itemName}</div>
            <div className="text-xs text-gray-500">{node.itemCode}</div>
          </div>

          <div className="flex items-center gap-2">
            {node.isCopq && (
              <Badge className="bg-red-100 text-red-700 hover:bg-red-200">
                COPQ
              </Badge>
            )}
            {node.unitCost && (
              <Badge variant="outline" className="text-green-700 border-green-300">
                <DollarSign className="w-3 h-3" />
                {(node.unitCost / 10000).toFixed(1)}만원
              </Badge>
            )}
          </div>
        </div>

        {node.children && expandedNodes.has(node.id) && (
          <div className="mt-1" key={`children-${node.id}`}>
            {renderTree(node.children, level + 1)}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Q-COST 분류체계/항목 마스터</h1>
          <p className="text-sm text-gray-500 mt-1">
            품질코스트 분류 체계 및 항목 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Search className="w-4 h-4 mr-2" />
            검색
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4 mr-2" />
            신규 항목
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 왼쪽: 트리 구조 */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Folder className="w-5 h-5 text-purple-600" />
              분류 체계
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Input
              placeholder="항목 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="mb-4"
            />

            <div className="max-h-[600px] overflow-y-auto space-y-1">
              {renderTree(filteredCategories)}
            </div>
          </CardContent>
        </Card>

        {/* 오른쪽: 항목 상세 */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>항목 상세</CardTitle>
              {selectedCategory && (
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Edit className="w-4 h-4 mr-2" />
                    수정
                  </Button>
                  <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                    <Trash2 className="w-4 h-4 mr-2" />
                    삭제
                  </Button>
                </div>
              )}
            </div>
          </CardHeader>

          <CardContent>
            {selectedCategory ? (
              <div className="space-y-6">
                {/* 기본 정보 */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">기본 정보</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs text-gray-500">항목 코드</label>
                      <p className="text-sm font-medium text-gray-800 font-mono">
                        {selectedCategory.itemCode}
                      </p>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">항목명</label>
                      <p className="text-sm font-medium text-gray-800">
                        {selectedCategory.itemName}
                      </p>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">관리 부서</label>
                      <p className="text-sm text-gray-800">{selectedCategory.department}</p>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">GL 계정</label>
                      <p className="text-sm text-gray-800 font-mono">{selectedCategory.glAccount}</p>
                    </div>
                  </div>
                </div>

                {/* 분류 정보 */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">분류 정보</h3>
                  <div className="flex gap-2 mb-3">
                    <Badge variant="outline" className="text-base">
                      {selectedCategory.lvl1}
                    </Badge>
                    <ChevronRight className="w-4 h-4 text-gray-400 mt-1" />
                    <Badge variant="outline" className="text-base">
                      {selectedCategory.lvl2}
                    </Badge>
                    <ChevronRight className="w-4 h-4 text-gray-400 mt-1" />
                    <Badge variant="outline" className="text-base">
                      {selectedCategory.lvl3}
                    </Badge>
                  </div>
                </div>

                {/* COPQ 여부 */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">COPQ 여부</h3>
                  {selectedCategory.isCopq ? (
                    <Badge className="bg-red-100 text-red-700 hover:bg-red-200">
                      COPQ 대상 (품질불량으로 인한 추가 비용)
                    </Badge>
                  ) : (
                    <Badge className="bg-blue-100 text-blue-700 hover:bg-blue-200">
                      COPQ 비대상 (정상 품질비용)
                    </Badge>
                  )}
                </div>

                {/* 단가 정보 */}
                {selectedCategory.unitCost && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">단가 정보</h3>
                    <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">기준 단가</span>
                        <span className="text-lg font-bold text-green-700">
                          ₩{selectedCategory.unitCost.toLocaleString()}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        * 규칙 기반 단가 산정에 활용
                      </p>
                    </div>
                  </div>
                )}

                {/* 감사로그 */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">변경 이력</h3>
                  <AuditLogButton
                    logs={[
                      {
                        id: '1',
                        actor: '김품질',
                        timestamp: '2026-01-12T10:30:00',
                        action: '항목 생성',
                        details: '최초 등록',
                      },
                      {
                        id: '2',
                        actor: '이관리',
                        timestamp: '2026-01-10T14:20:00',
                        action: '단가 변경',
                        details: '₩100,000 → ₩150,000',
                      }
                    ]}
                  />
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <Folder className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>항목을 선택하세요</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

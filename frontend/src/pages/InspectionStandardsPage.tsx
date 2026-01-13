import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { Dialog } from '../components/ui/Dialog';
import {
  Plus,
  Search,
  Edit,
  Trash2,
  FileText,
  CheckCircle,
  XCircle,
  AlertCircle,
  ClipboardCheck,
  Eye
} from 'lucide-react';
import { StatusBadge } from '../components/common';

interface ChecklistItem {
  id: string;
  category: string;
  process: string;
  checkpoint: string;
  standard: string;
  method: string;
  frequency: string;
  acceptanceCriteria: string;
  status: 'ACTIVE' | 'INACTIVE' | 'DRAFT';
  version: string;
  lastUpdated: string;
}

export const InspectionStandardsPage: React.FC = () => {
  const [checklists, setChecklists] = useState<ChecklistItem[]>([
    {
      id: '1',
      category: 'CNC 가공',
      process: '내경 가공',
      checkpoint: '내경 치수',
      standard: '10.00 ± 0.05mm',
      method: '마이크로미터',
      frequency: '2시간마다',
      acceptanceCriteria: '9.95 ~ 10.05mm',
      status: 'ACTIVE',
      version: '1.2',
      lastUpdated: '2026-01-12',
    },
    {
      id: '2',
      category: 'CNC 가공',
      process: '외경 가공',
      checkpoint: '외경 치수',
      standard: '50.00 ± 0.10mm',
      method: '버니어 캘리퍼',
      frequency: '2시간마다',
      acceptanceCriteria: '49.90 ~ 50.10mm',
      status: 'ACTIVE',
      version: '1.1',
      lastUpdated: '2026-01-10',
    },
    {
      id: '3',
      category: '세척',
      process: '초음파 세척',
      checkpoint: '이물 잔류',
      standard: '이물 없음',
      method: '육안 검사',
      frequency: '전수',
      acceptanceCriteria: '이물/오염 없음',
      status: 'ACTIVE',
      version: '1.0',
      lastUpdated: '2026-01-08',
    },
    {
      id: '4',
      category: '조립',
      process: '브레이크 패드 조립',
      checkpoint: '조립 완성도',
      standard: '조립도 준수',
      method: '치수 측정',
      frequency: '전수',
      acceptanceCriteria: '치수 공차 ±0.2mm 이내',
      status: 'ACTIVE',
      version: '1.3',
      lastUpdated: '2026-01-05',
    },
    {
      id: '5',
      category: '포장',
      process: '최종 포장',
      checkpoint: '포장 상태',
      standard: '포장 규격 준수',
      method: '육안 검사',
      frequency: '샘플링 (10%)',
      acceptanceCriteria: '파손/오염 없음',
      status: 'DRAFT',
      version: '0.1',
      lastUpdated: '2026-01-03',
    },
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [showPreview, setShowPreview] = useState(false);
  const [selectedChecklist, setSelectedChecklist] = useState<ChecklistItem | null>(null);

  const categories = ['ALL', ...Array.from(new Set(checklists.map(c => c.category)))];

  const filteredChecklists = checklists.filter(checklist => {
    const matchesSearch = searchTerm === '' ||
      checklist.checkpoint.toLowerCase().includes(searchTerm.toLowerCase()) ||
      checklist.process.toLowerCase().includes(searchTerm.toLowerCase()) ||
      checklist.standard.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCategory = selectedCategory === 'ALL' || checklist.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  const stats = {
    total: checklists.length,
    active: checklists.filter(c => c.status === 'ACTIVE').length,
    draft: checklists.filter(c => c.status === 'DRAFT').length,
    inactive: checklists.filter(c => c.status === 'INACTIVE').length,
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">검수 기준·체크리스트</h1>
          <p className="text-sm text-gray-500 mt-1">
            검사 기준 및 체크리스트 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileText className="w-4 h-4 mr-2" />
            템플릿 다운로드
          </Button>
          <Button className="bg-purple-600 hover:bg-purple-700">
            <Plus className="w-4 h-4 mr-2" />
            신규 체크리스트
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
                  placeholder="검사 항목, 프로세스, 규격 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              {categories.map(cat => (
                <Button
                  key={cat}
                  variant={selectedCategory === cat ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(cat)}
                  className={selectedCategory === cat ? 'bg-purple-600 hover:bg-purple-700' : ''}
                >
                  {cat === 'ALL' ? '전체' : cat}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 요약 정보 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-purple-100 mb-1">전체 체크리스트</div>
                <div className="text-3xl font-bold">{stats.total}개</div>
              </div>
              <ClipboardCheck className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <div className="text-sm text-gray-500">활성</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.active}개</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <AlertCircle className="w-4 h-4 text-yellow-600" />
                  <div className="text-sm text-gray-500">초안</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.draft}개</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <XCircle className="w-4 h-4 text-gray-600" />
                  <div className="text-sm text-gray-500">비활성</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.inactive}개</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 체크리스트 목록 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-600" />
            검수 기준 목록
            <Badge variant="outline" className="ml-2">
              {filteredChecklists.length}개
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {filteredChecklists.map((checklist) => (
              <div
                key={checklist.id}
                className="p-4 bg-white rounded-lg border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Badge variant="outline" className="text-xs">
                        {checklist.category}
                      </Badge>
                      <h3 className="font-semibold text-gray-900">{checklist.checkpoint}</h3>
                      <StatusBadge status={checklist.status} />
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-gray-500 text-xs">프로세스</div>
                        <div className="text-gray-900 font-medium">{checklist.process}</div>
                      </div>
                      <div>
                        <div className="text-gray-500 text-xs">규격</div>
                        <div className="text-gray-900 font-mono">{checklist.standard}</div>
                      </div>
                      <div>
                        <div className="text-gray-500 text-xs">검사 방법</div>
                        <div className="text-gray-900">{checklist.method}</div>
                      </div>
                      <div>
                        <div className="text-gray-500 text-xs">검사 빈도</div>
                        <div className="text-gray-900">{checklist.frequency}</div>
                      </div>
                    </div>

                    <div className="mt-3 p-2 bg-gray-50 rounded text-sm">
                      <div className="text-gray-500 text-xs mb-1">합격 판정 기준</div>
                      <div className="text-gray-900">{checklist.acceptanceCriteria}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedChecklist(checklist);
                        setShowPreview(true);
                      }}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredChecklists.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <ClipboardCheck className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>검수 기준이 없습니다</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 상세 보기 다이얼로그 */}
      {showPreview && selectedChecklist && (
        <Dialog open={showPreview} onOpenChange={setShowPreview}>
          <Dialog.Content className="max-w-2xl">
            <Dialog.Header>
              <Dialog.Title>검수 기준 상세</Dialog.Title>
            </Dialog.Header>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-500 mb-1">카테고리</div>
                  <div className="text-gray-900 font-medium">{selectedChecklist.category}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">버전</div>
                  <div className="text-gray-900 font-mono">{selectedChecklist.version}</div>
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-500 mb-1">프로세스</div>
                <div className="text-gray-900 font-medium">{selectedChecklist.process}</div>
              </div>

              <div>
                <div className="text-sm text-gray-500 mb-1">검사 항목</div>
                <div className="text-gray-900 font-semibold text-lg">{selectedChecklist.checkpoint}</div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-500 mb-1">규격</div>
                  <div className="text-gray-900 font-mono text-lg">{selectedChecklist.standard}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">검사 방법</div>
                  <div className="text-gray-900">{selectedChecklist.method}</div>
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-500 mb-1">검사 빈도</div>
                <div className="text-gray-900">{selectedChecklist.frequency}</div>
              </div>

              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="text-sm text-gray-700 mb-2 font-semibold">합격 판정 기준</div>
                <div className="text-gray-900">{selectedChecklist.acceptanceCriteria}</div>
              </div>

              <div className="flex items-center justify-between text-sm text-gray-500 pt-2 border-t">
                <div>최종 수정: {new Date(selectedChecklist.lastUpdated).toLocaleDateString('ko-KR')}</div>
                <StatusBadge status={selectedChecklist.status} />
              </div>
            </div>
          </Dialog.Content>
        </Dialog>
      )}
    </div>
  );
};

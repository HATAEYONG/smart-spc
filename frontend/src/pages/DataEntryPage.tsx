import React, { useState } from 'react';
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
  Database,
  Plus,
  Upload,
  Save,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  AlertCircle
} from 'lucide-react';

interface DataEntry {
  id: string;
  product: string;
  characteristic: string;
  sampleDate: string;
  sampleTime: string;
  subgroupSize: number;
  measurements: number[];
  operator: string;
  machine: string;
  status: 'PENDING' | 'VALIDATED' | 'ERROR';
}

export const DataEntryPage: React.FC = () => {
  const [entries, setEntries] = useState<DataEntry[]>([
    {
      id: '1',
      product: '브레이크 패드',
      characteristic: '내경',
      sampleDate: '2026-01-12',
      sampleTime: '09:00',
      subgroupSize: 5,
      measurements: [10.01, 10.02, 9.99, 10.00, 10.01],
      operator: '김작업',
      machine: 'CNC-001',
      status: 'VALIDATED',
    },
    {
      id: '2',
      product: '브레이크 패드',
      characteristic: '내경',
      sampleDate: '2026-01-12',
      sampleTime: '10:00',
      subgroupSize: 5,
      measurements: [10.03, 10.01, 10.02, 10.00, 9.98],
      operator: '김작업',
      machine: 'CNC-001',
      status: 'VALIDATED',
    },
    {
      id: '3',
      product: '브레이크 패드',
      characteristic: '외경',
      sampleDate: '2026-01-12',
      sampleTime: '09:00',
      subgroupSize: 5,
      measurements: [50.05, 50.03, 50.07, 50.02, 50.04],
      operator: '이작업',
      machine: 'CNC-002',
      status: 'ERROR',
    },
  ]);

  const [newEntry, setNewEntry] = useState({
    product: '브레이크 패드',
    characteristic: '내경',
    sampleDate: new Date().toISOString().split('T')[0],
    sampleTime: new Date().toTimeString().slice(0, 5),
    subgroupSize: 5,
    measurements: ['', '', '', '', ''] as string[],
    operator: '',
    machine: '',
  });

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'VALIDATED':
        return { label: '검증 완료', color: 'bg-green-100 text-green-700', icon: CheckCircle };
      case 'ERROR':
        return { label: '에러', color: 'bg-red-100 text-red-700', icon: XCircle };
      case 'PENDING':
      default:
        return { label: '대기 중', color: 'bg-yellow-100 text-yellow-700', icon: Clock };
    }
  };

  const handleSubmit = () => {
    const hasEmptyMeasurements = newEntry.measurements.some(m => m === '');
    if (hasEmptyMeasurements) {
      alert('모든 측정값을 입력해주세요.');
      return;
    }

    const entry: DataEntry = {
      id: Date.now().toString(),
      ...newEntry,
      measurements: newEntry.measurements.map(Number),
      status: 'PENDING',
    };

    setEntries([entry, ...entries]);

    // Reset form
    setNewEntry({
      product: '브레이크 패드',
      characteristic: '내경',
      sampleDate: new Date().toISOString().split('T')[0],
      sampleTime: new Date().toTimeString().slice(0, 5),
      subgroupSize: 5,
      measurements: ['', '', '', '', ''] as string[],
      operator: '',
      machine: '',
    });
  };

  const stats = {
    total: entries.length,
    validated: entries.filter(e => e.status === 'VALIDATED').length,
    errors: entries.filter(e => e.status === 'ERROR').length,
    today: entries.filter(e => e.sampleDate === new Date().toISOString().split('T')[0]).length,
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* 페이지 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">데이터 입력</h1>
          <p className="text-sm text-gray-500 mt-1">
            SPC 데이터 수동 입력 및 관리
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Upload className="w-4 h-4 mr-2" />
            일괄 업로드
          </Button>
          <Button variant="outline">
            <FileText className="w-4 h-4 mr-2" />
            엑셀 다운로드
          </Button>
        </div>
      </div>

      {/* 요약 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-purple-100 mb-1">총 입력 건수</div>
                <div className="text-3xl font-bold">{stats.total}건</div>
              </div>
              <Database className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <div className="text-sm text-gray-500">검증 완료</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.validated}건</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <XCircle className="w-4 h-4 text-red-600" />
                  <div className="text-sm text-gray-500">에러</div>
                </div>
                <div className="text-2xl font-bold text-gray-900">{stats.errors}건</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500 mb-1">오늘 입력</div>
                <div className="text-2xl font-bold text-gray-900">{stats.today}건</div>
              </div>
              <Clock className="w-8 h-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 데이터 입력 폼 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="w-5 h-5 text-purple-600" />
              새 데이터 입력
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">제품</label>
                <Select
                  value={newEntry.product}
                  onValueChange={(value) => setNewEntry({ ...newEntry, product: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="브레이크 패드">브레이크 패드</SelectItem>
                    <SelectItem value="클러치 판">클러치 판</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">특성</label>
                <Select
                  value={newEntry.characteristic}
                  onValueChange={(value) => setNewEntry({ ...newEntry, characteristic: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="내경">내경</SelectItem>
                    <SelectItem value="외경">외경</SelectItem>
                    <SelectItem value="두께">두께</SelectItem>
                    <SelectItem value="깊이">깊이</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">샘플 날짜</label>
                <Input
                  type="date"
                  value={newEntry.sampleDate}
                  onChange={(e) => setNewEntry({ ...newEntry, sampleDate: e.target.value })}
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">샘플 시간</label>
                <Input
                  type="time"
                  value={newEntry.sampleTime}
                  onChange={(e) => setNewEntry({ ...newEntry, sampleTime: e.target.value })}
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">작업자</label>
                <Input
                  value={newEntry.operator}
                  onChange={(e) => setNewEntry({ ...newEntry, operator: e.target.value })}
                  placeholder="이름 입력"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">설비</label>
                <Select
                  value={newEntry.machine}
                  onValueChange={(value) => setNewEntry({ ...newEntry, machine: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="CNC-001">CNC-001</SelectItem>
                    <SelectItem value="CNC-002">CNC-002</SelectItem>
                    <SelectItem value="WASH-001">세척-001</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                측정값 (샘플 크기: {newEntry.subgroupSize})
              </label>
              <div className="grid grid-cols-5 gap-2">
                {newEntry.measurements.map((value, idx) => (
                  <Input
                    key={idx}
                    type="number"
                    step="0.001"
                    value={value}
                    onChange={(e) => {
                      const newMeasurements = [...newEntry.measurements];
                      newMeasurements[idx] = e.target.value;
                      setNewEntry({ ...newEntry, measurements: newMeasurements });
                    }}
                    placeholder={`#${idx + 1}`}
                  />
                ))}
              </div>
            </div>

            <Button className="w-full bg-purple-600 hover:bg-purple-700" onClick={handleSubmit}>
              <Save className="w-4 h-4 mr-2" />
              데이터 저장
            </Button>
          </CardContent>
        </Card>

        {/* 입력 내역 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-purple-600" />
              입력 내역
              <Badge variant="outline">{entries.length}건</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {entries.map((entry) => {
                const statusConfig = getStatusConfig(entry.status);
                const StatusIcon = statusConfig.icon;
                const avg = entry.measurements.reduce((a, b) => a + b, 0) / entry.measurements.length;

                return (
                  <div
                    key={entry.id}
                    className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-gray-900">{entry.characteristic}</span>
                          <Badge variant="outline" className="text-xs">
                            {entry.product}
                          </Badge>
                          <Badge className={statusConfig.color}>
                            <div className="flex items-center gap-1">
                              <StatusIcon className="w-3 h-3" />
                              {statusConfig.label}
                            </div>
                          </Badge>
                        </div>
                        <div className="text-xs text-gray-500">
                          {entry.sampleDate} {entry.sampleTime} | {entry.operator} | {entry.machine}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-500">평균</div>
                        <div className="text-lg font-bold text-purple-600">
                          {avg.toFixed(3)}
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-1">
                      {entry.measurements.map((m, idx) => (
                        <div
                          key={idx}
                          className="flex-1 text-center p-2 bg-gray-50 rounded text-sm font-mono"
                        >
                          <div className="text-xs text-gray-500 mb-1">#{idx + 1}</div>
                          <div className="text-gray-900">{m.toFixed(3)}</div>
                        </div>
                      ))}
                    </div>

                    {entry.status === 'ERROR' && (
                      <div className="mt-2 p-2 bg-red-50 rounded text-xs text-red-700 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        규격 이탈: 측정값 #3이 UCL(10.05) 초과
                      </div>
                    )}
                  </div>
                );
              })}

              {entries.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>입력된 데이터가 없습니다</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DataEntryPage;

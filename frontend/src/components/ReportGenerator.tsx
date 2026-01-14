import React, { useState } from 'react';
import {
  FileText,
  Download,
  FileSpreadsheet,
  File,
  Loader2
} from 'lucide-react';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import {
  generatePDFReport,
  generateExcelReport,
  formatReportData
} from '../utils/reportGenerator';

interface ReportGeneratorProps {
  type: 'spc' | 'qcost' | 'sixSigma' | 'maintenance';
  data: any;
  filename?: string;
  variant?: 'button' | 'dropdown';
}

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  type,
  data,
  filename,
  variant = 'dropdown'
}) => {
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  const handleGenerate = async (format: 'pdf' | 'excel') => {
    setLoading(true);
    try {
      // 데이터 포맷팅
      let reportData;
      switch (type) {
        case 'spc':
          reportData = formatReportData.spc(data);
          break;
        case 'qcost':
          reportData = formatReportData.qcost(data);
          break;
        case 'sixSigma':
          reportData = formatReportData.sixSigma(data);
          break;
        case 'maintenance':
          reportData = {
            title: '설비 점검 보고서',
            subtitle: 'Predictive Maintenance',
            date: new Date().toLocaleDateString('ko-KR'),
            sections: [
              {
                title: '점검 내역',
                table: {
                  headers: ['날짜', '설비', '유형', '상태', '비용'],
                  rows: data.records?.map((r: any) => [
                    r.date,
                    r.equipment,
                    r.type,
                    r.status,
                    r.cost || '-'
                  ]) || []
                }
              }
            ]
          };
          break;
      }

      // 보고서 생성
      if (format === 'pdf') {
        generatePDFReport(reportData);
      } else {
        generateExcelReport(reportData);
      }

      setShowDropdown(false);
    } catch (error) {
      console.error('보고서 생성 오류:', error);
      alert('보고서 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (variant === 'button') {
    return (
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleGenerate('pdf')}
          disabled={loading}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <File className="w-4 h-4 mr-2" />
          )}
          PDF
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleGenerate('excel')}
          disabled={loading}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <FileSpreadsheet className="w-4 h-4 mr-2" />
          )}
          Excel
        </Button>
      </div>
    );
  }

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        onClick={() => setShowDropdown(!showDropdown)}
      >
        <Download className="w-4 h-4 mr-2" />
        보고서
      </Button>

      {showDropdown && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowDropdown(false)}
          />
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-20">
            <div className="p-2">
              <button
                onClick={() => handleGenerate('pdf')}
                disabled={loading}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded hover:bg-gray-100 transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <File className="w-4 h-4 text-red-600" />
                )}
                <span>PDF 보고서</span>
              </button>
              <button
                onClick={() => handleGenerate('excel')}
                disabled={loading}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded hover:bg-gray-100 transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <FileSpreadsheet className="w-4 h-4 text-green-600" />
                )}
                <span>Excel 보고서</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// 빠른 보고서 생성 버튼
export const QuickReportButton: React.FC<{
  onClick: () => void;
  label?: string;
}> = ({ onClick, label = '보고서' }) => {
  return (
    <Button
      variant="outline"
      size="sm"
      onClick={onClick}
    >
      <FileText className="w-4 h-4 mr-2" />
      {label}
    </Button>
  );
};

export default ReportGenerator;

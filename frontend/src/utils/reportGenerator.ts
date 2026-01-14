/**
 * Report Generator Utility
 * 보고서 생성 유틸리티 (PDF/Excel)
 */

import { jsPDF } from 'jspdf';
import * as XLSX from 'xlsx';

export interface ReportData {
  title: string;
  subtitle?: string;
  date: string;
  author?: string;
  sections: ReportSection[];
}

export interface ReportSection {
  title: string;
  content?: string;
  table?: {
    headers: string[];
    rows: (string | number)[][];
  };
  chart?: {
    imageData: string;
    caption?: string;
  };
}

/**
 * PDF 보고서 생성
 */
export const generatePDFReport = (data: ReportData): void => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  let yPosition = margin;

  // 한글 폰트 설정이 필요하지만, 현재는 기본 폰트 사용
  doc.setFontSize(20);
  doc.text(data.title, margin, yPosition);
  yPosition += 10;

  if (data.subtitle) {
    doc.setFontSize(12);
    doc.text(data.subtitle, margin, yPosition);
    yPosition += 7;
  }

  doc.setFontSize(10);
  doc.text(`생성일: ${data.date}`, margin, yPosition);
  yPosition += 15;

  // 섹션 처리
  data.sections.forEach((section) => {
    // 새 페이지 확인
    if (yPosition > pageHeight - 50) {
      doc.addPage();
      yPosition = margin;
    }

    // 섹션 제목
    doc.setFontSize(14);
    doc.text(section.title, margin, yPosition);
    yPosition += 8;

    // 섹션 내용
    if (section.content) {
      doc.setFontSize(10);
      const lines = doc.splitTextToSize(section.content, pageWidth - 2 * margin);
      doc.text(lines, margin, yPosition);
      yPosition += lines.length * 5 + 5;
    }

    // 테이블
    if (section.table) {
      const cellWidth = (pageWidth - 2 * margin) / section.table.headers.length;
      const cellHeight = 8;

      // 헤더
      doc.setFillColor(66, 139, 202);
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(9);
      section.table.headers.forEach((header, i) => {
        doc.rect(margin + i * cellWidth, yPosition, cellWidth, cellHeight, 'F');
        doc.text(header, margin + i * cellWidth + 2, yPosition + 5);
      });
      yPosition += cellHeight;

      // 데이터 행
      doc.setTextColor(0, 0, 0);
      doc.setFontSize(8);
      section.table.rows.forEach((row, rowIndex) => {
        // 행 색상 (짝수/홀수)
        if (rowIndex % 2 === 0) {
          doc.setFillColor(245, 245, 245);
          doc.rect(margin, yPosition, pageWidth - 2 * margin, cellHeight, 'F');
        }

        row.forEach((cell, cellIndex) => {
          doc.text(String(cell), margin + cellIndex * cellWidth + 2, yPosition + 5);
        });
        yPosition += cellHeight;

        // 페이지 넘김 확인
        if (yPosition > pageHeight - margin) {
          doc.addPage();
          yPosition = margin;
        }
      });

      yPosition += 10;
    }

    // 차트
    if (section.chart) {
      const maxWidth = pageWidth - 2 * margin;
      const maxHeight = 100;
      const imgWidth = Math.min(maxWidth, 200);
      const imgHeight = (imgWidth / 200) * maxHeight;

      try {
        doc.addImage(section.chart.imageData, 'JPEG', margin, yPosition, imgWidth, imgHeight);
        yPosition += imgHeight + 5;

        if (section.chart.caption) {
          doc.setFontSize(9);
          doc.text(section.chart.caption, margin, yPosition);
          yPosition += 5;
        }
      } catch (error) {
        console.error('이미지 추가 오류:', error);
      }

      yPosition += 10;
    }

    yPosition += 10;
  });

  // 페이지 번호
  const totalPages = doc.internal.pages.length - 1;
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(9);
    doc.text(
      `${i} / ${totalPages}`,
      pageWidth / 2,
      pageHeight - 10,
      { align: 'center' }
    );
  }

  // PDF 다운로드
  const fileName = `${data.title.replace(/\s+/g, '_')}_${new Date().getTime()}.pdf`;
  doc.save(fileName);
};

/**
 * Excel 보고서 생성
 */
export const generateExcelReport = (data: ReportData): void => {
  const wb = XLSX.utils.book_new();

  // 요약 시트
  const summaryData = [
    ['보고서 제목', data.title],
    ['부제목', data.subtitle || ''],
    ['생성일', data.date],
    ['작성자', data.author || ''],
    [],
  ];

  data.sections.forEach((section) => {
    summaryData.push([section.title]);
    if (section.content) {
      summaryData.push(['내용', section.content]);
    }
    if (section.table) {
      summaryData.push(['데이터', `${section.table.rows.length}행`]);
    }
    summaryData.push([]);
  });

  const summaryWs = XLSX.utils.aoa_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(wb, summaryWs, '요약');

  // 데이터 시트들
  data.sections.forEach((section, index) => {
    if (section.table) {
      const ws = XLSX.utils.aoa_to_sheet([
        section.table.headers,
        ...section.table.rows
      ]);
      XLSX.utils.book_append_sheet(wb, ws, section.title.substring(0, 31)); // 시트 이름 제한
    }
  });

  // Excel 다운로드
  const fileName = `${data.title.replace(/\s+/g, '_')}_${new Date().getTime()}.xlsx`;
  XLSX.writeFile(wb, fileName);
};

/**
 * CSV 보고서 생성
 */
export const generateCSVReport = (data: {
  filename: string;
  headers: string[];
  rows: (string | number)[][];
}): void => {
  const csvContent = [
    data.headers.join(','),
    ...data.rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  const BOM = '\uFEFF'; // UTF-8 BOM for Excel
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);

  link.setAttribute('href', url);
  link.setAttribute('download', `${data.filename}_${new Date().getTime()}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * 차트 이미지 캡처
 */
export const captureChart = async (elementId: string): Promise<string> => {
  const element = document.getElementById(elementId);
  if (!element) {
    throw new Error(`Element ${elementId} not found`);
  }

  // html2canvas 라이브러리 사용 필요
  // 이 함수는 사용 가능한 경우에만 작동
  return '';
};

/**
 * 보고서 데이터 포맷팅 헬퍼
 */
export const formatReportData = {
  spc: (data: any) => ({
    title: 'SPC 분석 보고서',
    subtitle: 'Statistical Process Control',
    date: new Date().toLocaleDateString('ko-KR'),
    sections: [
      {
        title: '개요',
        content: `품목: ${data.productName}\n공정: ${data.process}\n분석 기간: ${data.period}`,
      },
      {
        title: '공정 능력',
        table: {
          headers: ['지표', '값', '규격'],
          rows: [
            ['Cp', data.cp?.toFixed(3) || '-', '≥ 1.0'],
            ['Cpk', data.cpk?.toFixed(3) || '-', '≥ 1.0'],
            ['평균', data.mean?.toFixed(3) || '', data.target || ''],
            ['표준편차', data.stdDev?.toFixed(3) || '', ''],
          ],
        },
      },
    ],
  }),

  qcost: (data: any) => ({
    title: '품질 비용 분석 보고서',
    subtitle: 'Quality Cost Analysis',
    date: new Date().toLocaleDateString('ko-KR'),
    sections: [
      {
        title: 'COPQ 요약',
        table: {
          headers: ['항목', '금액(원)', '비율(%)'],
          rows: [
            ['내부 실패 비용', data.internalFailure?.toLocaleString() || 0, data.internalFailurePercent || 0],
            ['외부 실패 비용', data.externalFailure?.toLocaleString() || 0, data.externalFailurePercent || 0],
            ['평가 비용', data.appraisal?.toLocaleString() || 0, data.appraisalPercent || 0],
            ['예방 비용', data.prevention?.toLocaleString() || 0, data.preventionPercent || 0],
            ['합계', data.total?.toLocaleString() || 0, 100],
          ],
        },
      },
    ],
  }),

  sixSigma: (data: any) => ({
    title: 'Six Sigma 프로젝트 보고서',
    subtitle: data.projectName || 'DMAIC 프로젝트',
    date: new Date().toLocaleDateString('ko-KR'),
    sections: [
      {
        title: '프로젝트 정보',
        table: {
          headers: ['항목', '내용'],
          rows: [
            ['프로젝트 코드', data.projectCode || '-'],
            ['현재 단계', data.phase || '-'],
            ['진행률', `${data.progress || 0}%`],
            ['시작일', data.startDate || '-'],
            ['목표 종료일', data.targetEndDate || '-'],
          ],
        },
      },
    ],
  }),
};

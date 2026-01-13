import React from 'react';
import { Badge } from '../ui/Badge';

// 상태 타입 정의
export type StatusType =
  | 'DRAFT'      // 초안
  | 'ACTIVE'     // 활성
  | 'HOLD'       // 보류
  | 'OOS'        // 규격 이탈
  | 'OPEN'       // 미해결
  | 'CLOSED'     // 종료
  | 'IN_PROGRESS' // 진행중
  | 'RESOLVED';  // 해결됨

interface StatusBadgeProps {
  status: StatusType;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const getStatusConfig = (status: StatusType) => {
    switch (status) {
      case 'DRAFT':
        return {
          label: '초안',
          variant: 'secondary' as const,
        };
      case 'ACTIVE':
        return {
          label: '활성',
          variant: 'default' as const,
        };
      case 'HOLD':
        return {
          label: '보류',
          variant: 'outline' as const,
        };
      case 'OOS':
        return {
          label: '규격 이탈',
          variant: 'destructive' as const,
        };
      case 'OPEN':
        return {
          label: '미해결',
          variant: 'default' as const,
        };
      case 'CLOSED':
        return {
          label: '종료',
          variant: 'outline' as const,
        };
      case 'IN_PROGRESS':
        return {
          label: '진행중',
          variant: 'default' as const,
        };
      case 'RESOLVED':
        return {
          label: '해결됨',
          variant: 'outline' as const,
        };
      default:
        return {
          label: status,
          variant: 'secondary' as const,
        };
    }
  };

  const config = getStatusConfig(status);

  // 색상 커스텀
  const customClass = {
    'DRAFT': 'bg-gray-100 text-gray-700 hover:bg-gray-200',
    'ACTIVE': 'bg-green-100 text-green-700 hover:bg-green-200',
    'HOLD': 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200 border-yellow-300',
    'OOS': 'bg-red-100 text-red-700 hover:bg-red-200',
    'OPEN': 'bg-orange-100 text-orange-700 hover:bg-orange-200',
    'CLOSED': 'bg-blue-100 text-blue-700 hover:bg-blue-200 border-blue-300',
    'IN_PROGRESS': 'bg-purple-100 text-purple-700 hover:bg-purple-200',
    'RESOLVED': 'bg-teal-100 text-teal-700 hover:bg-teal-200 border-teal-300',
  }[status] || '';

  return (
    <Badge
      variant={config.variant}
      className={`px-3 py-1 font-semibold ${customClass} ${className}`}
    >
      {config.label}
    </Badge>
  );
};

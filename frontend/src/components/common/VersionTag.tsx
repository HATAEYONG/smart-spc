import React from 'react';
import { Badge } from '../ui/Badge';
import { Calendar, User } from 'lucide-react';

interface VersionTagProps {
  revNo: string;
  approver?: string;
  approvedDate?: string;
  className?: string;
}

export const VersionTag: React.FC<VersionTagProps> = ({
  revNo,
  approver,
  approvedDate,
  className = ''
}) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Badge variant="outline" className="px-3 py-1 font-mono font-semibold">
        Rev {revNo}
      </Badge>

      {(approver || approvedDate) && (
        <div className="flex items-center gap-3 text-xs text-gray-500">
          {approver && (
            <div className="flex items-center gap-1">
              <User className="w-3 h-3" />
              <span>{approver}</span>
            </div>
          )}
          {approvedDate && (
            <div className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              <span>{new Date(approvedDate).toLocaleDateString('ko-KR')}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

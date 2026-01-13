import React, { useState } from 'react';
import { Dialog } from '../ui/Dialog';
import { Button } from '../ui/Button';
import { ScrollArea } from '../ui/ScrollArea';
import { History } from 'lucide-react';
import { Badge } from '../ui/Badge';

export interface AuditLogEntry {
  id: string;
  actor: string;        // 누가
  timestamp: string;    // 언제
  action: string;       // 무엇을
  details?: string;     // 상세 내용
}

interface AuditLogButtonProps {
  logs: AuditLogEntry[];
  className?: string;
}

export const AuditLogButton: React.FC<AuditLogButtonProps> = ({
  logs,
  className = ''
}) => {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`${className}`}
          onClick={() => setOpen(true)}
        >
          <History className="w-4 h-4 mr-2" />
          감사로그
          <Badge variant="secondary" className="ml-2">
            {logs.length}
          </Badge>
        </Button>
      </Dialog.Trigger>

      <Dialog.Content className="max-w-2xl max-h-[600px]">
        <Dialog.Header>
          <Dialog.Title className="flex items-center gap-2">
            <History className="w-5 h-5" />
            감사로그 (Audit Log)
          </Dialog.Title>
        </Dialog.Header>

        <ScrollArea className="h-[450px] pr-4">
          <div className="space-y-3">
            {logs.map((log, idx) => (
              <div
                key={log.id}
                className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="font-mono text-xs">
                      {log.actor}
                    </Badge>
                    <span className="text-sm font-medium text-gray-800">
                      {log.action}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(log.timestamp).toLocaleString('ko-KR', {
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>

                {log.details && (
                  <div className="mt-2 pl-4 border-l-2 border-gray-300">
                    <p className="text-sm text-gray-600">{log.details}</p>
                  </div>
                )}
              </div>
            ))}

            {logs.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <History className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>감사로그가 없습니다</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </Dialog.Content>
    </Dialog>
  );
};

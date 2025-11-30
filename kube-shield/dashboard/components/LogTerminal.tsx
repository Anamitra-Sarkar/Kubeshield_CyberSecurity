'use client';

import { useEffect, useRef } from 'react';
import { Card, Title } from '@tremor/react';
import { SecurityEvent } from '@/types';
import { formatTimestamp, getSeverityColor, getEventTypeIcon, getActionColor, truncate } from '@/lib/utils';

interface LogTerminalProps {
  logs: SecurityEvent[];
  maxHeight?: string;
}

export function LogTerminal({ logs, maxHeight = '400px' }: LogTerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const autoScrollRef = useRef(true);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScrollRef.current && terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  // Handle scroll to detect if user scrolled up
  const handleScroll = () => {
    if (terminalRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = terminalRef.current;
      autoScrollRef.current = scrollHeight - scrollTop - clientHeight < 50;
    }
  };

  return (
    <Card className="bg-slate-950 border border-slate-800 ring-0 shadow-lg p-0 overflow-hidden">
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900/80 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-rose-500"></div>
            <div className="w-3 h-3 rounded-full bg-amber-500"></div>
            <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
          </div>
          <Title className="text-slate-400 text-sm font-mono ml-2">
            security-events.log
          </Title>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-mono">
            {logs.length} events
          </span>
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-xs text-emerald-500 font-mono">LIVE</span>
        </div>
      </div>

      {/* Terminal Body */}
      <div
        ref={terminalRef}
        onScroll={handleScroll}
        className="overflow-y-auto bg-slate-950 font-mono text-sm"
        style={{ maxHeight }}
      >
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-slate-600">
            <span>Waiting for security events...</span>
          </div>
        ) : (
          <div className="p-2 space-y-0.5">
            {logs.map((log, index) => (
              <LogEntry key={log.id || index} log={log} />
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}

function LogEntry({ log }: { log: SecurityEvent }) {
  const severityColors = getSeverityColor(log.severity);
  const icon = getEventTypeIcon(log.event_type);
  const actionColor = getActionColor(log.action);

  return (
    <div className="group flex items-start gap-2 py-1.5 px-2 rounded hover:bg-slate-900/50 transition-colors">
      {/* Timestamp */}
      <span className="text-slate-600 text-xs shrink-0 font-mono">
        [{formatTimestamp(log.timestamp)}]
      </span>

      {/* Severity Badge */}
      <span className={`${severityColors.bg} ${severityColors.text} ${severityColors.border} border px-1.5 py-0.5 text-xs rounded shrink-0`}>
        {log.severity}
      </span>

      {/* Icon */}
      <span className="shrink-0">{icon}</span>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <span className="text-slate-300">
          <span className="text-cyan-400">{log.event_type}</span>
          {' '}
          <span className="text-slate-500">in</span>
          {' '}
          <span className="text-amber-400">{log.namespace}/</span>
          <span className="text-emerald-400">{truncate(log.pod_name, 30)}</span>
        </span>
        
        {/* Reason */}
        <div className="text-slate-500 text-xs mt-0.5">
          {truncate(log.reason, 80)}
        </div>
      </div>

      {/* Action */}
      <span className={`${actionColor} text-xs font-medium shrink-0`}>
        {log.action}
      </span>
    </div>
  );
}

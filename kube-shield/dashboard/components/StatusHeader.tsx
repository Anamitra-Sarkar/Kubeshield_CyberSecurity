'use client';

import { ShieldCheckIcon } from '@heroicons/react/24/solid';
import { Badge } from '@tremor/react';

interface StatusHeaderProps {
  status: 'ENFORCING' | 'AUDIT' | 'DISABLED';
  uptime?: string;
}

export function StatusHeader({ status, uptime }: StatusHeaderProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'ENFORCING':
        return 'emerald';
      case 'AUDIT':
        return 'amber';
      case 'DISABLED':
        return 'rose';
      default:
        return 'slate';
    }
  };

  const getStatusGlow = () => {
    switch (status) {
      case 'ENFORCING':
        return 'shadow-emerald-500/20';
      case 'AUDIT':
        return 'shadow-amber-500/20';
      case 'DISABLED':
        return 'shadow-rose-500/20';
      default:
        return '';
    }
  };

  return (
    <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`p-2 rounded-lg bg-slate-900 border border-slate-800 shadow-lg ${getStatusGlow()}`}>
              <ShieldCheckIcon className="w-8 h-8 text-emerald-500" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-white tracking-tight">
                KUBE-SHIELD
              </h1>
              <p className="text-xs text-slate-500 font-mono uppercase tracking-wider">
                Zero-Trust Security Operator
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            {uptime && (
              <div className="text-right hidden sm:block">
                <p className="text-xs text-slate-500 uppercase tracking-wider">Uptime</p>
                <p className="text-sm font-mono text-slate-300">{uptime}</p>
              </div>
            )}
            
            <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-slate-900 border border-slate-800">
              <div className="flex items-center gap-2">
                <span className={`relative flex h-2.5 w-2.5`}>
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full bg-${getStatusColor()}-400 opacity-75`}></span>
                  <span className={`relative inline-flex rounded-full h-2.5 w-2.5 bg-${getStatusColor()}-500`}></span>
                </span>
                <span className="text-xs text-slate-400 uppercase tracking-wider font-medium">
                  System Status:
                </span>
              </div>
              <Badge color={getStatusColor()} size="sm">
                {status}
              </Badge>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

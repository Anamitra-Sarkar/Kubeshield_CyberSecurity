'use client';

import { Card, Metric, Text, Flex, ProgressBar } from '@tremor/react';
import {
  ShieldExclamationIcon,
  HeartIcon,
  DocumentCheckIcon,
} from '@heroicons/react/24/outline';

interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: 'threats' | 'health' | 'policies';
  trend?: 'up' | 'down' | 'neutral';
  color?: 'emerald' | 'rose' | 'amber' | 'blue';
  progress?: number;
}

const iconMap = {
  threats: ShieldExclamationIcon,
  health: HeartIcon,
  policies: DocumentCheckIcon,
};

export function MetricCard({
  title,
  value,
  subtitle,
  icon,
  color = 'emerald',
  progress,
}: MetricCardProps) {
  const Icon = iconMap[icon];

  const getColorClasses = () => {
    switch (color) {
      case 'emerald':
        return {
          icon: 'text-emerald-500',
          bg: 'bg-emerald-950/50',
          border: 'border-emerald-900/50',
          progress: 'bg-emerald-500',
        };
      case 'rose':
        return {
          icon: 'text-rose-500',
          bg: 'bg-rose-950/50',
          border: 'border-rose-900/50',
          progress: 'bg-rose-500',
        };
      case 'amber':
        return {
          icon: 'text-amber-500',
          bg: 'bg-amber-950/50',
          border: 'border-amber-900/50',
          progress: 'bg-amber-500',
        };
      case 'blue':
        return {
          icon: 'text-blue-500',
          bg: 'bg-blue-950/50',
          border: 'border-blue-900/50',
          progress: 'bg-blue-500',
        };
      default:
        return {
          icon: 'text-slate-500',
          bg: 'bg-slate-900',
          border: 'border-slate-800',
          progress: 'bg-slate-500',
        };
    }
  };

  const colors = getColorClasses();

  return (
    <Card className={`bg-slate-900/50 border border-slate-800 ring-0 shadow-lg ${colors.border}`}>
      <Flex alignItems="start" justifyContent="between">
        <div>
          <Text className="text-slate-400 text-xs uppercase tracking-wider font-medium">
            {title}
          </Text>
          <Metric className="text-white mt-1 font-mono text-2xl">
            {value}
          </Metric>
          {subtitle && (
            <Text className="text-slate-500 text-xs mt-1">
              {subtitle}
            </Text>
          )}
        </div>
        <div className={`p-2 rounded-lg ${colors.bg} ${colors.border} border`}>
          <Icon className={`w-5 h-5 ${colors.icon}`} />
        </div>
      </Flex>
      {progress !== undefined && (
        <div className="mt-4">
          <ProgressBar 
            value={progress} 
            color={color}
            className="h-1.5"
          />
        </div>
      )}
    </Card>
  );
}

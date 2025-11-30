'use client';

import { Card, Title, BarList, Text, DonutChart, Legend } from '@tremor/react';

interface EventBreakdownProps {
  eventsByType: Record<string, number>;
  eventsBySeverity: Record<string, number>;
}

export function EventBreakdown({ eventsByType, eventsBySeverity }: EventBreakdownProps) {
  // Transform type data for bar list
  const typeData = Object.entries(eventsByType)
    .map(([name, value]) => ({
      name: formatEventType(name),
      value,
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 6);

  // Transform severity data for donut chart
  const severityColors: Record<string, string> = {
    CRITICAL: 'rose',
    HIGH: 'orange',
    MEDIUM: 'amber',
    LOW: 'blue',
    INFO: 'slate',
  };

  const severityData = Object.entries(eventsBySeverity).map(([name, value]) => ({
    name,
    value,
    color: severityColors[name] || 'slate',
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Event Types */}
      <Card className="bg-slate-900/50 border border-slate-800 ring-0 shadow-lg">
        <Title className="text-white text-sm font-medium mb-4">
          Events by Type
        </Title>
        {typeData.length > 0 ? (
          <BarList
            data={typeData}
            className="mt-2"
            color="emerald"
            showAnimation={true}
          />
        ) : (
          <div className="h-32 flex items-center justify-center text-slate-600">
            <span>No events recorded</span>
          </div>
        )}
      </Card>

      {/* Severity Distribution */}
      <Card className="bg-slate-900/50 border border-slate-800 ring-0 shadow-lg">
        <Title className="text-white text-sm font-medium mb-4">
          Severity Distribution
        </Title>
        {severityData.length > 0 ? (
          <div className="flex items-center justify-between">
            <DonutChart
              data={severityData}
              category="value"
              index="name"
              colors={['rose', 'orange', 'amber', 'blue', 'slate']}
              className="w-32 h-32"
              showLabel={false}
              showAnimation={true}
            />
            <Legend
              categories={severityData.map((d) => d.name)}
              colors={['rose', 'orange', 'amber', 'blue', 'slate']}
              className="max-w-xs"
            />
          </div>
        ) : (
          <div className="h-32 flex items-center justify-center text-slate-600">
            <span>No events recorded</span>
          </div>
        )}
      </Card>
    </div>
  );
}

function formatEventType(type: string): string {
  return type
    .split('_')
    .map((word) => word.charAt(0) + word.slice(1).toLowerCase())
    .join(' ');
}

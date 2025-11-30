'use client';

import { Card, Title, AreaChart, Text } from '@tremor/react';
import { TimeSeriesPoint } from '@/types';

interface AttackChartProps {
  data: TimeSeriesPoint[];
  title?: string;
}

export function AttackChart({ data, title = 'Threat Volume' }: AttackChartProps) {
  // Transform data for Tremor chart
  const chartData = data.map((point) => ({
    time: new Date(point.timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }),
    Threats: point.value,
  }));

  // Calculate totals for display
  const totalThreats = data.reduce((sum, point) => sum + point.value, 0);
  const avgThreats = data.length > 0 ? (totalThreats / data.length).toFixed(1) : '0';

  return (
    <Card className="bg-slate-900/50 border border-slate-800 ring-0 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <Title className="text-white text-sm font-medium">{title}</Title>
          <Text className="text-slate-500 text-xs">Last 30 minutes</Text>
        </div>
        <div className="flex gap-4 text-right">
          <div>
            <Text className="text-slate-500 text-xs uppercase tracking-wider">Total</Text>
            <Text className="text-white font-mono">{totalThreats}</Text>
          </div>
          <div>
            <Text className="text-slate-500 text-xs uppercase tracking-wider">Avg/min</Text>
            <Text className="text-white font-mono">{avgThreats}</Text>
          </div>
        </div>
      </div>

      {chartData.length > 0 ? (
        <AreaChart
          className="h-44"
          data={chartData}
          index="time"
          categories={['Threats']}
          colors={['rose']}
          showLegend={false}
          showYAxis={true}
          showXAxis={true}
          showGridLines={true}
          curveType="monotone"
          yAxisWidth={32}
          customTooltip={({ payload }) => {
            if (!payload?.[0]) return null;
            return (
              <div className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 shadow-lg">
                <div className="text-slate-400 text-xs">
                  {payload[0].payload.time}
                </div>
                <div className="text-rose-400 font-mono font-medium">
                  {payload[0].value} threats
                </div>
              </div>
            );
          }}
        />
      ) : (
        <div className="h-44 flex items-center justify-center text-slate-600">
          <span>No data available</span>
        </div>
      )}
    </Card>
  );
}

'use client';

import { useEffect, useState, useCallback } from 'react';
import { 
  StatusHeader, 
  MetricCard, 
  LogTerminal, 
  AttackChart, 
  EventBreakdown 
} from '@/components';
import { 
  SecurityEvent, 
  Metrics, 
  TimeSeriesPoint, 
  StatusResponse 
} from '@/types';
import { formatUptime } from '@/lib/utils';

const API_BASE_URL = process.env.NEXT_PUBLIC_AUDIT_SERVICE_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [logs, setLogs] = useState<SecurityEvent[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [attackData, setAttackData] = useState<TimeSeriesPoint[]>([]);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [logsRes, metricsRes, attackRes, statusRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/logs?limit=50`),
        fetch(`${API_BASE_URL}/api/v1/metrics`),
        fetch(`${API_BASE_URL}/api/v1/attack-volume?minutes=30`),
        fetch(`${API_BASE_URL}/status`),
      ]);

      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setLogs(logsData);
      }

      if (metricsRes.ok) {
        const metricsData = await metricsRes.json();
        setMetrics(metricsData);
      }

      if (attackRes.ok) {
        const attackJson = await attackRes.json();
        setAttackData(attackJson.data || []);
      }

      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setStatus(statusData);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('Failed to connect to audit service');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData]);

  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <StatusHeader 
        status={status?.enforcement_status === 'ENFORCING' ? 'ENFORCING' : 'AUDIT'}
        uptime={status ? formatUptime(status.uptime_seconds) : undefined}
      />

      <main className="p-6">
        {error && (
          <div className="mb-6 p-4 bg-rose-950/50 border border-rose-800 rounded-lg">
            <p className="text-rose-400 text-sm font-mono">
              ⚠️ {error} - Displaying cached data
            </p>
          </div>
        )}

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {/* Metric Cards */}
          <MetricCard
            title="Threats Neutralized"
            value={metrics?.threats_neutralized ?? 0}
            subtitle="Pods terminated for violations"
            icon="threats"
            color="rose"
          />
          
          <MetricCard
            title="Cluster Health Score"
            value={`${metrics?.cluster_health_score ?? 100}%`}
            subtitle="Based on security posture"
            icon="health"
            color="emerald"
            progress={metrics?.cluster_health_score ?? 100}
          />
          
          <MetricCard
            title="Active Policies"
            value={metrics?.active_policies ?? 0}
            subtitle="Enforcing security rules"
            icon="policies"
            color="blue"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Log Terminal - Takes 2 columns */}
          <div className="lg:col-span-2">
            <LogTerminal logs={logs} maxHeight="500px" />
          </div>

          {/* Right Column - Attack Chart */}
          <div className="space-y-4">
            <AttackChart data={attackData} title="Threat Volume" />
            
            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">
                  Total Events
                </p>
                <p className="text-2xl font-mono text-white">
                  {metrics?.total_events ?? 0}
                </p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4">
                <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">
                  Critical Alerts
                </p>
                <p className="text-2xl font-mono text-rose-400">
                  {metrics?.events_by_severity?.CRITICAL ?? 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Event Breakdown Section */}
        <div className="mt-6">
          <EventBreakdown
            eventsByType={metrics?.events_by_type ?? {}}
            eventsBySeverity={metrics?.events_by_severity ?? {}}
          />
        </div>

        {/* Footer */}
        <footer className="mt-8 pt-6 border-t border-slate-800">
          <div className="flex items-center justify-between text-slate-600 text-xs font-mono">
            <span>KUBE-SHIELD v1.0.0</span>
            <span>
              {status?.simulation_enabled && (
                <span className="text-amber-500 mr-4">
                  ● SIMULATION MODE
                </span>
              )}
              Zero-Trust Kubernetes Security Operator
            </span>
          </div>
        </footer>
      </main>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-900 border border-slate-800 mb-4">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        </div>
        <h2 className="text-white text-lg font-medium mb-2">
          Initializing Kube-Shield
        </h2>
        <p className="text-slate-500 text-sm font-mono">
          Connecting to security infrastructure...
        </p>
      </div>
    </div>
  );
}

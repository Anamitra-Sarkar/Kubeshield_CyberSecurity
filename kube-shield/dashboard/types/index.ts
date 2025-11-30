/**
 * Type definitions for security events and API responses
 */

export interface SecurityEvent {
  id: string;
  timestamp: string;
  event_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  pod_name: string;
  namespace: string;
  container?: string;
  image?: string;
  reason: string;
  action: string;
  policy_name: string;
  node_name?: string;
  description: string;
  received_at: string;
  source: string;
}

export interface Metrics {
  threats_neutralized: number;
  cluster_health_score: number;
  active_policies: number;
  total_events: number;
  events_by_severity: Record<string, number>;
  events_by_type: Record<string, number>;
}

export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
}

export interface AttackVolumeData {
  data: TimeSeriesPoint[];
  interval: string;
}

export interface StatusResponse {
  enforcement_status: string;
  uptime_seconds: number;
  total_logs: number;
  simulation_enabled: boolean;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  simulation_active: boolean;
}

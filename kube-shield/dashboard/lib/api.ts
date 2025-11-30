/**
 * API client for the Kube-Shield Audit Service
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_AUDIT_SERVICE_URL || 'http://localhost:8000';

export async function fetchLogs(limit?: number) {
  const params = limit ? `?limit=${limit}` : '';
  const response = await fetch(`${API_BASE_URL}/api/v1/logs${params}`, {
    next: { revalidate: 0 },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch logs');
  }
  return response.json();
}

export async function fetchMetrics() {
  const response = await fetch(`${API_BASE_URL}/api/v1/metrics`, {
    next: { revalidate: 0 },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch metrics');
  }
  return response.json();
}

export async function fetchAttackVolume(minutes = 30) {
  const response = await fetch(`${API_BASE_URL}/api/v1/attack-volume?minutes=${minutes}`, {
    next: { revalidate: 0 },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch attack volume');
  }
  return response.json();
}

export async function fetchStatus() {
  const response = await fetch(`${API_BASE_URL}/status`, {
    next: { revalidate: 0 },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch status');
  }
  return response.json();
}

export async function fetchHealth() {
  const response = await fetch(`${API_BASE_URL}/health`, {
    next: { revalidate: 0 },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch health');
  }
  return response.json();
}

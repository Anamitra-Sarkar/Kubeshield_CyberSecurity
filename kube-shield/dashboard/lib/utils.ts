/**
 * Utility functions for formatting and data transformation
 */

export function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  
  if (days > 0) {
    return `${days}d ${hours}h ${mins}m`;
  }
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
}

export function getSeverityColor(severity: string): {
  bg: string;
  text: string;
  border: string;
} {
  switch (severity.toUpperCase()) {
    case 'CRITICAL':
      return {
        bg: 'bg-rose-950',
        text: 'text-rose-400',
        border: 'border-rose-800',
      };
    case 'HIGH':
      return {
        bg: 'bg-orange-950',
        text: 'text-orange-400',
        border: 'border-orange-800',
      };
    case 'MEDIUM':
      return {
        bg: 'bg-amber-950',
        text: 'text-amber-400',
        border: 'border-amber-800',
      };
    case 'LOW':
      return {
        bg: 'bg-blue-950',
        text: 'text-blue-400',
        border: 'border-blue-800',
      };
    default:
      return {
        bg: 'bg-slate-800',
        text: 'text-slate-400',
        border: 'border-slate-700',
      };
  }
}

export function getEventTypeIcon(eventType: string): string {
  const icons: Record<string, string> = {
    PRIVILEGED_CONTAINER: '🔓',
    DISALLOWED_REGISTRY: '📦',
    CVE_DETECTED: '🐛',
    UNAUTHORIZED_EGRESS: '🌐',
    CRYPTO_MINING: '⛏️',
    LATERAL_MOVEMENT: '↔️',
    CONFIG_DRIFT: '📊',
    ROOT_USER: '👤',
    HOST_NETWORK: '🔌',
    PRIVILEGE_ESCALATION: '⬆️',
    DATA_EXFILTRATION: '📤',
    SUSPICIOUS_PROCESS: '⚠️',
  };
  return icons[eventType] || '🔒';
}

export function getActionColor(action: string): string {
  switch (action.toUpperCase()) {
    case 'TERMINATED':
      return 'text-rose-500';
    case 'BLOCKED':
      return 'text-orange-500';
    case 'AUDIT':
      return 'text-amber-500';
    default:
      return 'text-slate-400';
  }
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return `${str.substring(0, length)}...`;
}

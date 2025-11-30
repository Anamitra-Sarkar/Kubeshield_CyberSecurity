"""
Log storage service with in-memory storage and maximum capacity.
"""
import threading
import uuid
from collections import deque
from datetime import datetime, timedelta
from typing import Optional

from ..models import SecurityEvent, StoredEvent


class LogStorage:
    """Thread-safe in-memory log storage with maximum capacity."""
    
    def __init__(self, max_logs: int = 100):
        self._logs: deque[StoredEvent] = deque(maxlen=max_logs)
        self._lock = threading.Lock()
        self._max_logs = max_logs
        self._time_series: deque[tuple[datetime, int]] = deque(maxlen=720)  # 1 hour at 5s intervals
        
    def add(self, event: SecurityEvent, source: str = "operator") -> StoredEvent:
        """Add a new event to storage."""
        stored_event = StoredEvent(
            id=str(uuid.uuid4()),
            timestamp=event.timestamp,
            event_type=event.event_type,
            severity=event.severity,
            pod_name=event.pod_name,
            namespace=event.namespace,
            container=event.container,
            image=event.image,
            reason=event.reason,
            action=event.action,
            policy_name=event.policy_name,
            node_name=event.node_name,
            description=event.description,
            received_at=datetime.utcnow().isoformat() + "Z",
            source=source,
        )
        
        with self._lock:
            self._logs.append(stored_event)
            self._update_time_series()
            
        return stored_event
    
    def _update_time_series(self) -> None:
        """Update time series data for attack volume tracking."""
        now = datetime.utcnow()
        # Round to nearest 5 seconds
        rounded = now.replace(second=(now.second // 5) * 5, microsecond=0)
        
        if self._time_series and self._time_series[-1][0] == rounded:
            # Increment existing bucket
            ts, count = self._time_series[-1]
            self._time_series[-1] = (ts, count + 1)
        else:
            self._time_series.append((rounded, 1))
    
    def get_all(self, limit: Optional[int] = None, severity: Optional[str] = None) -> list[StoredEvent]:
        """Get all stored events, optionally filtered."""
        with self._lock:
            events = list(self._logs)
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        # Return in reverse chronological order
        events.reverse()
        
        if limit:
            return events[:limit]
        return events
    
    def get_by_id(self, event_id: str) -> Optional[StoredEvent]:
        """Get a specific event by ID."""
        with self._lock:
            for event in self._logs:
                if event.id == event_id:
                    return event
        return None
    
    def count(self) -> int:
        """Get total number of stored events."""
        with self._lock:
            return len(self._logs)
    
    def get_metrics(self) -> dict:
        """Calculate metrics from stored events."""
        with self._lock:
            events = list(self._logs)
        
        if not events:
            return {
                "threats_neutralized": 0,
                "cluster_health_score": 100.0,
                "active_policies": 0,
                "total_events": 0,
                "events_by_severity": {},
                "events_by_type": {},
            }
        
        # Count by severity
        by_severity: dict[str, int] = {}
        for e in events:
            by_severity[e.severity] = by_severity.get(e.severity, 0) + 1
        
        # Count by type
        by_type: dict[str, int] = {}
        for e in events:
            by_type[e.event_type] = by_type.get(e.event_type, 0) + 1
        
        # Count unique policies
        policies = set(e.policy_name for e in events)
        
        # Count terminated threats
        terminated = sum(1 for e in events if e.action == "TERMINATED")
        
        # Calculate health score (higher is better)
        # Base 100, minus penalty for critical/high events
        critical_count = by_severity.get("CRITICAL", 0)
        high_count = by_severity.get("HIGH", 0)
        health_penalty = (critical_count * 5) + (high_count * 2)
        health_score = max(0.0, min(100.0, 100.0 - health_penalty))
        
        return {
            "threats_neutralized": terminated,
            "cluster_health_score": round(health_score, 1),
            "active_policies": len(policies),
            "total_events": len(events),
            "events_by_severity": by_severity,
            "events_by_type": by_type,
        }
    
    def get_attack_volume(self, minutes: int = 30) -> list[tuple[str, int]]:
        """Get attack volume time series for the last N minutes."""
        with self._lock:
            time_series = list(self._time_series)
        
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        result = []
        
        for ts, count in time_series:
            if ts >= cutoff:
                result.append((ts.isoformat() + "Z", count))
        
        return result
    
    def clear(self) -> int:
        """Clear all stored events. Returns count of cleared events."""
        with self._lock:
            count = len(self._logs)
            self._logs.clear()
            self._time_series.clear()
        return count


# Global singleton instance
_log_storage: Optional[LogStorage] = None


def get_log_storage(max_logs: int = 100) -> LogStorage:
    """Get the global log storage instance."""
    global _log_storage
    if _log_storage is None:
        _log_storage = LogStorage(max_logs)
    return _log_storage

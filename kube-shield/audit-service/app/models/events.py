"""
Pydantic models for security events and API responses.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Security event severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class EventType(str, Enum):
    """Types of security events."""
    PRIVILEGED_CONTAINER = "PRIVILEGED_CONTAINER"
    DISALLOWED_REGISTRY = "DISALLOWED_REGISTRY"
    ROOT_USER = "ROOT_USER"
    HOST_NETWORK = "HOST_NETWORK"
    CVE_DETECTED = "CVE_DETECTED"
    UNAUTHORIZED_EGRESS = "UNAUTHORIZED_EGRESS"
    SUSPICIOUS_PROCESS = "SUSPICIOUS_PROCESS"
    CONFIG_DRIFT = "CONFIG_DRIFT"
    CRYPTO_MINING = "CRYPTO_MINING"
    LATERAL_MOVEMENT = "LATERAL_MOVEMENT"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"


class SecurityEvent(BaseModel):
    """Model representing a security event."""
    
    timestamp: str = Field(..., description="ISO 8601 timestamp of the event")
    event_type: str = Field(..., alias="eventType", description="Type of security event")
    severity: str = Field(..., description="Severity level of the event")
    pod_name: str = Field(..., alias="podName", description="Name of the affected pod")
    namespace: str = Field(..., description="Kubernetes namespace")
    container: Optional[str] = Field(None, description="Container name if applicable")
    image: Optional[str] = Field(None, description="Container image if applicable")
    reason: str = Field(..., description="Brief reason for the event")
    action: str = Field(..., description="Action taken (TERMINATED, AUDIT, etc.)")
    policy_name: str = Field(..., alias="policyName", description="Name of the policy that triggered")
    node_name: Optional[str] = Field(None, alias="nodeName", description="Node where the pod runs")
    description: str = Field(..., description="Detailed description of the event")
    
    class Config:
        populate_by_name = True


class StoredEvent(BaseModel):
    """Model for stored events with additional metadata."""
    
    id: str = Field(..., description="Unique event ID")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    event_type: str = Field(..., description="Type of security event")
    severity: str = Field(..., description="Severity level")
    pod_name: str = Field(..., description="Pod name")
    namespace: str = Field(..., description="Namespace")
    container: Optional[str] = None
    image: Optional[str] = None
    reason: str = Field(..., description="Event reason")
    action: str = Field(..., description="Action taken")
    policy_name: str = Field(..., description="Policy name")
    node_name: Optional[str] = None
    description: str = Field(..., description="Event description")
    received_at: str = Field(..., description="Time event was received by service")
    source: str = Field(default="operator", description="Source of the event")


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""
    
    threats_neutralized: int = Field(..., description="Total threats neutralized")
    cluster_health_score: float = Field(..., description="Cluster health percentage")
    active_policies: int = Field(..., description="Number of active policies")
    total_events: int = Field(..., description="Total events logged")
    events_by_severity: dict[str, int] = Field(..., description="Events grouped by severity")
    events_by_type: dict[str, int] = Field(..., description="Events grouped by type")


class TimeSeriesPoint(BaseModel):
    """A single point in time series data."""
    
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    value: int = Field(..., description="Value at this time point")


class AttackVolumeResponse(BaseModel):
    """Response model for attack volume over time."""
    
    data: list[TimeSeriesPoint] = Field(..., description="Time series attack data")
    interval: str = Field(..., description="Time interval between points")


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="Service version")
    simulation_active: bool = Field(..., description="Whether simulation is running")


class StatusResponse(BaseModel):
    """Response model for system status."""
    
    enforcement_status: str = Field(..., description="ENFORCING or DISABLED")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    total_logs: int = Field(..., description="Total logs in storage")
    simulation_enabled: bool = Field(..., description="Simulation mode status")

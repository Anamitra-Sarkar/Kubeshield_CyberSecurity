"""
API routes for security event logging and retrieval.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..models import (
    SecurityEvent,
    StoredEvent,
    MetricsResponse,
    AttackVolumeResponse,
    TimeSeriesPoint,
)
from ..services import get_log_storage

router = APIRouter(prefix="/api/v1", tags=["logs"])


@router.post("/log", response_model=StoredEvent, status_code=201)
async def create_log(event: SecurityEvent) -> StoredEvent:
    """
    Create a new security event log.
    
    This endpoint receives security events from the Kube-Shield operator
    and stores them in memory for dashboard display.
    """
    storage = get_log_storage()
    stored_event = storage.add(event, source="operator")
    return stored_event


@router.get("/logs", response_model=list[StoredEvent])
async def get_logs(
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of logs to return"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
) -> list[StoredEvent]:
    """
    Get all stored security event logs.
    
    Returns logs in reverse chronological order (newest first).
    """
    storage = get_log_storage()
    return storage.get_all(limit=limit, severity=severity)


@router.get("/logs/{event_id}", response_model=StoredEvent)
async def get_log_by_id(event_id: str) -> StoredEvent:
    """
    Get a specific security event by ID.
    """
    storage = get_log_storage()
    event = storage.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """
    Get aggregated security metrics.
    
    Returns counts and statistics about security events.
    """
    storage = get_log_storage()
    metrics = storage.get_metrics()
    return MetricsResponse(**metrics)


@router.get("/attack-volume", response_model=AttackVolumeResponse)
async def get_attack_volume(
    minutes: int = Query(30, ge=5, le=120, description="Time range in minutes"),
) -> AttackVolumeResponse:
    """
    Get attack volume time series data.
    
    Returns the number of events per time bucket for charting.
    """
    storage = get_log_storage()
    data = storage.get_attack_volume(minutes=minutes)
    
    points = [TimeSeriesPoint(timestamp=ts, value=count) for ts, count in data]
    
    return AttackVolumeResponse(data=points, interval="5s")


@router.delete("/logs", status_code=204)
async def clear_logs():
    """
    Clear all stored logs.
    
    Used for testing and reset purposes.
    """
    storage = get_log_storage()
    storage.clear()
    return None


# Legacy endpoint for backward compatibility with original spec
legacy_router = APIRouter(tags=["legacy"])


@legacy_router.post("/log", response_model=StoredEvent, status_code=201)
async def legacy_create_log(event: SecurityEvent) -> StoredEvent:
    """Legacy endpoint: Create a new security event log."""
    storage = get_log_storage()
    stored_event = storage.add(event, source="operator")
    return stored_event


@legacy_router.get("/logs")
async def legacy_get_logs(limit: int = 50) -> list[StoredEvent]:
    """Legacy endpoint: Get stored logs."""
    storage = get_log_storage()
    return storage.get_all(limit=limit)

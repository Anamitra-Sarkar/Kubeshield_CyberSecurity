"""
Kube-Shield Audit Service
Main FastAPI application entry point.
"""
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core import get_settings
from .models import HealthResponse, StatusResponse, SecurityEvent
from .routers import router, legacy_router
from .services import get_log_storage, SimulationService

# Track start time for uptime calculation
START_TIME = time.time()

# Global simulation service reference
simulation_service: SimulationService | None = None


def simulation_callback(event: SecurityEvent) -> None:
    """Callback to store simulated events."""
    storage = get_log_storage()
    storage.add(event, source="simulation")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global simulation_service
    
    settings = get_settings()
    
    # Initialize log storage
    get_log_storage(settings.max_logs)
    
    # Start simulation if enabled
    if settings.simulation_enabled:
        simulation_service = SimulationService(
            callback=simulation_callback,
            interval=settings.simulation_interval,
            enabled=True,
        )
        simulation_service.start()
        print(f"[INFO] Simulation started with {settings.simulation_interval}s interval")
    
    yield
    
    # Cleanup
    if simulation_service:
        simulation_service.stop()


# Create FastAPI application
app = FastAPI(
    title="Kube-Shield Audit Service",
    description="Security event logging and monitoring service for Kube-Shield",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)
app.include_router(legacy_router)


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirect to docs."""
    return JSONResponse(
        content={
            "service": "Kube-Shield Audit Service",
            "version": "1.0.0",
            "docs": "/docs",
        }
    )


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Health check endpoint for Kubernetes probes."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version="1.0.0",
        simulation_active=simulation_service.is_running if simulation_service else False,
    )


@app.get("/ready", response_model=HealthResponse, tags=["health"])
async def readiness_check() -> HealthResponse:
    """Readiness check endpoint for Kubernetes probes."""
    return HealthResponse(
        status="ready",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version="1.0.0",
        simulation_active=simulation_service.is_running if simulation_service else False,
    )


@app.get("/status", response_model=StatusResponse, tags=["health"])
async def get_status() -> StatusResponse:
    """Get detailed service status."""
    storage = get_log_storage()
    uptime = time.time() - START_TIME
    
    return StatusResponse(
        enforcement_status="ENFORCING",
        uptime_seconds=round(uptime, 2),
        total_logs=storage.count(),
        simulation_enabled=simulation_service.is_running if simulation_service else False,
    )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

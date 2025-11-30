"""
Core configuration for the Audit Service.
"""
import os
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        self.app_name: str = os.getenv("APP_NAME", "Kube-Shield Audit Service")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.max_logs: int = int(os.getenv("MAX_LOGS", "100"))
        self.simulation_enabled: bool = os.getenv("SIMULATION_ENABLED", "true").lower() == "true"
        self.simulation_interval: int = int(os.getenv("SIMULATION_INTERVAL", "5"))
        self.cors_origins: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

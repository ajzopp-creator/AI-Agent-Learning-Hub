# schemas.py
# AI-Agent-Learning-Hub — Schwab API Integration
# Pydantic schemas for all persistent Schwab API file I/O

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SchwabTokenConfig(BaseModel):
    """Schema for P_020_schwab_config.json — schwab-py token file format.
    
    Note: app_key and app_secret are stored separately in credentials_cache.json
    by schwab-py. This schema reflects what schwab-py actually writes to disk.
    """

    creation_timestamp:     Optional[float]     = Field(default=None)
    token:                  Optional[dict]       = Field(default=None)
    token_metadata:         Optional[dict]       = Field(default=None)

    class Config:
        extra = "allow"   # Allow any extra fields schwab-py writes


class SchwabCredentials(BaseModel):
    """Schema for credentials_cache.json — app key and secret only."""

    app_key:    str = Field(..., description="Schwab app key")
    app_secret: str = Field(..., description="Schwab app secret")


class LastRunRecord(BaseModel):
    """Schema for P_020_last_run.json — tracks last successful API pull date."""

    last_run_date:      str                = Field(...,           description="ISO date string of last pull (YYYY-MM-DD)")
    last_run_account:   Optional[str]      = Field(default=None, description="Account number used in last run")
    last_run_timestamp: Optional[datetime] = Field(default=None, description="Full timestamp of last run")

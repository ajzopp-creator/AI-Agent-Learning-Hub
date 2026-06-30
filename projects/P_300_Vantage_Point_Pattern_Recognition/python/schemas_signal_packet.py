"""
FILE: schemas_signal_packet.py
VERSION: 1.0
DATE: 2026-06-07
AUTHOR: Claude (architect)
LAYER: schemas
DESCRIPTION:
    Pydantic models for P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0.
    Validates signal-packet JSON structure at write time.
    
    Signal packets are machine-readable handoffs from P_300 (and P_115)
    to P_400 Trade Order Management. Written to:
      <vault-root>/TradeOrderManagement/signals/YYYY-MM-DD_SYMBOL_signal.json
    
    P_300 signals: signal_source="P_300", strategy="pattern_analog"

CHANGELOG:
    - 2026-06-07 v1.0: Initial. Conforms to P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# SIGNAL PACKET CONTEXT
# ---------------------------------------------------------------------------

class SignalContext(BaseModel):
    """Contextual market data at the moment the signal fired."""
    model_config = ConfigDict(frozen=True)

    atm_at_signal: Optional[float] = Field(
        None,
        description="ATR(14) at signal time (optional)"
    )
    close_at_signal: float = Field(
        ...,
        gt=0,
        description="Close price at signal generation (audit trail)"
    )
    trailing_volume_30d: float = Field(
        ...,
        gt=0,
        description="Average daily volume, last 30 days (shares/day)"
    )
    signal_rationale: str = Field(
        ...,
        min_length=1,
        description="One-sentence or short thesis summary"
    )


# ---------------------------------------------------------------------------
# SIGNAL PACKET METADATA
# ---------------------------------------------------------------------------

class SignalMetadata(BaseModel):
    """Upstream session and source information for audit trail."""
    model_config = ConfigDict(frozen=True)

    p115_session_date: date = Field(
        ...,
        description="YYYY-MM-DD of the P_115/P_300 session that fired the signal"
    )
    p115_chart_timeframe: str = Field(
        ...,
        min_length=1,
        description="Chart timeframe (1D, 4H, 1H, etc.) — for P_300, always '1D'"
    )
    signal_source_link: str = Field(
        ...,
        min_length=1,
        description="Path to upstream P_115/P_300 .md file for traceability"
    )


# ---------------------------------------------------------------------------
# SIGNAL PACKET (Root)
# ---------------------------------------------------------------------------

class SignalPacket(BaseModel):
    """Machine-readable BUY signal handoff from P_115/P_300 to P_400."""
    model_config = ConfigDict(frozen=True)

    signal_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier (e.g., P300-2026-06-07-COHR-001)"
    )
    signal_timestamp: datetime = Field(
        ...,
        description="ISO-8601 UTC datetime when signal was generated"
    )
    signal_source: Literal["P_115", "P_300", "manual"] = Field(
        ...,
        description="Source of the signal"
    )
    strategy: str = Field(
        ...,
        min_length=1,
        description="Trading strategy (e.g., 'pattern_analog' for P_300)"
    )
    symbol: str = Field(
        ...,
        min_length=1,
        pattern="^[A-Z_]+$",
        description="Uppercase ticker symbol"
    )
    guideline_entry: float = Field(
        ...,
        gt=0,
        description="Recommended entry price from upstream signal"
    )
    guideline_stop: float = Field(
        ...,
        gt=0,
        description="Recommended stop-loss from upstream signal"
    )
    guideline_target: float = Field(
        ...,
        gt=0,
        description="Recommended profit target from upstream signal"
    )
    signal_horizon: str = Field(
        ...,
        min_length=1,
        description="Expected holding period (e.g., '3-5 days', '1-2 weeks')"
    )
    confidence_level: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        ...,
        description="Signal quality assessment"
    )
    context: SignalContext = Field(
        ...,
        description="Market data snapshot at signal time"
    )
    signal_metadata: SignalMetadata = Field(
        ...,
        description="Upstream session info and source link for audit trail"
    )

    @field_validator("guideline_entry", "guideline_stop", "guideline_target")
    @classmethod
    def validate_price_ordering(cls, v):
        """Ensure prices are non-zero and positive."""
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

    @field_validator("guideline_target")
    @classmethod
    def target_above_entry(cls, v, info):
        """Validate that target > entry (long trades)."""
        if "guideline_entry" in info.data:
            entry = info.data["guideline_entry"]
            if v <= entry:
                raise ValueError("target must be > entry for long trades")
        return v

    @field_validator("guideline_entry")
    @classmethod
    def entry_above_stop(cls, v, info):
        """Validate that entry > stop (long trades)."""
        if "guideline_stop" in info.data:
            stop = info.data["guideline_stop"]
            if v <= stop:
                raise ValueError("entry must be > stop for long trades")
        return v


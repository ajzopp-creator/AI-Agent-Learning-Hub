"""signal_schemas.py — Pydantic models for JSON signal packets.

Raw handoff artifacts between P_115/P_300 and P_400, NOT Obsidian notes.
Two versions: v1.0 (stock-only, P400SIG) and v2.0 (unified stock+options, SIGNAL_V2).

Shared sub-objects (SignalContext, SignalMetadata) provide audit trail and metadata.
No Note Standard fields, no verdict normalization, no provenance tracking.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


# ── SIGNAL PACKET SHARED SUB-OBJECTS ──────────────────────────────────────────
# Canonical context{} / signal_metadata{} pair. Shared by BOTH the legacy v1.0
# packet (P400SignalRecord) and the unified v2.0 packet (SignalV2).

class SignalContext(BaseModel):
    """context{} sub-object of a signal packet (shared by stocks and options)."""
    close_at_signal: float                       # close price at signal generation (audit)
    trailing_volume_30d: float                   # avg daily volume, last 30 days
    signal_rationale: str                        # short thesis summary
    atm_at_signal: Optional[float] = None        # ATR(14) at signal time (optional)


class SignalMetadata(BaseModel):
    """signal_metadata{} sub-object of a signal packet."""
    p115_session_date: str                       # YYYY-MM-DD of generating P_115 session
    p115_chart_timeframe: str                    # 1D | 4H | 1H | etc
    signal_source_link: str                      # path to upstream P_115/P_300 .md (audit)


# ── P_400 SIGNAL PACKET v1.0 (P400SIG) ────────────────────────────────────────
# Legacy stock-only packet. Locked to P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0.
# Retired at the SIGNAL_V2 cutover.

class P400SignalRecord(BaseModel):
    """One P_115 -> P_400 signal packet, v1.0 (JSON emit, Enhancement 1)."""
    signal_id: str                               # e.g. P115-2026-06-02-AMTM-001
    signal_timestamp: str                        # ISO 8601 (UTC) of generation
    signal_source: str                           # P_115 | P_300 | manual
    strategy: str                                # dip_buy | breakout | mean_reversion | etc
    symbol: str                                  # uppercase ticker
    guideline_entry: float                       # recommended entry price
    guideline_stop: float                        # recommended stop-loss
    guideline_target: float                      # recommended profit target
    signal_horizon: str                          # e.g. "3-5 days"
    confidence_level: str                        # HIGH | MEDIUM | LOW
    context: SignalContext
    signal_metadata: SignalMetadata


# ── UNIFIED SIGNAL PACKET v2.0 (SIGNAL_V2) ────────────────────────────────────
# Unified stock + option packet. Per P_115_P400_SIGNAL_PACKET_SCHEMA_v2_0.
# Optional/null fields discriminated by asset_class.

class AssetClass(str, Enum):
    """Discriminator for stock vs options signals."""
    STOCK = "stock"
    OPTION = "option"


class OptionType(str, Enum):
    """Options-only: call or put."""
    CALL = "call"
    PUT = "put"


class SignalV2(BaseModel):
    """Unified v2.0 signal schema for stocks and options."""
    signal_id: str
    signal_timestamp: str
    signal_source: str
    strategy: str
    symbol: str
    asset_class: AssetClass
    guideline_entry: float
    guideline_stop: float
    guideline_target: float
    signal_horizon: str
    confidence_level: str
    position_size: int
    strike_price: Optional[float] = None
    underlying_price: Optional[float] = None
    option_type: Optional[OptionType] = None
    expiration_date: Optional[str] = None
    context: SignalContext
    signal_metadata: SignalMetadata

    class Config:
        use_enum_values = True

    @field_validator("asset_class")
    @classmethod
    def validate_asset_class(cls, v):
        if v not in [AssetClass.STOCK, AssetClass.OPTION]:
            raise ValueError(f"asset_class must be 'stock' or 'option', got {v}")
        return v

    @model_validator(mode="after")
    def _check_asset_class_fields(self):
        """Enforce stock/option field completeness at the model level.

        Runs even when option fields are omitted — per-field validators skip
        absent fields that fall back to their default (None), which let
        malformed option packets through. asset_class / option_type arrive as
        plain strings here (Config.use_enum_values = True).
        """
        ac = getattr(self.asset_class, "value", self.asset_class)
        ot = getattr(self.option_type, "value", self.option_type)
        option_fields = {
            "strike_price": self.strike_price,
            "underlying_price": self.underlying_price,
            "option_type": ot,
            "expiration_date": self.expiration_date,
        }
        if ac == "option":
            missing = [k for k, val in option_fields.items() if val is None]
            if missing:
                raise ValueError(f"options require: {', '.join(missing)}")
            if ot not in ("call", "put"):
                raise ValueError(f"option_type must be 'call' or 'put', got {ot}")
            try:
                datetime.strptime(self.expiration_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"expiration_date must be YYYY-MM-DD, got {self.expiration_date}"
                )
        elif ac == "stock":
            present = [k for k, val in option_fields.items() if val is not None]
            if present:
                raise ValueError(
                    f"stock signals must leave null: {', '.join(present)}"
                )
        return self

    @field_validator("confidence_level")
    @classmethod
    def validate_confidence(cls, v):
        if v not in ["HIGH", "MEDIUM", "LOW"]:
            raise ValueError(f"confidence_level must be HIGH, MEDIUM, or LOW, got {v}")
        return v

    @field_validator("guideline_entry", "guideline_stop", "guideline_target")
    @classmethod
    def validate_prices_positive(cls, v):
        if v <= 0:
            raise ValueError(f"Price must be positive, got {v}")
        return v

    @field_validator("guideline_target")
    @classmethod
    def validate_price_logic(cls, v, info):
        entry = info.data.get("guideline_entry")
        stop = info.data.get("guideline_stop")
        if entry and v <= entry:
            raise ValueError(f"guideline_target ({v}) must be > guideline_entry ({entry})")
        if entry and stop and entry <= stop:
            raise ValueError(f"guideline_entry ({entry}) must be > guideline_stop ({stop})")
        return v
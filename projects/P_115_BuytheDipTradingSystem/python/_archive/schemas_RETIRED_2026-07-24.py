"""RETIRED 2026-07-24 -- dead code, do not import.

Only consumer was _archive\signal_writer_RETIRED_2026-06-11.py (already
retired). The live emit path (application\emit_signal.py ->
domain\signal_builder.py -> shared_resources.python_utils.write_to_vault)
never used this module -- it builds a plain dict and validates only
against the canonical shared SignalV2 schema
(shared_resources\python_utils\signal_schemas.py), which has no
signal_source enum restriction.

Retired as dead code -- unused by the live emit path, archived instead
of left live in python/ root where a future session could mistake it for
active validation. Its VALID_SOURCES restriction to {"P_115","P_300",
"manual"} was actually correct (P_116/P_118/P_910/P_920 are scan sources
analyzed BY P_115, not separate emitters -- they never belong in
signal_source), a fact this file's original retirement note got wrong.
See P_115_System_Architecture.v1.0.md v1.3/v1.4 Change Log.
"""
"""schemas.py — Pydantic models for the P_115 -> P_400 signal packet.

Mirrors P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0.md. Field declaration order
is preserved so emitted JSON matches the schema doc. Validation is pure
(no I/O), so these models are safe to construct in the domain layer.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

import config


class SignalContext(BaseModel):
    """Audit context captured at signal generation time."""

    model_config = ConfigDict(extra="forbid")

    atm_at_signal: float | None = None  # ATR(14); key name fixed by schema
    close_at_signal: float
    trailing_volume_30d: float
    signal_rationale: str


class SignalMetadata(BaseModel):
    """Linkage back to the upstream session and chart."""

    model_config = ConfigDict(extra="forbid")

    session_date: str
    chart_timeframe: str
    signal_source_link: str

    @field_validator("session_date")
    @classmethod
    def _date_format(cls, v: str) -> str:
        if not re.match(config.DATE_REGEX, v):
            raise ValueError("session_date must be YYYY-MM-DD")
        return v


class P400SignalRecord(BaseModel):
    """Full signal packet handed from P_115 to P_400."""

    model_config = ConfigDict(extra="forbid")

    signal_id: str
    signal_timestamp: str
    signal_source: str
    strategy: str
    symbol: str
    guideline_entry: float
    guideline_stop: float
    guideline_target: float
    signal_horizon: str
    confidence_level: str
    context: SignalContext
    signal_metadata: SignalMetadata

    @field_validator("signal_source")
    @classmethod
    def _source_known(cls, v: str) -> str:
        if v not in config.VALID_SOURCES:
            raise ValueError(f"signal_source must be one of {sorted(config.VALID_SOURCES)}")
        return v

    @field_validator("confidence_level")
    @classmethod
    def _confidence_known(cls, v: str) -> str:
        if v not in config.VALID_CONFIDENCE:
            raise ValueError(f"confidence_level must be one of {sorted(config.VALID_CONFIDENCE)}")
        return v

    @field_validator("symbol")
    @classmethod
    def _symbol_format(cls, v: str) -> str:
        if not re.match(config.TICKER_REGEX, v):
            raise ValueError("symbol must be an uppercase ticker (e.g. AMTM)")
        return v

    @field_validator("signal_horizon")
    @classmethod
    def _horizon_format(cls, v: str) -> str:
        if not re.match(config.HORIZON_REGEX, v):
            raise ValueError("signal_horizon must look like '3-5 days' or '1-2 weeks'")
        return v

    @model_validator(mode="after")
    def _price_order(self) -> "P400SignalRecord":
        if self.guideline_entry <= self.guideline_stop:
            raise ValueError("guideline_entry must be > guideline_stop (long)")
        if self.guideline_target <= self.guideline_entry:
            raise ValueError("guideline_target must be > guideline_entry (long)")
        return self
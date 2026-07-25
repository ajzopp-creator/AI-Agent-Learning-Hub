"""System attribution resolution chain (WO-P020-E1.007).

Decides which system a trade belongs to by consulting sources in
priority order: P_400 vault first, Tracker Dashboard second, default
last. Pure logic -- no file, network, or DB access. Both lookups are
passed in already-built by the infrastructure layer.

Shadow mode is the current operating state: resolve_shadow() computes
what the vault would have said without changing what gets written.
Tracker remains authoritative until shadow data justifies the cutover.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\domain\\system_resolver.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   domain
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Resolution:
    """Outcome of one attribution attempt.

    Attributes:
        system: Resolved system name (never None -- falls back to default).
        source: Which source produced it -- 'vault', 'tracker', or 'default'.
        vault_system: What the vault said, or None. Populated even when the
            vault did not win, so shadow mode can compare.
        vault_covered: True if any P_400 record covered this fill, whether
            or not it carried attribution. Measurable before why_code is
            populated upstream, which is why it is tracked separately.
    """

    system: str
    source: str
    vault_system: Optional[str] = None
    vault_covered: bool = False


def resolve(
    symbol: str,
    open_date: str,
    vault_lookup,
    tracker_lookup,
    default: str = "TOS_Import",
    forward_days: int = 7,
    shadow_mode: bool = True,
) -> Resolution:
    """Resolve a trade's system through the vault -> tracker -> default chain.

    Args:
        symbol: Underlying symbol.
        open_date: Fill date 'YYYY-MM-DD'.
        vault_lookup: VaultLookup instance, or None when unavailable.
        tracker_lookup: TrackerLookup instance, or None when unavailable.
        default: Fallback system name.
        forward_days: Max days a fill may lag its signal.
        shadow_mode: When True the vault result is recorded but never
            allowed to win -- tracker stays authoritative.

    Returns:
        Resolution carrying both the winning answer and the vault's
        opinion for comparison.
    """
    vault_system = None
    vault_covered = False

    if vault_lookup is not None:
        vault_system = vault_lookup.get_system(symbol, open_date, forward_days)
        vault_covered = vault_lookup.has_coverage(
            symbol, open_date, forward_days
        )

    if vault_system and not shadow_mode:
        return Resolution(
            system=vault_system,
            source="vault",
            vault_system=vault_system,
            vault_covered=vault_covered,
        )

    tracker_system = None
    if tracker_lookup is not None:
        result = tracker_lookup.get(symbol, open_date, default)
        if result != default:
            tracker_system = result

    if tracker_system:
        return Resolution(
            system=tracker_system,
            source="tracker",
            vault_system=vault_system,
            vault_covered=vault_covered,
        )

    return Resolution(
        system=default,
        source="default",
        vault_system=vault_system,
        vault_covered=vault_covered,
    )


@dataclass
class ShadowTally:
    """Running counts for one ingest batch's shadow comparison."""

    total: int = 0
    vault_covered: int = 0
    vault_attributed: int = 0
    agree: int = 0
    disagree: int = 0
    vault_only: int = 0

    def record(self, res: Resolution) -> None:
        """Fold one resolution into the tally."""
        self.total += 1
        if res.vault_covered:
            self.vault_covered += 1
        if res.vault_system:
            self.vault_attributed += 1
            if res.source == "tracker":
                if res.vault_system == res.system:
                    self.agree += 1
                else:
                    self.disagree += 1
            elif res.source == "default":
                self.vault_only += 1

    def summary(self) -> str:
        """Return a one-line shadow summary for logging."""
        return (
            f"Vault shadow: {self.vault_covered}/{self.total} covered by a "
            f"P_400 record, {self.vault_attributed} carried attribution "
            f"(agree {self.agree}, disagree {self.disagree}, "
            f"vault-only {self.vault_only})"
        )

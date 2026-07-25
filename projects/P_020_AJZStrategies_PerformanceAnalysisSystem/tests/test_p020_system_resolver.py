"""Regression tests -- WO-P020-E1.007 attribution chain.

Locks in the invariants that make vault-first matching safe:
  1. Shadow mode never lets the vault overwrite the tracker's answer.
  2. DROPPED records are excluded from matching (the MS 07-02 / 07-23
     case -- a signal that was passed on must not claim a later fill).
  3. Date matching is forward-only and window-bounded.
  4. p115_linked / p300_linked are never used for attribution.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\tests\\
           test_p020_system_resolver.py
"""

import sys
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[1] / "python" / "database"
sys.path.insert(0, str(DB_DIR))

from domain.system_resolver import ShadowTally, resolve  # noqa: E402
from infrastructure.vault_system_reader import (  # noqa: E402
    _extract_system,
    _parse_frontmatter,
)
from vault_schemas import VaultEntry, VaultLookup  # noqa: E402


def _vault(*entries: VaultEntry) -> VaultLookup:
    """Build a VaultLookup from entries, indexing both maps."""
    lk = VaultLookup(total_records=len(entries))
    for e in entries:
        lk.covered.setdefault(e.symbol, []).append(e)
        if e.system:
            lk.attributed.setdefault(e.symbol, []).append(e)
    return lk


class _FakeTracker:
    """Minimal stand-in exposing TrackerLookup's get() contract."""

    def __init__(self, mapping):
        self._m = mapping

    def get(self, symbol, trade_date, default="TOS_Import"):
        return self._m.get((symbol.upper(), trade_date), default)


# -- 1. shadow mode -----------------------------------------------------------

def test_shadow_mode_never_lets_vault_win():
    """Vault has an answer, tracker disagrees -- tracker must win."""
    vault = _vault(
        VaultEntry(symbol="AAPL", signal_date="2026-07-20",
                   system="VPT", lifecycle_status="SUBMITTED")
    )
    tracker = _FakeTracker({("AAPL", "2026-07-22"): "P_115"})

    res = resolve("AAPL", "2026-07-22", vault, tracker, shadow_mode=True)

    assert res.system == "P_115"
    assert res.source == "tracker"
    assert res.vault_system == "VPT"


def test_vault_wins_when_shadow_mode_off():
    """The same inputs flip once shadow mode is disabled."""
    vault = _vault(
        VaultEntry(symbol="AAPL", signal_date="2026-07-20",
                   system="VPT", lifecycle_status="SUBMITTED")
    )
    tracker = _FakeTracker({("AAPL", "2026-07-22"): "P_115"})

    res = resolve("AAPL", "2026-07-22", vault, tracker, shadow_mode=False)

    assert res.system == "VPT"
    assert res.source == "vault"


# -- 2. date window -----------------------------------------------------------

def test_signal_after_fill_never_matches():
    """A signal cannot post-date its own fill -- forward-only window."""
    vault = _vault(
        VaultEntry(symbol="MSFT", signal_date="2026-07-25",
                   system="BTD", lifecycle_status="SUBMITTED")
    )
    res = resolve("MSFT", "2026-07-20", vault, None, shadow_mode=False)

    assert res.system == "TOS_Import"
    assert res.vault_covered is False


def test_signal_outside_forward_window_never_matches():
    """MS case: signal 07-02, fill 07-23 -- 21 days, outside a 7-day window."""
    vault = _vault(
        VaultEntry(symbol="MS", signal_date="2026-07-02",
                   system="VPT", lifecycle_status="SUBMITTED")
    )
    res = resolve("MS", "2026-07-23", vault, None,
                  forward_days=7, shadow_mode=False)

    assert res.system == "TOS_Import"


def test_nearest_signal_wins_within_window():
    """Two candidates in range -- the closest signal_date is chosen."""
    vault = _vault(
        VaultEntry(symbol="NVDA", signal_date="2026-07-18",
                   system="BTD", lifecycle_status="SUBMITTED"),
        VaultEntry(symbol="NVDA", signal_date="2026-07-21",
                   system="EZB", lifecycle_status="SUBMITTED"),
    )
    res = resolve("NVDA", "2026-07-22", vault, None, shadow_mode=False)

    assert res.system == "EZB"


# -- 3. coverage vs attribution ----------------------------------------------

def test_coverage_true_without_attribution():
    """Current live state: record exists, why_code null -- covered, unattributed."""
    vault = _vault(
        VaultEntry(symbol="MRCY", signal_date="2026-07-23",
                   system=None, lifecycle_status="SUBMITTED")
    )
    res = resolve("MRCY", "2026-07-25", vault, None, shadow_mode=True)

    assert res.vault_covered is True
    assert res.vault_system is None
    assert res.system == "TOS_Import"


def test_missing_vault_degrades_to_tracker():
    """vault_lookup=None must not raise -- tracker-only matching."""
    tracker = _FakeTracker({("EBAY", "2026-07-20"): "SNT"})
    res = resolve("EBAY", "2026-07-20", None, tracker, shadow_mode=True)

    assert res.system == "SNT"
    assert res.source == "tracker"
    assert res.vault_covered is False


# -- 4. attribution field selection ------------------------------------------

def test_linked_booleans_are_never_attribution():
    """189/191 records carry p300_linked=true -- a default, not a signal."""
    fields = {
        "ticker": "WMT",
        "p115_linked": "false",
        "p300_linked": "true",
    }
    assert _extract_system(fields) is None


def test_why_code_preferred_over_signal_source():
    """VAULT_ATTRIBUTION_FIELDS order decides which field wins."""
    fields = {"why_code": "btd", "signal_source": "P_300"}
    assert _extract_system(fields) == "BTD"


def test_frontmatter_skips_null_and_nested_values():
    """'null' scalars are dropped; write_route_history lines are ignored."""
    note = (
        "---\n"
        "ticker: WMT\n"
        "why_code: null\n"
        "write_route_history:\n"
        "  - {write_route: BUY, run_date: 2026-07-14}\n"
        "lifecycle_status: PAPER\n"
        "---\n\n# WMT\n"
    )
    fields = _parse_frontmatter(note)

    assert fields["ticker"] == "WMT"
    assert "why_code" not in fields
    assert "write_route" not in fields
    assert fields["lifecycle_status"] == "PAPER"


# -- 5. tally -----------------------------------------------------------------

def test_tally_counts_disagreement():
    """Vault and tracker both answer but differ -- counted as disagree."""
    vault = _vault(
        VaultEntry(symbol="AAPL", signal_date="2026-07-20",
                   system="VPT", lifecycle_status="SUBMITTED")
    )
    tracker = _FakeTracker({("AAPL", "2026-07-22"): "P_115"})
    tally = ShadowTally()

    tally.record(resolve("AAPL", "2026-07-22", vault, tracker,
                         shadow_mode=True))

    assert tally.total == 1
    assert tally.disagree == 1
    assert tally.agree == 0

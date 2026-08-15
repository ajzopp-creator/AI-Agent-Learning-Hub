"""test_ranking.py -- Invariants for domain/ranking.py composite scoring.

WO-P400-E5.003 Scope 3. These tests encode WHY the score is shaped the way it
is, not merely that it runs. Each one corresponds to a design decision that
would otherwise be a comment nobody re-checks.

Placed in the tests directory per the Hub standard ratified in WO-P000-E13.001 Phase 1.
Imports resolve via the project conftest.py -- no sys.path manipulation here.
"""

from domain.ranking import order_by_score, score_candidate


# ---------------------------------------------------------------------------
# ATR headroom must discriminate among candidates that all cleared the gate
# ---------------------------------------------------------------------------

def test_greater_atr_headroom_scores_higher():
    """THE acceptance criterion (WO-P400-E5.003).

    Everything reaching ranking already cleared QUANT's stop >= 1x ATR gate,
    so the question ranking answers is not "is the stop legal" but "how much
    room does it actually have". A stop at 1.05x ATR is one bad tick from the
    block line; 2.40x has real room. Identical on every other factor, the
    roomier setup must rank higher.
    """
    tight, _ = score_candidate(3.5, 1.05, 0.10, 5_000_000, 0.5)
    roomy, _ = score_candidate(3.5, 2.40, 0.10, 5_000_000, 0.5)
    assert roomy > tight


def test_headroom_at_floor_earns_no_credit():
    """1.0x ATR is the entry requirement, not an achievement -- it scores 0
    on the headroom factor. Scoring the raw multiple would hand every
    candidate 33% of that factor for merely being legal."""
    _, components = score_candidate(3.5, 1.0, 0.10, 5_000_000, 0.5)
    assert components["atr_headroom"] == 0.0


# ---------------------------------------------------------------------------
# R:R alone must not drive the sort
# ---------------------------------------------------------------------------

def test_high_rr_on_thin_stop_loses_to_solid_setup():
    """R:R's denominator is risk-per-share, so a tight stop inflates it
    mechanically while making the setup less survivable. Live shape,
    2026-08-05: INDI screened R:R 22.78 on a 0.05 stop against 0.31 ATR --
    highest ratio in the batch, least survivable setup in it. QUANT blocks
    that case upstream, but the same distortion exists in milder form among
    candidates that DO pass, and ranking must not reward it."""
    inflated, _ = score_candidate(6.0, 1.02, 0.30, 2_000_000, 1.0)
    solid, _ = score_candidate(3.0, 2.60, 0.15, 8_000_000, 0.3)
    assert solid > inflated


def test_rr_saturates_at_ceiling():
    """Above the ceiling, extra R:R buys nothing -- this is what stops a
    mechanically inflated ratio from dominating."""
    _, at_ceiling = score_candidate(6.0, 2.0, 0.1, 5_000_000, 0.5)
    _, far_above = score_candidate(50.0, 2.0, 0.1, 5_000_000, 0.5)
    assert at_ceiling["rr"] == far_above["rr"] == 1.0


# ---------------------------------------------------------------------------
# Bounds and shape
# ---------------------------------------------------------------------------

def test_score_stays_within_unit_interval():
    """Score is a bounded composite. Out-of-range inputs must clamp, not
    escape the interval -- a score above 1.0 would break the schema's
    Field(ge=0.0, le=1.0) at the boundary and fail the run."""
    worst, _ = score_candidate(0.0, 1.0, 99.0, 1.0, 99.0)
    best, _ = score_candidate(99.0, 99.0, 0.0, 99_000_000, 0.0)
    assert 0.0 <= worst <= 1.0
    assert 0.0 <= best <= 1.0
    assert best > worst


def test_all_five_components_reported():
    """score_components exists so an ordering can be audited against its
    inputs. A missing factor would make the rank unexplainable."""
    _, components = score_candidate(3.5, 2.0, 0.1, 5_000_000, 0.5)
    assert set(components) == {"rr", "atr_headroom", "spread", "liquidity", "drift"}


def test_tighter_spread_and_more_volume_score_higher():
    """Direction check on the two inverted/log factors -- guards against a
    sign flip that would silently rank illiquid, wide-spread names first."""
    _, wide = score_candidate(3.5, 2.0, 0.90, 5_000_000, 0.5)
    _, tight = score_candidate(3.5, 2.0, 0.05, 5_000_000, 0.5)
    assert tight["spread"] > wide["spread"]
    _, thin = score_candidate(3.5, 2.0, 0.1, 150_000, 0.5)
    _, deep = score_candidate(3.5, 2.0, 0.1, 15_000_000, 0.5)
    assert deep["liquidity"] > thin["liquidity"]


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------

def test_order_is_deterministic_regardless_of_input_order():
    """The same batch must produce the same table every run, or rankings
    cannot be compared across sessions. Ties break alphabetically -- arbitrary
    but stable."""
    rows = [{"symbol": "ZZZ", "score": 0.5},
            {"symbol": "AAA", "score": 0.5},
            {"symbol": "MMM", "score": 0.9}]
    forward = [c["symbol"] for c in order_by_score([dict(r) for r in rows])]
    backward = [c["symbol"] for c in order_by_score([dict(r) for r in reversed(rows)])]
    assert forward == backward == ["MMM", "AAA", "ZZZ"]


def test_ranks_are_contiguous_from_one():
    """Rank is the reading order. A gap or a zero would mean a candidate was
    dropped between scoring and display."""
    rows = [{"symbol": s, "score": v} for s, v in
            [("AAA", 0.9), ("BBB", 0.7), ("CCC", 0.5), ("DDD", 0.3)]]
    ordered = order_by_score(rows)
    assert [c["rank"] for c in ordered] == [1, 2, 3, 4]


def test_empty_batch_returns_empty():
    """A screen where nothing is APPROVED is a normal outcome, not an error --
    2026-08-05 produced exactly that on 7 of 7 symbols."""
    assert order_by_score([]) == []

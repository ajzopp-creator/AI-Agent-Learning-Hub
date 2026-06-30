"""vehicle_selector.py -- Compare stock vs option R:R for a given setup.

Pure logic only -- no I/O, no network calls, no print.
Given stock sizing result, options sizing result, and the options council
viability verdict, returns comparison dict with recommendation. Neither
path is forced -- data drives the choice, and a council BLOCK on the
option side can never be silently outranked by raw R:R math.

Architecture v2.1 Section 7.3. Fixed under WO-P400-E3.004 (items 1, 2):
previously option_viable counted a 0-contract/override-required option as
"viable" and let it win the recommendation on R:R alone with no warning;
and options_council.py viability gates (OI/spread/RR-parity/IV-rank) were
never invoked anywhere in the live path. Both fixed here.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from config import MIN_ACCEPTABLE_RR
from domain.sizing import SizingResult
from domain.options_sizer import OptionSizingResult
from domain.options_council import OptionsCouncilResult

logger = logging.getLogger("p400.vehicle_selector")


@dataclass
class VehicleComparison:
    """Side-by-side comparison of stock vs option paths."""

    symbol: str
    stock_rr: float
    stock_shares: int
    stock_dollar_risk: float
    stock_viable: bool                  # shares > 0 and rr >= 2.0

    option_rr: float
    option_contracts: int
    option_dollar_risk: float
    option_viable: bool                 # STRICT: contracts > 0 (never override) and
                                         # rr >= 2.0 and council verdict != BLOCK
    option_override_available: bool     # True if 0 contracts but override would be
                                         # possible (council didn't BLOCK the strike itself)
    option_method: str                  # "chart_based" | "risk_budget_first"
    option_override_required: bool      # raw sizer flag (0 contracts after gate math)

    option_council_verdict: str         # "PASS" | "BLOCK" | "CAUTION" | "NOT_RUN"
    option_council_blocks: list
    option_council_cautions: list

    recommended: str                    # "STOCK" | "OPTION" | "SPREAD" | "OPTION_OVERRIDE_ONLY" | "NEITHER"
    recommendation_reason: str
    spread_recommended: bool            # True if IV rank > 50


def compare_vehicles(
    symbol: str,
    stock_sizing: SizingResult,
    option_sizing: OptionSizingResult,
    options_council_result: Optional[OptionsCouncilResult] = None,
) -> VehicleComparison:
    """Compare stock and option paths; return recommendation.

    Recommendation logic (post WO-P400-E3.004 fix):
    - Council BLOCK on the option (OI/spread/RR-parity/RR-min) removes the
      option from contention entirely -- it can never win, no matter what
      its raw R:R looks like. The block reason is surfaced in the result.
    - option_viable requires a REAL contract count (> 0), not an
      override-required 0-contract result. Override is tracked separately
      via option_override_available so it never silently outranks a
      fully-viable stock trade.
    - Both viable (real contracts, no block): higher R:R wins; option wins
      ties (leverage benefit).
    - Only stock viable: STOCK.
    - Only option viable (real contracts, stock sizes to 0): OPTION.
    - Option override-only (0 contracts, not blocked) AND stock viable:
      STOCK wins; override path noted but does not win on its own.
    - Option override-only AND stock NOT viable: OPTION_OVERRIDE_ONLY --
      distinct outcome, never silently relabeled "OPTION".
    - Neither viable, no override path: NEITHER.
    - Spread recommended (IV > 50): flag regardless of winner, but only
      attaches to a non-blocked option.

    Args:
        symbol: Ticker symbol.
        stock_sizing: Output of three_gate_size().
        option_sizing: Output of size_option_chart_based() or size_option_risk_budget().
        options_council_result: Output of run_options_council(). If None,
            council_verdict reports "NOT_RUN" and option viability falls
            back to contracts/rr only (council gates not evaluated --
            should not happen on the live compare path post-fix).

    Returns:
        VehicleComparison with recommendation and reasoning.
    """
    stock_viable = stock_sizing.shares > 0 and stock_sizing.rr_valid

    council_verdict = options_council_result.verdict if options_council_result else "NOT_RUN"
    council_blocked = council_verdict == "BLOCK"
    council_blocks = list(options_council_result.blocks) if options_council_result else []
    council_cautions = list(options_council_result.cautions) if options_council_result else []

    option_viable = (
        option_sizing.contracts > 0
        and option_sizing.rr_valid
        and not council_blocked
    )
    option_override_available = (
        option_sizing.contracts == 0
        and option_sizing.override_required
        and option_sizing.rr_valid
        and not council_blocked
    )

    if council_blocked:
        # Option is disqualified outright -- block reason wins regardless of R:R.
        block_summary = "; ".join(council_blocks) if council_blocks else "viability gate failed"
        if stock_viable:
            recommended = "STOCK"
            reason = f"Option BLOCKED by options council ({block_summary}) -- stock used."
        else:
            recommended = "NEITHER"
            reason = (f"Option BLOCKED by options council ({block_summary}); "
                      "stock also not viable.")
    elif stock_viable and option_viable:
        if option_sizing.rr_option >= stock_sizing.rr_at_t1:
            recommended = "OPTION"
            reason = (f"Option R:R {option_sizing.rr_option:.2f} >= "
                      f"stock R:R {stock_sizing.rr_at_t1:.2f} -- option preferred")
        else:
            recommended = "STOCK"
            reason = (f"Stock R:R {stock_sizing.rr_at_t1:.2f} > "
                      f"option R:R {option_sizing.rr_option:.2f} -- stock preferred")
    elif stock_viable and option_override_available:
        recommended = "STOCK"
        reason = (f"Stock viable ({stock_sizing.shares} sh, R:R {stock_sizing.rr_at_t1:.2f}). "
                  f"Option sizes to 0 contracts -- OVERRIDE REQUIRED to trade 1 "
                  f"(risk_per_contract ${option_sizing.risk_per_contract:.2f}). "
                  "Stock used; option available only via explicit override.")
    elif stock_viable:
        recommended = "STOCK"
        reason = "Stock viable; option path blocked or R:R insufficient"
    elif option_viable:
        recommended = "OPTION"
        reason = "Stock sizes to 0 or R:R fails; option path viable"
    elif option_override_available:
        recommended = "OPTION_OVERRIDE_ONLY"
        reason = (f"Stock not viable. Option sizes to 0 contracts -- OVERRIDE REQUIRED "
                  f"to trade 1 (risk_per_contract ${option_sizing.risk_per_contract:.2f}). "
                  "No vehicle is viable without an explicit override.")
    else:
        recommended = "NEITHER"
        reason = "Neither stock nor option clears viability gates"

    if option_sizing.spread_recommended and not council_blocked:
        if recommended == "OPTION":
            recommended = "SPREAD"
        reason += " -- IV rank > 50, spread structure preferred over single-leg"

    return VehicleComparison(
        symbol=symbol,
        stock_rr=stock_sizing.rr_at_t1,
        stock_shares=stock_sizing.shares,
        stock_dollar_risk=stock_sizing.dollar_risk,
        stock_viable=stock_viable,
        option_rr=option_sizing.rr_option,
        option_contracts=option_sizing.contracts,
        option_dollar_risk=option_sizing.total_risk_dollars,
        option_viable=option_viable,
        option_override_available=option_override_available,
        option_method=option_sizing.method,
        option_override_required=option_sizing.override_required,
        option_council_verdict=council_verdict,
        option_council_blocks=council_blocks,
        option_council_cautions=council_cautions,
        recommended=recommended,
        recommendation_reason=reason,
        spread_recommended=option_sizing.spread_recommended and not council_blocked,
    )
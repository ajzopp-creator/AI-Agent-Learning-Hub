"""fetch_chain.py -- `fetch-chain` CLI command (WO-P400-E4.002).

Fetches candidates -> domain\chain_selector.py picks one (or --strike/
--expiration override skips selection entirely) -> OptionChainInput ->
writes chain_SYMBOL.json. Manual override path is unchanged from before
this WO; auto-select is new.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import (
    OPTION_OI_MINIMUM,
    OPTION_SELECTION_MAX_DTE,
    OPTION_SELECTION_MIN_DTE,
    OPTION_SELECTION_TARGET_DELTA,
    OPTION_SPREAD_MAX_PCT,
    SCHWAB_CONFIG_PATH,
    SCHWAB_TOKEN_PATH,
)
from domain.chain_selector import ChainCandidate, select_optimal_contract
from schemas import OptionChainInput

PYTHON_DIR = Path(__file__).resolve().parents[1]  # chain_SYMBOL.json lives here


def _spread_pct(bid: float, ask: float) -> float:
    mid = (bid + ask) / 2
    return (ask - bid) / mid * 100 if mid > 0 else 0.0


def _viability_warning(chain: OptionChainInput) -> Optional[str]:
    """Scope 6 (WO-P400-E5.003): report-only check at fetch time -- the
    authoritative gates still live in options_council.py and are unchanged.
    Found live 2026-08-05: auto-selection could pick a contract already
    failing both gates with no console signal until compare/evaluate ran.
    """
    problems = []
    if chain.open_interest < OPTION_OI_MINIMUM:
        problems.append(f"OI={chain.open_interest} < {OPTION_OI_MINIMUM} minimum")
    if chain.spread_pct_of_mid > OPTION_SPREAD_MAX_PCT:
        problems.append(f"spread={chain.spread_pct_of_mid:.1f}% > {OPTION_SPREAD_MAX_PCT}% max")
    return "; ".join(problems) if problems else None


def cmd_fetch_chain(
    symbol: str,
    option_type: str,
    strike: Optional[float] = None,
    expiration: Optional[str] = None,
) -> int:
    from infrastructure.schwab_market_data import get_chain_candidates, get_quote_data

    symbol = symbol.upper()

    quote = get_quote_data(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH, symbol)
    if quote is None or quote["price"] is None:
        print(f"[ERROR] Could not fetch underlying quote for {symbol}. "
              f"No file written -- fall back to manual/TOS entry.")
        return 1

    candidates = get_chain_candidates(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH, symbol, option_type)
    if candidates is None:
        print(f"[ERROR] Could not fetch option chain for {symbol}. "
              f"No file written -- fall back to manual/TOS entry.")
        return 1

    if strike is not None and expiration is not None:
        picked = next(
            (c for c in candidates if c.strike == strike and c.expiration == expiration), None
        )
        if picked is None:
            print(f"[ERROR] No contract found at strike={strike} expiration={expiration} "
                  f"for {symbol}. No file written.")
            return 1
        print(f"[INFO] Manual override -- strike={strike} expiration={expiration}")
    else:
        picked = select_optimal_contract(
            candidates,
            target_delta=OPTION_SELECTION_TARGET_DELTA,
            min_dte=OPTION_SELECTION_MIN_DTE,
            max_dte=OPTION_SELECTION_MAX_DTE,
        )
        if picked is None:
            print(f"[ERROR] No contract for {symbol} in the "
                  f"{OPTION_SELECTION_MIN_DTE}-{OPTION_SELECTION_MAX_DTE} DTE window "
                  f"near {OPTION_SELECTION_TARGET_DELTA} delta. No file written -- "
                  f"fall back to manual/TOS entry.")
            return 1
        print(f"[INFO] Auto-selected -- strike={picked.strike} expiration={picked.expiration} "
              f"delta={picked.delta:.3f}")

    mid = (picked.bid + picked.ask) / 2
    now = datetime.now(timezone.utc)
    try:
        chain = OptionChainInput(
            symbol=symbol,
            underlying_price=quote["price"],
            expiration=picked.expiration,
            strike=picked.strike,
            option_type=option_type,
            bid=picked.bid,
            ask=picked.ask,
            mid=mid,
            delta=picked.delta,
            iv=picked.iv,
            open_interest=picked.open_interest,
            spread_pct_of_mid=_spread_pct(picked.bid, picked.ask),
            data_source="schwab_api",
            chain_timestamp=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
    except Exception as e:
        print(f"[ERROR] OptionChainInput validation failed for {symbol}: {e}. "
              f"No file written.")
        return 1

    out_path = PYTHON_DIR / f"chain_{symbol}.json"
    out_path.write_text(json.dumps(chain.model_dump(), indent=2), encoding="utf-8")
    print(f"[OK] chain_{symbol}.json written (data_source=schwab_api): {out_path}")
    print(f"  strike={chain.strike}  expiration={chain.expiration}  "
          f"delta={chain.delta:.3f}  OI={chain.open_interest}  "
          f"spread={chain.spread_pct_of_mid:.1f}%")
    warn = _viability_warning(chain)
    if warn:
        print(f"[WARN] {symbol} contract may fail options_council viability gates: {warn}")
    return 0
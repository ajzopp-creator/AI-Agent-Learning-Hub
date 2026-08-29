"""Tests for the WO-P020-E1.002-followup VERTICAL/IRON CONDOR extension to
domain.spread_leg_parser. All example description strings are real lines
pulled from actual paper AccountStatement.csv exports (2026-08-22 review),
not synthesized -- confirms the parser handles what TOS actually sends,
not an idealized version of it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domain.spread_leg_parser import parse_multi_leg_description

# Real lines, D_020_2026-08-11-AccountStatement.csv
VERTICAL_SOLD = "SOLD -1 VERTICAL SPY 100 (Weeklys) 6 AUG 26 735/730 PUT @1.40"
VERTICAL_BOT = "BOT +1 VERTICAL SPY 100 (Weeklys) 6 AUG 26 735/730 PUT @1.18"

# Real lines, D_020_2026-07-27_YTD_AccountStatement.csv / D_020_2026-08-11
IRON_CONDOR_SOLD = "SOLD -1 IRON CONDOR SPY 100 (Weeklys) 31 JUL 26 745/750/735/730 CALL/PUT @3.21"
IRON_CONDOR_BOT = "BOT +1 IRON CONDOR SPY 100 (Weeklys) 31 JUL 26 745/750/735/730 CALL/PUT @3.13"
IRON_CONDOR_NO_LEADING_ZERO_PRICE = (
    "SOLD -1 IRON CONDOR SPY 100 (Weeklys) 10 AUG 26 780/790/750/740 CALL/PUT @.69"
)


def test_vertical_sold_short_first_long_second():
    """Confirmed rule: SOLD -> first strike short, second strike long."""
    result = parse_multi_leg_description(VERTICAL_SOLD)
    assert result is not None
    assert result["strategy"] == "VERTICAL"
    assert result["leg_count"] == 2
    assert result["container_action"] == "SOLD"
    assert result["net_price"] == 1.40

    leg1, leg2 = result["legs"]
    assert leg1["strike"] == 735.0
    assert leg1["put_call"] == "PUT"
    assert leg1["direction"] == "short"
    assert leg2["strike"] == 730.0
    assert leg2["put_call"] == "PUT"
    assert leg2["direction"] == "long"
    # Both legs share the single listed expiration
    assert leg1["expiration"] == leg2["expiration"] == "6 AUG 26"


def test_vertical_bot_reverses_direction():
    """BOT container -> first strike long, second strike short (opposite
    of the SOLD case, not the same directions)."""
    result = parse_multi_leg_description(VERTICAL_BOT)
    assert result is not None
    assert result["container_action"] == "BOT"

    leg1, leg2 = result["legs"]
    assert leg1["strike"] == 735.0
    assert leg1["direction"] == "long"
    assert leg2["strike"] == 730.0
    assert leg2["direction"] == "short"


def test_iron_condor_sold_four_legs_two_rights():
    """Confirmed rule generalizes across both rights independently:
    745/750 CALL -> short 745 call / long 750 call
    735/730 PUT  -> short 735 put  / long 730 put"""
    result = parse_multi_leg_description(IRON_CONDOR_SOLD)
    assert result is not None
    assert result["strategy"] == "IRON CONDOR"
    assert result["leg_count"] == 4
    assert result["net_price"] == 3.21

    legs = result["legs"]
    assert legs[0] == {"leg_number": 1, "strike": 745.0, "put_call": "CALL",
                        "expiration": "31 JUL 26", "ratio": -1, "direction": "short"}
    assert legs[1] == {"leg_number": 2, "strike": 750.0, "put_call": "CALL",
                        "expiration": "31 JUL 26", "ratio": 1, "direction": "long"}
    assert legs[2] == {"leg_number": 3, "strike": 735.0, "put_call": "PUT",
                        "expiration": "31 JUL 26", "ratio": -1, "direction": "short"}
    assert legs[3] == {"leg_number": 4, "strike": 730.0, "put_call": "PUT",
                        "expiration": "31 JUL 26", "ratio": 1, "direction": "long"}


def test_iron_condor_bot_reverses_all_four_legs():
    result = parse_multi_leg_description(IRON_CONDOR_BOT)
    assert result is not None
    directions = [leg["direction"] for leg in result["legs"]]
    assert directions == ["long", "short", "long", "short"]


def test_iron_condor_price_with_no_leading_zero():
    """TOS sometimes writes '.69' instead of '0.69' -- must still parse."""
    result = parse_multi_leg_description(IRON_CONDOR_NO_LEADING_ZERO_PRICE)
    assert result is not None
    assert result["net_price"] == 0.69
    assert [leg["strike"] for leg in result["legs"]] == [780.0, 790.0, 750.0, 740.0]


def test_custom_format_still_parses_unaffected():
    """Regression: the original CUSTOM format (checked first internally)
    must still work exactly as before this extension."""
    desc = (
        "BOT +1 1/-1/1/-1 CUSTOM SPY 100 20 FEB 26/20 FEB 26/20 FEB 26/20 FEB 26 "
        "665/675/705/695 CALL/CALL/PUT/PUT @14.45"
    )
    result = parse_multi_leg_description(desc)
    assert result is not None
    assert result["leg_count"] == 4
    assert "strategy" not in result  # CUSTOM path never sets this key
    assert result["legs"][0]["direction"] == "long"
    assert result["legs"][1]["direction"] == "short"


def test_combo_still_gracefully_skipped():
    """COMBO remains unimplemented (one real fill ever, pre-reset) --
    must return None, not crash or misparse as CUSTOM/named-spread."""
    desc = "BOT +1 COMBO SPY 100 (Weeklys) 30 JAN 26 695/690 CALL/PUT @-1.28"
    assert parse_multi_leg_description(desc) is None


def test_single_leg_description_returns_none():
    """Ordinary single-leg lines must never match either pattern."""
    desc = "BOT +2 QBTS @2.32"
    assert parse_multi_leg_description(desc) is None


def test_none_input_returns_none():
    assert parse_multi_leg_description(None) is None

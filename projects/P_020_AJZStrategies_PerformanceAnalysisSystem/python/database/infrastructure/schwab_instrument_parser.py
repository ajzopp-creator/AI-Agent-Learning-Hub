"""Instrument-level field extraction from Schwab transferItems.

Split out of schwab_mapper.py 2026-09-15 (WO-P020-E1.018) -- schwab_mapper
was at 299/300 lines with no room left for the new expiration-field
extraction this WO needs. Single reason to change: parsing one instrument
dict's fields, independent of order aggregation/mapping orchestration
(which stays in schwab_mapper.py).
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Fee types Schwab includes in transferItems as CURRENCY instruments
FEE_TYPES = {"COMMISSION", "SEC_FEE", "OPT_REG_FEE", "TAF_FEE", "EXCHANGE_FEE"}


def extract_instrument(transfer_items: List[Dict]) -> Optional[Dict]:
    """Extract the non-CURRENCY instrument item from transferItems.

    NOTE: returns only the first non-CURRENCY leg found. Multi-leg orders
    (spreads) have more than one such leg -- not yet supported, tracked in
    WO-P020-E1.002. Single-leg calls/puts/stock are unaffected.

    Args:
        transfer_items: List of transferItem dicts from a Schwab transaction.

    Returns:
        The instrument transferItem dict, or None if not found.
    """
    for item in transfer_items:
        instrument = item.get("instrument", {})
        if instrument.get("assetType") not in ("CURRENCY", None):
            return item
    return None


def sum_fees(transfer_items: List[Dict]) -> float:
    """Sum all fee amounts from CURRENCY transferItems.

    Args:
        transfer_items: List of transferItem dicts.

    Returns:
        Total fees as a positive float rounded to 2 decimal places.
    """
    total = 0.0
    for item in transfer_items:
        instrument = item.get("instrument", {})
        if instrument.get("assetType") == "CURRENCY":
            fee_type = item.get("feeType", "")
            if fee_type in FEE_TYPES:
                total += abs(item.get("amount", 0.0))
    return round(total, 2)


def map_asset_type(schwab_asset_type: str, put_call: Optional[str]) -> str:
    """Map Schwab assetType + putCall to our schema asset_type.

    Args:
        schwab_asset_type: 'OPTION' or 'EQUITY' from Schwab.
        put_call: 'CALL', 'PUT', or None.

    Returns:
        Schema asset_type: 'call', 'put', 'stock'.
    """
    if schwab_asset_type == "OPTION":
        if put_call == "PUT":
            return "put"
        return "call"
    return "stock"


def extract_expiration_fields(instrument: Dict, asset_type: str) -> Dict:
    """Extract expiration_date/settlement_price from an OPTION instrument.

    WO-P020-E1.018 -- these two fields are the only signal available for
    detecting a 0DTE expiration with no closing transaction. Only present
    on OPTION instruments; stock/etf get None for both, which
    domain.expiration_closer treats as automatically ineligible.

    Args:
        instrument: The 'instrument' dict from a transferItem.
        asset_type: Our mapped schema asset_type ('call', 'put', 'stock').

    Returns:
        Dict with 'expiration_date' (date or None) and 'settlement_price'
        (float or None).
    """
    if asset_type not in ("call", "put"):
        return {"expiration_date": None, "settlement_price": None}

    expiration_date = None
    raw_expiration = instrument.get("expirationDate")
    if raw_expiration:
        try:
            expiration_date = datetime.fromisoformat(
                raw_expiration.replace("+0000", "+00:00")
            ).date()
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse expirationDate: {raw_expiration!r}")

    settlement_price = instrument.get("closingPrice")
    if settlement_price is not None:
        try:
            settlement_price = float(settlement_price)
        except (ValueError, TypeError):
            settlement_price = None

    return {"expiration_date": expiration_date, "settlement_price": settlement_price}

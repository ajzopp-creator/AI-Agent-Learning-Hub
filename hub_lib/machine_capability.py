"""Machine-capability detection for hub_lib.

Small hostname -> capability lookup so ModelManager can auto-route local_*
tasks to their cloud_* equivalent on machines with no local LLM tier (LM
Studio), instead of failing when nothing is listening on localhost:1234.

Update MACHINE_CAPABILITY and P_000_LLM_Model_Hardware_Spec.md's Machines
table together whenever a machine is added, replaced, or upgraded.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Hostname -> whether this machine has a usable local LLM tier (LM Studio).
MACHINE_CAPABILITY: dict[str, bool] = {
    "AJZ-TRADING-LAP": True,   # ASUS TUF F16 - RTX 5070 8GB, full LM Studio tier
    "AJZSTRATEGIESLG": False,  # LG Gram 17Z990-R - integrated GPU only, cloud-only
}


def current_machine_id() -> str:
    """Return this machine's hostname, uppercased for capability lookup.

    Returns:
        The value of the COMPUTERNAME environment variable, uppercased and
        stripped. Empty string if COMPUTERNAME is unset.
    """
    return os.environ.get("COMPUTERNAME", "").strip().upper()


def has_local_llm(machine_id: Optional[str] = None) -> bool:
    """Return whether the given (or current) machine has a local LLM tier.

    Unregistered hostnames default to False (route to cloud) rather than
    raising, so an unrecognized machine fails safe instead of crashing --
    but logs a warning so the gap gets noticed and MACHINE_CAPABILITY gets
    updated.

    Args:
        machine_id: Hostname to check. Defaults to current_machine_id().

    Returns:
        True if the machine has a working local LLM tier, False otherwise.
    """
    machine_id = machine_id or current_machine_id()
    if machine_id not in MACHINE_CAPABILITY:
        logger.warning(
            "Machine %r not in MACHINE_CAPABILITY -- defaulting to no local "
            "LLM tier (routes to cloud). Add it to "
            "hub_lib/machine_capability.py and "
            "P_000_LLM_Model_Hardware_Spec.md's Machines table.",
            machine_id,
        )
        return False
    return MACHINE_CAPABILITY[machine_id]

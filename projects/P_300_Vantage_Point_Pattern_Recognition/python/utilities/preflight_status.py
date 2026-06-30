"""
FILE: preflight_status.py
VERSION: 1.0
DATE: 2026-06-18
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Gathers catalog health (cli.py catalog-summary equivalent) and LM
    Studio readiness (p300_status_check.py equivalent), writes both to
    P_300_preflight_status.json in the project root. Run via
    P_300_Preflight.bat, OUTSIDE the Claude chat session, on the same
    operating model as P_300_AddPattern.bat / P_300_DailyEval_v2.bat.

    INIT Steps 5b/5c (SIP v3.2) read the JSON this writes via
    windows-mcp:FileSystem instead of invoking python via
    windows-mcp:PowerShell -- removing the ~4-min subprocess timeout
    ceiling (M-030, peh-handoff) from every INIT run. See WO-P000-E4.001.

    Reuses existing catalog logic (db_utils.get_latest_catalog,
    verify_ingestion._check_no_hollow_instances) and the existing LM
    Studio wrapper (integrations.lm_studio.infrastructure.lm_studio_api.
    get_wrapper_status) -- no catalog or LM Studio logic reimplemented
    here, only orchestration + JSON serialization.

CHANGELOG:
    - 2026-06-18 v1.0: Created for WO-P000-E4.001.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from schemas_preflight import PreflightStatus  # noqa: E402


def _get_catalog_status() -> dict:
    """Catalog health -- same data as `cli.py catalog-summary`, no print."""
    from utilities.db_utils import get_latest_catalog
    from utilities.db_connect import connection_context
    from infrastructure.verify_ingestion import _check_no_hollow_instances

    try:
        catalog_path = Path(get_latest_catalog())
    except Exception as e:
        return {
            "catalog_path": "", "catalog_filename": "",
            "pattern_count": 0, "symbol_count": 0, "hollow_count": 0,
            "catalog_overall": "ERROR", "catalog_error": str(e),
        }

    try:
        with connection_context(catalog_path=str(catalog_path)) as conn:
            pattern_count = conn.execute(
                "SELECT COUNT(*) FROM pattern_instances"
            ).fetchone()[0]
            symbol_count = conn.execute(
                "SELECT COUNT(DISTINCT symbol_id) FROM pattern_instances"
            ).fetchone()[0]
            hollow_count, _ = _check_no_hollow_instances(conn)
    except Exception as e:
        return {
            "catalog_path": str(catalog_path),
            "catalog_filename": catalog_path.name,
            "pattern_count": 0, "symbol_count": 0, "hollow_count": 0,
            "catalog_overall": "ERROR", "catalog_error": str(e),
        }

    overall = "HEALTHY" if hollow_count == 0 else "ATTENTION REQUIRED"
    return {
        "catalog_path": str(catalog_path),
        "catalog_filename": catalog_path.name,
        "pattern_count": pattern_count,
        "symbol_count": symbol_count,
        "hollow_count": hollow_count,
        "catalog_overall": overall,
        "catalog_error": None,
    }


def _get_lm_studio_status() -> dict:
    """LM Studio readiness -- same data as p300_status_check.py, no print.

    integrations/ is NOT covered by the Hub editable install (confirmed
    in tasks/todo.md ENH-P000 note), so this needs its own HUB_ROOT
    bootstrap -- same as p300_status_check.py. Verified against a known
    Hub-level directory rather than trusted blind (M-036 history)."""
    _hub_root = Path(__file__).resolve().parents[4]
    if not (_hub_root / "integrations" / "lm_studio").is_dir():
        return {
            "lm_studio_running": False, "lm_studio_model": None,
            "lm_studio_model_mismatch": False, "lm_studio_message": "",
            "lm_studio_error": f"HUB_ROOT resolution failed: {_hub_root}",
        }
    if str(_hub_root) not in sys.path:
        sys.path.insert(0, str(_hub_root))

    try:
        from integrations.lm_studio.infrastructure.lm_studio_api import (
            get_wrapper_status,
        )
        status = asyncio.run(get_wrapper_status())
    except Exception as e:
        return {
            "lm_studio_running": False, "lm_studio_model": None,
            "lm_studio_model_mismatch": False, "lm_studio_message": "",
            "lm_studio_error": str(e),
        }

    return {
        "lm_studio_running": status.get("lm_studio_running", False),
        "lm_studio_model": status.get("current_model"),
        "lm_studio_model_mismatch": status.get("model_mismatch", False),
        "lm_studio_message": status.get("message", ""),
        "lm_studio_error": None,
    }


def run_preflight() -> PreflightStatus:
    """Gather catalog + LM Studio status into one PreflightStatus."""
    now_et = datetime.now(ZoneInfo("America/New_York"))
    return PreflightStatus(
        generated_at=now_et.isoformat(),
        **_get_catalog_status(),
        **_get_lm_studio_status(),
    )


def main() -> int:
    status = run_preflight()
    out_path = Path(__file__).resolve().parents[2] / "P_300_preflight_status.json"
    out_path.write_text(status.model_dump_json(indent=2), encoding="utf-8")

    print("P_300 Preflight")
    print(
        f"Catalog:   {status.catalog_overall} "
        f"({status.pattern_count} patterns / {status.symbol_count} symbols, "
        f"{status.hollow_count} hollow)"
    )
    lm_label = "running" if status.lm_studio_running else "NOT running"
    model_note = f" ({status.lm_studio_model})" if status.lm_studio_model else ""
    print(f"LM Studio: {lm_label}{model_note}")
    print(f"Written:   {out_path}")
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

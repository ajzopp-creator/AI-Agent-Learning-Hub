"""
FILE: verify_ingestion.py
VERSION: 1.0
DATE: 2026-05-15
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Stage 3 of the Lock + Temp-DB + Atomic Move write protocol
    (architecture §2.6). After catalog_writer has finished writing into
    temp_working.db, verify_ingestion:

        1. Confirms the temp DB opens cleanly under db_connect (FK ON).
        2. Probes row counts on all 7 catalog tables.
        3. Compares actual delta vs expected_delta — any mismatch FAILs.
        4. Scans for hollow pattern_instances (missing pattern_bars or
           forward_labels) — the EC-027 / EC-057 protection.
        5. On PASS: atomically replaces master with temp (.bak preserved
           for one cycle).
        6. On FAIL: leaves temp in place for forensic inspection; master
           untouched.

    Layer rules:
        - No business logic — pure verify-and-move.
        - Connection lifecycle owned here (opened via db_connect against
          the temp DB path).
        - The orchestrator (application/add_pattern_pipeline.py) calls
          verify_and_promote() at the end of every ingest.

    Atomic move semantics:
        - Path.replace() is atomic on Windows when source and destination
          are on the same volume. Both temp and master live under the
          project's models/ directory by design.
        - Backup file: <master>.bak. Overwritten on each successful
          promote so only the previous master is retained.

CHANGELOG:
    - 2026-05-15 v1.0: Stage 4 file #8 of plan. verify_temp_db,
      _check_no_hollow_instances, atomic_move, verify_and_promote.
"""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from infrastructure.catalog_writer import CATALOG_TABLES  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Result type
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class VerificationResult:
    """Outcome of verify_and_promote. The orchestrator inspects `passed`
    to decide whether to commit or roll back."""
    passed: bool
    failures: list[str] = field(default_factory=list)
    post_counts: dict[str, int] = field(default_factory=dict)
    backup_path: Path | None = None
    master_promoted: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Integrity checks against an open SQLite connection
# ─────────────────────────────────────────────────────────────────────────────

def _row_counts(conn) -> dict[str, int]:
    """Probe row counts on all 7 catalog tables."""
    return {
        t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in CATALOG_TABLES
    }


def _check_no_hollow_instances(conn) -> tuple[int, list[int]]:
    """Find any pattern_instances missing pattern_bars or forward_labels.
    Hollow records are the EC-027 / EC-057 failure mode that Path B's
    schema-as-protection layer is supposed to make impossible — this
    check is the runtime tripwire that confirms it stayed impossible.
    Returns (count, list_of_pattern_instance_ids)."""
    sql = """
        SELECT pi.pattern_instance_id
          FROM pattern_instances pi
         WHERE NOT EXISTS (
                   SELECT 1 FROM pattern_bars pb
                    WHERE pb.pattern_instance_id = pi.pattern_instance_id
               )
            OR NOT EXISTS (
                   SELECT 1 FROM forward_labels fl
                    WHERE fl.pattern_instance_id = pi.pattern_instance_id
               )
    """
    rows = conn.execute(sql).fetchall()
    hollow_ids = [r[0] for r in rows]
    return len(hollow_ids), hollow_ids


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def verify_temp_db(
    temp_path: Path,
    expected_delta: dict[str, int],
    pre_counts: dict[str, int],
) -> tuple[bool, list[str], dict[str, int]]:
    """Run all integrity checks against temp_working.db.

    Returns:
        (all_passed, failure_messages, post_counts)

    Does NOT promote — caller decides based on the result.
    """
    failures: list[str] = []

    with connection_context(catalog_path=str(temp_path)) as conn:
        post_counts = _row_counts(conn)

        # Per-table delta vs expectation
        for table, expected in expected_delta.items():
            actual = post_counts[table] - pre_counts.get(table, 0)
            if actual != expected:
                failures.append(
                    f"{table}: expected +{expected}, got +{actual} "
                    f"(pre={pre_counts.get(table, 0)}, post={post_counts[table]})"
                )

        # Hollow record scan — Path B's schema should make this trivially zero
        hollow_count, hollow_ids = _check_no_hollow_instances(conn)
        if hollow_count > 0:
            sample = hollow_ids[:10]
            more = f" (+{hollow_count - 10} more)" if hollow_count > 10 else ""
            failures.append(
                f"hollow pattern_instances detected: {hollow_count} "
                f"missing pattern_bars or forward_labels. IDs: {sample}{more}"
            )

    return (len(failures) == 0, failures, post_counts)


def atomic_move(temp_path: Path, master_path: Path) -> Path | None:
    """Atomically replace master_path with temp_path. If master exists,
    it is first renamed to <master>.bak (overwriting any previous backup).
    Returns the backup path, or None if no master existed.

    Both paths must be on the same volume for true atomicity. The project
    keeps both under models/ which satisfies this by construction."""
    backup_path: Path | None = None
    if master_path.exists():
        backup_path = master_path.with_suffix(master_path.suffix + ".bak")
        # Path.replace() is atomic and overwrites any existing destination.
        master_path.replace(backup_path)
    temp_path.replace(master_path)
    return backup_path


def verify_and_promote(
    temp_path: Path,
    master_path: Path,
    expected_delta: dict[str, int],
    pre_counts: dict[str, int],
) -> VerificationResult:
    """End-of-ingest entrypoint. Verifies temp_working.db, and on PASS
    atomically promotes it to master. On FAIL, temp is left in place
    and master is untouched."""
    if not temp_path.exists():
        return VerificationResult(
            passed=False,
            failures=[f"temp DB not found: {temp_path}"],
        )

    passed, failures, post_counts = verify_temp_db(
        temp_path, expected_delta, pre_counts
    )
    if not passed:
        logger.error("verify_temp_db FAILED: %s", failures)
        logger.error(
            "Temp DB left in place for inspection: %s. Master untouched.",
            temp_path,
        )
        return VerificationResult(
            passed=False,
            failures=failures,
            post_counts=post_counts,
        )

    backup_path = atomic_move(temp_path, master_path)
    logger.info(
        "Promoted temp -> master. master=%s backup=%s post_counts=%s",
        master_path, backup_path, post_counts,
    )
    return VerificationResult(
        passed=True,
        post_counts=post_counts,
        backup_path=backup_path,
        master_promoted=True,
    )

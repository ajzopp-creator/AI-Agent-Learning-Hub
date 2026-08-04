"""
FILE: verify_ingestion.py
VERSION: 1.2
DATE: 2026-08-04
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Stage 3 of the Lock + Temp-DB + Atomic Move write protocol
    (architecture §2.6). After catalog_writer has finished writing into
    temp_working.db, verify_ingestion:

        1. Confirms the temp DB opens cleanly under db_connect (FK ON).
        2. Probes row counts on all catalog tables (CATALOG_TABLES --
           8 as of decision #7, up from 7; this file iterates the
           tuple generically and needed no change for that growth).
        3. Compares actual delta vs expected_delta — any mismatch FAILs.
        4. Scans for hollow pattern_instances (missing pattern_bars or
           forward_labels) — the EC-027 / EC-057 protection.
        4a. Optionally (check_topk_cache=True) also scans for
            pattern_instances missing topk_cache rows -- the same
            EC-027/EC-057 class of bug, added for WO-P300-E4.006
            (decision #7a). NOT unconditional: single-pattern
            AddPattern (application/add_pattern_pipeline.py) also
            calls verify_temp_db()/verify_and_promote() and was never
            scoped to populate topk_cache (decision #6/#7 both scope
            that population to BulkAddPattern's cycle specifically) --
            an unconditional check here would fail every real
            AddPattern run for a table it was never meant to touch.
            Default False preserves every existing caller's behavior
            unchanged; application/catalog_merge_pipeline.py's
            promote_staging_to_live() does NOT pass True either
            (decision #10, corrected v1.2) -- expected_delta's exact
            count-based check already catches real population failures
            there, without check_topk_cache's false-positive risk on a
            genuinely degenerate-corpus pattern. No caller currently
            passes True.
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
    - 2026-08-04 v1.2 (cosmetic doc fix, no behavior change): corrected
      3 copies of a stale claim -- the module docstring above, verify_
      temp_db()'s docstring, and verify_and_promote()'s docstring all
      wrongly stated "application/catalog_merge_pipeline.py's promote_
      staging_to_live() is the one caller that passes True" for
      check_topk_cache. It doesn't -- confirmed via direct read of
      catalog_merge_pipeline.py's actual call site (verify_and_promote()
      called with 4 positional args, check_topk_cache never passed,
      uses the False default). Found during WO-P300-E5.002's independent
      review (2026-07-29), logged there, fixed here. No functional
      change -- check_topk_cache's real behavior (default False, no
      caller currently passes True) was always correct; only the prose
      describing it was wrong.
    - 2026-07-19 v1.1 (WO-P300-E4.006, decision #7a): Added
      _check_no_hollow_topk() and verify_temp_db()/verify_and_
      promote()'s check_topk_cache parameter (default False -- opt-in,
      not unconditional, since not every caller of this shared file
      populates topk_cache). Docstring's hardcoded "7 catalog tables"
      references corrected -- CATALOG_TABLES is 8 as of decision #7;
      _row_counts() needed no code change since it already iterates
      the tuple generically.
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
    """Probe row counts on all CATALOG_TABLES tables."""
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


def _check_no_hollow_topk(conn) -> tuple[int, list[int]]:
    """Find any pattern_instances missing topk_cache rows (WO-P300-
    E4.006, decision #7a). Same EC-027/EC-057 class of bug
    _check_no_hollow_instances already guards pattern_bars/forward_
    labels against. Only called when verify_temp_db's check_topk_cache
    is True -- see that function's docstring for why this isn't
    unconditional. Returns (count, list_of_pattern_instance_ids)."""
    sql = """
        SELECT pi.pattern_instance_id
          FROM pattern_instances pi
         WHERE NOT EXISTS (
                   SELECT 1 FROM topk_cache tc
                    WHERE tc.pattern_instance_id = pi.pattern_instance_id
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
    check_topk_cache: bool = False,
) -> tuple[bool, list[str], dict[str, int]]:
    """Run all integrity checks against temp_working.db.

    check_topk_cache: if True, also scans for pattern_instances
    missing topk_cache rows (decision #7a). Default False -- every
    caller of this shared function leaves it at False, including
    application/catalog_merge_pipeline.py's promote_staging_to_live()
    (decision #10, corrected v1.2): expected_delta's exact count-based
    check already catches real population failures there without
    _check_no_hollow_topk's false-positive risk on a genuinely
    degenerate-corpus pattern. No caller currently passes True.

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

        # Hollow topk_cache scan — opt-in, see docstring above
        if check_topk_cache:
            hollow_topk_count, hollow_topk_ids = _check_no_hollow_topk(conn)
            if hollow_topk_count > 0:
                sample = hollow_topk_ids[:10]
                more = (
                    f" (+{hollow_topk_count - 10} more)"
                    if hollow_topk_count > 10 else ""
                )
                failures.append(
                    f"hollow topk_cache detected: {hollow_topk_count} "
                    f"pattern_instances missing topk_cache rows. "
                    f"IDs: {sample}{more}"
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
    check_topk_cache: bool = False,
) -> VerificationResult:
    """End-of-ingest entrypoint. Verifies temp_working.db, and on PASS
    atomically promotes it to master. On FAIL, temp is left in place
    and master is untouched. check_topk_cache: see verify_temp_db's
    docstring -- default False; no caller passes True, including
    catalog_merge_pipeline.py's promote_staging_to_live() (decision #10,
    corrected v1.2)."""
    if not temp_path.exists():
        return VerificationResult(
            passed=False,
            failures=[f"temp DB not found: {temp_path}"],
        )

    passed, failures, post_counts = verify_temp_db(
        temp_path, expected_delta, pre_counts, check_topk_cache=check_topk_cache,
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

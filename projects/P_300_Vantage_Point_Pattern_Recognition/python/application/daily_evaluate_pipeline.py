"""
FILE: daily_evaluate_pipeline.py
VERSION: 1.20
DATE: 2026-06-17
AUTHOR: Anthony Zophi + Claude
LAYER: application
DESCRIPTION:
    Pipeline B orchestrator -- Daily Evaluate.

    Wires the read-side of P_300:

        vp_xlsx_reader.parse_live_file
            -> _build_live_candidate (slice + normalize)
            -> catalog_reader.bulk_load_* (read PATTERN_IDENT corpus)
            -> similarity.rank_by_distance
            -> aggregator.catalog_baseline_win_rates + aggregate_top_k
            -> signal_classifier.classify_signal
            -> [v1.2] volatility_divergence.compute_volatility_divergence
            -> SignalReport (signal_class + chosen_horizon + volatility_divergence
               locked here)
            -> [v1.1 Stage 8] narrator_prompt + llm_client -> narration
            -> [v1.4] signal_emitter.emit_signal_packet (JSON to vault for P_400)
            -> report_writer.print_signal_report  (+ optional write_signal_report)

    LM Studio readiness:
        Pipeline B checks LM Studio status via get_wrapper_status() (read-only).
        If LM Studio is not running or the wrong model is loaded, Pipeline B
        prints a clear message and exits with code 1. The operator runs
        lm_studio_launcher.py manually to fix the issue, then re-runs.
        Pipeline B never launches LM Studio or prompts for model switches --
        that is the launcher's job.

        Use --no-narrator (or NARRATOR_ENABLED=False in config) to skip
        the LLM call entirely for fast testing or LM-Studio-down sessions.

    Layer rules (architecture 8.4.5):
        - This file is the ONLY place where infrastructure + domain
          modules get composed. Domain modules don't reach into
          infrastructure; infrastructure modules don't make business
          decisions.
        - Reads the catalog via a single sqlite3.Connection scoped to
          one evaluation pass (M-012 -- PRAGMA foreign_keys = ON via
          db_connect.connection_context()).
        - Stage 6 decision E: EVAL_SET is transient in-memory only --
          this pipeline never writes back to the catalog.
        - NFR-1: BUY/WATCH/PASS classification is locked BEFORE the
          narrator call. Narration is a post-decision read-only label;
          its presence, absence, or content never affects the signal.

    Entry points:
        run_daily_evaluate(xlsx_path, ...) -> SignalReport
            Library-style callable. cli.py routes the daily-evaluate
            subcommand here. Returns the assembled report for callers
            that want to consume it programmatically.
        main()
            Stand-alone CLI for direct invocation:
                python application/daily_evaluate_pipeline.py --xlsx <path>

CHANGELOG:
    - 2026-06-17 v1.20: M-043 fix. _obsidian_write() call (Stage 8a) was
      discarding its True/False return -- a clean False (no report file
      found, signal parse failed) logged nothing at all, silently
      indistinguishable from success. Now logs WARNING on False. Paired
      with report_writer.py v1.8 (M-051 fix on the console-output side of
      the same vault-write path).
    - 2026-06-17 v1.19: atr_adjusted_stop guard (WO-P300-E1.003). The
      max(_is1, _atr_floor) selection assumed _is1 (IntelliScan support_1)
      always sits below entry. Caught via DRD 2026-06-17: support_1=25.46
      sat above entry=25.40, max() picked the invalid above-entry value as
      the stop. Now _is1 only counts as a candidate when it's < _close;
      otherwise atr_adjusted_stop = the ATR floor alone. The old `else`
      branch (max(_close - _atr, _atr_floor)) was always just _atr_floor
      written confusingly -- collapsed to that directly.
    - 2026-06-16 v1.18: IntelliScan stop integration (WO-P300-E1.001).
      load_intelliscan() called once per run at pipeline start. Per-symbol
      get_support_levels() feeds atr_adjusted_stop, intelliscan_support_1,
      intelliscan_support_2 into emit_signal_packet(). Non-blocking when
      IntelliScan file absent -- all three fields emit as None.
    - 2026-06-10 v1.16: ATR upgraded from high-low-only simple-average
      proxy to full True Range + Wilder smoothing via the shared hub util
      shared_resources.python_utils.atr.compute_atr_wilder. Removed local
      _compute_atr_from_bars. Classification path unchanged (ATR only
      drives guideline stop/target); determinism replay confirms
      BUY/WATCH/PASS byte-identical, only guideline stop/target shift.
    - 2026-06-08 v1.15: Stage 5a corrected. Gate widened from BUY-only to
      config.LEDGER_LOG_CLASSES = (BUY, WATCH) so WATCH signals are also
      laddered to the ledger and emitted. Removed the broken vault_root
      kwarg + vault path construction; signal_emitter v2.0 now routes the
      packet via the P_800 Hub interface (SIGNAL_V2). Added chosen_horizon
      to the emit call; dropped pipeline-side logging of the emit result
      (the emitter logs INFO on success / WARNING on failure internally).
    - 2026-06-07 v1.14: Added signal_emitter.emit_signal_packet() call
      after ledger_record (Enhancement 1: P_300 → P_400 signal packet).
      BUY and WATCH signals now write JSON to vault for P_400 ingestion.
    - 2026-05-30 v1.13: Removed _diag_log path construction; check() no
      longer takes diag_log param (lm_studio_status.py v1.2).
    - 2026-05-30 v1.12: lm_studio_status import updated to Hub-level.
    - 2026-05-30 v1.11: _check_lm_studio() removed. Replaced with
      infrastructure.lm_studio_status.check() per Process Boundary
      Standard — LMS status is infrastructure, not orchestration.
    - 2026-05-30 v1.10: _check_lm_studio() redirects stdout to
      logs/lms_diag.log during asyncio.run(get_wrapper_status()) to
      suppress LM Studio server diagnostics from the console.
    - 2026-05-29 v1.9: Fixed Hub root sys.path bootstrap. _HUB_ROOT was
      resolved as 4 x .parent from daily_evaluate_pipeline.py, landing at
      projects/ instead of AI-Agent-Learning-Hub/. Corrected to 5 x .parent.
      This caused ModuleNotFoundError on integrations.lm_studio when invoked
      via cli.py (which sets CWD to python/, not Hub root).
    - 2026-05-29 v1.8: Removed ensure_lm_studio_ready() from main(). Pipeline B
      checks LM Studio status via get_wrapper_status() only. If not running or
      wrong model, prints actionable message and exits code 1. Operator runs
      lm_studio_launcher.py manually.
    - 2026-05-29 v1.7: Fixed clean-mode INFO bleed from launcher.
    - 2026-05-29 v1.6: Added Hub root sys.path bootstrap and LM Studio
      auto-launch via ensure_lm_studio_ready() in main().
    - 2026-05-28 v1.5: Fixed clean-mode log suppression via logging.disable().
    - 2026-05-28 v1.4: Added print_output param; raised log level to WARNING
      in clean mode to suppress INFO chatter.
    - 2026-05-28 v1.3: Fixed double-report bug (print_output param).
    - 2026-05-20 v1.2: Wired post-classification volatility divergence.
    - 2026-05-19 v1.1: Wired Stage 8 Post-Decision Narrator.
    - 2026-05-18 v1.0: Initial release. Stage 6 file #8 of 10.
"""
from __future__ import annotations

import argparse
import dataclasses
import logging
import sys
from datetime import datetime
from pathlib import Path

# sys.path bootstrap for direct invocation (python/ dir).
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

# Hub root bootstrap so integrations.lm_studio resolves from any CWD.
# Path: daily_evaluate_pipeline.py -> application/ -> python/ -> P_300_*/ -> projects/ -> Hub root
_HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(_HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(_HUB_ROOT))

from application import ledger_record  # noqa: E402
from config import (  # noqa: E402
    LEDGER_LOG_CLASSES, LOG_FORMAT, LOG_LEVEL, NARRATOR_ENABLED,
    ORIGIN_PATTERN_IDENT, REPORTS_DIR, TOP_K_MATCHES,
)
from domain import aggregator, similarity, signal_classifier  # noqa: E402
from domain.narrator_prompt import (  # noqa: E402
    NARRATOR_SYSTEM_PROMPT, build_narrator_user_prompt,
)
from domain.normalization import NormalizedValues, normalize_window  # noqa: E402
from domain.volatility_divergence import (  # noqa: E402
    compute_volatility_divergence,
)
from infrastructure import catalog_reader, report_writer, signal_emitter  # noqa: E402
from write_signal_to_obsidian import parse_report_and_write as _obsidian_write  # noqa: E402
from integrations.lm_studio.infrastructure.lm_studio_status import check as lm_studio_check  # noqa: E402
from shared_resources.python_utils.atr import compute_atr_wilder  # noqa: E402
from utilities.intelliscan_reader import (  # noqa: E402
    load_intelliscan, get_support_levels,
)
from infrastructure.report_writer import (  # noqa: E402
    print_signal_report_clean,
)
from infrastructure.llm_client import call_lm_studio  # noqa: E402
from infrastructure.vp_xlsx_reader import parse_live_file  # noqa: E402
from schemas import VPBarRaw  # noqa: E402
from schemas_pipeline_b import (  # noqa: E402
    LiveCandidate, MatchResult, NormalizedBar, SignalReport,
)
from utilities.db_connect import connection_context  # noqa: E402

# M-011: route logging to stdout for PowerShell visibility.
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, stream=sys.stdout)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Live-candidate assembly (raw bars + normalized values -> Pydantic models)
# ---------------------------------------------------------------------------

def _build_normalized_bar(
    raw: VPBarRaw,
    norm: NormalizedValues,
    bar_offset: int,
) -> NormalizedBar:
    """Combine one VPBarRaw + matching NormalizedValues into a NormalizedBar."""
    return NormalizedBar(
        bar_offset=bar_offset,
        bar_date=raw.bar_date,
        open=raw.open, high=raw.high, low=raw.low, close=raw.close,
        volume=raw.volume,
        stdiff=raw.stdiff, mtdiff=raw.mtdiff, ltdiff=raw.ltdiff,
        pred_high=raw.pred_high, pred_low=raw.pred_low,
        pred_range=raw.pred_range,
        williams_emai=raw.williams_emai, psi=raw.psi,
        neural_index=raw.neural_index,
        triple_cross_short=raw.triple_cross_short,
        triple_cross_medium=raw.triple_cross_medium,
        triple_cross_long=raw.triple_cross_long,
        **dataclasses.asdict(norm),
    )


def _build_live_candidate(
    raw_bars: list[VPBarRaw],
    symbol: str,
    window_length: int,
) -> LiveCandidate:
    """Slice the most-recent N raw bars, normalize, return a LiveCandidate.

    Anchor = the most recent bar (offset 0); earlier bars run -1, -2, ...,
    -(window_length - 1). Normalization uses normalize_window's default
    LAUNCH-anchor framing (bars[-1] as anchor).
    """
    if len(raw_bars) < window_length:
        raise ValueError(
            f"Need at least {window_length} bars; live XLSX provided "
            f"{len(raw_bars)}"
        )
    window = raw_bars[-window_length:]
    norm_values = normalize_window(window)
    if len(norm_values) != window_length:
        raise RuntimeError(
            f"normalize_window returned {len(norm_values)} entries; "
            f"expected {window_length}"
        )
    bars: list[NormalizedBar] = []
    for i, (raw, norm) in enumerate(zip(window, norm_values)):
        bar_offset = i - (window_length - 1)  # last = 0, earlier negative
        bars.append(_build_normalized_bar(raw, norm, bar_offset))
    return LiveCandidate(
        ticker=symbol,
        anchor_date=window[-1].bar_date,
        window_length=window_length,
        bars=bars,
    )


# ---------------------------------------------------------------------------
# End-to-end pipeline
# ---------------------------------------------------------------------------

def run_daily_evaluate(
    xlsx_path: Path,
    window_length: int = 20,
    top_k: int = TOP_K_MATCHES,
    write_file: bool = True,
    reports_dir: Path | None = None,
    narrator_enabled: bool = NARRATOR_ENABLED,
    print_output: bool = True,
) -> SignalReport:
    """Parse one live XLSX, score it against the catalog, return the report.

    Args:
        xlsx_path: Path to `History Grid (SYMBOL).xlsx`.
        window_length: Candidate window size; default 20 bars.
        top_k: Number of historical analogs to surface; default
            config.TOP_K_MATCHES.
        write_file: If True, also persist the formatted report to disk.
        reports_dir: Override target directory for the written report.
            Defaults to config.REPORTS_DIR inside report_writer.
        narrator_enabled: If True, build a narration prompt from the
            classified report and call LM Studio for human-readable
            color (Stage 8). Default is config.NARRATOR_ENABLED. Any
            failure attaches narration=None without affecting the signal.
        print_output: If True (default), print the dense signal report to
            stdout at Stage 8. Set False when --clean is active so that
            main() controls the sole console print via
            print_signal_report_clean(). File write is unaffected.

    Returns:
        SignalReport with classified signal + top-K matches +
        per-horizon stats, and (when narrator_enabled and successful)
        a populated narration field.
    """
    logger.info("Pipeline B start: %s", xlsx_path.name)

    # IntelliScan stop grid -- loaded once per pipeline run (non-blocking).
    # Provides VP structural support levels for atr_adjusted_stop calculation.
    # Returns {} if file absent; emit_signal_packet receives None fields.
    _intelliscan = load_intelliscan()

    # Stage 1: parse + normalize live candidate (no DB touch yet)
    symbol, raw_bars = parse_live_file(xlsx_path)
    candidate = _build_live_candidate(raw_bars, symbol, window_length)
    logger.info(
        "Candidate built: %s anchor=%s window_length=%d",
        candidate.ticker, candidate.anchor_date, candidate.window_length,
    )

    # Stage 2: read-only catalog pass -- one connection for the whole run
    with connection_context() as conn:
        all_pids = catalog_reader.get_all_pattern_ids(
            conn, origin_type=ORIGIN_PATTERN_IDENT,
        )
        if not all_pids:
            raise RuntimeError(
                "Catalog contains no PATTERN_IDENT patterns; "
                "ingest historical patterns via Pipeline A first."
            )
        historical_windows = catalog_reader.bulk_load_normalized_windows(
            conn, all_pids,
        )
        all_labels = catalog_reader.bulk_load_forward_labels(conn, all_pids)
        all_metadata = catalog_reader.bulk_load_pattern_metadata(
            conn, all_pids,
        )

    # Stage 3: similarity ranking
    ranked = similarity.rank_by_distance(candidate.bars, historical_windows)
    top_k_tuples = ranked[:top_k]
    top_k_pids = [t[0] for t in top_k_tuples]
    logger.info(
        "Ranked %d patterns; took top %d (best composite=%.4f)",
        len(ranked), len(top_k_tuples),
        top_k_tuples[0][1] if top_k_tuples else float("nan"),
    )

    # Stage 4: assemble MatchResult objects for the top-K
    top_matches: list[MatchResult] = []
    for pid, composite_dist, per_feat in top_k_tuples:
        meta = all_metadata.get(pid)
        if meta is None:
            logger.warning("Skipping pid=%d -- no metadata loaded", pid)
            continue
        top_matches.append(MatchResult(
            pattern_instance_id=pid,
            ticker=meta.ticker,
            anchor_date=meta.anchor_date,
            composite_distance=composite_dist,
            per_feature_distances=per_feat,
            forward_labels=all_labels.get(pid, {}),
        ))

    # Stage 5: per-horizon aggregation + cross-horizon classification
    baseline = aggregator.catalog_baseline_win_rates(all_labels)
    top_k_label_map = {pid: all_labels.get(pid, {}) for pid in top_k_pids}
    per_horizon_stats = aggregator.aggregate_top_k(top_k_label_map, baseline)
    signal_class, chosen_horizon = signal_classifier.classify_signal(
        per_horizon_stats,
    )

    # Stage 5a: record fired signal to ledger + emit P_400 signal packet
    # (Enhancement 1). Both fire on actionable classes per
    # config.LEDGER_LOG_CLASSES = (BUY, WATCH). Best-effort, non-blocking --
    # a failure in either hook logs a WARNING but never blocks the signal.
    if top_k_pids and signal_class.value in LEDGER_LOG_CLASSES:
        best_pattern_id = top_k_pids[0]
        aggregated_horizon = per_horizon_stats[chosen_horizon]
        ledger_record.record_fired_signal(
            ticker=candidate.ticker,
            signal_date=candidate.anchor_date,
            signal_class=signal_class,
            chosen_horizon=chosen_horizon,
            pattern_id=best_pattern_id,
            aggregated_horizon=aggregated_horizon,
        )
        
        # Emit SIGNAL_V2 packet for P_400 via the P_800 Hub interface.
        # signal_emitter owns the SIGNAL_V2 dict + write_to_vault call;
        # P_300 passes data only, never constructs a vault path (M-038).
        # The emitter logs INFO on success / WARNING on failure internally.
        anchor_iso = candidate.anchor_date.isoformat()
        _close = candidate.bars[-1].close
        _atr = compute_atr_wilder([(b.high, b.low, b.close) for b in candidate.bars])
        _is1, _is2 = get_support_levels(candidate.ticker, _intelliscan)
        # atr_adjusted_stop: IntelliScan support_1 only counts as a candidate
        # when it sits below entry -- a valid stop for a long (WO-P300-E1.003;
        # an above-entry level isn't a stop at all). Otherwise the ATR floor
        # alone is used.
        _atr_floor = _close - _atr
        if _is1 is not None and _is1 < _close:
            _atr_adjusted_stop = max(_is1, _atr_floor)
        else:
            _atr_adjusted_stop = _atr_floor

        signal_emitter.emit_signal_packet(
            symbol=candidate.ticker,
            signal_date=anchor_iso,
            chosen_horizon=chosen_horizon,
            n_matches=len(top_matches),
            wr=aggregated_horizon.win_rate * 100,  # 0.0-1.0 -> 0-100
            mean_ret=aggregated_horizon.mean_return_pct,
            z_score=aggregated_horizon.z_score,
            close_at_signal=_close,
            atm_at_signal=_atr,
            trailing_volume_30d=candidate.bars[-1].volume,
            signal_source_link=(
                f"trading_journal/TradeManagement/P300/"
                f"{anchor_iso}_{candidate.ticker}.md"
            ),
            atr_adjusted_stop=_atr_adjusted_stop,
            intelliscan_support_1=_is1,
            intelliscan_support_2=_is2,
        )

    # Stage 5b (v1.2): volatility divergence flag.
    volatility_divergence = None
    if top_matches:
        candidate_range_pcts = [b.range_pct for b in candidate.bars]
        topk_range_pcts = [
            [b.range_pct for b in historical_windows[m.pattern_instance_id]]
            for m in top_matches
        ]
        volatility_divergence = compute_volatility_divergence(
            candidate_range_pcts, topk_range_pcts,
        )
        logger.info(
            "Volatility divergence: candidate_median=%.4f topk_median=%.4f "
            "ratio=%.2f severity=%s",
            volatility_divergence.candidate_median_range_pct,
            volatility_divergence.topk_median_range_pct,
            volatility_divergence.ratio,
            volatility_divergence.severity.value,
        )
    else:
        logger.warning(
            "Volatility divergence: skipped (top_matches is empty); "
            "signal still emits per existing pipeline behavior."
        )

    # Stage 6: assemble SignalReport (NFR-1 -- signal locked here, BEFORE LLM)
    report = SignalReport(
        ticker=candidate.ticker,
        anchor_date=candidate.anchor_date,
        signal_class=signal_class,
        chosen_horizon=chosen_horizon,
        per_horizon_stats=per_horizon_stats,
        top_matches=top_matches,
        generated_at=datetime.now(),
        volatility_divergence=volatility_divergence,
    )

    # Stage 7 (v1.1): Post-Decision Narrator.
    if narrator_enabled:
        logger.info("Narrator enabled -- calling LM Studio for narration")
        narration = call_lm_studio(
            system_prompt=NARRATOR_SYSTEM_PROMPT,
            user_prompt=build_narrator_user_prompt(report),
        )
        report = report.model_copy(update={"narration": narration})
        if narration is None:
            logger.info("Narration unavailable; signal emits clean (NFR-1).")
    else:
        logger.info("Narrator disabled -- skipping LM Studio call")

    # Stage 8: emit report (terminal + optional file).
    # print_output=False when --clean is set; main() owns the console print.
    if print_output:
        report_writer.print_signal_report(report)
    if write_file:
        out_path = report_writer.write_signal_report(report, reports_dir)
        logger.info("Wrote report to %s", out_path)
        # Stage 8a: write P_300 Obsidian note for actionable signals.
        # Best-effort -- failure logs a warning and never blocks the signal.
        if signal_class.value in LEDGER_LOG_CLASSES:
            try:
                _obsidian_ok = _obsidian_write(
                    candidate.ticker, reports_dir or REPORTS_DIR,
                )
                if not _obsidian_ok:
                    # M-043: a clean False return (no exception -- e.g. no
                    # report file found, signal parse failed) was
                    # previously discarded silently. Log it at WARNING so
                    # it doesn't disappear the way the M-051 console bug
                    # let operators believe every actionable signal was
                    # vault-logged.
                    logger.warning(
                        "Obsidian write returned False for %s (no exception "
                        "-- see [SKIP]/[FAIL] line above for reason)",
                        candidate.ticker,
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Obsidian write failed for %s: %s", candidate.ticker, exc)

    logger.info(
        "Pipeline B done: %s -> %s at horizon %d",
        candidate.ticker, signal_class.value, chosen_horizon,
    )
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Pipeline B (Daily Evaluate): parse a live VP History Grid "
            "XLSX, match against the catalog, emit a BUY/WATCH/PASS report."
        ),
    )
    parser.add_argument(
        "--xlsx", required=True,
        help="Path to History Grid (SYMBOL).xlsx",
    )
    parser.add_argument(
        "--window-length", type=int, default=20,
        help="Candidate window size in bars (default 20).",
    )
    parser.add_argument(
        "--top-k", type=int, default=TOP_K_MATCHES,
        help=f"Top-K matches to surface (default {TOP_K_MATCHES}).",
    )
    parser.add_argument(
        "--no-write-file", action="store_true",
        help="Skip persisting the report to disk; print to terminal only.",
    )
    parser.add_argument(
        "--reports-dir", type=Path, default=None,
        help=f"Override target dir for the written report (default {REPORTS_DIR}).",
    )
    parser.add_argument(
        "--no-narrator", action="store_true",
        help=(
            "Skip the LLM narration call entirely. Faster for testing or "
            "when LM Studio is down. Signal class unaffected (NFR-1)."
        ),
    )
    parser.add_argument(
        "--clean", action="store_true",
        help=(
            "Use clean console output (minimal banner + signal + status). "
            "Designed for batch multi-symbol evaluation (20+ runs). "
            "Details suppressed from console (already in Obsidian vault)."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    narrator_enabled = NARRATOR_ENABLED and not args.no_narrator

    if args.clean:
        logging.disable(logging.WARNING)

    try:
        # v1.8: read-only LM Studio status check. If not ready, print
        # actionable message and exit. Operator runs launcher manually.
        if narrator_enabled:
            if not lm_studio_check(clean=args.clean):
                return 1

        report = run_daily_evaluate(
            xlsx_path=Path(args.xlsx),
            window_length=args.window_length,
            top_k=args.top_k,
            write_file=not args.no_write_file,
            reports_dir=args.reports_dir,
            narrator_enabled=narrator_enabled,
            print_output=not args.clean,
        )
    finally:
        if args.clean:
            logging.disable(logging.NOTSET)

    if args.clean:
        narrator_warning = narrator_enabled and report.narration is None
        report_writer.print_signal_report_clean(
            report,
            xlsx_path=Path(args.xlsx),
            narrator_warning=narrator_warning,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())


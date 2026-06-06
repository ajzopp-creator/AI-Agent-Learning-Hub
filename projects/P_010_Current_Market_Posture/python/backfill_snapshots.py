# Backfill script
from datetime import date, datetime
from pathlib import Path
from market_health.config import SNAPSHOT_DIR, DISTRIBUTION_WINDOW_DAYS
from domain.distribution_day import count_distribution_days
from domain.market_phase import derive_phase
from domain.rally_state import RallyTracker
from infrastructure.vp_reader import read_vp_history
from market_health.schemas import IndexHealth, MarketHealthOutput
import traceback

DATES_FILE = Path(r'C:\Users\Trader\AppData\Local\Temp\backfill_dates.txt')

def build_index_health(ticker, rows, as_of):
    tracker = RallyTracker()
    tracker.walk(rows)
    reset = tracker.last_5pct_reset_date
    window = (DISTRIBUTION_WINDOW_DAYS if reset is None
              else min(DISTRIBUTION_WINDOW_DAYS, max((as_of - reset).days, 0)))
    dist_count, dist_dates = count_distribution_days(rows, as_of, window)
    tracker.invalidate_ftd_if_needed(dist_count)
    return IndexHealth(
        ticker=ticker, last_date=rows[-1].trade_date, last_close=rows[-1].close,
        dist_count=dist_count, dist_dates=dist_dates, rally_state=tracker.state,
        rally_low=tracker.rally_low, rally_low_date=tracker.rally_low_date,
        rally_attempt_day=tracker.attempt_day, follow_through_day=tracker.ftd_date,
        ftd_age_days=tracker.ftd_age_days(as_of),
    )

print('Loading VP...', flush=True)
spy_all = read_vp_history('SPY')
qqq_all = read_vp_history('QQQ')
print(f'SPY={len(spy_all)} QQQ={len(qqq_all)}', flush=True)
days = [l.strip() for l in DATES_FILE.read_text().splitlines() if l.strip()]
print(f'Dates: {len(days)}', flush=True)
ok = skip = fail = 0
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
for ds in days:
    snap = SNAPSHOT_DIR / (ds.replace('-','') + '.json')
    if snap.exists():
        skip += 1; continue
    print(f'  {ds}', flush=True)
    try:
        as_of = date.fromisoformat(ds)
        spy_rows = [r for r in spy_all if r.trade_date <= as_of]
        qqq_rows = [r for r in qqq_all if r.trade_date <= as_of]
        if not spy_rows or not qqq_rows:
            fail += 1; continue
        spy_h = build_index_health('SPY', spy_rows, as_of)
        qqq_h = build_index_health('QQQ', qqq_rows, as_of)
        phase, reason = derive_phase(spy_h, qqq_h)
        out = MarketHealthOutput(generated_at=datetime.now(), as_of_date=as_of,
            spy=spy_h, qqq=qqq_h,
            max_dist_count=max(spy_h.dist_count, qqq_h.dist_count),
            market_phase=phase, phase_reason=reason)
        snap.write_text(out.model_dump_json(indent=2), encoding='utf-8')
        ok += 1
    except Exception as e:
        fail += 1; print(f'  FAIL {ds}: {e}', flush=True); traceback.print_exc()
print(f'DONE ok={ok} skip={skip} fail={fail}', flush=True)
"""
run_this_P820_20260909_161728.py
P_820 vault write -- two P_210 signals (One Click Trading 2PM Income Trade)
NDX call credit spread 9/4/26 (opened, rolled, expired ITM for a loss)
NDX put credit spread 9/9/26 (opened, expired OTM near max profit)
"""
import sys
import traceback
from pathlib import Path
from datetime import datetime

HUB = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
sys.path.insert(0, str(HUB))

SCRIPT_PATH = Path(__file__)
DONE_PATH = Path(str(SCRIPT_PATH) + ".done")


def write_done(status, exit_code):
    DONE_PATH.write_text(
        f"status: {status}\nexit_code: {exit_code}\ntimestamp: {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )


def main():
    from shared_resources.python_utils.vault_interface import write_to_vault

    r1 = write_to_vault("P820", {
        "symbol": "NDX",
        "signal_date": "2026-09-04",
        "why_code": "P_210",
        "entry_price": 2.05,
        "notes": (
            "Bear call credit spread (One Click Trading 2PM Income Trade). "
            "Opened 29520/29530 CALL @.95 credit (14:10:25 ET). Rolled long "
            "leg 29530->29540 @1.10 additional credit (14:21:52 ET), net "
            "position 29520/29540 CALL, total credit 2.05. Expired ITM at "
            "9/4 close (NDX closed above 29540). Short leg assigned "
            "-2416.00, long leg settled +416.00, net settlement -2000.00. "
            "Realized loss approx -1795 (2.05*100 credit - 2000 settlement, "
            "before commissions)."
        ),
        "written_by": "P_820/chat_dictation",
    })

    r2 = write_to_vault("P820", {
        "symbol": "NDX",
        "signal_date": "2026-09-09",
        "why_code": "P_210",
        "entry_price": 1.15,
        "notes": (
            "Bull put credit spread (One Click Trading 2PM Income Trade). "
            "Sold 29370/29360 PUT @1.15 credit (14:07:30 ET). Max profit if "
            "NDX closes above 29370. Expired OTM at 9/9 close (NDX closed "
            "above 29370) -- max profit achieved, 1.15 credit kept (approx "
            "$115/contract before commissions)."
        ),
        "written_by": "P_820/chat_dictation",
    })

    print("r1:", r1)
    print("r2:", r2)
    return bool(r1) and bool(r2)


if __name__ == "__main__":
    try:
        ok = main()
    except Exception:
        traceback.print_exc()
        ok = False

    if ok:
        print("PASS")
        write_done("PASS", 0)
        sys.exit(0)
    else:
        print("FAIL")
        write_done("FAIL", 1)
        sys.exit(1)

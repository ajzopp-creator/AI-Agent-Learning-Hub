"""run_this_P805_20260829_180500.py -- WO-P000-E2.003 verification.

Confirms config.py imports cleanly after removing the dead P800_SCRIPTS
sys.path insert, and that obsidian_writers.application.write_handler
still resolves via the Hub editable install with no path wiring.

Self-contained; does not modify any production file.
"""
import sys
import traceback
from pathlib import Path
from datetime import datetime

DONE_MARKER = Path(__file__).with_suffix(".py.done")
P805_PYTHON = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python"


def write_done(status: str, detail: str) -> None:
    DONE_MARKER.write_text(
        f"status={status}\n"
        f"detail={detail}\n"
        f"timestamp={datetime.now().isoformat()}\n",
        encoding="utf-8",
    )


def main() -> int:
    if P805_PYTHON not in sys.path:
        sys.path.insert(0, P805_PYTHON)  # own-project sibling import, matches how P_805 runs normally

    try:
        import config  # noqa: F401 -- import-only check, confirms no sys.path insert needed
    except Exception:
        detail = "config.py failed to import:\n" + traceback.format_exc()
        print("FAIL:", detail)
        write_done("FAIL", detail)
        return 1

    try:
        from obsidian_writers.application.write_handler import handle_write  # noqa: F401
    except Exception:
        detail = "obsidian_writers.application.write_handler failed to import:\n" + traceback.format_exc()
        print("FAIL:", detail)
        write_done("FAIL", detail)
        return 1

    if hasattr(config, "sys"):
        detail = "config module still exposes a 'sys' name -- dead import may not be fully removed"
        print("FAIL:", detail)
        write_done("FAIL", detail)
        return 1

    print("PASS")
    write_done("PASS", "config.py and obsidian_writers.application.write_handler both import cleanly, no sys.path insert present")
    return 0


if __name__ == "__main__":
    sys.exit(main())

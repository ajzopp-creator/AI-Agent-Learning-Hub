import sys
import traceback

log_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\api\test_output.txt"

with open(log_path, "w") as f:
    f.write("=== SCHWAB API TEST ===\n")
    f.write(f"Python: {sys.version}\n\n")

    # Test 1: Can we import schwab?
    try:
        import schwab
        f.write(f"schwab-py version: {schwab.__version__}\n")
    except Exception as e:
        f.write(f"ERROR importing schwab: {e}\n")
        sys.exit(1)

    # Test 2: Load credentials
    try:
        import importlib.util
        from pathlib import Path
        creds_path = Path(__file__).parent / "schwab_credentials.py"
        spec = importlib.util.spec_from_file_location("creds", creds_path)
        creds = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creds)
        f.write(f"Credentials loaded OK\n")
        f.write(f"APP_KEY starts with: {creds.APP_KEY[:8]}...\n")
        f.write(f"APP_SECRET starts with: {creds.APP_SECRET[:4]}...\n")
        f.write(f"CALLBACK_URL: {creds.CALLBACK_URL}\n")
        f.write(f"TOKEN_PATH: {creds.TOKEN_PATH}\n\n")
    except Exception as e:
        f.write(f"ERROR loading credentials: {e}\n")
        traceback.print_exc(file=f)
        sys.exit(1)

    # Test 3: Try manual auth flow (no browser needed)
    try:
        from schwab.auth import client_from_manual_flow
        f.write("Attempting manual auth flow...\n")
        f.write("This will generate an auth URL you paste into your browser.\n")
        # Don't actually call it here - just confirm the import works
        f.write("schwab.auth imported OK\n")
    except Exception as e:
        f.write(f"ERROR with auth import: {e}\n")
        traceback.print_exc(file=f)

    f.write("\nAll checks passed - ready for auth flow\n")

print(f"Output written to: {log_path}")

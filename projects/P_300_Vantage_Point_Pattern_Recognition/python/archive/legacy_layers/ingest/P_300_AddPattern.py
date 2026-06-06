"""
FILE: P_300_AddPattern.py
VERSION: 1.10 (LOCKED TO TONY'S ARCHITECTURE)
DATE: 2026-05-11
DESCRIPTION: 
    System Vault Engine. Points strictly to 'historical_patterns' 
    as documented in Tony's legacy comments.
"""
import sys
from pathlib import Path

# 1. SETUP PATHS
BASE_DIR = Path(r"C:/Users/Trader/AI-Agent-Learning-Hub/projects/P_300_Vantage_Point_Pattern_Recognition")
PYTHON_ROOT = BASE_DIR / "python"
VAULT_SOURCE = BASE_DIR / "data" / "historical_patterns"

# Path Injection
for path in [PYTHON_ROOT, PYTHON_ROOT / "utilities"]:
    if str(path) not in sys.path:
        sys.path.append(str(path))

# 2. V6 MODULE IMPORT
try:
    import P_300_vantagepoint_batch_convert_v6 as converter
    import ingest_vp_catalog as ingester
    print(f"[SUCCESS] v6 Engine linked from {PYTHON_ROOT}")
except ImportError as e:
    print(f"\n[!] CRITICAL ERROR: {e}")
    sys.exit(1)

def main():
    print("\n" + "="*50)
    print(" P_300 VANTAGE POINT PATTERN VAULTING (v1.10)")
    print("="*50)
    
    # Check the real folder
    if not VAULT_SOURCE.exists():
        print(f"[!] ABORTED: Folder {VAULT_SOURCE} does not exist.")
        return

    files = list(VAULT_SOURCE.glob("*.xlsx")) + list(VAULT_SOURCE.glob("*.csv"))
    if not files:
        print(f"[!] ABORTED: No files found in {VAULT_SOURCE}")
        return

    # [1/2] CONVERT
    print(f"[1/2] Converting {len(files)} patterns from 'historical_patterns'...")
    converter.process_files()
    
    # [2/2] INGEST
    print("[2/2] Ingesting into Catalog DB...")
    if hasattr(ingester, 'main'):
        ingester.main()
    
    print("\n--- VAULT UPDATE SUCCESSFUL ---")

if __name__ == "__main__":
    main()
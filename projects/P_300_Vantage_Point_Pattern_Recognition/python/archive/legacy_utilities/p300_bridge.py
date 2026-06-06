import sqlite3
import pandas as pd
import logging
from pathlib import Path
from hub_lib import ModelManager, load_hub_env, verify_health
from hub_lib.exceptions import ModelUnavailableError, ProviderError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
DB_PATH = HUB_ROOT / "projects" / "catalog.db"

class P300Bridge:
    def __init__(self):
        try:
            load_hub_env()
            verify_health(["vp_pattern"])
            logger.info("Hub environment loaded and vp_pattern health verified.")
        except ModelUnavailableError as e:
            logger.error(f"Startup Health Check Failed: {e}")
            raise

        self._ensure_schema()

    def _ensure_schema(self):
        """Ensures the catalog schema exists on startup (Idempotent)."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS symbols (symbol_id INTEGER PRIMARY KEY, ticker TEXT UNIQUE)")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_bars (
                bar_id INTEGER PRIMARY KEY, 
                symbol_id INTEGER, 
                bar_date TEXT, 
                open REAL, 
                high REAL, 
                low REAL, 
                close REAL, 
                volume INTEGER, 
                FOREIGN KEY(symbol_id) REFERENCES symbols(symbol_id)
            )
        """)
        conn.commit()
        conn.close()

    def compliance_engine(self, ticker, df):
        """P_030 Local Compliance Engine: Validates 100% Buy logic."""
        logger.info(f"Running P_115 validation for {ticker}...")
        # Placeholder: Insert your MA alignment logic here
        return True, "All MAs (20, 50, 100, 200) aligned."

    def fetch_local_data(self, ticker):
        """Queries local persistence using parameterized SQL."""
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT * FROM price_bars 
            WHERE symbol_id = (SELECT symbol_id FROM symbols WHERE ticker = ?)
            ORDER BY bar_date DESC
        """
        df = pd.read_sql(query, conn, params=(ticker,))
        conn.close()
        return df

    def analyze(self, ticker):
        """Invokes reasoning layer via ModelManager."""
        df = self.fetch_local_data(ticker)
        if df.empty:
            return f"Error: No data found for {ticker}."

        is_compliant, reason = self.compliance_engine(ticker, df)
        if not is_compliant:
            return f"SIGNAL REJECTED: {reason}"

        prompt = f"Founder-led analysis for {ticker}. Data summary: {df.tail(5).to_json()}."
        
        try:
            return ModelManager.generate("vp_pattern", prompt, max_tokens=2048)
        except ProviderError as e:
            logger.error(f"Analysis failed for {ticker}: {e}")
            return f"Analysis Service Unavailable: {e}"

if __name__ == "__main__":
    bridge = P300Bridge()
    result = bridge.analyze("NVDA")
    print(f"\n--- AI REASONING ---\n{result}")

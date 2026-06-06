To ensure your execution strategy is crystal clear and adheres to your specific risk parameters, I have reorganized the **TOS Execution & Decision Logic**.

This structure integrates the asset sizing requirements from your **P_115** system directly into the decision-making flow for thinkorswim (TOS).

---

### 🛠 Phase 3: TOS Execution & Position Sizing Logic

When determining the final trade structure, I will follow this hierarchical decision tree:

#### 1. The Vehicle Decision (Stock vs. Options)

Based on the **Market Posture Status** and **Trading Mode**, I will recommend the vehicle using these criteria:

* **Equity (Stock):** Recommended if the asset is in a **CORRECTION** mode, has high volatility, or if the spread between P-Mid and P-Low is tight. Best for "Lower Risk" profiles.
* **Leverage (Options):** Recommended during **HOT MARKET** or **STANDARD** modes when the setup has "Strong" zone strength.
* *Constraint:* Option premiums must fit within **Gate 3 ($1,750)** concentration limits.



#### 2. The Three-Gate Sizing Calculation

I will calculate the final position size by taking the **SMALLEST** of these three values:
| Gate | Type | Logic / Formula |
| :--- | :--- | :--- |
| **Gate 1** | **Risk-Based** | $525 / (Entry - Stop)$ |
| **Gate 2** | **Cash Flow** | Manual user-provided liquidity cap per trade. |
| **Gate 3** | **Concentration** | Max $1,750 total cost (Basis for Stocks / Premium for Options). |

#### 3. thinkorswim (TOS) Order Parameters

I will provide the specific order entry details as follows:

* **Entry Price:** Ideally at **P-Mid** or on a successful test of **P-Low**.
* **Stop-Loss (Hard Floor):** * **Logic:** Set **15–20 cents** below the **P-Low**.
* **TOS Type:** **MARKET STOP** triggered by the **Stock Price** (to avoid being wicked out by option spread volatility).


* **Take-Profit (The 2-Tranche Exit):**
* **T1 (Limit Order):** 50% of position at **P-High** (or first major resistance).
* **T2 (Trailing):** 50% of position using a **Weekly ATR Trailing Stop** to capture extended trends.



---

### 📊 Updated Posture Reference Table

*I will use this format to visualize your current risk environment before giving the verdict:*

| Parameter | Current Value |
| --- | --- |
| **Account Balance** | $35,000 |
| **Base Risk (1.5%)** | $525 per trade |
| **Max Allocation** | $1,750 per trade |
| **Current Mode** | [Reading P_010_RiskConfig.json...] |

---

**Would you like me to run a test analysis on a specific ticker (e.g., NVDA, BTC, or SPY) using this reorganized logic?**
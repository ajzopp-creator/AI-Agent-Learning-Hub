Folder,Purpose,Maintenance Rule
00_Inbox/,"Temporary landing for PDFs, transcripts, and screenshots.",Empty weekly; move to 10_Sources.
10_Sources/,"Read-only archive of raw data (The ""Hoard"").","AI only reads these during ""Ingest."""
20_Wiki/,"The Brain. Evergreen pages on ""Market Regimes,"" ""Technical Indicators,"" and ""Asset Classes.""",Compounded with every new source.
30_Analysis/,"Active trade logs, P_115 technical checks, and Risk Management logs.",Linked to relevant Wiki pages.
40_Operations/,"Memory.md, Identity.md, SOPs, and project trackers.","The ""Chief of Staff"" instruction set."
System/,Templates and the CLAUDE.md rules file.,Invisible logic layer.
# AJZ Strategies: Knowledge Operating System

## CORE DIRECTIVE
The vault is the "Single Source of Truth." Before answering, search `20_Wiki/` and `30_Analysis/`. After answering, update the Wiki so knowledge compounds.

## TRADING CONSTRAINTS (P_115)
- **Signal Check:** 100% Buy across 20, 50, 100, and 200-day MAs.
- **Risk Budget:** $525 (1.5% of $35k).
- **Size Penalty:** Apply if price < 200MA.
- **Liquidity:** Spread ≤ 10%, OI ≥ 150.

## KNOWLEDGE MAINTENANCE
- **Founder-led vs. Manager-led:** Always categorize corporate analysis through this lens.
- **Strategic Summary:** Link Macro-Environmental shifts to Operational stocks.
- **Flush the Noise:** In periods of high volatility, prioritize technical signals over "narrative" news.

To integrate the **AI Chief of Staff** and the **Compounding Wiki** into a unified Obsidian Strategy for **AJZ Strategies LLC**, we will focus on a "Quantitative Knowledge Base" (QKB). This setup ensures that market research directly informs trade validation without creating a "bookmark graveyard."

### 1. Folder Architecture (The Vault Structure)
Combine the operational focus of the Chief of Staff with the compounding nature of the Wiki.

| Folder | Purpose | Maintenance Rule |
| :--- | :--- | :--- |
| `00_Inbox/` | Temporary landing for PDFs, transcripts, and screenshots. | Empty weekly; move to `10_Sources`. |
| `10_Sources/` | Read-only archive of raw data (The "Hoard"). | AI only reads these during "Ingest." |
| `20_Wiki/` | **The Brain.** Evergreen pages on "Market Regimes," "Technical Indicators," and "Asset Classes." | Compounded with every new source. |
| `30_Analysis/` | Active trade logs, $P\_115$ technical checks, and Risk Management logs. | Linked to relevant Wiki pages. |
| `40_Operations/` | `Memory.md`, `Identity.md`, SOPs, and project trackers. | The "Chief of Staff" instruction set. |
| `System/` | Templates and the `CLAUDE.md` rules file. | Invisible logic layer. |

---

### 2. The Integrated "Ingest & Compound" Prompt
Use this prompt when adding new market research or data to the vault. It merges the "Summary" role of a Chief of Staff with the "Building" role of the Wiki.

**Prompt:**
> "I am adding [File Name] to the `00_Inbox`. Act as the AI Chief of Staff. 
> 1. **Summarize** the core thesis and extract any 'Strategic Shifts' (e.g., changes in software resilience or trade policy).
> 2. **Update the Wiki:** Check `20_Wiki/` for existing pages on these topics. If they exist, append new insights and flag any contradictions. If not, create a new 'Concept Page.'
> 3. **Identify Opportunities:** Does this data suggest a ticker for the $P115$ system? If so, flag it for the `30_Analysis/` folder.
> 4. **Strategic Link:** Relate this back to our 'Core Philosophical Pillars' (American Dynamism / Risk Over Return)."

---

### 3. $P\_115$ Technical Validation Strategy
The Wiki isn't just for reading; it's for validating. Integrate your specific trading rules into the Obsidian "Query" workflow.

* **Logic Rule:** When querying the vault about a specific trade, the AI must cross-reference the **Technical Rules** (MA 20, 50, 100, 200) with the **Market Regime** notes currently in the Wiki.
* **Risk Guardrail:** Every analysis output must calculate the $1.5\%$ Risk Budget ($525 per trade based on $35k) and check for the "200MA Size Penalty."

---

### 4. The Master `CLAUDE.md` (Strategy Edition)
Create this file in the root of your Obsidian vault to keep the AI aligned.

```markdown
# AJZ Strategies: Knowledge Operating System

## CORE DIRECTIVE
The vault is the "Single Source of Truth." Before answering, search `20_Wiki/` and `30_Analysis/`. After answering, update the Wiki so knowledge compounds.

## TRADING CONSTRAINTS (P_115)
- **Signal Check:** 100% Buy across 20, 50, 100, and 200-day MAs.
- **Risk Budget:** $525 (1.5% of $35k).
- **Size Penalty:** Apply if price < 200MA.
- **Liquidity:** Spread ≤ 10%, OI ≥ 150.

## KNOWLEDGE MAINTENANCE
- **Founder-led vs. Manager-led:** Always categorize corporate analysis through this lens.
- **Strategic Summary:** Link Macro-Environmental shifts to Operational stocks.
- **Flush the Noise:** In periods of high volatility, prioritize technical signals over "narrative" news.
```

---

### 5. Strategy for Maintenance ("The Lint Check")
Once a month, run a "Strategic Lint" prompt to ensure the vault remains "Coherent":
* **Contradiction Check:** "Scan the `20_Wiki/` folder. Are there any market theses from 3 months ago that are contradicted by price action in `30_Analysis/`?"
* **Logic Cleanup:** "Identify any 'orphaned' notes in `10_Sources/` that haven't been synthesized into the Wiki yet."

This system ensures that your **Obsidian Brain** is an active participant in your trading firm, turning "hoarded gold" into a functional, quantitative edge.
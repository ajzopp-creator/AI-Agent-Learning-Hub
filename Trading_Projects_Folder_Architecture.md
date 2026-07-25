# Trading Projects Folder Architecture
## Integrated Structure for AI-Agent-Learning-Hub

This architecture organizes your three trading projects while maintaining integration points for Local LLMs, TOS Scripts, and Python automation.

---

## Recommended Root Structure

```
AI-Agent-Learning-Hub/
│
├── 📁 projects/
│   ├── 📁 P_300_Vantage_Point_Pattern_Recognition/
│   ├── 📁 P_110_TradetheBounce_OIL/
│   └── 📁 P_010_Market_Posture_Weekly_Forecasts/
│
├── 📁 shared_resources/
│   ├── 📁 tos_scripts/
│   ├── 📁 python_utils/
│   ├── 📁 data_exports/
│   └── 📁 llm_prompts/
│
├── 📁 integrations/
│   ├── 📁 lm_studio/
│   ├── 📁 schwab_api/
│   └── 📁 automation/
│
└── 📁 docs/
    ├── 📁 learning_modules/
    └── 📁 project_notes/
```

---

## Detailed Project Structures

### P_300_Vantage_Point_Pattern_Recognition

```
P_300_Vantage_Point_Pattern_Recognition/
│
├── 📁 python/
│   ├── v2_posture.py                    # Main analysis script
│   ├── pattern_detector.py              # Pattern recognition logic
│   └── requirements.txt
│
├── 📁 tos_scripts/
│   ├── vp_signals.ts                    # ThinkScript indicators
│   └── vp_scanner.ts                    # Custom scanner scripts
│
├── 📁 data/
│   ├── 📁 xml_exports/
│   │   ├── History-Grid-SPY-_v2.xml
│   │   └── History-Grid-QQQ-_v2.xml
│   ├── 📁 processed/
│   └── 📁 historical/
│
├── 📁 models/
│   ├── 📁 trained/                      # Saved pattern models
│   └── 📁 configs/                      # Model configurations
│
├── 📁 outputs/
│   ├── 📁 reports/
│   ├── 📁 charts/
│   └── 📁 alerts/
│
└── README.md
```

### P_110_TradetheBounce_OIL

```
P_110_TradetheBounce_OIL/
│
├── 📁 python/
│   ├── bounce_detector.py               # Main bounce logic
│   ├── oil_data_fetcher.py              # Data acquisition
│   ├── backtest_engine.py               # Strategy backtesting
│   └── requirements.txt
│
├── 📁 tos_scripts/
│   ├── oil_bounce_indicator.ts          # Visual bounce signals
│   ├── oil_levels.ts                    # Support/resistance
│   └── oil_scanner.ts                   # Bounce scanner
│
├── 📁 data/
│   ├── 📁 xml_exports/                  # TOS grid exports
│   ├── 📁 price_data/                   # Historical oil data
│   └── 📁 correlations/                 # Related instruments
│
├── 📁 strategies/
│   ├── 📁 rules/                        # Entry/exit rules
│   └── 📁 backtests/                    # Backtest results
│
├── 📁 outputs/
│   ├── 📁 trade_logs/
│   ├── 📁 performance/
│   └── 📁 alerts/
│
└── README.md
```

### P_010_Market_Posture_Weekly_Forecasts

```
P_010_Market_Posture_Weekly_Forecasts/
│
├── 📁 python/
│   ├── weekly_posture.py                # Main forecast generator
│   ├── data_aggregator.py               # Multi-source data
│   ├── forecast_engine.py               # Prediction logic
│   └── requirements.txt
│
├── 📁 tos_scripts/
│   ├── posture_dashboard.ts             # Weekly dashboard
│   ├── breadth_indicators.ts            # Market breadth
│   └── sector_rotation.ts               # Sector analysis
│
├── 📁 data/
│   ├── 📁 xml_exports/
│   ├── 📁 weekly_snapshots/
│   └── 📁 economic_calendar/
│
├── 📁 forecasts/
│   ├── 📁 2025/                         # Organized by year
│   │   ├── 📁 Q1/
│   │   ├── 📁 Q2/
│   │   ├── 📁 Q3/
│   │   └── 📁 Q4/
│   └── 📁 archive/
│
├── 📁 outputs/
│   ├── 📁 reports/
│   ├── 📁 visualizations/
│   └── 📁 email_summaries/
│
└── README.md
```

---

## Shared Resources Structure

```
shared_resources/
│
├── 📁 tos_scripts/
│   ├── 📁 indicators/                   # Reusable indicators
│   ├── 📁 scanners/                     # Common scanners
│   ├── 📁 strategies/                   # Shared strategies
│   └── 📁 templates/                    # Script templates
│
├── 📁 python_utils/
│   ├── xml_parser.py                    # TOS XML parsing
│   ├── data_cleaner.py                  # Data preprocessing
│   ├── chart_generator.py               # Visualization utils
│   ├── alert_system.py                  # Notification system
│   └── config.py                        # Shared configurations
│
├── 📁 data_exports/
│   ├── 📁 raw/                          # Unprocessed TOS exports
│   ├── 📁 cleaned/                      # Processed data
│   └── 📁 combined/                     # Multi-project data
│
└── 📁 llm_prompts/
    ├── 📁 analysis/                     # Market analysis prompts
    ├── 📁 summarization/                # Report generation
    └── 📁 trade_review/                 # Trade journaling prompts
```

---

## LLM Integration Structure

```
integrations/
│
├── 📁 lm_studio/
│   ├── 📁 models/                       # Model references
│   ├── 📁 prompts/
│   │   ├── pattern_analysis.txt
│   │   ├── bounce_evaluation.txt
│   │   └── weekly_summary.txt
│   ├── 📁 outputs/                      # LLM-generated content
│   └── config.json                      # LM Studio settings
│
├── 📁 schwab_api/
│   ├── 📁 credentials/                  # API keys (gitignored!)
│   ├── 📁 wrappers/                     # Python API wrappers
│   ├── account_manager.py
│   ├── position_sizer.py
│   └── order_manager.py                 # Future: order submission
│
└── 📁 automation/
    ├── 📁 schedulers/                   # Cron jobs, task scheduling
    ├── 📁 workflows/                    # End-to-end pipelines
    ├── 📁 email_agents/                 # Email automation
    └── 📁 alerts/                       # Alert routing
```

---

## Quick Setup Commands (PowerShell)

```powershell
# Navigate to your AI-Agent-Learning-Hub root
cd "C:\path\to\AI-Agent-Learning-Hub"

# Create project directories
$projects = @(
    "projects\P_300_Vantage_Point_Pattern_Recognition\python",
    "projects\P_300_Vantage_Point_Pattern_Recognition\tos_scripts",
    "projects\P_300_Vantage_Point_Pattern_Recognition\data\xml_exports",
    "projects\P_300_Vantage_Point_Pattern_Recognition\data\processed",
    "projects\P_300_Vantage_Point_Pattern_Recognition\data\historical",
    "projects\P_300_Vantage_Point_Pattern_Recognition\models\trained",
    "projects\P_300_Vantage_Point_Pattern_Recognition\models\configs",
    "projects\P_300_Vantage_Point_Pattern_Recognition\outputs\reports",
    "projects\P_300_Vantage_Point_Pattern_Recognition\outputs\charts",
    "projects\P_300_Vantage_Point_Pattern_Recognition\outputs\alerts",
    
    "projects\P_110_TradetheBounce_OIL\python",
    "projects\P_110_TradetheBounce_OIL\tos_scripts",
    "projects\P_110_TradetheBounce_OIL\data\xml_exports",
    "projects\P_110_TradetheBounce_OIL\data\price_data",
    "projects\P_110_TradetheBounce_OIL\data\correlations",
    "projects\P_110_TradetheBounce_OIL\strategies\rules",
    "projects\P_110_TradetheBounce_OIL\strategies\backtests",
    "projects\P_110_TradetheBounce_OIL\outputs\trade_logs",
    "projects\P_110_TradetheBounce_OIL\outputs\performance",
    "projects\P_110_TradetheBounce_OIL\outputs\alerts",
    
    "projects\P_010_Market_Posture_Weekly_Forecasts\python",
    "projects\P_010_Market_Posture_Weekly_Forecasts\tos_scripts",
    "projects\P_010_Market_Posture_Weekly_Forecasts\data\xml_exports",
    "projects\P_010_Market_Posture_Weekly_Forecasts\data\weekly_snapshots",
    "projects\P_010_Market_Posture_Weekly_Forecasts\data\economic_calendar",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\2025\Q1",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\2025\Q2",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\2025\Q3",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\2025\Q4",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\archive",
    "projects\P_010_Market_Posture_Weekly_Forecasts\outputs\reports",
    "projects\P_010_Market_Posture_Weekly_Forecasts\outputs\visualizations",
    "projects\P_010_Market_Posture_Weekly_Forecasts\outputs\email_summaries"
)

foreach ($folder in $projects) {
    New-Item -ItemType Directory -Path $folder -Force
}

# Create shared resources
$shared = @(
    "shared_resources\tos_scripts\indicators",
    "shared_resources\tos_scripts\scanners",
    "shared_resources\tos_scripts\strategies",
    "shared_resources\tos_scripts\templates",
    "shared_resources\python_utils",
    "shared_resources\data_exports\raw",
    "shared_resources\data_exports\cleaned",
    "shared_resources\data_exports\combined",
    "shared_resources\llm_prompts\analysis",
    "shared_resources\llm_prompts\summarization",
    "shared_resources\llm_prompts\trade_review"
)

foreach ($folder in $shared) {
    New-Item -ItemType Directory -Path $folder -Force
}

# Create integrations
$integrations = @(
    "integrations\lm_studio\models",
    "integrations\lm_studio\prompts",
    "integrations\lm_studio\outputs",
    "integrations\schwab_api\credentials",
    "integrations\schwab_api\wrappers",
    "integrations\automation\schedulers",
    "integrations\automation\workflows",
    "integrations\automation\email_agents",
    "integrations\automation\alerts"
)

foreach ($folder in $integrations) {
    New-Item -ItemType Directory -Path $folder -Force
}

# Create docs
$docs = @(
    "docs\learning_modules",
    "docs\project_notes"
)

foreach ($folder in $docs) {
    New-Item -ItemType Directory -Path $folder -Force
}

Write-Host "Folder structure created successfully!" -ForegroundColor Green
```

---

## .gitignore Recommendations

```gitignore
# Sensitive data
integrations/schwab_api/credentials/
*.env
**/api_keys.*

# Data files (too large for git)
**/data/xml_exports/*.xml
**/data/historical/
**/data/price_data/

# Outputs (regenerated)
**/outputs/
**/forecasts/archive/

# Python
__pycache__/
*.pyc
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## Integration Workflow Example

```
1. TOS Export → data/xml_exports/
2. Python Parser → data/processed/
3. Analysis Script → outputs/reports/
4. LLM Summary → integrations/lm_studio/outputs/
5. Email Agent → Automated delivery
```

---

## Next Steps

1. **Move existing files**: Place `v2_posture.py` and XML files into P_300 structure
2. **Create shared utils**: Build `xml_parser.py` for all projects to use
3. **Set up .gitignore**: Protect sensitive data and large files
4. **Document each project**: Create README.md files with project goals


---

## Python Environment

### Shared Conda Environment: p140

All projects use a **single shared conda environment** named p140.

- **Location:** C:\Users\Trader\.conda\envs\p140\
- **Python executable:** C:\Users\Trader\.conda\envs\p140\python.exe
- **Scope:** Shared across P_010, P_020, P_300, and all future projects

**Key packages installed:**
- pandas, numpy � data analysis
- pandas_ta � technical analysis indicators
- numba � performance acceleration
- python-dotenv � environment variables
- pyyaml � config file support
- loguru � logging
- colorama, tqdm, pytz, pytest

### Why one shared environment?
Each project does NOT have its own venv. A single conda environment means:
- One place to install packages
- No broken venvs if disk issues occur
- All projects stay in sync on package versions

### How batch files reference it:
Every .bat file calls Python directly by full path � no activation needed:
`
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\your_script.py"
`

### Future rename note:
The name p140 is a legacy placeholder with no meaningful connection to this project.
If renamed in the future, all .bat files across P_010 (3 files), P_020 (10+ files),
and P_300 (2 files) must be updated to point to the new environment path.

---
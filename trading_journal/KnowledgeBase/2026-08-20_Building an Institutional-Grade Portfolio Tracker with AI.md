---
title: "Building an Institutional-Grade Portfolio Tracker with AI"
source: "https://mispricedassets.substack.com/p/building-an-institutional-grade-portfolio?r=30kzn1&utm_medium=ios&triedRedirect=true"
author:
  - "[[Nick Nemeth]]"
date: "2026-08-20"
published: 2026-01-24
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
sector:
origin:
---
![](https://substackcdn.com/image/fetch/$s_!P-D_!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F75339ad4-5768-4a0b-a175-76b8b63397a5_1280x737.webp)

## Why You Should Spend a Couple Hours Learning This

Learning to use Claude Code is one of the highest-ROI skills you can develop right now. I’m not exaggerating when I say it feels like a video game.

Think about it: you describe what you want in plain English, and an AI builds it for you in real-time. You watch it write code, fetch data, create files, fix its own errors. When something isn’t quite right, you just say “make the headers darker” or “add a correlation matrix” and it does it. Almost instantaneously.

**The investment:** A couple hours to learn the basics, $20/month for Claude Pro.

**The payoff:** You now have a personal AI developer who works 24/7, never gets tired, never judges your questions, and can build literally anything you can describe. Portfolio trackers today. Automated reports tomorrow. Data analysis tools next week. The skill compounds forever.

This guide will walk you through building one specific project - a portfolio tracker - but the real value is learning how to work with Claude. Once you get it, you’ll start seeing opportunities everywhere. “Wait, Claude could automate this.” “Claude could build me a tool for that.” It changes how you think about problems.

Trust me: the couple hours you spend on this will pay for itself many times over in time saved and opportunities captured.

---

## What We Are Building

By the end of this guide, you will have a fully automated Excel workbook that:

- Fetches live stock prices automatically from Yahoo Finance
- Calculates P&L, returns, and portfolio weights using dynamic Excel formulas
- Includes institutional-grade risk analytics (VaR, Sharpe Ratio, correlations)
- Features Bloomberg Terminal-style professional formatting
- Updates with a single command - no manual data entry ever again

**The best part?** You do not need to know how to code. The AI writes all the code for you. You just need to describe what you want in plain English.

![](https://substackcdn.com/image/fetch/$s_!2OT0!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe6a64089-3fca-4738-b5da-81c743cd7a41_1502x680.png)

Do you know how your names are correlated (I was surprised by some of mine!)

---

## What is Claude?

Claude is an AI assistant created by Anthropic. Think of it as an extremely knowledgeable colleague who can write code, analyze data, and help you build tools. Unlike ChatGPT, Claude has a feature called “Claude Code” - a command-line interface that can directly read and write files on your computer, run Python scripts, and interact with your system.

### Why Claude Code is Different

Regular AI chatbots can only give you text responses. You ask for code, they show you code, and then you have to figure out how to run it yourself. Claude Code actually executes the code for you.

**Claude Code can:**

- Read your existing files (like your trade log spreadsheet)
- Write and execute Python code directly on your computer
- Create Excel files with complex formulas and formatting
- Fetch live data from the internet (stock prices, company info)
- Make changes iteratively based on your feedback
- Fix its own errors when something goes wrong

It is like having a developer sitting next to you, except this developer works instantly, never gets frustrated, and is available at 3am when you have a random idea.

---

## Why Build a Custom Portfolio Tracker?

### The Problem with Existing Solutions

**Brokerage Platforms:** Limited customization. You cannot add your own metrics, investment theses, or risk analytics. You are stuck with whatever they give you.

**Google Sheets/Excel Templates:** Static and dumb. They do not fetch live data. Every update requires manual copy-paste. They break constantly.

**Portfolio Apps (Sharesight, Stock Events, etc.):** Monthly subscription fees. Your data lives on their servers. You cannot see how calculations work. You cannot export your logic. If they shut down, you lose everything.

**Bloomberg Terminal:** $24,000 per year. Enough said.

### The Solution: Your Own Glass Box System

With Claude, you build exactly what you want:

- **Full transparency** - click any cell and see exactly how it is calculated
- **No subscriptions** - runs on your computer, you own everything forever
- **Fully customizable** - want a new metric? Tell Claude to add it
- **Live updates** - change any input and everything recalculates instantly
- **Professional output** - Bloomberg-quality formatting without Bloomberg prices
- **Your data stays private** - nothing leaves your computer

---

## What You Need Before Starting

### 1\. Claude Pro Subscription ($20/month)

Claude Code requires a Claude Pro subscription at minimum. This costs $20/month and gives you access to Claude Code and extended conversation limits.

**Sign up at:**

[https://claude.ai](https://claude.ai/)

> **Note:** For complex projects, you might hit usage limits with Pro. Claude Max ($100/month) gives you more capacity. But start with Pro - it should be enough for this project.

---

### 2\. Python Installation

Python is a programming language that Claude will use to build your spreadsheet. Do not worry - you will not need to write any Python yourself. Claude does all of that.

**Download from:** [https://www.python.org/downloads/](https://www.python.org/downloads/)

#### Windows Installation

1. Go to python.org and click “Download Python” (get the latest version, like 3.12)
2. Run the installer
3. **⚠️ CRITICAL:** Check the box that says **“Add Python to PATH”** during installation. If you miss this, nothing will work.
4. Click “Install Now”
5. Verify it worked: Open Command Prompt (search “cmd” in Windows) and type:
```markup
python --version
```

You should see something like “Python 3.12.0”

#### Mac Installation

**Option A: Download from python.org**

- Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Download the macOS installer
- Run the `.pkg` file and follow the prompts

**Option B: Using Homebrew (recommended for Mac users)**

```markup
brew install python
```

Verify it worked: Open **Terminal** (search “Terminal” in Spotlight) and type:

```markup
python3 --version
```

> **⚠️ Important Mac Note:** On Mac, use `python3` and `pip3` instead of `python` and `pip`.

---

### 3\. Node.js Installation

Node.js is required to install Claude Code.

**Download from:**

https://nodejs.org

Download the LTS (Long Term Support) version.

#### Windows

Run the installer with default settings.

#### Mac

**Option A:** Run the.pkg installer from nodejs.org

**Option B:** Using Homebrew:

```markup
brew install node
```

Verify installation:

```markup
node --version
```

---

### 4\. Claude Code Installation

Once Node.js is installed, open your terminal and run:

Windows Mac `npm install -g @anthropic-ai/claude-code` `npm install -g @anthropic-ai/claude-code`

If you get a permission error on Mac, try:

```markup
sudo npm install -g @anthropic-ai/claude-code
```

---

### 5\. Your Trade Log Spreadsheet

Here you go — same content, just formatted so Substack cleanly renders the code as code blocks (and everything is easy to copy/paste). Nothing is changed.

---

## 5\. Your Trade Log Data

You have two options for getting your trade data into the system:

**Option A: Manual Excel File (Tedious)**

Create an Excel file (e.g., “My Portfolio.xlsx”) with a sheet named exactly `Trade_Log` containing these columns:

- Trade\_ID - Unique number for each trade (1, 2, 3...)
- Date - Trade date (YYYY-MM-DD format, e.g., 2025-12-31)
- Ticker - Stock symbol (e.g., AAPL, MSFT, GOOGL)
- Action - BUY or SELL (must be capitalized)
- Shares - Number of shares traded
- Price - Price per share at time of trade
- Gross\_Value - Shares × Price
- Commission - Trading fees (put 0 if no commission)
- Net\_Cost - Gross\_Value + Commission for buys, Gross\_Value - Commission for sells
- Cash\_Balance - Running cash balance after each trade
- Notes - Optional notes (e.g., “Initial allocation”)

**Option B: Connect to Your Broker API (Automated)**

Most major brokers offer APIs that let you pull your trade history automatically. Here’s how to set this up with popular brokers:

*Interactive Brokers (IBKR)*

```markup
pip install ib_insync
```

Tell Claude:

```markup
Connect to my Interactive Brokers account using ib_insync and pull my trade history. My TWS is running on localhost port 7497.
```

*TD Ameritrade / Charles Schwab*

```markup
pip install schwab-py
```

Tell Claude:

```markup
Use the Schwab API to fetch my trade history. Here's my API key: [your key]. Save it in the Trade_Log format.
```

*Robinhood (Unofficial)*

```markup
pip install robin_stocks
```

Tell Claude:

```markup
Use robin_stocks to log into my Robinhood account and export my trade history. My credentials are [email] and I'll enter my MFA code when prompted.
```

*Fidelity / Vanguard / Others*

These brokers don’t have public APIs. Export your trades as CSV from their website, then tell Claude:

```markup
Read my exported trades from [path]/fidelity_trades.csv and convert them to the Trade_Log format.
```

**Example Prompt for Broker Connection:**

```markup
Connect to my Alpaca brokerage account and sync my trades:
- API Key: PKXXXXXXXXXXXXXXXX
- Secret Key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
- Use paper trading endpoint (or: use live endpoint)

Pull all trades from the last 12 months and format them into my Trade_Log sheet. Then fetch current positions and reconcile against my trade history.
```

⚠️ **Security Note:** Never share API keys in public channels. Consider using environment variables:

Tell Claude:

```markup
Read my Alpaca API credentials from environment variables ALPACA_API_KEY and ALPACA_SECRET_KEY
```

**Setting Up Environment Variables:**

Windows (Command Prompt):

```markup
set ALPACA_API_KEY=your_key_here
set ALPACA_SECRET_KEY=your_secret_here
```

Mac/Linux (Terminal):

```markup
export ALPACA_API_KEY=your_key_here
export ALPACA_SECRET_KEY=your_secret_here
```

**Which Option Should You Choose?**

- Just getting started, few trades → Option A (Manual Excel)
- Active trader, 10+ trades/month → Option B (Broker API)
- Multiple brokers → Option A + manual consolidation
- Want fully automated updates → Option B with daily sync script

Once your `Trade_Log` is populated (either way), Claude can build the rest of the system on top of it.

---

## Information You Need to Gather Before Starting

Before launching Claude, gather this information. Having it ready will make the process much smoother.

### Required Information

**File Path to Your Trade Log:** The exact location of your Excel file.

Windows Mac `C:\Users\YourName\Desktop\My Portfolio.xlsx` `/Users/YourName/Desktop/My Portfolio.xlsx`

**Output File Path:** Where should Claude save the new workbook? Use a DIFFERENT name to avoid overwriting.

Windows Mac `C:\Users\YourName\Desktop\My Portfolio_BUILT.xlsx` `/Users/YourName/Desktop/My Portfolio_BUILT.xlsx`

**Starting Capital:** How much cash did you start with? Example: $1,000,000

**Start Date:** When did you begin? This is usually when you made your first trades. Example: December 31, 2024

> **💡 Mac Tip: Getting File Paths**  
> To get the exact path of any file on Mac:
> 
> 1. Right-click the file in Finder
> 2. Hold **Option** key
> 3. Click “Copy as Pathname”

---

## Step-by-Step Instructions

### Step 1: Prepare Your Trade Log

Create an Excel file with your trades. Here is an example of what the Trade\_Log sheet should look like:

![](https://substackcdn.com/image/fetch/$s_!ZQZ9!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F37929a6e-fe32-4668-bfcd-e9c9f9942f80_1458x394.png)

> **⚠️ Important:** The Cash\_Balance column should show your running cash balance AFTER each trade. Start with your initial capital and subtract each BUY (add back each SELL).

---

### Step 2: Launch Claude Code

Open your terminal and navigate to where your files are:

Windows Mac Open Command Prompt (search “cmd”) Open Terminal (search “Terminal”) `cd Desktop` `cd ~/Desktop` `claude` `claude`

The first time you run this, it will ask you to authenticate. Follow the prompts to log in with your Anthropic account.

---

### Step 3: Give Claude Your Initial Prompt

This is the most important step. Copy the prompt below and modify the bracketed sections with your actual information.

> **⚠️ CRITICAL:** Notice how the prompt explicitly tells Claude to use FORMULAS, not hardcoded values. This is essential.

```markup
I want you to build me a portfolio tracking spreadsheet. Here are my requirements:

**FILE LOCATIONS:**
- Input: [YOUR PATH]/My Portfolio.xlsx (contains Trade_Log sheet with my trades)
- Output: [YOUR PATH]/My Portfolio_BUILT.xlsx (create NEW file, do NOT overwrite my original)

**PORTFOLIO DETAILS:**
- Starting capital: $[YOUR AMOUNT] (e.g., $1,000,000)
- Start date: [YOUR DATE] (e.g., December 31, 2025)
- All initial positions bought at closing prices on the start date

**CRITICAL - FORMULA-BASED ARCHITECTURE:**
The Python script should ONLY:
1. Read my Trade_Log
2. Fetch market data via yfinance (prices, volumes, company info)
3. Build the Excel structure with FORMULAS

IMPORTANT: Use Excel FORMULAS for ALL calculations. Do NOT hardcode any calculated values.
Every P&L, every percentage, every total should be a formula like =D2*F2, not a static number.
The spreadsheet must update automatically when I change any price in Market_Data.

**SHEETS TO CREATE:**

Data Lakes (Python fills these with raw data):
- Trade_Log: Copy of my trades
- Market_Data: Daily closing prices (rows = dates, columns = tickers)
- Reference_Data: Company name, sector, industry, country, beta for each ticker
- Daily_Units: Number of shares held per ticker per day (calculated from trades)
- Daily_Cash: Cash balance per day

Analytics Sheets (ALL FORMULAS - no hardcoded values):
- Dashboard: KPIs (NAV, Total Return, Sharpe Ratio, Max Drawdown), NAV chart, allocation pie chart
- Positions: Ticker, Company, Sector, Shares, Avg Cost, Current Price, Day Change %, Cost Basis, Market Value, Unrealized P&L, P&L %, Portfolio Weight
- Equity_Curve: Date, Cash, Invested Value, Total NAV, Daily Return, Cumulative Return, Drawdown
- Sector_Exposure: Sector breakdown with dollar amounts and weights
- Geographic_Exposure: Country breakdown with dollar amounts and weights

**STYLING:**
- Professional Bloomberg Terminal look
- Segoe UI font, 85% zoom, hide gridlines
- Dark navy headers (#1C2541) with white text
- Alternating row colors (zebra striping) for readability
- Green (#007A33) for positive values, Red (#B81D13) for negative
- Freeze the header row and first column on each sheet

Please start by reading my Trade_Log file, then build the complete system.
```

---

### Step 4: Watch Claude Work

This is the fun part. Claude will start working and you will see real-time output:

```markup
-> Reading Trade_Log...
-> Found 15 unique tickers: AAPL, MSFT, GOOGL...
-> Fetching market data from Yahoo Finance...
  + AAPL: 18 trading days
  + MSFT: 18 trading days
  ...
-> Fetching reference data...
  + AAPL: Apple Inc., Technology, United States
  ...
-> Building workbook...
-> Creating Dashboard sheet...
-> Creating Positions sheet with formulas...
-> Creating Equity_Curve sheet...
  ...
-> BUILD COMPLETE
-> Saved to: [Your output path]
```

Claude may ask permission to install Python packages (like yfinance, xlsxwriter). Say yes.

---

### Step 5: Open and Verify the Formulas

Tell Claude:

```markup
open the spreadsheet
```

Excel will open. Now verify the formulas are working correctly:

1. Go to the **Positions** sheet
2. Click on any P&L cell
3. Look at the formula bar at the top - you should see a formula like `=I2-H2`, NOT just a number
4. Go to **Market\_Data** sheet
5. Manually change one price to a different number
6. Go back to **Positions** - the P&L should have updated automatically

> **⚠️ If the P&L did NOT update:** Tell Claude: “The P&L cells have hardcoded values. Rebuild with formulas instead.”

---

## Enhancing Your Portfolio Tracker

Once you have the basic system working, you can keep asking Claude to add more features. This is where it gets really fun - you just describe what you want and watch it appear.

### Adding Risk Analytics

Copy and paste this prompt:

```markup
Add the following risk analytics sheets to my portfolio:

- Correlation: A matrix showing the correlation between all my positions. Use 3-color conditional formatting (green for low correlation, yellow for medium, red for high).

- Risk_Metrics: A summary sheet with these metrics:
  - Annualized Return
  - Annualized Volatility
  - Sharpe Ratio
  - Sortino Ratio
  - Maximum Drawdown
  - Beta to SPY
  - VaR 95% (Value at Risk)
  - VaR 99%
  - CVaR 95% (Conditional VaR)

- Stress_Testing: Show what happens to my portfolio in these scenarios:
  - Market crash: -20%
  - Correction: -10%
  - Flash crash: -5%
  - Rally: +10%
  Calculate the impact using my portfolio's beta.

Use formulas where possible. Apply the same professional styling as the other sheets.
```

---

### Adding Investment Theses

Provide your investment thesis for each position:

```markup
Add an Investment_Theses sheet with columns: Ticker, Weight (formula linking to Positions), Thesis, Catalyst, Edge

Here are my theses (adjust column widths so the text is readable, use text wrapping):

AAPL:
- Thesis: iPhone installed base approaching 2 billion creates massive services revenue opportunity. Hardware is mature but services growing 15%+ annually.
- Catalyst: India manufacturing expansion reduces China risk, unlocks next billion users.
- Edge: Market treats it as ex-growth hardware company, missing services compounding.

MSFT:
- Thesis: Cloud + AI leadership. Azure growing faster than AWS. Copilot monetization just starting.
- Catalyst: Enterprise Copilot adoption hitting inflection point in 2026.
- Edge: Multiple expansion as market realizes AI revenue is real, not hype.

[Continue for each of your tickers...]

Set row heights to 50-60 pixels so the text fits. Use zebra striping.
```

---

### Creating the Update Script

You do not want to rebuild the entire workbook every day. Ask Claude to create an update script:

```markup
Create an update_portfolio.py script that I can run daily to update my portfolio. It should:

1. Read the existing workbook (not rebuild it)
2. Fetch new market data from Yahoo Finance for all dates after the last date in Market_Data
3. Append the new prices to Market_Data
4. Check my original Trade_Log file for any new trades and sync them
5. Update Daily_Units and Daily_Cash with the new dates
6. If there is a new ticker I have never traded before, add it to Reference_Data and create new columns in Market_Data and Daily_Units

Include three ways to run it:
- python update_portfolio.py (full sync: trades + prices)
- python update_portfolio.py quick (just fetch latest prices, faster)
- python update_portfolio.py trade 34 2026-01-27 AAPL BUY 100 150.50 (add a single trade manually)

Important: This script should APPEND data, not rebuild. The Excel formulas will automatically recalculate when the new data appears.
```

---

## Your Daily Workflow (After Setup)

Once everything is set up, your daily routine is simple:

### To Update Prices (30 seconds)

Windows Mac Open Command Prompt Open Terminal `cd Desktop` `cd ~/Desktop` `python update_portfolio.py quick` `python3 update_portfolio.py quick`

Open your spreadsheet - all prices and calculations are updated.

### To Log a New Trade

**Option A** - Add to your original Trade\_Log Excel file, then run:

Windows Mac `python update_portfolio.py` `python3 update_portfolio.py`

**Option B** - Command line:

Windows Mac `python update_portfolio.py trade 34 2026-01-27 AAPL BUY 100 150.50` `python3 update_portfolio.py trade 34 2026-01-27 AAPL BUY 100 150.50`

### To Add a New Feature

1. Launch Claude Code: `claude`
2. Describe what you want: “Add a sheet that shows my best and worst performers this month”
3. Watch Claude build it
4. If it’s not quite right: “Make the percentages show 2 decimal places”
5. Repeat until perfect

---

## Troubleshooting Common Issues

### “python” is not recognized as an internal or external command

#### Windows

Python was not added to PATH during installation. Uninstall Python, reinstall it, and **CHECK THE BOX** that says “Add Python to PATH”.

#### Mac

On Mac, use `python3` instead of `python`:

```markup
python3 --version
python3 update_portfolio.py
```

---

### “pip: command not found” (Mac)

Use `pip3` instead:

```markup
pip3 install yfinance
```

---

### “PermissionError: \[Errno 13\] Permission denied”

The Excel file is open. Close Excel completely before running the script.

---

### “ModuleNotFoundError: No module named ‘yfinance’”

Run this command to install the missing package:

Windows Mac `pip install yfinance` `pip3 install yfinance`

---

### Permission errors when installing packages (Mac)

Add `--user` flag:

```markup
pip3 install --user yfinance openpyxl xlsxwriter
```

---

### Excel file won’t open from Terminal (Mac)

On Mac, use:

```markup
open "My Portfolio_BUILT.xlsx"
```

Or tell Claude to use: `open "/Users/YourName/Desktop/My Portfolio_BUILT.xlsx"`

---

### “yfinance returns empty data”

Either the ticker symbol is wrong (check Yahoo Finance for the correct symbol) or Yahoo Finance is temporarily unavailable. Try again in a few minutes.

---

### “UnicodeEncodeError or encoding errors”

Run Python with:

```markup
python -X utf8 your_script.py
```

---

### “Claude says it ran out of context”

Start a new conversation. Tell Claude: “Read my file at \[path\] and continue where we left off.” Claude can read the files from previous sessions.

---

### “Cells show numbers instead of formulas”

Claude hardcoded values instead of using formulas. Tell Claude: “The cells in column J have hardcoded values. Rebuild this column using formulas like =I2-H2 so they update automatically.”

---

### Homebrew not installed? (Mac)

Install it first (one-time setup):

```markup
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## What Success Looks Like

When complete, your workbook will have sheets like these:

Sheet What It Shows Dashboard Executive summary with big KPIs, NAV chart, allocation donut Positions Live P&L for each stock with data bars showing weights Equity\_Curve Daily portfolio value with running drawdown Investment\_Theses Your thesis, catalyst, and edge for each position Valuation P/E, EV/EBITDA, P/B with heat map formatting Profitability Margins and ROE with 3-color scales Risk\_Trading Beta, short interest, distance from 52-week high Analyst\_Estimates Price targets and rating badges Smart\_Labels Thematic exposure tags with color coding Correlation Matrix showing how your stocks move together Risk\_Metrics VaR, Sharpe, Sortino, Beta, Max Drawdown Stress\_Testing What happens in a crash Sector\_Exposure Sector breakdown with weight bars Geographic\_Exposure Country breakdown Trade\_Log All your transactions Market\_Data Daily prices (the data lake) Reference\_Data Company info (the data lake) Daily\_Units Shares held each day Daily\_Cash Cash balance each day

---

## Quick Reference: Windows vs Mac Commands

Task Windows Mac Open terminal Search “cmd” Search “Terminal” Navigate to Desktop `cd Desktop` `cd ~/Desktop` Run Python `python script.py` `python3 script.py` Install packages `pip install package` `pip3 install package` Check Python version `python --version` `python3 --version` Open Excel file `start "file.xlsx"` `open "file.xlsx"` File paths `C:\Users\Name\Desktop\file.xlsx` `/Users/Name/Desktop/file.xlsx` Launch Claude Code `claude` `claude`

---

## Final Thoughts

You just built something that would cost you $24,000/year from Bloomberg, or $50-100/month from portfolio apps, or weeks of developer time if you hired someone. **Total cost: $20/month for Claude Pro and a couple hours of your time.**

But the real value is not the spreadsheet. It is that you now know how to use Claude Code. This same skill works for building reports, automating data analysis, creating dashboards, processing documents, and a thousand other things.

Once you get comfortable with Claude, you will start seeing opportunities everywhere. “Wait, Claude could automate this boring task.” “Claude could build a tool for that.” It fundamentally changes how you think about problems.

Remember: Claude is not a magic wand. You will hit bugs. Things will break. Claude will occasionally misunderstand you. But the iteration cycle is so fast that it does not matter. Just tell Claude what went wrong and it fixes it. That is the game. And it is a fun game.
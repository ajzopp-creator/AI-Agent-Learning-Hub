# =============================================================================
# P_300 Remaining Setup - Shared Utils, LLM Prompts, Launcher
# =============================================================================
# Your files are already in place! This script adds:
#   1. shared_resources/python_utils/xml_parser.py
#   2. shared_resources/llm_prompts/analysis/*.txt
#   3. run_P300.ps1 launcher at root
# =============================================================================
# Run from: C:\users\trader\AI-Agent-Learning-Hub
# =============================================================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  P_300 Remaining Setup                    " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = Get-Location
Write-Host "Root: $rootPath" -ForegroundColor Yellow
Write-Host ""

# -----------------------------------------------------------------------------
# STEP 1: CREATE SHARED XML PARSER UTILITY
# -----------------------------------------------------------------------------

Write-Host "STEP 1: Creating shared_resources/python_utils/xml_parser.py..." -ForegroundColor Magenta

$sharedUtils = Join-Path $rootPath "shared_resources\python_utils"

if (!(Test-Path $sharedUtils)) {
    New-Item -ItemType Directory -Path $sharedUtils -Force | Out-Null
}

$xmlParserContent = @"
# =============================================================================
# xml_parser.py - Shared TOS XML Export Parser
# =============================================================================
# Location: shared_resources/python_utils/xml_parser.py
# Used by: P_300, D_130, P_010 projects
# =============================================================================

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


def parse_history_xml(xml_path: str) -> Dict:
    """
    Parse TOS History Grid XML export file.
    
    Args:
        xml_path: Path to the XML file (e.g., History Grid (SPY)_v2.xml)
    
    Returns:
        Dictionary containing parsed data with keys:
        - 'symbol': Stock symbol
        - 'data': List of dictionaries with OHLCV data
        - 'metadata': Additional file metadata
    
    Example:
        from shared_resources.python_utils.xml_parser import parse_history_xml
        
        data = parse_history_xml('data/xml_exports/History Grid (SPY)_v2.xml')
        df = pd.DataFrame(data['data'])
    """
    
    path = Path(xml_path)
    if not path.exists():
        raise FileNotFoundError(f"XML file not found: {xml_path}")
    
    tree = ET.parse(path)
    root = tree.getroot()
    
    # Extract symbol from filename (e.g., "History Grid (SPY)_v2.xml" -> "SPY")
    filename = path.stem
    symbol = None
    if '(' in filename and ')' in filename:
        symbol = filename.split('(')[1].split(')')[0]
    
    result = {
        'symbol': symbol,
        'data': [],
        'metadata': {
            'source_file': str(path.name),
            'full_path': str(path.absolute())
        }
    }
    
    # Parse based on TOS XML structure
    for row in root.findall('.//Row'):
        row_data = {}
        for cell in row:
            tag = cell.tag
            value = cell.text
            
            # Convert numeric values
            if value and tag in ['Open', 'High', 'Low', 'Close', 'Volume', 'Price']:
                try:
                    value = float(value.replace(',', '')) if '.' in value else int(value.replace(',', ''))
                except ValueError:
                    pass
            
            row_data[tag] = value
        
        if row_data:
            result['data'].append(row_data)
    
    return result


def parse_multiple_xmls(xml_folder: str, pattern: str = "*.xml") -> Dict[str, Dict]:
    """
    Parse multiple XML files from a folder.
    
    Args:
        xml_folder: Path to folder containing XML files
        pattern: Glob pattern for matching files (default: *.xml)
    
    Returns:
        Dictionary with symbols as keys and parsed data as values
    """
    
    folder = Path(xml_folder)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {xml_folder}")
    
    results = {}
    for xml_file in folder.glob(pattern):
        try:
            parsed = parse_history_xml(str(xml_file))
            key = parsed['symbol'] or xml_file.stem
            results[key] = parsed
        except Exception as e:
            print(f"Warning: Failed to parse {xml_file.name}: {e}")
    
    return results


def xml_to_dataframe(xml_path: str) -> pd.DataFrame:
    """
    Convenience function to directly get a DataFrame from XML.
    
    Args:
        xml_path: Path to the XML file
    
    Returns:
        pandas DataFrame with the parsed data
    """
    parsed = parse_history_xml(xml_path)
    df = pd.DataFrame(parsed['data'])
    df.attrs['symbol'] = parsed['symbol']
    return df


# =============================================================================
# Module test
# =============================================================================
if __name__ == "__main__":
    print("XML Parser Utility - Test Mode")
    print("=" * 50)
    
    test_path = Path(__file__).parent.parent.parent / "projects" / "P_300_Vantage_Point_Pattern_Recognition" / "data" / "xml_exports"
    
    if test_path.exists():
        print(f"Found folder: {test_path}")
        xml_files = list(test_path.glob("*.xml"))
        print(f"XML files found: {len(xml_files)}")
        
        for f in xml_files:
            print(f"\n  Parsing: {f.name}")
            try:
                data = parse_history_xml(str(f))
                print(f"    Symbol: {data['symbol']}")
                print(f"    Rows: {len(data['data'])}")
            except Exception as e:
                print(f"    Error: {e}")
    else:
        print(f"Test folder not found: {test_path}")
"@

$xmlParserPath = Join-Path $sharedUtils "xml_parser.py"
$xmlParserContent | Out-File -FilePath $xmlParserPath -Encoding utf8
Write-Host "  + Created: xml_parser.py" -ForegroundColor DarkMagenta

# Create __init__.py
$initContent = @"
# shared_resources/python_utils/__init__.py
from .xml_parser import parse_history_xml, parse_multiple_xmls, xml_to_dataframe

__all__ = ['parse_history_xml', 'parse_multiple_xmls', 'xml_to_dataframe']
"@

$initPath = Join-Path $sharedUtils "__init__.py"
$initContent | Out-File -FilePath $initPath -Encoding utf8
Write-Host "  + Created: __init__.py" -ForegroundColor DarkMagenta

# -----------------------------------------------------------------------------
# STEP 2: CREATE LLM PROMPT TEMPLATES
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "STEP 2: Creating LLM prompt templates..." -ForegroundColor Blue

$llmPrompts = Join-Path $rootPath "shared_resources\llm_prompts\analysis"

if (!(Test-Path $llmPrompts)) {
    New-Item -ItemType Directory -Path $llmPrompts -Force | Out-Null
}

# V2 Posture Analysis Prompt
$posturePromptContent = @"
# V2 POSTURE ANALYSIS PROMPT
# Use with: LM Studio or any local LLM

You are a market analysis assistant for the V2 Posture trading system.

## Context
The V2 Posture system analyzes SPY and QQQ to determine:
- Overall market posture (Bullish/Bearish/Neutral)
- Key support and resistance levels
- Pattern recognition signals

## Your Task
Analyze the provided market data and give:

1. **Current Posture Assessment**
   - Market stance: bullish, bearish, or neutral
   - Confidence level: high/medium/low

2. **Key Levels**
   - Critical support levels
   - Critical resistance levels
   - Confluence zones

3. **Pattern Recognition**
   - Chart patterns forming
   - Typical pattern resolution

4. **Risk Assessment**
   - Primary risks to current thesis
   - Suggested position sizing

## Data Input
[PASTE YOUR MARKET DATA HERE]

## Output
Provide clear, actionable analysis. Be specific with price levels.
"@

$posturePromptPath = Join-Path $llmPrompts "v2_posture_analysis.txt"
$posturePromptContent | Out-File -FilePath $posturePromptPath -Encoding utf8
Write-Host "  + Created: v2_posture_analysis.txt" -ForegroundColor DarkBlue

# Pattern Recognition Prompt
$patternPromptContent = @"
# PATTERN RECOGNITION PROMPT
# Use with: LM Studio or any local LLM

You are a technical analysis expert for chart pattern recognition.

## Patterns to Identify

### Reversal Patterns
- Head and Shoulders / Inverse H&S
- Double Top / Double Bottom
- Triple Top / Triple Bottom

### Continuation Patterns
- Bull/Bear Flags
- Pennants
- Wedges (Rising/Falling)

### Candlestick Patterns
- Doji variants
- Engulfing patterns
- Hammer / Hanging Man
- Morning/Evening Star

## Data Input
[PASTE OHLCV DATA HERE]

## Output Format
For each pattern found:
1. Pattern name
2. Location (date/price range)
3. Status: forming or complete
4. Target price if complete
5. Invalidation level
6. Confidence (1-10)
"@

$patternPromptPath = Join-Path $llmPrompts "pattern_recognition.txt"
$patternPromptContent | Out-File -FilePath $patternPromptPath -Encoding utf8
Write-Host "  + Created: pattern_recognition.txt" -ForegroundColor DarkBlue

# Risk Config Prompt
$riskPromptContent = @"
# RISK CONFIGURATION PROMPT
# Use with: LM Studio or any local LLM

You are a risk management assistant for trading.

## Market Data
[PASTE CURRENT POSTURE DATA HERE]

## Account Parameters
- Account Size: [ENTER]
- Max Risk Per Trade: [ENTER]%
- Max Daily Loss: [ENTER]%

## Generate Risk Config

Provide recommendations for:
1. Position size (% of account)
2. Stop loss placement
3. Take profit targets (scale out levels)
4. Risk/Reward ratio assessment

## Output as JSON:
{
  "position_size_pct": 0.0,
  "stop_loss_pct": 0.0,
  "take_profit_1_pct": 0.0,
  "take_profit_2_pct": 0.0,
  "risk_reward_ratio": 0.0,
  "confidence": "high/medium/low"
}
"@

$riskPromptPath = Join-Path $llmPrompts "risk_config_generator.txt"
$riskPromptContent | Out-File -FilePath $riskPromptPath -Encoding utf8
Write-Host "  + Created: risk_config_generator.txt" -ForegroundColor DarkBlue

# -----------------------------------------------------------------------------
# STEP 3: CREATE ROOT LAUNCHER SCRIPT
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "STEP 3: Creating run_P300.ps1 launcher..." -ForegroundColor Yellow

$runScriptContent = @"
# =============================================================================
# run_P300.ps1 - Quick launcher for P_300 Posture System
# =============================================================================
# Usage: .\run_P300.ps1 [mode]
# Modes: live, backtest, test
# Example: .\run_P300.ps1 live
# =============================================================================

param(
    [string]`$Mode = "live"
)

`$p300Path = Join-Path `$PSScriptRoot "projects\P_300_Vantage_Point_Pattern_Recognition\python"

if (Test-Path `$p300Path) {
    Push-Location `$p300Path
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  P_300 Posture System - `$Mode mode" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Directory: `$p300Path" -ForegroundColor Gray
    Write-Host ""
    
    python P_300_Posture_V2.py `$Mode
    
    Pop-Location
} else {
    Write-Host "Error: P_300 folder not found" -ForegroundColor Red
    Write-Host "Expected: `$p300Path" -ForegroundColor Red
}
"@

$runScriptPath = Join-Path $rootPath "run_P300.ps1"
$runScriptContent | Out-File -FilePath $runScriptPath -Encoding utf8
Write-Host "  + Created: run_P300.ps1" -ForegroundColor DarkYellow

# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!                          " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created:" -ForegroundColor White
Write-Host "  shared_resources/python_utils/xml_parser.py" -ForegroundColor Gray
Write-Host "  shared_resources/python_utils/__init__.py" -ForegroundColor Gray
Write-Host "  shared_resources/llm_prompts/analysis/v2_posture_analysis.txt" -ForegroundColor Gray
Write-Host "  shared_resources/llm_prompts/analysis/pattern_recognition.txt" -ForegroundColor Gray
Write-Host "  shared_resources/llm_prompts/analysis/risk_config_generator.txt" -ForegroundColor Gray
Write-Host "  run_P300.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "To run posture system:" -ForegroundColor Green
Write-Host "  .\run_P300.ps1 live" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test xml_parser:" -ForegroundColor Green
Write-Host "  cd shared_resources\python_utils" -ForegroundColor Yellow
Write-Host "  python xml_parser.py" -ForegroundColor Yellow
Write-Host ""

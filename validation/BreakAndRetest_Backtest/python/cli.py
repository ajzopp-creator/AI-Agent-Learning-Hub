"""
FILE: cli.py
VERSION: 1.0
DATE: 2026-08-26
AUTHOR: Tony + Claude
LAYER: cli
DESCRIPTION:
    Entry point for the Break-and-Retest backtest.
    Run with: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe cli.py

CHANGELOG:
    - 2026-08-26 v1.0: Initial build.
"""
from application.backtest_runner import run

if __name__ == "__main__":
    run()

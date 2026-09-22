"""WO-P025-EN.004 — Equity_Curve cash sums all primary accounts."""

from __future__ import annotations

from domain.formula_templates import equity_curve_cash_formula


def test_cash_formula_sums_all_accounts_not_ajz_only():
    f = equity_curve_cash_formula(2)
    assert "SUMIF(Daily_Cash!A:A,A2,Daily_Cash!C:C)" in f
    assert "AJZ6348" not in f
    assert "SUMIFS" not in f

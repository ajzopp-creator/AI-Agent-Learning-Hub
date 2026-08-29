"""
P_025 Infrastructure — Sector & Correlation Analytics Sheets

Separated from analytics_sheets.py to stay under the 300-line hard limit.
"""

from __future__ import annotations

import logging

from openpyxl.workbook.workbook import Workbook

from domain.formula_templates import sector_exposure_headers
from infrastructure.excel_formatter import (
    BODY_FONT,
    HEADER_FILL,
    HEADER_FONT,
    THIN_BORDER,
    TITLE_FONT,
    auto_column_width,
    clear_sheet,
    style_header_row,
)

logger = logging.getLogger(__name__)


def build_sector_exposure(wb: Workbook) -> None:
    """Sector $ and % from Positions Market Value + Reference_Data Sector."""
    ws = wb["Sector_Exposure"]
    clear_sheet(ws)
    headers = sector_exposure_headers()
    style_header_row(ws, headers)

    ws.insert_rows(1)
    title = ws.cell(1, 1, "Sector Exposure — AJZ6348")
    title.font = TITLE_FONT
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))

    for col, header in enumerate(headers, start=1):
        cell = ws.cell(2, col, header)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.border = THIN_BORDER
    ws.freeze_panes = "A3"

    ref = wb["Reference_Data"]
    sectors: list[str] = []
    seen: set[str] = set()
    for row in range(2, ref.max_row + 1):
        s = ref.cell(row, 3).value
        if s and str(s).strip() and str(s).strip() not in seen:
            seen.add(str(s).strip())
            sectors.append(str(s).strip())
    sectors = sorted(sectors)[:40]

    for i, sector in enumerate(sectors):
        r = i + 3
        ws.cell(r, 1, sector).font = BODY_FONT
        formula_mv = (
            f'=IFERROR(SUMPRODUCT((Reference_Data!$C$2:$C$500=A{r})*'
            f'(Positions!$A$3:$A$202=Reference_Data!$A$2:$A$500)*'
            f'Positions!$D$3:$D$202),0)'
        )
        ws.cell(r, 2, formula_mv).font = BODY_FONT
        ws.cell(r, 2).number_format = "$#,##0.00"
        ws.cell(r, 3, f'=IF(SUM($B$3:$B$50)=0,0,B{r}/SUM($B$3:$B$50))').font = BODY_FONT
        ws.cell(r, 3).number_format = "0.00%"
        ws.cell(r, 4, f'=COUNTIF(Reference_Data!$C$2:$C$500,A{r})').font = BODY_FONT

        for col in range(1, 5):
            ws.cell(r, col).border = THIN_BORDER

    auto_column_width(ws)
    logger.info("Sector_Exposure sheet built with %d sectors", len(sectors))


def build_correlation(wb: Workbook) -> None:
    """Correlation matrix structure for top tickers (labels only for v1)."""
    ws = wb["Correlation"]
    clear_sheet(ws)

    ws.cell(1, 1, "Correlation Matrix — Top Positions (structure)").font = TITLE_FONT

    tickers: list[str] = []
    if "Positions" in wb.sheetnames:
        pos = wb["Positions"]
        for row in range(3, min(pos.max_row + 1, 15)):
            t = pos.cell(row, 1).value
            if t:
                tickers.append(str(t).strip().upper())
    if not tickers and "Reference_Data" in wb.sheetnames:
        ref = wb["Reference_Data"]
        for row in range(2, min(ref.max_row + 1, 14)):
            t = ref.cell(row, 1).value
            if t:
                tickers.append(str(t).strip().upper())

    for i, t in enumerate(tickers):
        cell_h = ws.cell(3, i + 2, t)
        cell_h.fill = HEADER_FILL
        cell_h.font = HEADER_FONT
        cell_h.border = THIN_BORDER
        cell_v = ws.cell(i + 4, 1, t)
        cell_v.fill = HEADER_FILL
        cell_v.font = HEADER_FONT
        cell_v.border = THIN_BORDER

    for i in range(len(tickers)):
        for j in range(len(tickers)):
            cell = ws.cell(i + 4, j + 2)
            cell.border = THIN_BORDER
            cell.font = BODY_FONT
            if i == j:
                cell.value = 1
                cell.number_format = "0.00"
            else:
                cell.value = None

    ws.column_dimensions["A"].width = 12
    logger.info("Correlation sheet structured with %d tickers", len(tickers))

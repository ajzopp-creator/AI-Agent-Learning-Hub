"""HTML template for P_020 performance dashboard."""
import json

SYSTEM_COLORS = {
    "P_118": "#0ea572", "P_115": "#3882ef", "P_300": "#9b77f5",
    "P_117": "#e8a21c", "P_910": "#e85060", "SNT":   "#0ab4d4",
    "P_116": "#e87c1c",
}

def _pnl(v):
    v = float(v)
    return (f"+${v:,.2f}" if v >= 0 else f"−${abs(v):,.2f}")

def _cls(v):
    v = float(v)
    return "pos" if v > 0 else ("neg" if v < 0 else "neutral")

def _wr_cls(pct):
    v = float(pct)
    return "pos" if v >= 50 else ("amb" if v >= 30 else "neg")

def _system_rows(systems):
    rows = []
    for s in systems:
        c   = SYSTEM_COLORS.get(s["system"], "#888")
        wr  = float(s["win_rate_pct"]) if s["win_rate_pct"] else 0
        cl  = _wr_cls(wr)
        pf  = s["profit_factor"] if s["profit_factor"] else "—"
        rows.append(f"""
        <tr>
          <td><span class="sdot" style="background:{c}"></span><span class="sname">{s["system"]}</span></td>
          <td>{int(s["total_trades"]) - int(s["open_trades"])}</td>
          <td><div class="wr-wrap"><div class="wr-bg"><div class="wr-fill" style="width:{min(wr,100):.0f}%;background:{c}"></div></div>
              <span class="{cl}">{wr:.1f}%</span></div></td>
          <td class="{_cls(s["total_pnl"])}">{_pnl(s["total_pnl"])}</td>
          <td class="{_cls(s["avg_R"])}">{float(s["avg_R"]):+.2f}R</td>
          <td class="{_cls(float(pf)-1 if pf != "—" else -1)}">{pf}</td>
          <td>{float(s["avg_hold_days"]):.1f}d</td>
        </tr>""")
    return "\n".join(rows)

def _monthly_rows(monthly):
    rows = []
    max_abs = max(abs(float(r["total_pnl"])) for r in monthly) or 1
    for r in monthly:
        pnl = float(r["total_pnl"])
        bar_w = int(abs(pnl) / max_abs * 60)
        bar_c = "#0ea572" if pnl >= 0 else "#e85060"
        rows.append(f"""
        <tr>
          <td>{r["month"]}</td>
          <td>{r["trades_closed"]}</td>
          <td class="{_wr_cls(r["win_rate_pct"])}">{float(r["win_rate_pct"]):.1f}%</td>
          <td class="{_cls(pnl)}">
            <div class="pnl-bar-wrap">
              <div class="pnl-bar" style="width:{bar_w}px;background:{bar_c}"></div>
              {_pnl(pnl)}
            </div>
          </td>
          <td class="{_cls(r["avg_R"])}">{float(r["avg_R"]):+.2f}R</td>
        </tr>""")
    return "\n".join(rows)

def _open_rows(positions):
    rows = []
    for p in positions:
        upnl = float(p.get("unrealized_pnl", 0))
        rows.append(f"""
        <tr>
          <td>{p["symbol"]}<span class="atype">{p["asset_type"]}</span></td>
          <td>{float(p["qty"]):.2f}</td>
          <td>${float(p["avg_price"]):,.4f}</td>
          <td>${float(p["market_value"]):,.2f}</td>
          <td class="{_cls(upnl)}">{_pnl(upnl)}</td>
          <td class="{_cls(p["day_pnl"])}">{_pnl(p["day_pnl"])}</td>
        </tr>""")
    return "\n".join(rows)

def _equity_js(equity):
    labels = json.dumps([r["exit_date"] for r in equity])
    total  = json.dumps([float(r["cumulative_pnl"]) for r in equity])
    datasets = [f'{{"label":"Total","data":{total},"borderColor":"#dde8f5","borderWidth":2,"pointRadius":0,"tension":.3,"fill":false}}']
    for sys, col in SYSTEM_COLORS.items():
        key  = f"cum_{sys}"
        vals = json.dumps([float(r.get(key, 0)) for r in equity])
        datasets.append(f'{{"label":"{sys}","data":{vals},"borderColor":"{col}","borderWidth":1.5,"pointRadius":0,"tension":.3,"fill":false,"borderDash":[4,3]}}')
    return f"labels:{labels},datasets:[{','.join(datasets)}]"

def _dd_js(drawdown):
    labels = json.dumps([r["exit_date"] for r in drawdown])
    vals   = json.dumps([float(r["drawdown_dollar"]) for r in drawdown])
    return f"labels:{labels},datasets:[{{label:'Drawdown $',data:{vals},borderColor:'#e85060',backgroundColor:'rgba(232,80,96,.15)',fill:true,borderWidth:1.5,pointRadius:0,tension:.3}}]"

def _r_js(r_dist):
    labels = json.dumps([r["bucket"] for r in r_dist])
    vals   = json.dumps([int(r["count"]) for r in r_dist])
    colors = json.dumps(["#e85060" if "-" in r["bucket"] else ("#888" if r["bucket"] in ("0R scratch",) else "#0ea572") for r in r_dist])
    return f"labels:{labels},datasets:[{{label:'Trades',data:{vals},backgroundColor:{colors},borderRadius:4}}]"

def build_html(data):
    k = data["kpis"]
    pnl_cls = _cls(k["net_pnl"])
    exp_cls = _cls(k["expectancy"])
    best    = k["best"]
    bc      = SYSTEM_COLORS.get(best["system"], "#888")
    as_of   = k["as_of"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AJZ Strategies — Performance Analytics</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#0a1628;--bg2:#07101e;--panel:#0e1f36;--panel2:#122540;--border:#173458;--border2:#1e3f6e;--text1:#dde8f5;--text2:#6a94be;--text3:#375875;--green:#0ea572;--green-bg:rgba(14,165,114,.12);--red:#e85060;--red-bg:rgba(232,80,96,.12);--amber:#e8a21c;--blue:#3882ef;--purple:#9b77f5;--teal:#0ab4d4;--orange:#e87c1c;--mono:'JetBrains Mono',monospace;--sans:'Inter',sans-serif}}
html,body{{background:var(--bg);color:var(--text1);font-family:var(--sans);font-size:14px;min-height:100vh;line-height:1.5}}
.hdr{{display:flex;align-items:center;justify-content:space-between;padding:14px 28px;border-bottom:1px solid var(--border);background:var(--bg2);position:sticky;top:0;z-index:20}}
.hdr-l{{display:flex;align-items:center;gap:16px}}
.logo{{width:36px;height:36px;border:2px solid var(--green);border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:10px;font-weight:600;color:var(--green)}}
.hdr-title{{font-size:17px;font-weight:600;letter-spacing:.04em}}
.hdr-sub{{font-family:var(--mono);font-size:10px;color:var(--text2);margin-top:2px;letter-spacing:.06em}}
.hdr-r{{display:flex;align-items:center;gap:16px}}
.badge{{font-family:var(--mono);font-size:10px;color:var(--text2);border:1px solid var(--border2);border-radius:5px;padding:4px 10px;letter-spacing:.05em}}
.dot{{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green);animation:pulse 2.5s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.page{{padding:20px 28px;max-width:1480px;margin:0 auto}}
.sec-lbl{{font-family:var(--mono);font-size:10px;color:var(--text2);letter-spacing:.14em;text-transform:uppercase;margin-bottom:10px;padding-left:2px}}
.sec-lbl em{{color:var(--text3);margin-right:8px;font-style:normal}}
.panel{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:18px 20px}}
.panel-hdr{{font-size:12px;font-weight:500;color:var(--text2);letter-spacing:.08em;text-transform:uppercase;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between}}
.panel-hdr span{{font-family:var(--mono);font-size:10px;color:var(--text3);font-weight:400}}
.mb20{{margin-bottom:20px}}
.kpi-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}}
.kpi{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:20px 22px;position:relative;overflow:hidden}}
.kpi::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--kc);opacity:.8}}
.kpi-label{{font-family:var(--mono);font-size:10px;color:var(--text2);letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px}}
.kpi-value{{font-family:var(--mono);font-size:26px;font-weight:500;line-height:1;letter-spacing:-.01em}}
.kpi-sub{{font-family:var(--mono);font-size:10px;color:var(--text2);margin-top:8px}}
.pos{{color:var(--green)}} .neg{{color:var(--red)}} .neutral{{color:var(--text2)}} .amb{{color:var(--amber)}}
.g2{{display:grid;grid-template-columns:1.25fr 1fr;gap:14px;margin-bottom:20px}}
.g2b{{display:grid;grid-template-columns:1fr 1.5fr;gap:14px;margin-bottom:20px}}
.tbl{{width:100%;border-collapse:collapse}}
.tbl th{{font-family:var(--mono);font-size:10px;color:var(--text3);letter-spacing:.08em;text-transform:uppercase;padding:0 10px 10px;text-align:right;border-bottom:1px solid var(--border)}}
.tbl th:first-child{{text-align:left}}
.tbl td{{font-family:var(--mono);font-size:11.5px;padding:9px 10px;text-align:right;border-bottom:1px solid var(--border);color:var(--text1)}}
.tbl td:first-child{{text-align:left}}
.tbl tr:last-child td{{border-bottom:none}}
.tbl tr:hover td{{background:rgba(255,255,255,.025)}}
.sdot{{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:8px;vertical-align:middle}}
.sname{{font-weight:500}}
.wr-wrap{{display:inline-flex;align-items:center;gap:7px}}
.wr-bg{{width:48px;height:4px;background:var(--border2);border-radius:2px;display:inline-block;position:relative}}
.wr-fill{{height:4px;border-radius:2px;position:absolute;left:0;top:0}}
.pnl-bar-wrap{{display:flex;align-items:center;gap:8px;justify-content:flex-end}}
.pnl-bar{{height:5px;border-radius:3px;min-width:3px}}
.atype{{font-size:9px;color:var(--text2);font-family:var(--mono);border:1px solid var(--border2);border-radius:3px;padding:1px 5px;display:inline-block;margin-left:6px;vertical-align:middle}}
.footer{{margin-top:24px;padding:14px 0;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;font-family:var(--mono);font-size:10px;color:var(--text3);letter-spacing:.05em}}
</style>
</head>
<body>
<header class="hdr">
  <div class="hdr-l">
    <div class="logo">AJZ</div>
    <div>
      <div class="hdr-title">AJZ STRATEGIES LLC</div>
      <div class="hdr-sub">PERFORMANCE ANALYTICS &nbsp;/&nbsp; P_020 &nbsp;/&nbsp; ACCOUNT ...6348</div>
    </div>
  </div>
  <div class="hdr-r">
    <div class="badge">YTD 2026</div>
    <div class="badge">{k["closed"]} CLOSED &nbsp;/&nbsp; {k["open_total"]} OPEN</div>
    <div class="badge">UPDATED {as_of}</div>
    <div class="dot"></div>
  </div>
</header>

<div class="page">
  <div class="kpi-row">
    <div class="kpi" style="--kc:{'var(--green)' if k['net_pnl']>=0 else 'var(--red)'}">
      <div class="kpi-label">Net P&amp;L (YTD Closed)</div>
      <div class="kpi-value {pnl_cls}">{_pnl(k["net_pnl"])}</div>
      <div class="kpi-sub">{k["month_sub"]}</div>
    </div>
    <div class="kpi" style="--kc:{'var(--green)' if k['win_rate']>=50 else 'var(--amber)'}">
      <div class="kpi-label">Win Rate</div>
      <div class="kpi-value {'pos' if k['win_rate']>=50 else 'amb'}">{k["win_rate"]:.1f}%</div>
      <div class="kpi-sub">{k["wins"]} wins &nbsp;/&nbsp; {k["losses"]} losses &nbsp;/&nbsp; {k["closed"]} closed</div>
    </div>
    <div class="kpi" style="--kc:{'var(--green)' if k['expectancy']>=0 else 'var(--red)'}">
      <div class="kpi-label">Portfolio Expectancy</div>
      <div class="kpi-value {exp_cls}">{k["expectancy"]:+.2f}R</div>
      <div class="kpi-sub">Avg R per closed trade across all systems</div>
    </div>
    <div class="kpi" style="--kc:{bc}">
      <div class="kpi-label">Best System</div>
      <div class="kpi-value" style="font-size:22px;margin-top:3px;color:{bc}">{best["system"]}</div>
      <div class="kpi-sub">{float(best["win_rate_pct"]):.0f}% WR &nbsp; {_pnl(best["total_pnl"])} &nbsp; Kelly {best["kelly_pct"]}%</div>
    </div>
  </div>

  <div class="sec-lbl"><em>01</em>EQUITY CURVE</div>
  <div class="panel mb20">
    <div class="panel-hdr">Cumulative P&amp;L by System <span>JAN 2026 — {as_of}</span></div>
    <div style="height:220px"><canvas id="eqChart"></canvas></div>
  </div>

  <div class="g2 mb20">
    <div class="panel">
      <div class="panel-hdr">System Performance <span>YTD CLOSED TRADES</span></div>
      <table class="tbl">
        <thead><tr><th>System</th><th>Closed</th><th>Win %</th><th>Net P&amp;L</th><th>Avg R</th><th>Prof Factor</th><th>Avg Hold</th></tr></thead>
        <tbody>{_system_rows(data["systems"])}</tbody>
      </table>
    </div>
    <div class="panel">
      <div class="panel-hdr">Drawdown — Dollar <span>FROM ${max(float(r["peak_pnl"]) for r in data["drawdown"]):,.0f} PEAK</span></div>
      <div style="height:270px"><canvas id="ddChart"></canvas></div>
    </div>
  </div>

  <div class="g2b mb20">
    <div class="panel">
      <div class="panel-hdr">R Distribution <span>{k["closed"]} CLOSED TRADES</span></div>
      <div style="height:220px"><canvas id="rChart"></canvas></div>
    </div>
    <div class="panel">
      <div class="panel-hdr">Monthly Summary <span>2026 YTD</span></div>
      <table class="tbl">
        <thead><tr><th>Month</th><th>Closed</th><th>Win %</th><th>Net P&amp;L</th><th>Avg R</th></tr></thead>
        <tbody>{_monthly_rows(data["monthly"])}</tbody>
      </table>
    </div>
  </div>

  <div class="sec-lbl"><em>02</em>OPEN POSITIONS — AS OF {as_of}</div>
  <div class="panel mb20">
    <table class="tbl">
      <thead><tr><th>Symbol</th><th>Qty</th><th>Avg Price</th><th>Mkt Value</th><th>Unrealized P&amp;L</th><th>Day P&amp;L</th></tr></thead>
      <tbody>{_open_rows(data["open_pos"])}</tbody>
    </table>
  </div>

  <div class="footer">
    <span>P_020 AJZ STRATEGIES PERFORMANCE SYSTEM</span>
    <span>GENERATED {as_of} &nbsp;/&nbsp; DATA: account ...6348</span>
  </div>
</div>

<script>
const eqCtx = document.getElementById('eqChart').getContext('2d');
new Chart(eqCtx, {{type:'line',data:{{{_equity_js(data["equity"])}}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{position:'bottom',labels:{{color:'#6a94be',font:{{size:10,family:"'JetBrains Mono'"}}}}}}}},scales:{{x:{{ticks:{{color:'#375875',maxTicksLimit:10,font:{{size:9}}}},grid:{{color:'#173458'}}}},y:{{ticks:{{color:'#375875',font:{{size:9}},callback:v=>v>=0?'+$'+v.toLocaleString():'−$'+Math.abs(v).toLocaleString()}},grid:{{color:'#173458'}}}}}}}}}});
const ddCtx = document.getElementById('ddChart').getContext('2d');
new Chart(ddCtx, {{type:'line',data:{{{_dd_js(data["drawdown"])}}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{x:{{ticks:{{color:'#375875',maxTicksLimit:8,font:{{size:9}}}},grid:{{color:'#173458'}}}},y:{{ticks:{{color:'#375875',font:{{size:9}},callback:v=>'$'+v.toLocaleString()}},grid:{{color:'#173458'}}}}}}}}}});
const rCtx = document.getElementById('rChart').getContext('2d');
new Chart(rCtx, {{type:'bar',data:{{{_r_js(data["r_dist"])}}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{x:{{ticks:{{color:'#375875',font:{{size:9}}}},grid:{{color:'#173458'}}}},y:{{ticks:{{color:'#375875',font:{{size:9}}}},grid:{{color:'#173458'}}}}}}}}}});
</script>
</body>
</html>"""

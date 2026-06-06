---
date: <% tp.date.now("YYYY-MM-DD") %>
day_of_week: <% tp.date.now("dddd") %>
template_version: "3.0"
template_owner: "P_800"
market_posture: null
market_regime: null
risk_level: null
trade_count: 0
key_setups: []
session_status: open
---

# <% tp.date.now("dddd, MMMM D, YYYY") %>

## 1. Morning Starter

### Verse of the Day
<%*
try {
  const r = await tp.obsidian.requestUrl({
    url: "https://labs.bible.org/api/?passage=votd&type=json&formatting=plain"
  });
  const data = r.json;
  const v = data[0];
  tR += `> ${v.text}\n> -- ${v.bookname} ${v.chapter}:${v.verse}`;
} catch (e) {
  tR += "> _Verse fetch failed -- " + e.message + "_";
}
%>

### Daily Quote
<%*
try {
  const quote = await tp.web.daily_quote();
  tR += quote;
} catch (e) {
  tR += "_Quote fetch failed._";
}
%>

### Joke of the Day
<%*
try {
  const r = await tp.obsidian.requestUrl({
    url: "https://v2.jokeapi.dev/joke/Any?safe-mode&type=single"
  });
  const data = r.json;
  tR += data.joke || "_No joke today._";
} catch (e) {
  tR += "_Joke fetch failed -- " + e.message + "_";
}
%>

---

## 2. Senior Exercise (Wrist-Friendly)

- [ ] Neck rolls -- 10 each direction
- [ ] Shoulder shrugs -- 15 reps
- [ ] Seated marches -- 60 seconds
- [ ] Calf raises -- 20 reps
- [ ] Ankle circles -- 10 each foot
- [ ] Deep breathing -- 5 minutes

---

## 3. Schedule Check

<% tp.file.cursor(1) %>

_Tell Claude: "Inject today''s Google Calendar events into this section."_

---

## 4. Market Analysis

### Pre-Market Analysis
_TOS + VantagePoint observations_

<% tp.file.cursor(2) %>

### Market Posture
_Paste the P_010 Market Posture JSON block below._

```json
<% tp.file.cursor(3) %>
```

---

## 5. AI Trends & Research

<% tp.file.cursor(4) %>

---

## 6. Daily Rollover / Review

- [ ] Trades logged to Excel tracker
- [ ] Outstanding tasks reviewed
- [ ] Tomorrow''s prep complete

<% tp.file.cursor(5) %>

---

*Template owner: P_800 -- v3.0*
---
date: <% tp.date.now("YYYY-MM-DD") %>
day: <% tp.date.now("dddd") %>
week: <% tp.date.now("[Week] WW") %>
tags: daily-flow
---

# 📅 Daily Flow — <% tp.date.now("dddd, MMMM D, YYYY") %>

**Energy Level Today:** ⭐⭐⭐ _(edit: 1–5 stars)_

---

## 1️⃣ Inspiration & Warmup

### 💬 Quote of the Day
<% tp.web.daily_quote() %>

### 😄 Humor / Lightness
> <% tp.file.cursor(1) %>

---

## 2️⃣ Senior Exercise Routine
> ⚠️ Wrist-friendly — modify or skip any movement as needed

**Warmup**
- [ ] Deep breathing / box breathing (2 min)
- [ ] Neck rolls — slow left / right (5 each side)
- [ ] Shoulder rolls — forward / backward (10 each)
- [ ] Seated torso twists (10 each side)
- [ ] Ankle circles (10 each foot)

**Strength & Balance**
- [ ] Seated leg lifts (10 each leg)
- [ ] Standing wall push-ups — no wrist strain (10 reps)
- [ ] Calf raises — standing (15 reps)
- [ ] Seated marching — high knees (30 sec)
- [ ] Side leg raises — standing, hold chair (10 each side)

**Cooldown**
- [ ] Gentle forward fold / hamstring stretch (30 sec)
- [ ] Chest opener — arms back, deep breath (3x)
- [ ] Wrist-free shoulder stretch across chest (30 sec each)

---

## 3️⃣ Schedule Check

### 📆 Google Calendar — <% tp.date.now("dddd MMMM D") %>

> _Open Obsidian Google Calendar plugin (sidebar) and paste today's events below_

| Time | Event | Notes |
|------|-------|-------|
|      |       |       |
|      |       |       |
|      |       |       |

---

## 4️⃣ WhatsApp Trading Channels

> _Open WhatsApp Web → copy channel content → paste into each block below_

> [!info] 📲 Impens — Pioneer Club
> <% tp.file.cursor(2) %>

> [!info] 📲 Anderssen — Club 84
> <% tp.file.cursor(3) %>

---

## 5️⃣ Market Posture — <% tp.date.now("YYYY-MM-DD") %>

### 🧭 Bias & Regime

> _Open Claude → P_010 Market Posture prompts → generate JSON → paste below_

```json
{
  "date": "<% tp.date.now("YYYY-MM-DD") %>",
  "bias": "",
  "regime": "",
  "key_setups": [],
  "risk_level": "",
  "notes": ""
}
```

### 📝 Posture Summary Notes
<% tp.file.cursor(4) %>

---

## 6️⃣ TOS + VantagePoint Analysis

### 📊 Pre-Market Scan — <% tp.date.now("h:mm A") %> start

**Market Overview**
- SPY: 
- QQQ: 
- VIX: 

**VantagePoint Signals Today**

| Ticker | VP Signal | Predicted High | Predicted Low | My Read |
|--------|-----------|----------------|---------------|---------|
|        |           |                |               |         |
|        |           |                |               |         |
|        |           |                |               |         |

### 🖼️ Chart Screenshots
_Paste or drag TOS screenshots here_

### 🎙️ Dictated Analysis Notes
> _Use Win+H to dictate — paste here_

<% tp.file.cursor(5) %>

---

## 7️⃣ Trade Execution Log

| Time | Ticker | Direction | Entry | Exit | P&L | Notes |
|------|--------|-----------|-------|------|-----|-------|
|      |        |           |       |      |     |       |
|      |        |           |       |      |     |       |

**Trade Notes / Lessons**
<% tp.file.cursor(6) %>

---

## 8️⃣ Manual Notebook Activities

> _Reference physical notebook, scanning, or other offline work_

<% tp.file.cursor(7) %>

---

## 9️⃣ AI Trends & Research

### 🤖 Tools Reviewed Today
- [ ] Claude
- [ ] Grok
- [ ] Perplexity
- [ ] Gemini / NotebookLM
- [ ] Other: 

### 📌 Key Takeaways
<% tp.file.cursor(8) %>

---

## 🔁 Daily Rollover / Review

### ✅ Wins Today
- 

### 🔧 Improve Tomorrow
- 

### 📋 Tasks Carried Forward
- [ ] <% tp.file.cursor(9) %>

---
_Note created: <% tp.date.now("YYYY-MM-DD [at] h:mm A") %>_

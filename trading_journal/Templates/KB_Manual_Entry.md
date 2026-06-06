<% tp.date.now("YYYY-MM-DD") %>
<% await tp.system.prompt("Title") %>

---
date: <% tp.date.now("YYYY-MM-DD") %>
title: "<% await tp.system.prompt("Title") %>"
kb_type: <% await tp.system.prompt("Type", "Article") %>
origin: <% await tp.system.prompt("Origin", "Email") %>
from: "<% await tp.system.prompt("From", "") %>"
ai_summarized: false
tags: []
ticker_relevance: []
sector: null
market_regime: null
linked_trades: []
---

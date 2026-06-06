---
source: KB
schema_version: "1.0"
date: 2026-05-25
title: RIP "Think Step by Step"
kb_type: Article
origin: Email
ai_summarized: false
tags: []
ticker_relevance: []
sector: null
market_regime: null
linked_trades: []
---

**Reading time: 5 minutes**

Greetings from above,

Why does your AI give a perfect answer, keep thinking, and then come back with the wrong one? (Spoiler: it's not broken — it's just overthinking, exactly like your cousin at pub quiz.)

I used to think longer reasoning meant better answers. So I kept writing prompts like "think step by step, take your time, reason through this carefully." Felt thorough. Felt smart. 

Turns out I was basically telling my AI to talk itself out of the right answer on a timer. The second I read this paper out of Nanjing University, I stopped using chain-of-thought prompts on anything straightforward. 

My outputs got tighter, faster, and actually more accurate. Sometimes less really is just more.

**Today, we'll talk about:**

* What the Nanjing University paper actually found and why it matters

* The exact token threshold where AI reasoning starts hurting your output

* How to rewrite your prompts so the model stops second-guessing itself

Let's get into it!

### Stop babysitting dashboards. Ship from Slack. Touch grass.

View image: (https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/asset/file/5ac91da5-aa0f-4bfd-b8ed-906df9926501/SPEC_4___Touch_Grass_.png?t=1775150731)
Follow image link: (https://ref.getviktor.com/vik-bh-mediabuy-primary1?utm_campaign=OWVBCIB2AQ&_bhiiv=opp_863393d2-46ec-4723-82d1-ed5d6a9c0c4d_7761da30&bhcl_id=cf6b9d52-9896-42ce-85da-acc65075ffcf_7f829cdc-7046-45df-b6cb-8b67c33e8521_e791ae38-29b1-4cc1-bb00-ea03b68f14b6)
Caption: 

700+ teams have [Viktor](https://ref.getviktor.com/vik-bh-mediabuy-primary1?utm_campaign=OWVBCIB2AQ&_bhiiv=opp_863393d2-46ec-4723-82d1-ed5d6a9c0c4d_7761da30&bhcl_id=cf6b9d52-9896-42ce-85da-acc65075ffcf_7f829cdc-7046-45df-b6cb-8b67c33e8521_e791ae38-29b1-4cc1-bb00-ea03b68f14b6) reading their Google Ads every morning.

Your media team opens Slack at 8am. There's a cross-platform brief in #growth: Google Ads spend vs. ROAS, Meta CPA by campaign, Stripe revenue by channel. Viktor posted it at 6am. Nobody asked for it.

Last week, one team's [Viktor](https://ref.getviktor.com/vik-bh-mediabuy-primary1?utm_campaign=OWVBCIB2AQ&_bhiiv=opp_863393d2-46ec-4723-82d1-ed5d6a9c0c4d_7761da30&bhcl_id=cf6b9d52-9896-42ce-85da-acc65075ffcf_7f829cdc-7046-45df-b6cb-8b67c33e8521_e791ae38-29b1-4cc1-bb00-ea03b68f14b6) caught a spend spike at 2am on a broad match campaign and flagged it in Slack: "CPA up 340%. Recommend pausing and shifting budget to the top two performers." That would have burned $3K by morning. The media buyer woke up to a problem already handled.

Your strategist reviews spend trends. Your account manager checks revenue attribution. Same Slack channel, same colleague, before anyone's first coffee.

Google Ads, Meta, Stripe. One message. No Looker, no Data Studio. Anomaly detection runs around the clock. Cross-platform reporting runs on autopilot.

5,700+ teams. SOC 2 certified. Your data never trains models.

"[Viktor](https://ref.getviktor.com/vik-bh-mediabuy-primary1?utm_campaign=OWVBCIB2AQ&_bhiiv=opp_863393d2-46ec-4723-82d1-ed5d6a9c0c4d_7761da30&bhcl_id=cf6b9d52-9896-42ce-85da-acc65075ffcf_7f829cdc-7046-45df-b6cb-8b67c33e8521_e791ae38-29b1-4cc1-bb00-ea03b68f14b6) is now an integral team member, and after weeks of use we still feel we haven't uncovered the full potential." — Patrick O'Doherty, Director, Yarra Web

[Start free. $100 in credits →](https://ref.getviktor.com/vik-bh-mediabuy-primary1?utm_campaign=OWVBCIB2AQ&_bhiiv=opp_863393d2-46ec-4723-82d1-ed5d6a9c0c4d_7761da30&bhcl_id=cf6b9d52-9896-42ce-85da-acc65075ffcf_7f829cdc-7046-45df-b6cb-8b67c33e8521_e791ae38-29b1-4cc1-bb00-ea03b68f14b6)

### **THE PROBLEM WITH "THINK STEP BY STEP"**

So, here's the thing basically every prompt engineer got wrong — including the good ones. The assumption that more thinking produces better answers was never actually tested at scale until now. It just felt logical. 

Humans reason better when they slow down, so AI should too, right? Not really. Nanjing University and Baidu tracked individual answers across 32 different reasoning budgets — from 500 tokens all the way to 16,000 — and what they found is kind of uncomfortable. At around 7,000 tokens, something flips. 

The model stops finding new correct answers and starts abandoning the ones it already had. They call these "negative flips." Correct to incorrect. The model had the right answer, kept thinking, and talked itself out of it. That's not a glitch. That's not hallucination. That's the model second-guessing itself straight into failure.

### **WHY THIS PAPER CHANGES HOW YOU WRITE PROMPTS:**

* It proves that shorter, directed prompts with clear constraints will outperform "think step by step" on most everyday tasks

* It shows that the simpler your question is, the faster the model hits the overthinking zone — so easy questions actually need tighter token limits, not looser ones

* It gives you a concrete cap to work with — stopping at 60% of the model's natural reasoning length maintained 97% of peak accuracy with significantly less compute

———————————————————————————

### **RIP "THINK STEP BY STEP" — SCIENCE JUST KILLED PROMPT ENGINEERING'S FAVOURITE TRICK**

Ok, so this is the part that actually stings a little if you've spent serious time building chain-of-thought prompts. The research is pretty clear. Longer reasoning isn't just unhelpful past a certain point — it's actively destructive. And the tell is sitting right there in your outputs if you know what to look for.

Here's what the paper found, broken down into what it actually means for your prompts:

———————————————————————————

### ⚙️ **Here's what the research reveals, step by step:**

**Finding 1 — The 7,000 Token Flip**

At roughly 7,000 tokens of reasoning, the model crosses a threshold where it starts abandoning correct answers faster than it finds new ones. Before that point, more thinking generally helps. After it, the model is statistically more likely to hurt its own answer than improve it. So if your outputs are regularly running long, you're probably already past the threshold on most tasks.

**Finding 2 — 67.5% of Negative Flips Are Pure Overthinking**

This is the one that really stings. Nearly 67.5% of cases where the model flipped from a correct answer to a wrong one weren't random errors — they were deliberate reconsiderations. The model explicitly looked at its correct answer, said something like "wait, let me double-check," and replaced it with a wrong one. Not a glitch. A choice. A very confident, very wrong choice.

**Finding 3 — Watch for These Phrases in Your Outputs**

The paper identified the exact language that signals the model is about to hurt its own answer. If you see any of these appearing late in a response, accuracy is very likely already dropping:

* _"Actually…"_

* _"Let me reconsider…"_

* _"I may have overcounted…"_

* _"Wait, on reflection…"_

These aren't signs of thoroughness. They're signs the model is losing confidence and spiralling. The correct answer was already there. The model just kept going.

**Finding 4 — Easy Questions Hit the Overthinking Zone Faster**

Simple problems hit the overthinking threshold at around 2,000 tokens. Hard problems don't hit it until roughly 8,000. So the simpler your question, the faster you need to stop the model from thinking too long. This is basically the opposite of what most people do — they give hard questions tight prompts and let easy questions run freely. That's the wrong way around.

**Finding 5 — Optimal Reasoning Length Varies 7.5x by Difficulty**

Uniform token budgets across different task types are structurally the wrong approach. A prompt that works perfectly for a complex strategic question will actively damage the output on a straightforward task. The research found that optimal thinking length varies by as much as 7.5x depending on how difficult the problem actually is. One-size-fits-all prompting is costing you accuracy you already had.

**Finding 6 — The 60% Rule**

When researchers capped reasoning at 60% of the model's natural output length, it maintained 97% of peak accuracy. That's almost no accuracy loss for a very significant reduction in compute and bloat. In practical terms — if your model naturally wants to write 2,000 tokens on a task, stopping it at around 1,200 gets you nearly the same answer with none of the second-guessing spiral.

**Finding 7 — The Model Writes More When It Knows Less**

This one is arguably the most useful signal for anyone using AI daily. The research found that longer natural outputs correlated directly with lower accuracy. Outputs under 4,000 tokens hit 71.9% accuracy. Outputs above 12,000 tokens dropped to 44.7%. So a bloated, overlong response isn't a sign the model is being thorough. It's a sign the model is uncertain and filling space. If your output feels overengineered and keeps second-guessing itself, that's a confidence problem — not a reasoning one.

———————————————————————————

### **What To Actually Do With This From Today:**

* **Stop using open-ended chain-of-thought prompts on simple tasks.** "Think step by step" is genuinely counterproductive on anything straightforward. Use it only on problems that are actually complex.

* **Add a length constraint to your prompts.** Something like "respond in under 300 words" or "give me your first answer without reconsidering" actively prevents the model from entering the overthinking spiral.

* **Watch for the reconsideration phrases.** If you see "actually" or "let me reconsider" appearing late in a response, the model has very likely already passed its accuracy peak. Regenerate with a tighter prompt.

* **Match your token budget to your task difficulty.** Easy question — short, directed prompt with a word limit. Complex question — slightly more room, but still capped. Never uniform across both.

### **RIP "THINK STEP BY STEP" PAPER — SUMMARY**

* At 7,000 tokens, AI reasoning crosses a threshold where it starts abandoning correct answers faster than finding new ones — and 67.5% of those flips are the model explicitly reconsidering a correct answer and replacing it with a wrong one

* Simple questions hit the overthinking zone at just 2,000 tokens, so tighter prompts on easy tasks aren't lazy — they're actually more accurate

* Capping reasoning at 60% of the model's natural length maintains 97% of peak accuracy — and a bloated output isn't thoroughness, it's the model writing more because it knows less

### **WRAP UP:**

What you learned today:

**Lesson 1:** "Think step by step" was never tested at scale before this paper — and now that it has been, the results are pretty clear that longer reasoning actively hurts output quality past a certain threshold

**Lesson 2:** The model writing more is a signal of uncertainty, not confidence — if your output feels bloated and keeps reconsidering itself, a tighter prompt will almost always outperform a longer one

**Lesson 3:** Match your reasoning budget to your task difficulty — easy questions need short, directed prompts with clear constraints, and hard questions still need a cap, just a slightly higher one

The best prompt engineers have always known that clarity beats length. Now there's a paper that proves it with 32 reasoning budgets and 16,000 tokens of data. Your AI isn't being careful when it second-guesses itself — it's losing confidence in real time. Shorter prompts, clear constraints, and a hard stop before the spiral kicks in. That's the actual upgrade most people skip because it feels too simple to work. It works.

And as always, thanks for being a part of my lovely community,

Keep learning, 

🔑** Robert from God of Prompt**


———

You are reading a plain text version of this post. For the best experience, copy and paste this link in your browser to view the post online:
https://godofprompt.beehiiv.com/p/rip-think-step-by-step

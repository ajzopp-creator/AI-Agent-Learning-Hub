---
title: "The Claude Loops Nobody Builds: NotebookLM Audits My AI Chip Portfolio"
source: "https://www.learnwithmeai.com/p/claude-loops-notebooklm-chip-audit?utm_source=substack&utm_medium=email#media-5ea5fbcb-07b9-483a-a0b6-d3945a088c6b"
author:
  - "[[Gencay]]"
date: "2026-06-19"
published: 2026-06-18
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
sector:
origin:
---
### A Claude loop with five NotebookLM notebooks and five agents, auditing AI chip stocks from verified sources only.

Boris Cherny, the creator of Claude Code, said he no longer writes prompts.

 <video controls=""><source src="https://www.learnwithmeai.com/api/v1/video/upload/ca9ffa58-3e85-4f2d-ab99-4523e39c91c5/src?override_publication_id=1867502&amp;type=hls" type="application/x-mpegURL"> <source src="https://www.learnwithmeai.com/api/v1/video/upload/ca9ffa58-3e85-4f2d-ab99-4523e39c91c5/src?override_publication_id=1867502&amp;type=mp4" type="video/mp4"></video>

Then everyone talked about loops.

New terms showed up overnight.

> *Loop Engineering. Harness Engineering.*

That is how this field moves. Before 2022, we did not know what prompting was. Prompt engineering came later.

A trend is forming. We dig deeper.

I explained what a Claude loop is in [this one](https://www.learnwithmeai.com/p/claude-loops-vs-automations), and I turned 3 of my own automation skills into loops.

Then this morning, on a walk, I asked a different question.

> *How do I put NotebookLM inside one?*

I went back through my old articles.

I had been building loops for a year using [NotebookLM](https://www.learnwithmeai.com/t/notebooklm) and [Claude Code](https://www.learnwithmeai.com/t/claude-code).

Nobody called them loops back then.

So let’s [build](https://www.learnwithmeai.com/t/build-it) a new loop using NotebookLM and Claude Agents.

A loop that audits my AI investment.

Those companies have been racing for years.

## What will we build with Claude loops?

 <video controls=""><source src="https://www.learnwithmeai.com/api/v1/video/upload/5ea5fbcb-07b9-483a-a0b6-d3945a088c6b/src?override_publication_id=1867502&amp;type=hls" type="application/x-mpegURL"> <source src="https://www.learnwithmeai.com/api/v1/video/upload/5ea5fbcb-07b9-483a-a0b6-d3945a088c6b/src?override_publication_id=1867502&amp;type=mp4" type="video/mp4"></video>

We will have a system where Claude agents ask NotebookLM questions about AI chips.

![](https://substackcdn.com/image/fetch/$s_!tSS0!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7f7fba4a-c34c-43cb-a011-3f2bef416c5e_3440x1780.png)

The sector notebook answering a Taiwan concentration question. Every number carries a citation back to the source.

Here we’ll set the Claude agents, which will be the goal of this automation, making the entire system a loop.

Those notebooks are trained on verified sources only, mostly government filings.

![](https://substackcdn.com/image/fetch/$s_!Mlib!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff3ef0ed3-1edb-4588-9f87-8136b3d68a02_1596x384.png)

The source list is behind one notebook. Government filings and market reports.

After the agents query them, they move to the second layer, one notebook for the industry, and a third for the global economy.

### Why NotebookLM?

We cannot afford hallucination. NotebookLM hallucinates far less.

We also customize each notebook to stay silent when the answer is not in its source.

![](https://substackcdn.com/image/fetch/$s_!vZOM!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6df14c77-0070-44d9-9b22-21f062d9ca2b_2054x1296.png)

The custom instruction is on every notebook. No source, no answer. It replies Not in source and stops.

Two layers of protection against a made-up number.

The end result is one website.

![](https://substackcdn.com/image/fetch/$s_!Ld3J!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F1487fb65-a200-4251-9ca7-9d8371082c3c_1750x1288.png)

The output. One page that names the bottleneck and the structural risk, not a buy or sell call.

Everything in one place, sourced.

Let me explain the technical structure.

## How is the Claude loop structured?

![](https://substackcdn.com/image/fetch/$s_!JPzN!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F68fdcd29-c7d5-49fd-9d5b-6bc45d6c0adc_1758x1266.png)

The loop in one picture. Three layers, five notebooks, five agents, and a retry cap of three.

I did this for AI chips. You can do it for any industry you want to invest in.

Three layers.

- **Layer 1, the companies.** One NotebookLM per company, built from verified sources only. Mine: Nvidia, AMD, TSMC.
- **Layer 2, the industry.** One NotebookLM for the sector those companies sit in. Mine: the 2026 global semiconductor market.
- **Layer 3, the global economy.** One NotebookLM for the macro backdrop. Rates, inflation, demand.

Each layer gets its own agents.

Every company has a sub-agent that questions only its own notebook.

The Context Analyst takes those answers and tests them against Layer 2 and Layer 3.

![](https://substackcdn.com/image/fetch/$s_!s0Fs!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd942493f-84f4-41ff-ae3f-d705aa2e49c2_1456x1052.png)

The Claude loop running inside Claude Code. Four agents, the context test in progress, every token logged.

They question everything. Nothing passes without a source.

The output comes back as a website.

I wrapped the whole thing in a skill. It asks which industry you want to invest in, builds the system, and installs the NotebookLM CLI if your environment does not have it.

Here is how it works.

## How do you set up the Claude loop?

![](https://substackcdn.com/image/fetch/$s_!JiKc!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F8e266a09-33fb-4209-a5bc-c8a36872156c_1376x358.png)

The setup is two questions. Drop the skill in, name the companies and the industry, and it builds the rest.

Drop the skill into Claude Code, a desktop app. Agent orchestration does not run in VS Code yet.

It asks two things. Which companies, which industry?

The rest is the skill’s job. It trains a notebook per layer from verified sources, wires the agents, and runs the three steps.

The last step hands you a site.

You answer two questions. It builds the analysis.

---

POLL

### If I offered to build this system for you as part of a paid membership, would you be interested?

Yes, I’d be interested

Maybe, I’d like to learn more

No, I’d rather build it myself

6 DAYS REMAINING

---

![](https://substackcdn.com/image/fetch/$s_!L4Zq!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0ccc4a2a-09cd-483a-a0e4-76c7f15b99c3_1672x941.png)

---

### Next Step: A Claude skill that ships the loop for you

![](https://substackcdn.com/image/fetch/$s_!CEmu!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F00395264-0fc5-455a-ad02-5bc8a2bb0e02_2954x748.png)

The skill folder you download. SKILL.md, the config, and the prompts that wire the loop.

I wrapped this whole Claude agent loop into one skill so you do not rebuild it by hand.

Download the folder. Drop it into Claude Code.

Then paste one prompt, and it installs itself.

It sets up the NotebookLM CLI, trains a notebook for each layer, wires the agents, and ships the analysis as a site.

You point it at an industry and answer two questions. The same skill works for any sector you want to audit, not just AI chips.

Everything below the line is yours. The skill files, the five notebook prompts, the orchestration prompt, and the layer-by-layer setup.

Here are the links.

Hi **ajzopp@gmail.com**

## This post is for paid subscribers

[Already a paid subscriber? **Switch accounts**](https://substack.com/sign-in?redirect=%2Fp%2Fclaude-loops-notebooklm-chip-audit%3Futm_source%3Dsubstack%26utm_medium%3Demail%23media-5ea5fbcb-07b9-483a-a0b6-d3945a088c6b&for_pub=gencay&change_user=true)
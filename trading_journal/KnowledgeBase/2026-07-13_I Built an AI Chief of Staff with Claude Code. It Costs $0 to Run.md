---
title: "I Built an AI Chief of Staff with Claude Code. It Costs $0 to Run"
source: "https://www.learnwithmeai.com/p/build-claude-loop-local-models?img=https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa77945f4-245f-4ad3-9255-8056d4d67627_1456x971.webp&open=false"
author:
  - "[[Gencay]]"
date: "2026-07-13"
published: 2026-07-12
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
sector:
origin:
---
### Prompt engineering is out. Loop engineering is in. I built a Claude loop on local models that reads my logs and reports what I dropped, every morning. Free.

Believe it or not.

This is the new trend.

*Loop Engineering.*

5 years ago, nobody knew what prompt engineering was.

Now, we don’t need it anymore.

Everything started after Boris Cherny’s words.

*(Boris Cherny, the creator of Claude Code.)*

 <video controls=""><source src="https://www.learnwithmeai.com/api/v1/video/upload/f84b7534-d3fe-4053-a915-76a7c7e17723/src?override_publication_id=1867502&amp;type=hls" type="application/x-mpegURL"> <source src="https://www.learnwithmeai.com/api/v1/video/upload/f84b7534-d3fe-4053-a915-76a7c7e17723/src?override_publication_id=1867502&amp;type=mp4" type="video/mp4"></video>

If you are not writing the loops, you are not ahead of the curve.

But there is one more thing.

After Claude Fable 5 was pulled by goverment, it’ll released again on Jul 1.

![Notice that Claude Fable 5 was pulled by the government and re-released on July 1](https://substackcdn.com/image/fetch/$s_!xukD!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb42016ec-2a27-4ac5-8358-a24f56506666_960x1040.webp)

Fable 5 was gone, then back on July 1.

But it’ll be available until July 19.

Then you can only use it with pay as you go model, so you need to pay expensive bills.

![](https://substackcdn.com/image/fetch/$s_!kyCJ!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4e0cb9c6-8ac9-41d9-8d4d-8645e61dbc53_2872x562.png)

After 19, it will be pay-as-you-go. The bills add up fast.

That’s why everyone was searching for a new path.

A new path that does not require frontier models.

Satya Nadella, the CEO of microsoft even suggests this by writing a new article on X.

![Satya Nadella X post about moving off frontier models with 66 million views](https://substackcdn.com/image/fetch/$s_!SHhz!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd0fb6faa-1334-45ea-b29c-702b56036d58_946x416.webp)

Even Nadella pointed at this path. 66M views.

This has been viewed *66 M.*

Your frontier models can go instantly.

Like Claude, Fable 5 has gone.

So I merged two things.

Loops on local models.

The result is an AI Chief of Staff, and it costs $0 to run.

Let me show you what I built.

## What We'll Build: A Local-Model Chief of Staff

![Overview of a local-model Chief of Staff agent that reads your daily AI conversations](https://substackcdn.com/image/fetch/$s_!Rmg5!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa77945f4-245f-4ad3-9255-8056d4d67627_1456x971.webp)

The Chief of Staff. It reads everything you did today.

*A Chief of Staff.*

A Chief of Staff covers your back. It reads everything you did today, using your conversation with AI. ( We’ll make it read Claude Code & Hermes.)

Why? Because agents do a dozen things at once now, and someone has to track the loose ends you drop along the way.

So I built it, using local models. But I did it using two different paths, so no matter which system you’re using, you can build it.

### Path A: Hermes/OpenClaw Agentic System

Here is my Chief of Staff. It lives inside Telegram. The agent is Hermes, powered by Gemma 4, a fully open source model.

![Hermes Chief of Staff agent running on Gemma inside Telegram, reporting unfinished tasks](https://substackcdn.com/image/fetch/$s_!wEPw!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4ee77951-f715-47c8-ab29-8e9a92c1cd69_1456x1196.webp)

Path A: Hermes in Telegram, powered by Gemma. Fully open source.

It tracks all of my latest conversations from logs, and tells me what I did/finished or what’s left uncovered.

### Path B: Claude Code Agentic System

But not all of you have the Hermes agent, so here’s Plan B: use Claude Code to build the same system, powered by Qwen8B.

![Claude Code Chief of Staff system powered by Qwen8B listing unfinished threads](https://substackcdn.com/image/fetch/$s_!3Tt9!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F8dfd168e-4b55-4d68-95ef-84047bc4da9f_1438x1516.webp)

Path B: same system in Claude Code, powered by Qwen8B.

I have to be honest. After reading these reports, I went back and finished some of the tasks I had left unfinished.

**Tech Stack**: Qwen8B(Opensource, for path B), Claude Code(to build the system at the beginning), Hermes(Agentic System for Path-A)

## How the Claude Loop Works

![Diagram of how the Claude loop works with a dumb script half and a local model half](https://substackcdn.com/image/fetch/$s_!nZWn!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F91554b6d-5196-45cc-9ddb-5ed27d4c1bf0_1456x971.webp)

Two halves. One does not think. One is the local model.

The loop has two halves.

The **first half** *does not think*.

A small script opens the conversation logs and pulls today’s messages into plain text.

- On the Mac mini, it reads the Hermes database.
- On the laptop, it reads the Claude Code logs.

The **second half** is the *local model.*

That plain text goes in with one job. Find the threads I left open.

A thread is open when I asked a question that never got answered. When I said “ *do this* ” and nothing confirmed it got done.

When I said “ *I will finish this next* ” and never came back.

Then the model checks its own work.(***loop***)

It scores the list. Real threads with real evidence, or guesses?

If the score is low, it reads the transcript again.

*Up to three passes.* (threshold)

Then it writes the report. If nothing is open, it says nothing. No invented busywork.

The report comes out in the same shape every run.

In the automation part, my Hermes agent does this every day at 9:00 PM. I read the report before planning the next day, usually around 8:30 AM on my computer, so I can double-check what I did on both my MacBook (Claude Code) and my Mac mini (Hermes). That way, I don’t miss anything.

## Set Up Your Own Claude Loop in 10 Minutes

![Two paths to set up the same Claude loop, Hermes agent or your own machine](https://substackcdn.com/image/fetch/$s_!-Dg0!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F01c7ad7b-4798-481a-99e9-996e4a4bbb34_1456x971.webp)

Two ways, same loop.

Two ways, same loop.

I set both up with Claude Code. Not by writing code. By telling it what I wanted and handing it the files. You can do the same with Codex, OpenCode, or whatever agent you run.

- **Path A is the Hermes agent.**
	- Upload the ***Soul.MD***, I give you, it’ll ask you a couple of questions to build the cron, and you are ready.
- **Path B is your own machine.**
	- Open Claude Code, Codex or any agentic system you use, and paste my prompt.

You’ll be ready.

But before setting this up, you need to download one application to run your local models, for both your Hermes and your own computer.

And do not download the local model before reading this, because if you did not check two things I am going to tell you, your computer might freeze after running these models.(Mine did!)

All setups will last 10 minutes at most. Let’s start.

![Claude loop full setup finished in three steps in under ten minutes](https://substackcdn.com/image/fetch/$s_!b6L7!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F91ecf956-dc84-4e7a-8363-2669d9cba7c1_1456x971.webp)

Everything in 3 steps. 10 minutes, tops.
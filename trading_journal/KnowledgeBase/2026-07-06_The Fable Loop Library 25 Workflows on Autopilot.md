---
title: "The Fable Loop Library: 25 Workflows on Autopilot"
source: "https://x.com/exm7777/article/2073432521954697653"
author:
  - "[[Machina (@EXM7777)]]"
date: "2026-07-06"
published: 2026-07-04
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
  - "X (formerly Twitter)"
sector:
origin:
---
![Image](https://pbs.twimg.com/media/HMY1oSEacAA8lgB?format=jpg&name=large)

i'm going to teach you how to run Fable 5 on autopilot, using my own library of loops and goals... 25 workflows, each with a prompt and the exact tool it plugs into

the method follows karpathy's recipe for agents: "here's an objective, here's a metric, here's your boundaries of what you can and cannot do. And go"

every workflow below is exactly that... an objective, boundaries, and the proof it's done

Fable 5 is the model built for this: it holds one job for hours without losing the plot, where other models wander off after minutes

remember these two Claude Code commands:

\> /loop - a job that repeats on a schedule until it's done

\> /goal - a finish line you write once, and the model works alone until it's crossed

one warning before you schedule anything: a model that never gets tired never stops on its own, and Fable is the most expensive model on the market

run it without a budget and a stop rule and the bill will find you... every workflow below carries both

the ready-to-run versions of these loops, and the training on turning them into income, live in the real time AI ops community: [weeklyaiops.com](https://weeklyaiops.com/)

# what's a loop?

a loop is a job your agent repeats on a schedule: every morning, or every time something new lands

five parts, always:

\> a schedule - when it wakes up

\> ONE change per round - it fixes the single most important thing it found, never everything at once

\> the same check every time - so this week's score can be compared against last week's

\> a state file - a text file where it writes what it did and what's queued next

\> a stop - a hard cap on rounds and a rule for what "done" and "blocked" look like

it's the same shape frontier researchers run their own experiments on: change one thing, test it, keep it only if it improved, write it down, repeat

the state file is the part almost everyone skips, and it's the part that makes every run smarter than the last

the model reads its own history before every round, so it never redoes finished work

every loop below also carries a color:

\> green - safe to run alone: it only reads things and writes to its own files

\> yellow - it drafts, you approve: replies, page edits, PRs, anything a human ships

\> red - never runs alone: money, production, outbound messages, or anything a customer sees

run any loop once by hand before you schedule it

and route it cheap: a smaller model runs the routine rounds, Fable steps in only where the cheap model failed

# what's a goal?

a goal is the other shape of work: not a schedule, a finish line

you type /goal, describe what done looks like, and the model keeps working on its own... a second, smaller model reads along as the judge and confirms when the line is crossed

one detail decides whether this is useful or a token bonfire: the judge only sees the conversation

it can't open your files, can't run your tests, can't check your site

so "done when the tests pass" is a wish... "done when the full green test run is PASTED in the chat" is a contract

agents say "done" all the time without it being true... proof you can read is the only version that counts

every goal below ends the same way: paste the proof, and if you can't, paste the failures and stop

# the library

how to read each entry: the name, the tool it plugs into, why it earns a slot... and the full working prompt, ready for your terminal

two words you'll see:

\> MCP - a plug that gives your agent direct access to an app (your inbox, your analytics, your repo, your ad account)

\> API key - a password that lets the agent read a service on your behalf

the tools named per loop were researched for agent access specifically... hosted MCPs with OAuth where they exist, cheap pay-as-you-go APIs where they don't

paste each prompt into Claude Code, set the cadence line as your schedule, and swap the bracketed parts for your business

## marketing + content

1\. answer-engine gap loop · Exa MCP

your buyers ask ChatGPT and Perplexity questions your site should be the answer to, and every unanswered one is a competitor's citation

this loop finds the gaps and closes exactly one per week

![Image](https://pbs.twimg.com/media/HMZFfK4bMAAnDBF?format=jpg&name=large)

2\. programmatic-page quality gate · Search Console MCP

if you generate pages from a template, thin and duplicate pages leak into google's index and drag the whole site down

the gate catches the worst pattern before google does

![Image](https://pbs.twimg.com/media/HMZFsL3bkAECsdm?format=jpg&name=large)

3\. share-of-model brand watch · Perplexity API key

when buyers ask AI engines "best \[your category\]", you're either in the answer or invisible

every week it asks the same questions and logs where you stand, so you see the trend instead of guessing

![Image](https://pbs.twimg.com/media/HMZF5SHbcAAwShZ?format=jpg&name=large)

4\. competitor-content watch loop · DataForSEO MCP + Firecrawl monitor

your competitors tell you their SEO strategy every week... in the articles they publish and the keywords those articles chase

reading both and planning your next moves against their gaps is a friday job... this is the friday job

![Image](https://pbs.twimg.com/media/HMZGDAlbkAAENIC?format=jpg&name=large)

5\. content-brief backlog loop · Search Console MCP

the writing pipeline dies at the blank page, not at the writing

the backlog stays stocked with fully specified briefs mined from your own traffic and questions

![Image](https://pbs.twimg.com/media/HMZGWZPbkAAfFBb?format=jpg&name=large)

6\. X content-idea miner · [twitterapi.io](https://twitterapi.io/) + Typefully

the accounts you respect are running your content R&D for free... every high-performing post in your niche is a proven angle waiting for your version

a watched list, a ranking of what's working, and your take drafted in your own voice, every morning

![Image](https://pbs.twimg.com/media/HMZGglIbsAAPjBp?format=jpg&name=large)

7\. ad-creative fatigue drafting loop · Meta Marketing API

ad sets decay, and the usual response is noticing two weeks late

the next batch sits drafted before the drop, grounded in what already won for you... and nothing launches without you

![Image](https://pbs.twimg.com/media/HMZGlI2bQAAyJOK?format=jpg&name=large)

8\. expectation-gap audit · Zendesk MCP

when a customer writes "i thought it did X", a page somewhere promised them X

this audit starts from the disappointment and walks backwards to the sentence that caused it

![Image](https://pbs.twimg.com/media/HMZGvjhaEAATqcE?format=jpg&name=large)

9\. presale questions loop

the questions people ask BEFORE buying are answers you keep retyping

they're already sitting in your DMs, comments and emails... this loop turns them into an answer bank you never write twice

marketing finds the demand... product decides what gets built next

![Image](https://pbs.twimg.com/media/HMZG45hawAA0_Xl?format=jpg&name=large)

## product

10\. brand-mention feature radar · Reddit API + HN Algolia + Exa

people tell the internet what they wish your product did, they just never tell you

the mentions get swept weekly, the complaints and feature asks clustered, and the loudest one arrives as a drafted implementation plan

![Image](https://pbs.twimg.com/media/HMZHX9cbAAAQxRC?format=jpg&name=large)

11\. review-mine to roadmap · app store review APIs

your customers write your roadmap every week in reviews and support messages... in their words, ranked by pain

it just needs compiling

![Image](https://pbs.twimg.com/media/HMZHM3HagAAiGgz?format=jpg&name=large)

12\. drop-point copy loop · PostHog MCP

somewhere in your product, users hit a moment that makes them give up... and the words on that screen are usually half the reason

analytics finds the moment, this loop fixes the words

product listens... operations answers

![Image](https://pbs.twimg.com/media/HMZKpOHa4AAf3Sn?format=jpg&name=large)

## business ops

13\. inbox-to-decision triage loop · Gmail MCP

a shared inbox is a decision queue wearing a disguise

every unread item becomes decide / delegate / defer / drop, with the top reply already drafted

![Image](https://pbs.twimg.com/media/HMZLrf4bwAARDqd?format=jpg&name=large)

14\. month-close reconciliation prep · QuickBooks API

the boring half of closing the books is categorizing transactions against your own history

this loop does the boring half and hands a human a short exception list... it never files anything

![Image](https://pbs.twimg.com/media/HMZMeyiagAAFw-g?format=jpg&name=large)

15\. SOP-drift catcher · Notion MCP

the written process and the real process drift apart in silence, and the doc is always the last to know

comparing how work actually happened against the SOP is a job, and this one does it weekly

![Image](https://pbs.twimg.com/media/HMZMtmObIAAbsJw?format=jpg&name=large)

16\. proposal / RFP backlog drafter

every RFP asks 80% questions you've answered before and 20% that are genuinely new

this loop drafts the 80 from your answer library and flags the 20, so proposals move daily instead of stalling

![Image](https://pbs.twimg.com/media/HMZM0cta0AA1L_M?format=jpg&name=large)

17\. KPI anomaly watch · PostHog MCP + Stripe

dashboards show everything, which is why nobody looks

silent on normal days, and when a metric breaks its band you get paged with the likely cause pre-investigated

![Image](https://pbs.twimg.com/media/HMZM9mWaoAAM0Qn?format=jpg&name=large)

18\. unpaid-invoice chaser · Stripe API key

b2b clients pay late because late payment usually costs them nothing

this loop keeps an aging ledger and drafts the next nudge at each threshold... you send, it remembers

operations keeps the machine running... research decides where it points next

![Image](https://pbs.twimg.com/media/HMZNFaob0AA2T8z?format=jpg&name=large)

## research + decisions

19\. overnight intel refresh · Exa MCP + Firecrawl monitor

markets move weekly whether you're watching or not

a cheap model watches your tracked sources on schedule, and the big model only writes the monthly synthesis

![Image](https://pbs.twimg.com/media/HMZNJV9asAANfWP?format=jpg&name=large)

20\. regulatory / source digest · Firecrawl MCP

some sources you can't afford to skim: the regulators and the two papers that will change your niche

only what materially changed gets digested, with a plain-language "so what"

![Image](https://pbs.twimg.com/media/HMZNkmSbAAEB1vj?format=jpg&name=large)

21\. hard-question escalation queue

paying flagship prices for questions a cheap model answers is the default way agent bills explode

this queue makes every question earn its escalation: cheap model first, Fable only on a logged failure

![Image](https://pbs.twimg.com/media/HMZN1B8awAAqMMF?format=jpg&name=large)

22\. kill-criteria loop

options survive meetings because nobody wrote down what would disqualify them

here every live option declares its kill condition upfront... then the evidence hunt begins

![Image](https://pbs.twimg.com/media/HMZNvBPbEAAAeu5?format=jpg&name=large)

23\. pre-mortem loop

it's 12 months from now and the decision failed... writing that story before you commit is the cheapest insurance there is

![Image](https://pbs.twimg.com/media/HMZN80VbQAAmZWH?format=jpg&name=large)

24\. repeat-offender digest

the same failure showing up in two different workflows is not two bugs... it's one system problem wearing two costumes

this digest reads every run ledger and hunts the costume changes

![Image](https://pbs.twimg.com/media/HMZOKEmaEAAcQWs?format=jpg&name=large)

25\. shadow prompt loop

testing a new prompt on hand-picked examples tells you it passed your imagination, nothing more

run it in the shadows against real traffic and let the disagreements decide

and if your business ships software, the next thirteen live inside your repo and your CI... the system that auto-runs your tests on every change

![Image](https://pbs.twimg.com/media/HMZOP8JaEAAMGTO?format=jpg&name=large)

# start here

the whole system, in order... copy this:

\> pick ONE loop that touches your biggest leak: inbox, KPIs, content, errors

\> run it once by hand and read the state file it writes

\> schedule it, with the cadence line as written

\> after a week, add a second loop or hand a cursed one-shot to a /goal with pasted-proof done conditions

\> route cheap: a smaller model runs the routine rounds, Fable takes what the cheap model failed

\> money, production and outbound messages always end at a human... the prompts are built that way, keep it that way

one more thing on cost: Fable 5 comes off subscription plans on july 7 and moves to pay-as-you-go credits

after that date the cheap-first routing and the hard caps in these prompts stop being style and start being the bill

that endurance is sitting in your terminal right now

these 25 give it a job and a finish line

the smallest start is one loop and one state file

the rest schedules itself

join the best AI community in the world: [weeklyaiops.com](https://weeklyaiops.com/)

(part 2 coming soon with 25 new workflows...)
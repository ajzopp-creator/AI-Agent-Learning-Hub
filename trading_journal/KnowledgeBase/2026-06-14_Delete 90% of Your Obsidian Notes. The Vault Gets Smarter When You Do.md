---
title: "Delete 90% of Your Obsidian Notes. The Vault Gets Smarter When You Do."
source: "https://x.com/DamiDefi/article/2061034224107311153"
author:
  - "[[Dami-Defi (@DamiDefi)]]"
date: "2026-06-14"
published: 2026-05-31
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
  - "X (formerly Twitter)"
sector:
origin:
---
![Image](https://pbs.twimg.com/media/HJpDrjbWUAIpIyZ?format=jpg&name=large)

Last month I deleted 1,890 of the 2,100 notes in my Obsidian vault in a single afternoon. Ninety percent of everything I had saved in two years, gone in one sitting.

Articles I had clipped and never reread. Highlights I saved because the sentence sounded smart. Voice notes that were half-formed thoughts I had already either acted on or forgotten. Tweets I bookmarked in a dopamine reflex and never returned to.

I expected to feel the loss. I had spent two years accumulating that material. Some part of me believed every note was a small insurance policy against forgetting something important.

Instead the vault got sharper the next morning.

Here is the exact difference. The morning before the cleanup, Claude's daily brief told me that a note on stablecoin regulation connected to a note on a DeFi lending protocol. Technically true. They both contained the word "yield." Useless. That was the kind of connection a bloated vault produces: two notes linked by a shared word, not a shared idea.

The morning after the cleanup, Claude connected a thesis I had written on institutional crypto adoption to a six-week-old note on a specific Federal Reserve working paper I had forgotten I saved. That connection became the spine of an article. Same AI. Same prompt. The only thing that changed was that I removed 1,890 notes of noise it had been wading through to find the signal.

I had not added any intelligence to the system. I had removed noise from it. And removing noise turned out to be the same thing as adding signal.

This goes against everything the productivity world tells you. Capture everything. Never lose an idea. Your second brain should hold it all. That advice is wrong, and the reason it is wrong is mechanical, not philosophical.

Here is why a smaller vault is a smarter vault.

## The Belief That Is Quietly Costing You

Every note-taking guide is built on the same unexamined assumption: more captured information equals more knowledge.

It does not. Captured information is not knowledge. It is raw material. And raw material has a cost that nobody talks about: it dilutes everything around it.

When your vault was a passive archive that you searched manually, this did not matter much. A bloated vault just meant your search returned more results. Annoying but survivable.

The moment you connect an AI to your vault, the math changes completely. Now the vault is not a thing you search. It is the context an intelligence reasons across. And the quality of that reasoning is bounded by the ratio of signal to noise in what it reads.

A vault that is 90% low-value captures is a vault where Claude spends 90% of its attention on material that does not matter. The connections it surfaces are drawn from a pool that is mostly junk. The patterns it finds are diluted by patterns that are noise. You did not build a second brain. You built a haystack and asked an AI to find needles in it.

## The Mechanism Nobody Explains

There is a principle from working with AI instruction files that applies directly here.

A CLAUDE.md file performs worse when it is bloated. Models reliably follow a limited number of distinct instructions before they start dropping things. Every line you add past the useful ones competes with the lines that actually matter for the model's attention. The fix is not more instructions. It is fewer, better ones.

A vault is the same system at a larger scale.

When Claude reads across your vault to produce a synthesis, it is working within a finite attention budget. Every note it reads is a claim on that budget. A vault of 210 high-signal notes gives Claude 210 things that matter to reason across. A vault of 2,100 notes where 1,890 are noise gives Claude the same 210 things to find, buried under ten times their volume in material that actively degrades the search.

This is not a storage problem. Storage is infinite and cheap. This is an attention problem. And attention, for both you and the AI reading your vault, is the scarcest resource in the entire system.

More notes do not make the vault more capable. Past a certain point they make it less capable, because they lower the signal density that the intelligence depends on.

## What I Actually Deleted

The 1,890 notes I removed fell into four categories. Every one of them felt important when I saved it and turned out to be noise.

**1\. Saved articles I never reprocessed**If I clipped an article and never went back to extract the one idea worth keeping, the article was not knowledge. It was an intention I never fulfilled. The full text sat in my vault diluting every search. I kept the handful where I had actually written a reaction. I deleted the rest.

**2\. Highlights with no reaction attached**A highlighted sentence with no note from me about why it mattered is someone else's thought sitting in my vault. It is not mine until I have done something with it. Hundreds of these went.

**3\. Quick captures I never developed**The voice notes and Telegram messages that were genuinely just fleeting thoughts. If a thought was worth keeping it had already graduated into a real note. The rest were mental residue.

**4\. Duplicate thinking**The same idea captured five times across five months in slightly different words. I kept the sharpest version and deleted the four echoes.

What survived was the material I had actually thought about. My own reactions. My theses. The sources where I had extracted and recorded what mattered. The questions I keep returning to. Roughly 210 notes that were genuinely mine.

## The Test for What Stays

The rule I now use is simple and it is brutal.

A note earns its place in the vault only if it contains thinking, not just information.

Information is what you collected. Thinking is what you did with it. An article is information. Your one-paragraph reaction to why that article is wrong is thinking. A highlighted quote is information. Your note on how that quote connects to something you believe is thinking.

The vault should hold your thinking and the minimum information required to support it. Everything else is available on the internet when you need it, which means storing it in your vault buys you nothing and costs you signal density.

When I am unsure whether a note stays, I ask one question: if I deleted this, would I lose anything I could not retrieve in 30 seconds from a search engine? If the answer is no, it is not a vault note. It is a bookmark pretending to be knowledge.

There is one exception worth naming. Some information is pure data, has no thinking attached, and is genuinely hard to re-find. An obscure on-chain figure. A primary source that has since been taken down. A data point from a report behind a paywall. These are rare, but they are real. The rule for them is simple: keep the data point itself, stripped down to one line, and delete everything around it. You are not keeping the article. You are keeping the single irreplaceable fact and discarding the 2,000 words of noise it arrived wrapped in. The signal stays. The volume goes.

## The Prompt That Does the Audit For You

You do not have to make all 1,400 decisions manually. Claude can do the first pass if you point it at your vault and give it the right criteria.

**Prompt**

> Read across my Obsidian vault. I am doing a signal-density cleanup. My goal is to delete notes that contain only collected information and keep notes that contain my own thinking.For each note, classify it into one of three buckets:KEEP: Contains my own reaction, thesis, analysis, or a question I am actively working on. This is my thinking, not just collected material.DELETE: Contains only information I clipped or highlighted with no reaction from me. Retrievable from the internet in seconds. Adds volume without adding [signal.REVIEW](https://signal.review/): Genuinely ambiguous. Could go either way. I will decide manually.For the DELETE bucket, do not delete anything. Just produce the list with a one-line reason for each so I can review before removing. Be aggressive. When a note is borderline between KEEP and DELETE, lean DELETE. The cost of keeping noise is higher than the cost of losing a marginal note.

The instruction to lean toward deletion is the important part. Your instinct will be to keep everything because loss feels expensive. The whole point of this exercise is that keeping noise is more expensive than losing marginal notes. The prompt has to fight your hoarding instinct because you will not fight it yourself.

## What Changed After

**The daily brief got sharper**

Before the cleanup, Claude's morning synthesis would surface connections that were technically real but useless. Two notes linked by a shared word, not a shared idea. The noise in the vault was producing noise in the output. After the cleanup, when Claude surfaced a link between two notes, the link was meaningful, because almost everything left in the vault was meaningful.

**Retrieval started sounding like me**

When I asked the vault a question, the answer came from my actual thinking rather than from a sentence I had highlighted from someone else two years ago and forgotten. The vault started sounding like me because what was left in it was actually me.

**The psychological shift I did not expect**

A vault of 210 notes I had genuinely thought about felt like an asset. A vault of 2,100 notes that was mostly clippings felt like a chore I was perpetually behind on. Deleting the noise did not just improve the system. It removed the low-grade guilt of a backlog I was never going to process.

## The Two Objections and Why Both Are Wrong

The first objection is obvious. What if you delete something you needed later?

In a month of running the leaner vault, here is how many times I reached for a deleted note and could not find what I needed: zero. Not because I am lucky. The notes I deleted were notes I had already not looked at for months. Deleting something you have ignored for a year is not a loss. It is an admission of what was already true. And for the rare case where you do need a deleted article, it is on the internet. The vault was never the only copy.

The second objection is the serious one, and it is the one capture-everything people actually believe: compounding requires volume. You cannot know today which note will matter in two years, so you keep everything and let the connections emerge over time.

This sounds right and it is wrong, because it confuses two different things that compound very differently.

Two things compound very differently inside a vault:

**Your thinking compounds.** The reactions you write, the theses you build, the questions you keep returning to — these get more valuable as they accumulate because they connect to each other and to your future thinking. Volume genuinely helps here.

**Collected information does not compound.** A clipped article you never reacted to does not become more valuable over two years. It just sits there. It will not connect to anything because you never gave it a connection point. You never told the vault what it meant to you. It is inert. Ten thousand inert notes do not compound into insight. They compound into noise.

The capture-everything crowd is right that something compounds. They are wrong about what. Keep the thing that compounds, which is your thinking. Delete the thing that does not, which is everything you collected and never processed.

The asymmetry is the entire argument. Keeping a noise note costs you signal density every single day. Deleting it costs you a 30-second search on the rare day you need it. Optimising for the rare day at the expense of every day is the exact mistake the capture-everything crowd makes.

## How to Run the Cleanup This Weekend

Set aside two hours. Not more. This is a cull, not a renovation.

**Step 1: Run the audit prompt**Let Claude produce the DELETE list. Read it. Do not agonise. For each note your only question is whether you would lose anything you could not re-find in 30 seconds.

**Step 2: Move before you delete**Archive everything flagged for deletion into a single folder rather than deleting permanently. Leave it there for two weeks. If you do not reach for anything in that folder in two weeks, delete the folder. You will not reach for it.

**Step 3: Run the daily brief the next morning**Notice what changed. The vault will be sharper because you finally stopped asking it to reason across material you never thought about yourself.

The productivity world sold you on capturing everything because capturing feels like progress. It is not. Thinking is progress. The vault should hold your thinking and almost nothing else.

Delete the 90% that is noise. Watch what the remaining 10% can do.

Follow [@damidefi](https://x.com/@damidefi) on X for daily Claude AI tools, crypto analysis, and the full journey to 100K. Bookmark this. Share it with one person whose vault has become a graveyard they feel guilty about.
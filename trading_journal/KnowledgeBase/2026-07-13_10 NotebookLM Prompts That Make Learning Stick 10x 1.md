---
title: "10 NotebookLM Prompts That Make Learning Stick 10x"
source: "https://www.learnwithmeai.com/p/10-notebooklm-prompts-that-make-learning?utm_source=post-email-title&publication_id=1867502&post_id=203528833&utm_campaign=email-post-title&isFreemail=true&r=30kzn1&triedRedirect=true&utm_medium=email"
author:
  - "[[Gencay]]"
date: "2026-07-13"
published: 2026-07-11
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
sector:
origin:
---
### Ten NotebookLM prompts that make learning stay, each one built on how your brain actually encodes information.

A couple of weeks ago, I wrote an article with 1 [0 NotebookLM prompts to learn anything faster.](https://www.learnwithmeai.com/p/notebooklm-prompts-to-learn)

Learning fast was good, but what if you don’t have a time constraint?

So this time I went looking for the other half.

Not how to learn fast, but how to make it stay.

I found six methods.

![Six learning science methods that make memory stick, from cognitive load to generation](https://substackcdn.com/image/fetch/$s_!bCYY!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7c5f558e-41c4-43a7-bdc7-6303b8e03880_1456x819.png)

Six methods, each backed by how the brain encodes, not study-tip folklore.

Every one of them is backed by how the brain actually encodes information, not by study-tip folklore.

Now I have written 10 prompts for these six methods.

Here are all of them.

![10 prompts that make learning stick 10x](https://substackcdn.com/image/fetch/$s_!YbG_!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F833a245b-d7eb-4f05-a650-781e13ed7e49_1456x819.png)

Ten prompts. One goal. Understand it well enough to teach it.

I trained a NotebookLM on [Anthropic’s own video on prompting](https://www.youtube.com/watch?v=T9aRN5JkmL8), so the source is the people who built the model rather than a blog summarizing them.

Here it is.

![](https://substackcdn.com/image/fetch/$s_!WqJq!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F71549de1-ee10-4673-8b2c-0de565d731ba_1456x747.png)

The source is the people who built the model, not a blog summarizing them.

Let’s start.

If you don’t know the basics of the [NotebookLM](https://www.learnwithmeai.com/t/notebooklm), read [this one](https://www.learnwithmeai.com/p/how-to-use-notebooklm-better-than).

---

**Technique 1: Cognitive load.**

*Feed it in pieces.*

Working memory is small. You can hold a few things at once, and everything past that spills before it ever reaches long-term memory.

The next two prompts do that.

- The first one breaks a new topic into pieces that your memory can carry.
- The second one strips out the noise that was eating the space those pieces needed.

---

## Prompt 1: The breakdown that fits one concept in your head

You open the source on prompting, and the first stretch throws clear communication, theory of mind, few-shot examples, and a chain of thought at you all at once, so you read all four and hold none.

The material was not too hard; it was too much at once.

### The 1-click way: Report feature

Open your notebook, and in the Studio panel, click Reports, then pick Briefing doc.

![NotebookLM Reports panel with Create your own selected for the breakdown prompt](https://substackcdn.com/image/fetch/$s_!5TB9!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa1c36ee3-5d91-4603-8f94-5f7b4f86b72f_1456x758.png)

Report → NotebookLM Studio

NotebookLM compresses your whole source into one summary, so you get every idea on a single page.

![NotebookLM briefing doc that flattens every concept to one level](https://substackcdn.com/image/fetch/$s_!jjFT!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6715a3e7-f156-4616-bf30-d812b95bf025_1456x1145.png)

The briefing doc hands you the whole map when you need the first turn.

But a briefing doc flattens everything to one level, where the concept you have never seen sits at the same weight as the five you already know, so your brain cannot tell new from review.

It hands you the whole map when all you needed was the first turn.

**UI selections before you paste (you click these yourself):**  
Report → Create your own.

Use this prompt.

```markup
Break {topic} into the smallest concepts from the sources that still stand on their own. 
Order them so each concept only depends on the ones before it, and never use a term before 
an earlier concept has defined it. For each concept give one plain sentence of what it is, 
one sentence of why it matters, and one short example drawn from the sources. 
Fully finish one concept before starting the next, and do not summarize all of them up front.
```

For {topic}, here I used **prompt engineering fundamentals**, since the source opens by defining the field from four angles.

![](https://substackcdn.com/image/fetch/$s_!EU7x!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F39b73942-acab-4996-9317-e32c6f2408f3_1456x1145.png)

Each concept lands with its own definition, weight, and one example from the source.

Each concept lands with its own definition, its weight, and an example pulled straight from the source, so you meet them one at a time instead of all four in the same breath.

### When to use which?

- **Briefing doc feature** → A fast overview, when you already know most of the material and want it on one page.
- **Custom prompt** → A first encounter, when the topic is new, and you need it broken down small enough to hold.

## Prompt 2: The cut that leaves only what you need

Your source has forty minutes of talk in it, and maybe eight minutes of it is the part you actually have to know.

The rest is intros, side stories, and a tangent about Pokémon.

You read all of it, and the eight minutes drown in the other thirty-two.

Reading more is not learning more.

The noise takes up the same space in your head that the signal needed.

### The 1-click way: Report feature

Open your notebook, and in the Studio panel, click Reports, then pick Study guide.

![NotebookLM Reports panel with Create your own selected for the breakdown prompt](https://substackcdn.com/image/fetch/$s_!0T34!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2a49fdf4-83d1-4ee8-bd90-036fd7f24a20_1456x758.png)

Report → NotebookLM Studio

NotebookLM turns your source into a guide with questions, terms, and a glossary, all in one pass.

![NotebookLM study guide report with quiz, terms, and glossary in one pass](https://substackcdn.com/image/fetch/$s_!VYm2!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F044d4ec2-754c-4f79-8cdf-efda8766db8b_1456x1058.png)

A study guide keeps everything, because it does not know what you are studying for.

But a study guide keeps everything, because it does not know what you are studying for. The throwaway anecdote gets a glossary entry next to the core principle, and you spend attention on both. It tidied the room without throwing anything out.

So you tell it what you are studying for, and make it cut everything that does not serve that.

**UI selections before you paste (you click these yourself):**  
Report → Create your own.

Use this prompt. Customize the `{topic}` and the `{goal}`.

```markup
Go through the sources on {topic} and keep only what serves {goal}. 
Cut intros, asides, repeated points, and anything that does not change how I would 
answer a question on {goal}. For each thing you keep, give one line on what it is and 
one line on why it matters for {goal}. List what you cut at the end in a single line, 
so I can confirm nothing important was dropped.
```
- {topic} → prompt engineering fundamentals
- {goal} → writing a prompt that holds up across many different inputs
 <video controls=""><source src="https://www.learnwithmeai.com/api/v1/video/upload/375dd331-8426-4ba5-867c-c51c29d0b41f/src?override_publication_id=1867502&amp;type=hls" type="application/x-mpegURL"> <source src="https://www.learnwithmeai.com/api/v1/video/upload/375dd331-8426-4ba5-867c-c51c29d0b41f/src?override_publication_id=1867502&amp;type=mp4" type="video/mp4"></video>

Now the source comes back stripped to the part that moves your goal, with the side stories named and set aside instead of sitting in the middle of your notes.

### When to use which?

- **Study guide feature** → A full sweep, when you want every term and question the source contains.
- **Custom prompt** → A focused run, when you know what you are studying for and the source is padded with everything else.

---

**Technique 2: Dual coding: build two paths to the same idea**

Read a definition, and you store it in one way, as words. Code that same idea a second time as a picture, a layout, a spatial map, and you store it twice, on two separate tracks.

When recall fails on one track, the other still fires.

Two paths to one memory beat one path every time.

The next two prompts cross the wires on purpose. The first turns words into a picture. The second turns a picture back into words, so the idea gets built from both ends.

---

## Prompt 3: Turn a process into a picture you can see

You read how the experts iterate on a prompt, the back and forth, the restart button, the edge case hunt, and it makes sense line by line.

Then you try to recall the whole loop a week later, and you get three steps out of seven, in the wrong order.

The words were clear. They just never turned into a shape you could see.

### The 1-click way: Infographics feature

Open your notebook, and in the Studio panel, click Infographics.

![NotebookLM Studio panel with the Infographics feature highlighted](https://substackcdn.com/image/fetch/$s_!JJX7!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff2159cd7-695b-417b-afc7-0262ae1ac37f_1456x755.png)

Studio → Infographics. One click to lay the source out as a visual.

NotebookLM reads your source and lays the ideas out as a visual, with blocks and icons and a bit of color.

But by default, it decorates the whole source evenly, so the throwaway stat gets the same bright block as the step that actually matters.

![Default NotebookLM infographic decorating the whole source evenly](https://substackcdn.com/image/fetch/$s_!58tE!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff8b8b37a-ef3c-4a13-af06-83d900d24639_1456x813.png)

Looks like an explanation without being one. A poster, not a map of how it works.

You get something that looks like an explanation without being one. It is a poster, not a map of how the thing works.

So you tell it to draw one specific process, in the order the steps actually happen.

**UI selections before you paste (you click these yourself):**  
Infographics → Visual Style: Sketch Note, Orientation: Square, Detail Level: Standard.

Use this prompt. Customize the `{process}`.

```markup
Map {process} from the sources as a single linear flow, step by step in the order it happens. 
Show each step as one block with a three-word label and one line of what happens there. 
Draw the arrows between steps so the path is the point, not the decoration. 
Mark the one step where most people go wrong. Use only steps the sources actually describe, 
and do not invent stages to fill space.
```

For `{process}` here I used **how a prompt engineer iterates on a prompt**, the loop the experts describe again and again.

![Custom NotebookLM infographic mapping the prompt engineering iteration loop step by step](https://substackcdn.com/image/fetch/$s_!3EsR!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff1a4f54b-7906-40fe-bff7-d6b890ab9741_1456x1456.png)

Now the loop is a shape you can walk along, with the failure point marked.

Now the loop is a thing you can see, with the steps in order and the failure point marked, so recall has a shape to walk along instead of seven loose words to gather.

### When to use which?

- **Infographics feature** → A quick visual, when you want the source to look organized at a glance.
- **Custom prompt** → Real encoding, when you need one process drawn as a path, you can replay in your head.

## Prompt 4: Say the picture back in your own words

You build the clean diagram, the one with the loop and the labeled steps, and it sits there looking finished.

You glance at it, you nod, and you move on, because it looks like you understand it. Then someone asks you to explain the loop out loud, and you point at the picture instead of saying it.

Looking at a diagram is not the same as holding it. The second channel only opens when you put the picture into words yourself.

### The 1-click way: none

There is no button for this one, and that is the point. A feature can draw the picture for you, but it cannot make you translate it back, because the translation is the part that does the work.

So you set it up in the Chat, where you say the thing first, and the model checks you after.

**UI selections before you paste (you click these yourself):**  
Open the Chat, click Configure.

![NotebookLM chat with Configure notebook option for setting a custom persona](https://substackcdn.com/image/fetch/$s_!71wD!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd1cb5346-1385-4ed0-81b7-e91af3d93e88_1456x737.png)

Chat → Configure. You set the persona, then say the idea cold.

Use this prompt.

```markup
I am going to describe structure from the sources in my own words, from memory, without looking back. 
Let me finish before you say anything. Then check what I said against the sources and tell me 
which parts I got right, which I got wrong, and which steps or links I left out. 
Do not explain the whole thing back to me. Point only at the gaps, and name the one I should fix first.
```

With the persona set, I picked one idea and tried to say it cold. Here is what I typed.

```markup
Let's talk about chain of thought. From what I understood, chain of thought is when 
you make the model write out its reasoning before the answer, and it works better mostly 
because it gives the model more space to compute, like more attention over the tokens.
```

And here is my answer.

![NotebookLM chat catching the one thing said backwards about chain of thought](https://substackcdn.com/image/fetch/$s_!S_g6!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff4ccb605-cf42-4110-be76-6710628b7634_1456x1293.png)

Saying it back surfaced the gap. Now the idea is wired to language.

You said it cold, and the model caught the one thing you had backwards, the idea that the chain of thought is just extra room to compute.

That was the link you skipped, and the source disproves it with the um-and-ah test, where padding the output with filler tokens did nothing.

Saying it back is what surfaced the gap, and now the idea is wired to language instead of sitting on the screen.

### When to use which?

- **Plain Chat** → A quick answer, when you just want to look something up in the source.
- **Custom prompt** → Real encoding, when you have the picture but cannot yet say it, because saying it is the second path memory needs.

---

**Technique 3: Chunking: bind the scattered pieces into one shape**

A beginner holds forty separate rules and drops half of them under pressure. An expert holds four groups, and each group carries ten rules inside it without taking extra space. Same information, far less load, because the mind stores patterns, not loose facts.

This prompt does the binding for you. It takes the scattered tips in your source and groups them under a few patterns you can actually carry.

---

## Prompt 5: Group the loose facts under patterns you can hold

Your source on prompting throws a dozen separate tips at you. Give the model an out. Read every output. Test the edge cases. Give it the paper. Each one makes sense alone, and together they are a pile you cannot lift, because twelve loose items is exactly seven too many to hold.

The tips were not wrong. They were just never grouped into something your memory could carry as one piece.

### The 1-click way: Report feature

Open your notebook, and in the Studio panel, click Reports, then pick Briefing doc.

![NotebookLM Studio panel with Reports highlighted for the chunking prompt](https://substackcdn.com/image/fetch/$s_!PMna!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F5532afd2-7f52-41b1-942f-2f07ed914145_1456x753.png)

Studio → Reports → Briefing doc. The default rundown, before you group anything.

NotebookLM lists the key points from your source in a clean rundown, one after another.

But a rundown is still a list, just a tidy one, and a list of twelve is twelve things to remember. It put the items in a row without telling you which ones belong together, so you are still carrying each one on its own.

![NotebookLM briefing doc listing takeaways as a flat equal column](https://substackcdn.com/image/fetch/$s_!xvCB!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe7de06a7-0e7a-4a3b-bc2b-ff61d8a399aa_1456x1159.png)

A list of twelve is still twelve things to remember. It never told you which belong together.

Here the briefing doc lists the takeaways in a clean column, Iteration Loop, Fidelity, Psychological Alignment, Future Shift, each one bold and equal. It is tidy, but it is still a flat list, so you are left holding four separate items with nothing telling you how they connect.

**UI selections before you paste (you click these yourself):**  
Report → Create your own.

Use this prompt. Customize the `{topic}`.

```markup
Pull every separate tip and technique about {topic} from the sources. 
Then find the three to five patterns underneath them, and file every tip inside one pattern. 
Name each pattern in two or three words, and under it list the tips it holds as short lines. 
A tip belongs to one pattern only, the one that fits best. 
Do not leave a leftovers group, and do not pad to reach five if three is the real number.
```

For `{topic}` here I used **prompt engineering techniques**, since the source scatters at least a dozen of them across the conversation.

 <video controls=""><source src="https://www.learnwithmeai.com/api/v1/video/upload/1e7f3b06-08ed-4acd-8bea-9829d899408e/src?override_publication_id=1867502&amp;type=hls" type="application/x-mpegURL"> <source src="https://www.learnwithmeai.com/api/v1/video/upload/1e7f3b06-08ed-4acd-8bea-9829d899408e/src?override_publication_id=1867502&amp;type=mp4" type="video/mp4"></video>

Here, the same tips fold into three named patterns, with every technique filed under the one it belongs to and a summary table holding all three on one line each. The dozen loose items became three handles, and recalling one handle brings its whole group along.

### When to use which?

- **Briefing doc feature** → A plain rundown, when you want every tip listed in one place.
- **Custom prompt** → Real chunking, when the list is too long to hold, and you need it bound into a few patterns you can carry.

---

**Technique 4: Elaboration**: ask why until it connects

Knowing what something is gets you a definition you can lose. Knowing why it works gets you a reason that holds, because a reason hooks onto things you already understand, and a definition floats alone. Elaboration is the habit of asking why and how until the new idea is tied to old ones.

The next two prompts force that question. The first makes you explain why each thing works instead of just naming it. The second ties a new idea to something you already know, so it has somewhere to land.

---

## Prompt 6: Chase the why down to the reason

You learn that chain of thought makes the model perform better, and you write it down, and you feel like you understand it.

Then someone asks why it works, and you have nothing, because you learned the fact without the reason under it.

A fact with no reason under it is the first thing to go. The why is the hook the fact hangs on.

### The 1-click way: Quiz feature

Open your notebook, and in the Studio panel, click Quiz.

![NotebookLM Studio panel with the Quiz feature highlighted](https://substackcdn.com/image/fetch/$s_!m3V7!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9423e389-6d37-4ceb-a4d2-9153fb2b1d29_1456x759.png)

Studio → Quiz. It checks what you can name, not what you can explain.

NotebookLM writes questions from your source and scores your answers, so you find out what you remember.

![NotebookLM multiple choice quiz question about prompt engineering](https://substackcdn.com/image/fetch/$s_!4_Z2!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F913df137-6403-49bf-86db-1da03b2f2985_1456x1159.png)

A quiz mostly asks what, not why. You can pass without the reason.

But a quiz mostly asks what, not why. It checks whether you can name chain of thought, not whether you can explain what it does to the model, so you can pass every question and still not know why any of it works.

So you set up a chat that refuses the what and keeps pushing you for the why.

**UI selections before you paste (you click these yourself):**  
Open the Chat, click Configure.

![NotebookLM chat Configure notebook step for the elaboration prompt](https://substackcdn.com/image/fetch/$s_!qQQC!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F80547529-09d0-4b72-82bd-c2dd7fd8c99e_1456x755.webp)

Chat → Configure. Set up a chat that refuses the what and pushes for the why.

Use this prompt. Customize the `{topic}`.

```markup
I want to understand {topic} from the sources, not just name it. 
When I give you my understanding, do not confirm it and move on. 
Ask me why it works, then ask why again on my answer, and keep going until I reach a reason 
the sources actually support or I admit I do not know. 
If I give a surface answer, name it as surface and push once more. 
Stay on one idea until the reason underneath it is clear.
```

For `{topic}` here I used **why chain of thought improves model performance**, the exact claim the experts argue is more than just extra compute.

And next, I used this prompt to test it.

```markup
Chain of thought works because you make the model show its reasoning before the answer, 
and seeing the steps makes the output more reliable.
```

After pasting this, here is the answer.

![NotebookLM chat throwing the why back instead of confirming the answer](https://substackcdn.com/image/fetch/$s_!8lxh!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F07afff9d-ee41-49fe-98d7-ff4226ad4685_1456x800.png)

The model refused your answer. You cannot coast on the definition.

The model refused your answer and threw the why back at you, asking whether those steps are real reasoning or just computational room. You cannot coast on the definition anymore, because the next turn only opens once you produce a reason of your own.

### When to use which?

- **Quiz feature** → A fast check, when you want to know whether the facts stuck.
- **Custom prompt** → Real understanding, when you need the reason under the fact and not just the fact.

## Prompt 7: Tie the new thing to something you already own

You read that the model is like a temp agency worker, competent but with no context on your task. It clicks for a second. Then, a week later, the idea is gone, because it landed on nothing. You had no hook already in your head for it to grab.

A new idea with nothing to hold onto slides off. It stays only when it catches on something you already know.

### The 1-click way: Quiz feature

Open your notebook, and in the Studio panel, click Quiz.

![A quiz feature of NotebookLM](https://substackcdn.com/image/fetch/$s_!-cdv!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F95753ddc-60c0-4d7d-9a92-2c264d4b3797_1456x759.png)

A quiz checks whether you can repeat the idea back in the source's own terms.

A quiz checks whether you can repeat the idea back in the source’s own terms.

![](https://substackcdn.com/image/fetch/$s_!PDAJ!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F92042cbe-adc5-40ee-a94d-b4709c3ab82f_1456x1159.png)

A quiz checks whether you can repeat the idea back in the source's own terms.

But repeating it in the source’s terms is not the same as owning it, because the words are borrowed and the moment they fade, the idea has nowhere to live.

It tests recall of the phrasing, not whether the idea connects to anything you brought with you.

So you make the model tie each new idea to something already in your own life.

**UI selections before you paste (you click these yourself):**  
Open the Chat, click Configure.

![NotebookLM chat Configure step for the analogy prompt drawn from a field you know](https://substackcdn.com/image/fetch/$s_!IOiK!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe6d96b51-6568-422e-891e-e448f8af1a50_1456x755.png)

Chat → Configure. You tell it to tie each new idea to a field you already know.

Use this prompt. Customize the `{field}` you want your analogies drawn from.

```markup
For every idea I ask about from the sources, connect it to something from {field}, 
which is a world I already know well. Give me the plain version first, then one analogy 
from {field} that maps onto it part for part, and tell me where the analogy holds and 
where it breaks. If I offer my own analogy, check whether it actually fits or just sounds close. 
Use only the source for the idea itself, and keep the mapping honest.
```

For `{field}` here I used **briefing Claude Code on a task**, since I do it every day and the source is describing the same thing, a competent worker that knows its craft but nothing about my specific job.

And next, I used this prompt to test it.

```markup
Explain the temp agency worker idea from the source, and connect it to briefing Claude Code on a coding task.
```

After pasting this, here is the answer.

![otebookLM output mapping the temp agency worker idea onto briefing Claude Code part for part](https://substackcdn.com/image/fetch/$s_!mrwA!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F616a5a0c-e3dc-47e2-a4bf-45bb61fea78b_968x1304.png)

The idea landed on something you touch every day, so it stopped being a line from a source.

The idea landed on something you touch every day, spinning up Claude Code in a fresh repo, so it stopped being a line from a source and became a thing you already know. And the break it flagged, that a wrong human brief costs you cleanup while a wrong Claude Code brief costs you a `git checkout`, is the part that keeps you from stretching the analogy too far.

### When to use which?

- **Quiz feature** → A recall check, when you want to see if the phrasing stuck.
- **Custom prompt** → Real connection, when a new idea keeps sliding off and needs to hook onto something you already own.

---

**Technique 5: Desirable difficulty: make it harder on purpose**

Easy practice feels good and fades fast. The material you breeze through leaves nothing behind, because your brain only files what it had to work for. Adding friction on purpose, a delay, a missing hint, a harder question, slows you down now and makes the memory hold later.

This prompt builds that friction in. It takes the questions your source could ask you gently and makes them ask you the hard way instead.

---

## Prompt 8: Strip the hints and make yourself reach

You run through the easy questions and get them all right, and it feels like the material is yours. The version with a word bank, a multiple choice, a hint in the stem. Then the real test gives you a blank and no options, and the thing you breezed through last night will not come.

Easy questions test recognition, not memory. The hint you leaned on is the exact crutch the real test takes away.

### The 1-click way: Quiz feature

Open your notebook, and in the Studio panel, click Quiz.

![NotebookLM Studio panel with the Quiz feature highlighted to generate questions](https://substackcdn.com/image/fetch/$s_!gfJt!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F055e0b57-63fc-40d0-9ae3-2840d1e0d979_1456x759.png)

Studio → Quiz. NotebookLM writes questions from your source and checks your answers.

NotebookLM writes questions from your source and checks your answers.

![NotebookLM default multiple choice quiz where the phrasing half-carries you to the answer](https://substackcdn.com/image/fetch/$s_!oGWI!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F999a01cc-fe85-47ad-b1ea-7b29d6acf10a_1456x1159.png)

On its default setting it asks the gentle version, where recognizing the option feels like knowing it.

But on its default setting, it asks the gentle version, the kind where the phrasing half-carries you to the answer, and recognizing the right option feels like knowing it. It grades what you can spot, not what you can produce from an empty page.

So you tell it to pull the hints out and make every question start from nothing.

**UI selections before you paste (you click these yourself):**  
Quiz → Difficulty: Hard, Question Type: Short Answer.

Use this prompt. Customize the `{topic}`.

```markup
Write hard questions on {topic} from the sources. 
Ask for a reason or an application rather than a term, so each answer needs a full thought 
and not a single word. Pull the questions from the trickiest parts of the sources, 
the edge cases and the claims the experts argue about, not the easy definitions.
```

For `{topic}` here I used **prompt engineering techniques and why they work**, so the questions ask for reasons, not just names.

 <video controls=""><source src="https://www.learnwithmeai.com/api/v1/video/upload/41138f5c-7876-45e1-a452-8d6591f24486/src?override_publication_id=1867502&amp;type=hls" type="application/x-mpegURL"> <source src="https://www.learnwithmeai.com/api/v1/video/upload/41138f5c-7876-45e1-a452-8d6591f24486/src?override_publication_id=1867502&amp;type=mp4" type="video/mp4"></video>

Every question here asks for a reason or a call, not a word you can point at, so recognizing the right option no longer saves you. You have to pull the answer up cold, and that pull is slower and harder than a gentle quiz, which is exactly why it lasts.

### When to use which?

- **Quiz feature** → A gentle check, when you want a quick pass and do not mind the hints.
- **Custom prompt** → Real preparation, when you want the friction that makes it stick, because easy now means gone later.

---

**Technique 6: Generation: produce it before you see it**

The strongest memory comes from making your brain reach for an answer it does not have yet. The reach is what wires the answer in, and even a wrong guess leaves a hook the right answer can hang on later. This is the one thing a button cannot do for you, so both prompts here drop the 1-click feature.

The next two prompts force the reach. The first makes you guess before the source speaks. The second makes you say it so simply that any gap shows.

---

## Prompt 9: Guess before you read

You open the source and let it walk you through the answer, and it all makes sense while you read. Then you close the tab an hour later and almost none of it stays, because the answer never cost you anything, so your brain filed it as something it could always look up again.

Reading an answer is not the same as producing one. The answer you never reached for is the answer you forget first.

##### The 1-click way: none

There is no button for this, and that is the point. A feature can hand you the answer, but it cannot make you guess before you see it, and the guess is the part that wires the memory. So you set it up in the Chat, where you commit to an answer before the source opens its mouth.

**UI selections before you paste (you click these yourself):**  
Open the Chat, click Configure.

![NotebookLM chat Configure step for the guess-before-you-read prompt](https://substackcdn.com/image/fetch/$s_!xqA5!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F393dd258-8045-4e4b-adc1-400f49f5d321_1456x755.png)

Chat → Configure. There is no button for this. You set the model up to ask before it tells.

Use this prompt. Customize the `{topic}`.

```markup
Walk me through {topic} from the sources one idea at a time. 
Before you explain each idea, ask me a question about it and stop, and tell me to answer 
from my own head before I read on. Wait for my answer. 
Only then give the correct version and tell me where mine was right and where it was off. 
Move one idea at a time, and never explain an idea before I have guessed at it.
```

For `{topic}` here I used **the differences between prompting an enterprise system, a research task, and a chat**, since the source draws sharp lines between the three and I could test whether I actually held them.

And next, I used this prompt to test it.

```markup
Let's start. Ask me the first question.
```

Here is the answer.

![NotebookLM asking a question and stopping so you commit to an answer before seeing the source](https://substackcdn.com/image/fetch/$s_!Vih4!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F3b08f784-fe53-456a-9ec3-fdb67240130c_1456x745.png)

The model asked before it told, and stopped. That guess is the whole point.

The model asked before it told, and stopped, so you have to commit to a number and a reason before you ever see the source’s answer. That guess is the whole point, because the gap between what you say and what the source says is where the idea finally lands.

### When to use which?

- **Plain Chat** → A quick answer, when you just want to look something up in the source.
- **Custom prompt** → Real encoding, when you want the idea to stay instead of making sense for a minute and then leaving.

## Prompt 10: Say it simply enough that the gaps show

You read the chapter and understood every line, and you wrote clean notes. Then someone asks you to explain it to a person who knows nothing, and you freeze, because the words you had were the source’s words. Borrow the explanation and you never find the hole in your own.

Understanding a sentence as you read it is not the same as being able to build it from nothing. The simple version is where the gap shows.

##### The 1-click way: none

There is no button for this either. A feature can simplify the source for you, but the simplifying is the test, and if the model does it you learn nothing. So you set up the Chat to make you produce the simple version and then catch where it went vague.

**UI selections before you paste (you click these yourself):**  
Open the Chat, click Configure.

![NotebookLM chat Configure step for the explain-it-simply prompt](https://substackcdn.com/image/fetch/$s_!0-J_!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F40ad3370-aaf8-4c83-9196-9758a7f6328c_1456x755.png)

Chat → Configure. No button for this either. The simplifying is the test, so you produce it yourself.

Use this prompt. Customize the `{topic}`.

```markup
I am going to explain {topic} from the sources as if I were teaching a smart twelve-year-old 
who knows nothing about it. Let me write my explanation first, in my own words, 
with no jargon and no borrowed phrases from the source. 
Then check it against the sources and point at every place I went vague, hand-waved, 
or used a word a twelve-year-old would not follow. 
Name the one spot where my simple version hid a gap in my own understanding.
```

For `{topic}` here I used **why you should not lie to the model about who you are**, since the source argues it plainly, and it sounds obvious until you try to explain why.

And next, I used this prompt to test it.

```markup
Here is my explanation. You should just tell the model the truth about what you are doing, 
because the model already knows what things like evals are, so pretending you are a teacher 
making a quiz just gives it a worse version of the task you actually want.
```

Here is the output.

![NotebookLM catching the one word hidden behind a simple explanation of the source](https://substackcdn.com/image/fetch/$s_!y_fB!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff2643934-04ac-4a6a-86a0-fc695cb4ee3d_1652x830.png)

Your simple version sounded right until the model caught the word you were hiding behind.

Your simple version sounded right until the model caught the one word you were hiding behind, that lying gives a “worse” task when the source says it gives a different one. The spot where your plain explanation went fuzzy was the exact spot you had not understood, and now it is named instead of buried.

### When to use which?

- **Plain Chat** → A quick answer, when you just want the source to explain something to you.
- **Custom prompt** → Real understanding, when you need to produce the simple version yourself, and find the gap it exposes.

## First, thank you.

LearnAIWithMe grew from 5,000 to 16,000 subscribers in three months, but why the jump?

![Substack network effect chart showing subscriber sources for LearnAIWithMe over 90 days](https://substackcdn.com/image/fetch/$s_!5QXZ!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F1556419a-40ea-4873-b45b-4f81cd34288d_1456x804.png)

LearnAIWithMe grew from 5,000 to 16,000 subscribers in three months.

Last 3 months, I’ve been writing 3 posts each week, M-W-F, including actual builds, using AI, and this series, [build-it](https://www.learnwithmeai.com/t/build-it) like a lot by you.

We [built the Polymarket bot](https://www.learnwithmeai.com/p/claude-code-polymarket-bot), which does 2.1x in just 18 days, and copied [trades of millionaires](https://www.learnwithmeai.com/p/claude-trading-bot-hyperliquid) for better results, or **[r](https://www.learnwithmeai.com/p/reverse-engineer-startup-claude-code)** [everse-engineered a $60K MRR AI](https://www.learnwithmeai.com/p/reverse-engineer-startup-claude-code).

I shared everything in plain English, wrapped it as a Skill, script, or prompt so you can run it without too much work, but also gave you the information to build it from scratch.

And it paid off. LearnAIWithMe just hit #4 on Substack and is rising on the Technology list.

![Gencay's LearnAIWithMe Substack profile ranked number 4 rising in Technology](https://substackcdn.com/image/fetch/$s_!cU4W!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fced787f1-fd12-4e99-b237-252b09863118_1278x408.png)

This one doesn't belong to someone else's company. It belongs to LearnAIWithMe.

Over the course of my career, from engineering to AI, this is the achievement I am most proud of.

Because this one doesn’t belong to someone else’s company. It belongs to LearnAIWithMe.

No manager, client, or company can limit what I write, build, or share next; you do.

So stick with LearnAIWithMe.

Every week, my goal is to make it more valuable than the week before.

I’m building a place where people don’t just learn AI.

They actually build with it.

So, let’s build together!
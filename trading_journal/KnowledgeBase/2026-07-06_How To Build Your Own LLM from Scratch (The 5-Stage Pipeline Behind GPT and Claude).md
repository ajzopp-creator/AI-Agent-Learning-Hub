---
title: "How To Build Your Own LLM from Scratch (The 5-Stage Pipeline Behind GPT and Claude)"
source: "https://x.com/eng_khairallah1/status/2073334640123769289"
author:
  - "[[@eng_khairallah1]]"
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
![Image](https://pbs.twimg.com/media/HMX2sGLWEAAGntm?format=jpg&name=large)

Most people use ChatGPT and Claude every single day and have no idea how they were actually built.

Save this :)

A small group of people understand the exact pipeline that turns raw internet text into a model that can write, reason, and code. And understanding that pipeline changes how you use these tools forever, because you finally see what's happening under the hood instead of treating it as magic.

The difference between those two groups is not a math degree.

It is one clear mental model.

Here is the truth almost nobody explains simply: every frontier model, GPT, Claude, all of them, is built through the same five-stage pipeline. The companies differ in scale, data, and a thousand engineering details, but the shape of the process is the same everywhere. Learn the shape and you understand how all of them are made.

Let me set expectations honestly before we start. You are not going to train a model that rivals GPT or Claude from scratch on your laptop. Those models cost tens of millions of dollars in compute and require enormous engineering teams. That's not the goal here. The goal is to understand the pipeline so deeply that you could build a tiny working version yourself, reason about how the big ones behave, and stop being mystified by any of it. That understanding is worth far more than most people realize, and it's completely within reach.

Here are the five stages, in order, exactly as they happen.

## Stage 1: Data — The Foundation Everything Is Built On

Before there is a model, there is text. An enormous amount of it.

The first stage is gathering and preparing the data the model will learn from. For a frontier model this means a staggering quantity of text: a large fraction of the public internet, books, code repositories, and more. But raw text is messy, so most of the work in this stage is not collecting, it's cleaning.

The data gets filtered to remove junk, duplicated content is stripped out (the same paragraph appearing a thousand times would warp what the model learns), and low-quality or harmful material is filtered down. This cleaning matters more than people think. The old principle holds: garbage in, garbage out. A model trained on cleaner, higher-quality data learns better than one trained on more but messier data. Data quality is one of the most important and least glamorous levers in the entire field.

Then comes the step that surprises beginners: **tokenization.** The model can't read text directly. The text gets broken into tokens, which are chunks roughly the size of a word-part. The phrase "tokenization" might become three or four tokens. Every piece of training data gets converted into these tokens, and from that point on the model only ever sees numbers representing tokens, never letters. This is why models sometimes miscount the letters in a word: they never saw the letters, only the token.

The output of this stage is a massive, clean, tokenized dataset. Nothing has been learned yet. You've just prepared the raw material.

**What to Do to Learn This Stage**

- Learn what a tokenizer actually does by running text through one and watching it split into tokens
- Take a small text dataset and practice cleaning it: removing duplicates, filtering junk, normalizing format
- Understand why data quality beats data quantity by comparing what a small model learns from clean versus messy data
- Read about how the major labs describe their data filtering, and notice how much effort goes into it

## Stage 2: Pretraining — Where the Model Actually Learns Language

This is the stage that costs the millions, and it's where the model learns almost everything it knows.

Pretraining has a beautifully simple objective: predict the next token. The model is shown a sequence of tokens and asked to guess the next one. It guesses, the guess is compared to the actual next token, and the model's internal numbers (its parameters, often billions of them) are nudged to make a better guess next time. Then it does this again. And again. Across trillions of tokens.

That's the whole training objective. Predict the next token, over and over, on a colossal scale. And out of that absurdly simple goal, something remarkable emerges. To get good at predicting the next token across all of human text, the model is forced to learn grammar, facts, reasoning patterns, coding syntax, and the structure of arguments, because all of those help it predict better. Nobody explicitly taught it grammar. It learned grammar because grammar helps it guess the next word.

The result of pretraining is called a **base model.** It's a powerful engine of language, but it's raw. A base model doesn't know it's supposed to be a helpful assistant. Ask it a question and it might just continue your sentence, or generate a list of similar questions, because all it learned to do is continue text plausibly. It has vast knowledge and zero manners. It's an incredibly capable instrument that hasn't been told what job it has.

Understanding this stage is the single biggest unlock in this whole article. Once you understand that the core of these models is next-token prediction at massive scale, their fluency and their hallucinations both make perfect sense. They're built to continue plausibly, not to tell the truth. Truth is something the later stages and your own engineering have to add.

**What to Do to Learn This Stage**

- Internalize the next-token prediction objective until you can explain it to a friend in one sentence
- Train a tiny language model on a small dataset (there are well-known beginner tutorials for this) to feel the loop firsthand
- Understand the relationship between parameters, data, and compute, and why scaling all three improved models
- Notice how this stage explains both why models are fluent and why they confidently make things up

## Stage 3: Supervised Fine-Tuning — Teaching the Model to Be Useful

Now you take that brilliant, mannerless base model and teach it what job it has.

The base model knows language but doesn't know it's supposed to answer questions helpfully. Supervised fine-tuning, usually shortened to SFT, fixes that. You show the model thousands of examples of the behavior you want: a question paired with a good answer, an instruction paired with a correct response, a problem paired with a clear solution.

The model is trained on these examples the same way it was pretrained, predicting tokens, but now the data is curated demonstrations of exactly how a helpful assistant should respond. It learns the format of being useful: when given a question, produce a helpful answer rather than continuing the text or rambling.

The quality of these examples matters enormously, and they're often written or carefully curated by humans. This is far less data than pretraining, sometimes thousands or tens of thousands of examples rather than trillions of tokens, but it's high-quality, deliberate, and targeted. A relatively small amount of excellent demonstration data transforms a raw base model into something that behaves like an assistant.

After SFT, you have a model that's genuinely useful. It follows instructions, answers questions, and stays on task. For many purposes this is already a working assistant. But it's not yet as helpful, harmless, and refined as the models you actually use, and that's what the last two stages are for.

**What to Do to Learn This Stage**

- Understand the difference between a base model and a fine-tuned model by reading examples of how each responds
- Build or examine a small instruction dataset: question-and-answer pairs that demonstrate the behavior you want
- Try fine-tuning a small open model on a focused task and watch its behavior change
- Notice how much the quality of demonstration examples matters compared to their quantity

## Stage 4: Reward Modeling — Teaching a Model What "Good" Looks Like

This is the stage most explanations skip, and it's the clever heart of how modern models get so polished.

Here's the problem the labs faced. After SFT, a model gives good answers, but "good" is hard to define with examples alone. For most questions there isn't one correct answer; there are better and worse ones. How do you teach a model to prefer the better answer when you can't write a rule for it?

The solution is elegant. You have the model generate several different answers to the same prompt. Then humans look at those answers and rank them: this one is better than that one. You collect a large number of these human preference comparisons. And then, instead of using them directly, you train a second model, called a **reward model**, whose entire job is to look at any answer and predict how a human would rate it.

Think about what that accomplishes. You can't have humans rate every answer the main model ever produces; that would never scale. But you can train a reward model on a sample of human judgments, and now you have an automated stand-in for human preference that can score millions of answers. The reward model is the bridge between "what humans like" and "something a computer can optimize against."

The reward model never talks to users. It's a behind-the-scenes judge. But it's the key that unlocks the final stage, because it gives you a way to push the main model toward answers humans actually prefer, at a scale no human team could ever match.

**What to Do to Learn This Stage**

- Understand why ranking answers (this is better than that) is easier and more scalable than writing perfect answers
- Grasp the core idea: a reward model learns to imitate human judgment so it can score answers automatically
- Read about how preference data is collected through human comparisons
- See how this stage connects the messiness of human taste to something a training process can use

## Stage 5: Reinforcement Learning — Polishing the Model Into What You Use

The final stage takes everything built so far and refines the model into the helpful, careful assistant you actually interact with.

This stage is usually called RLHF, reinforcement learning from human feedback. Here's how the pieces fit together. You take your fine-tuned model from Stage 3 and the reward model from Stage 4. The fine-tuned model generates answers. The reward model scores them. And the fine-tuned model is nudged, through reinforcement learning, to produce answers that score higher. It's a loop: generate, score, improve, repeat.

Because the reward model can score endlessly, the main model can practice and improve far beyond what direct human examples could ever provide. Over many rounds, it learns to be more helpful, more coherent, better at following nuance, and better at declining things it shouldn't do. This is the stage that gives the models their polish, their good judgment, and a lot of their safety behavior.

A modern variation worth knowing: some of the human feedback can be replaced or supplemented with feedback generated according to a written set of principles, an approach sometimes called RLAIF or constitutional methods. The spirit is the same: instead of relying solely on humans to rate everything, you scale up the feedback that shapes the model's behavior, guided by clearly stated values.

After this stage, you have the finished product. A model that's fluent from pretraining, useful from fine-tuning, and refined and aligned from reinforcement learning. This is what you're talking to when you open ChatGPT or Claude. Five stages, each building on the last.

**What to Do to Learn This Stage**

- Understand the loop: the model generates, the reward model scores, the model improves toward higher scores
- Grasp why this lets the model practice far beyond the limits of direct human examples
- Read about the difference between learning from human feedback and learning from AI feedback guided by principles
- See how this final stage produces the helpfulness, judgment, and safety behavior you experience as a user

## The Whole Pipeline in One Breath

Let me put it all together so it locks in.

You gather and clean a mountain of text and turn it into tokens. You train a model to predict the next token across all of it, and out of that simple goal emerges a base model that understands language but has no manners. You fine-tune it on curated examples so it learns to behave like a helpful assistant. You collect human rankings of its answers and train a reward model to imitate human judgment. And finally you use that reward model to refine the assistant through reinforcement learning until it's polished, helpful, and aligned.

Data, pretraining, fine-tuning, reward modeling, reinforcement learning. Five stages. That's how every frontier model is made.

## The Honest Truth About Building Your Own LLM

You're not going to out-build the frontier labs from your bedroom, and that was never the point.

The point is understanding. Once this pipeline is clear in your head, you stop being a passive user of these tools and start being someone who reasons about them. You understand why they hallucinate (next-token prediction). You understand why prompting works (you're shaping what gets predicted). You understand why some models feel more aligned than others (the quality of stages four and five). You understand why your own data, in your own fine-tuning experiments, matters so much. This understanding is the foundation that the most capable AI builders are standing on.

And here's the genuinely empowering part: you can build a tiny working version of every one of these stages yourself, on a small scale, to learn. People train miniature models, fine-tune small open ones, and experiment with preference data all the time. You won't build Claude. But you can build something that teaches you exactly how Claude was built, and that knowledge compounds for the rest of your career in this field.

**Most people will use these models for years and never once understand how they were made.**

You just read the whole pipeline. You're already ahead of nearly everyone who types into these tools every day.

**The only question is whether you'll go build a small version yourself and turn understanding into something you can actually do.**

The five stages are right above you. Pick stage one, and start.

**If you found this useful, follow me** [@eng\_khairallah1](https://x.com/@eng_khairallah1) **for more AI content like this. I post breakdowns, courses, and tools every week.**

**hope this was useful for you, Khairallah** **❤️**
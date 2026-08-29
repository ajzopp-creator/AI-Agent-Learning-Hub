---
title: "I Read Every Page Of The xAI Docs. Here Are 12 Grok Bot Rules Nobody Talks About"
source: "https://x.com/heynavtoor/status/2091508628939542924"
author:
  - "[[@heynavtoor]]"
date: "2026-08-24"
published: 2026-08-23
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
  - "X (formerly Twitter)"
sector:
origin:
---
![Image](https://pbs.twimg.com/media/HQaHCAlbcAABwQd?format=jpg&name=large)

Everyone is using Grok Bot wrong. Not because they are dumb. Because the rules that matter most are buried in the docs.

Most creators write about Grok Bot features. Nobody writes about the rules. And the rules are what make the difference between a Bot team that works and a Bot team that breaks your account.

I spent the last 3 days reading every page of the official xAI Grok Bot docs. All 10 of them. Word for word.

Here is what I found. 12 rules that will change how you use Grok Bot forever. Every single one is a real quote from xAI's own docs. Every claim links back to the source page. This is not opinion. This is not a hot take. This is what the docs say.

Ready? Lets go.

# Why These Rules Matter

Grok Bot launched on August 11, 2026. It is 12 days old right now.

Millions of people signed up in the first week. Most of them read the marketing page and jumped in. They never touched the actual documentation.

That is a problem. Because Grok Bot is not like ChatGPT. It is not like Claude. It runs on a shared cloud computer. It has its own security model. It has hard limits on skills and routines. It has behaviors that will surprise you if you do not know them upfront.

Every rule below is one most users are missing. Every one is a real doc quote. Every one prevents a real problem.

**None of these are secrets.** Every rule is public. Every rule is in the docs right now. Nobody is talking about them because nobody reads the docs.

That is your edge.

# Phase 1: The Shared Computer Rules

This is the part most people get wrong. They think each Bot has its own machine, its own logins, its own connectors. It does not.

## Rule 1: Every Bot On Your Account Shares One Computer

Read this slow.

The xAI docs say it in plain words: "Every Bot on your account uses the same computer" [(xAI computer docs)](https://docs.x.ai/grok-bot/computer-and-apps).

Not each Bot has a computer. **One computer for all of them.**

That means:

- Browser cookies are shared
- Signed in sessions are shared
- Command line credentials are shared
- Files are visible to every Bot

If you save a client file with one Bot, every other Bot can read it. If you download something, every Bot can see it.

The docs say it directly: "Do not place a credential or file on it if another Bot on your account should not be able to use it."

Think about that. If you build a Bot for your business and another Bot for personal stuff, they share everything. There is no wall between them.

## Rule 2: Signing Into One Bot Signs In Every Bot

This is Rule 1 in action. And it is the rule that catches people off guard.

Direct quote: "Because the browser is shared, signing in for one Bot makes the session available to your other Bots" [(xAI computer docs)](https://docs.x.ai/grok-bot/computer-and-apps).

You sign into LinkedIn for your Sales Bot. Your Research Bot can now browse LinkedIn too. Your Content Bot can read LinkedIn posts. Your Ops Bot can access LinkedIn settings.

The upside: you only sign in once. Every Bot inherits the session. No need to sign in six times for six Bots.

The downside: there is no way to give one Bot access to a tool and block another Bot from using it. Every login is shared with every Bot on your account.

**The fix:** only sign into tools where you are comfortable with ALL your Bots having access. If a tool is sensitive like banking, payroll, or legal, use a connector with scoped permissions instead of a browser login. Or sign out when the work is done.

## Rule 3: Connectors Are Account Wide Too

Same pattern. Different surface.

Direct quote: "Installed connectors are account-wide. Their availability is not isolated to one Bot" [(xAI computer docs)](https://docs.x.ai/grok-bot/computer-and-apps).

You install the Gmail connector for your Inbox Manager. Every Bot on your account can now use Gmail. Your Research Bot. Your Sales Bot. Your Content Bot. All of them.

There is no per Bot connector. There is no way to say "only this Bot can use Gmail." The connector lives at the account level.

**The fix:** only install connectors where you want every Bot to have access. If you need one Bot to have it and others to stay away, write "Never use Gmail" into the other Bots' charters. The restriction is enforced by instructions, not by architecture.

That is a real trust boundary. Not a technical one.

# Phase 2: The Deletion Rules

This is where people lose data. Learn these before you delete anything.

## Rule 4: Deleting A Bot Does Not Remove Its Files

Read this one twice.

Direct quote from the security page: "Deleting a Bot does not remove shared-computer files or browser sessions" [(xAI approvals docs)](https://docs.x.ai/grok-bot/approvals-security-and-privacy).

So you delete a Bot. You think its data is gone. It is not. The files it saved to the shared workspace are still there. The browser sessions it signed into are still there. The credentials it stored are still there.

If you want to actually remove the data, you have to:

- Sign out of every service the Bot used
- Delete the files from the shared workspace manually
- Revoke connector permissions in each source service

The docs spell it out: "Sign out of a service when it should no longer be available. Remove sensitive temporary files after the work is complete. Delete a connector or revoke its authorization in the source service when access is no longer needed."

Deleting a Bot cleans up the Bot. It does not clean up the mess the Bot made.

## Rule 5: Deleting A Bot DOES Delete Its Routines

But wait. There is one thing deletion DOES take with it.

Direct quote: "Deleting a Bot also removes routines owned by that Bot" [(xAI skills docs)](https://docs.x.ai/grok-bot/skills-routines-and-automations).

So if your Sales Bot has 30 routines set up. Nightly lead research. Weekly reports. Daily inbox triage. All of them. And you delete the Bot.

Every routine dies with it.

The files stay. The browser sessions stay. But the automation you built goes to zero.

And there is no undo. The next rule explains why.

## Rule 6: Deleting A Routine Is Immediate And Has No Undo

Direct quote: "Deleting a routine is immediate and has no undo" (xAI skills docs).

No confirmation window. No trash bin. No 30 day recovery. It is gone the second you tap delete.

If you built a complicated multi step routine over a week and you tap the wrong button, you rebuild it from scratch.

**The fix:** before deleting anything, screenshot the routine setup. Save the schedule. Save the trigger. Save the steps. Treat every routine delete like a nuclear option.

# Phase 3: The Skills And Routines Rules

This is where most creators mess up. They think testing is safe. They think skills are automations. They think they can walk away. None of that is true.

## Rule 7: Teaching A Task Is Capped At 10 Minutes

You know that cool feature where you record yourself doing something and the Bot learns it? Great feature. But it has hard limits.

Direct quote: "Teaching records visible computer interaction for up to ten minutes" [(xAI skills docs)](https://docs.x.ai/grok-bot/skills-routines-and-automations).

Ten minutes. Not fifteen. Not "a while." Ten minutes.

If your workflow takes 12 minutes to demonstrate, the last 2 minutes never get recorded. The Bot only learns half the task.

And there is a second limit: "It does not record microphone audio."

So if you were planning to narrate the steps while you demonstrate them, the Bot cannot hear you. It only sees what you click, type, and select.

Design your workflows to fit under 10 minutes. Break longer workflows into multiple skills. Talk out loud all you want but write the important context into the Bot description instead.

## Rule 8: Test Runs Do REAL Work. They Are Not Simulations.

This is the rule that has probably caused more accidental damage than any other.

Direct quote: "A test run performs real work. It can navigate websites, change files, and call connected tools. Use safe inputs and keep write actions behind approval" [(xAI skills docs)](https://docs.x.ai/grok-bot/skills-routines-and-automations).

When you click Test on a routine, Grok Bot does not simulate the task. It actually does it.

If your routine sends emails, the test sends real emails. If your routine updates a spreadsheet, the test updates the real spreadsheet. If your routine posts to Slack, the test posts a real message in a real channel that real coworkers will see.

Most people assume test means safe. It does not. Test means "run it once right now so you can watch."

**The fix:** before hitting Test, set up approval boundaries on every external action. Make sure send, post, delete, and publish all require your OK before they fire. Then test. Watch the output. Approve or deny each step manually. Only enable the schedule after you are confident the routine does what you expect.

Never hit Test on a fresh routine without approvals in place. That is how test posts end up in the wrong channel.

## Rule 9: Grok Bot Pauses Your Routines If You Disappear

This one surprises people who set up routines and go on vacation.

Direct quote: "To control unattended usage, Grok Bot may ask whether to keep routines running after a long period away and pause them if there is no response. Review paused routines when you return" [(xAI skills docs)](https://docs.x.ai/grok-bot/skills-routines-and-automations).

You set up 5 routines. You go on a 2 week vacation. You expect them to run every day while you are gone.

After a few days, Grok Bot notices you have not opened the app. It sends you a check in. If you do not respond, it pauses your routines.

This is a safety feature. It prevents Bots from running unchecked for weeks without a human watching. But if you do not know it exists, you come back from vacation expecting 14 days of completed work and find everything paused.

**The fix:** if you are going to be away, check in with the app briefly every few days. A quick message to any Bot is enough to signal you are still active. Or plan to review paused routines when you return and re enable them manually.

Do not assume routines run forever without you. They do not.

## Rule 10: Only 20 Run Records Are Kept Per Routine

Direct quote: "The app keeps the 20 most recent run records for each routine" [(xAI skills docs)](https://docs.x.ai/grok-bot/skills-routines-and-automations).

Twenty. Only twenty.

So if you have a routine that runs every morning, you can only see the last 20 mornings. Anything before that is gone from the run history.

If your routine breaks and you want to figure out when it started breaking, you have 20 runs of data to work with. If it has been broken for more than 20 runs, the evidence is gone.

**The fix:** ask your Bot to log important results to a file in the shared workspace after every routine run. That way you have your own history that is not capped at 20.

# Phase 4: The Approvals And Stop Rules

These are the last two rules. And they are the ones that actually save your account when something goes wrong.

## Rule 11: Require Approval Always Beats Allow

This one is buried in the troubleshooting page. Most people never find it.

Direct quote: "Require rules take precedence over allow rules" [(xAI troubleshooting docs)](https://docs.x.ai/grok-bot/troubleshooting).

Grok Bot has an Auto review system where you can set two kinds of rules. Always Allow. And Require Approval.

If you set a Require Approval rule for "sending emails" and an Always Allow rule for "using Gmail," the Require Approval wins. The Bot can read Gmail freely but will stop and ask before sending any email.

This is huge. It means you can layer safety on top of convenience. Give a Bot broad access to a tool. Then lock down the dangerous actions with Require Approval. The Require rule always wins.

**The fix:** when in doubt, add a Require Approval rule. You can always remove it later once you trust the Bot. But if you start with Always Allow and something goes wrong, the next rule applies.

## Rule 12: A Stop Message Does Not Undo Completed Actions

This is the one that costs people the most.

Direct quote: "Send a direct 'Stop now' message when work should end immediately. This does not undo actions the Bot already completed" [(xAI chat docs)](https://docs.x.ai/grok-bot/chat-and-collaboration).

Read that again.

You watch your Bot start doing something wrong. You panic and send Stop. The Bot stops moving forward. Good.

But everything it already did? Still done. The email it sent. The record it updated. The purchase it made. All permanent.

**The fix:** never let a Bot take consequential actions without approval. The docs literally list this as a rule: "Keep consequential external actions behind approval."

Set up Require Approval rules (see Rule 11) before the Bot can send a message, change a record, or spend money. Then a Stop message actually saves you. Without approval rules, Stop only saves you from the next mistake.

Stop is a brake. It is not a rewind button.

# What Makes This Work

Let me be honest. None of these 12 rules are hidden.

They are all in the docs. Right now. Public. Free to read.

But nobody reads docs anymore. People watch tutorials. People read threads. People try things and hope for the best.

That is why 12 days after launch, most Grok Bot users:

- Think each Bot has its own logins (Rule 1 and 2)
- Think connectors are per Bot (Rule 3)
- Think deleting a Bot cleans up its data (Rule 4)
- Think Test runs are safe simulations (Rule 8)
- Think routines run forever without them (Rule 9)
- Think Stop actually undoes the mistake (Rule 12)

They are wrong on all of it. And they will figure it out the hard way.

You do not have to. You just read them.

# The 60 Second Checklist

Open Grok Bot right now. Check these six things.

**1.** Are you signed into any tool inside a Bot that other Bots on your account should not touch? (Rule 1 and 2)

**2.** Do all Bots with external actions have Require Approval rules on send, post, delete, and publish? (Rule 11 and 12)

**3.** About to hit Test on a new routine? Approvals set first? (Rule 8)

**4.** About to delete a Bot that owns routines you care about? Hide it instead. (Rule 5)

**5.** Going away for a week? Set a reminder to check in every few days. (Rule 9)

**6.** Do you have a connector installed that you only wanted one Bot to use? Add "Never use X" to the other Bots' charters. (Rule 3)

Six checks. Sixty seconds. Each one prevents a real problem.

hope this was useful.

Nav ❤️
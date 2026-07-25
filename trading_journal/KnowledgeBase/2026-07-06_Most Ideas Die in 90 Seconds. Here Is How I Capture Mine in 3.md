---
title: "Most Ideas Die in 90 Seconds. Here Is How I Capture Mine in 3."
source: "https://x.com/DamiDefi/status/2067906901266911515"
author:
  - "[[@DamiDefi]]"
date: "2026-07-06"
published: 2026-06-19
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
  - "X (formerly Twitter)"
sector:
origin:
---
![Image](https://pbs.twimg.com/media/HLIFJgsW0AAgxUn?format=jpg&name=large)

Ideas have a 90-second window.

Not a metaphor. A practical observation about how memory works under distraction. An idea that arrives while you are doing something else survives approximately 90 seconds before the surrounding context overwrites it. If you have not captured it by then, it is gone. Not suppressed. Gone. The next thought moved in.

Most capture systems lose ideas in the gap between the idea arriving and the system being ready to receive it.

You have to stop what you are doing. Open a note-taking app. Navigate to the right place. Decide how to categorise it. Type it. Put the app away. By step three, the idea is competing with whatever you opened the app to do, and by step five, you have been distracted by something else in the app and the original idea is sitting half-formed in a field you will not finish.

QuickAdd removes every step except one. You press a keyboard shortcut. A floating input box appears over whatever you are working on. You type the idea. You press enter. The idea is in your vault. The app you were working in is still open. Nothing was interrupted.

Three seconds. Tested repeatedly. Consistent.

Here is where the three seconds actually goes: pressing the shortcut is instant. The floating box appearing is instant. Typing a short idea, "custody is the real DeFi bottleneck" or similar, takes one to two seconds depending on length. Pressing enter is instant. The total is rarely more than three seconds for anything under fifteen words, which covers the vast majority of captures. Longer ideas take longer to type, obviously, but the system overhead, the part QuickAdd controls, stays at zero the entire time.

## What QuickAdd Actually Is

QuickAdd is a free community plugin for Obsidian. It has one job: reduce the friction between an idea arriving and that idea landing in the correct place in your vault.

It does this through three types of actions: captures, templates, and macros.

**Captures** are what this article is about: a keyboard shortcut that takes input and appends it somewhere predetermined. This is the daily-use mechanism.

**Templates** insert a pre-built note structure when you create a new note, useful for things like a standard format for protocol research notes or weekly review notes, but not relevant to fast capture.

**Macros** chain multiple QuickAdd actions or Obsidian commands together into one shortcut, useful for more advanced workflows like capture-then-tag-then-move, but unnecessary for the system in this article. Captures alone solve the speed problem.

If you explore QuickAdd's settings and see Template and Macro as options, that is what they are for. This article only needs Captures.

No navigation. No decision-making. No opening a folder and finding the right note. You defined all of that when you built the capture workflow. At capture time, the only task is typing the idea.

## The Four Capture Workflows I Run

I have four QuickAdd captures set up, each mapped to a different keyboard shortcut, each sending input to a different section of my daily note.

**General Capture**Hotkey: Cmd + Shift + C Destination: today's daily note, under the ## Captures heading Use: anything that does not fit the other three categories. A half-formed thought, an observation, a word that needs to be looked up later. Everything goes here first.

**Research Signal**Hotkey: Cmd + Shift + R Destination: today's daily note, under the ## Research heading Use: anything with research implications. A data point that challenges a thesis, a name I need to investigate, a source I want to find later.

**Content Idea**Hotkey: Cmd + Shift + I Destination: today's daily note, under the ## Ideas heading Use: angles, hooks, article concepts, post ideas. Anything I would want to find the next time I am looking for what to write about.

**Source / Link**Hotkey: Cmd + Shift + L Destination: 00-Inbox as a standalone note with today's date Use: URLs and links I want to return to. The format appends the URL plus a one-line note about why I saved it.

The shortcuts are on the left side of the keyboard. Two fingers, no reaching. The whole interaction is fast enough that I run it without breaking typing flow on whatever I was doing before.

One check before committing to these specific shortcuts: confirm they are not already bound to something else. Cmd+Shift+C, R, I, and L can conflict with browser shortcuts, OS-level shortcuts, or other Obsidian plugins already installed. On Mac, check System Settings → Keyboard → Keyboard Shortcuts. In Obsidian, check Settings → Hotkeys and search each combination before assigning it. A silent conflict, where the shortcut appears to do nothing, is the most common reason this setup feels broken on the first attempt. If any of the four are taken, swap in Cmd+Shift+1 through 4, which are rarely bound to anything.

## How to Set This Up

**Install QuickAdd**

> Open Obsidian Go to Settings → Community Plugins → Browse Search for QuickAdd Install and enable it QuickAdd now appears in your left sidebar as a lightning bolt icon

**Create your first capture**

> Go to Settings → QuickAdd Click the + button to add a new choice Select Capture as the type Name it (example: General Capture) Click the gear icon next to it to configure

**Configure the capture**

> File to append to: enter the path to your daily note template Example: Daily Notes/{{DATE:YYYY-MM-DD}}.md This tells QuickAdd to always append to today's daily noteIn the Capture Format field, enter how the captured text should appear: - {{VALUE}} appends exactly what you typed - To add a timestamp: \[{{DATE:HH:mm}}\] {{VALUE}} - To add a checkbox: - \[ \] {{VALUE}}Enable Append to bottom of file if you want captures added at the end Enable Prepend if you want them at the top

**Advanced: splitting input into multiple fields**

If you want a single capture to ask for more than one piece of information, for example an idea plus a one-word category, QuickAdd supports multi-value input using a comma as the separator inside the box, referenced as {{VALUE:1}} and {{VALUE:2}} in the Capture Format.

> Example Capture Format: \[{{DATE:HH:mm}}\] {{VALUE:1}} — Category: {{VALUE:2}} Typing into the box: "custody is the bottleneck, defi" produces: \[09:14\] custody is the bottleneck — Category: defi

This is optional. The four single-value captures in this article cover most use cases without it. Add multi-value fields only if you find yourself wanting to tag captures at the moment of creation rather than during processing.

**Assign a hotkey**

> Go to Settings → Hotkeys Search for QuickAdd: Run General Capture Click the + button and press your chosen shortcut Recommended: Cmd + Shift + C on Mac, Ctrl + Shift + C on Windows

**Repeat for each capture workflow**

Build the Research Signal, Content Idea, and Source Link captures the same way. The only things that change between them are the name, the destination file or heading, and the hotkey.

**Create the headings in your daily note template**

For the captures to land in the right section, your daily note template needs the matching headings:

> \## Captures (QuickAdd appends here for General Capture)## Research (QuickAdd appends here for Research Signal)## Ideas (QuickAdd appends here for Content Idea)

QuickAdd's heading insertion feature finds the heading by name and appends below it. If the heading does not exist in today's note, it creates it.

**The most common setup failure: the daily note does not exist yet.**

QuickAdd can append to a file. It cannot create a daily note from scratch with your template applied unless you tell it to. If you open Obsidian in the morning before your daily note plugin has generated today's note, the first capture of the day will either fail silently or create a bare file without your headings.

The fix: in the same File to append to field, QuickAdd supports the same {{DATE}} syntax your daily notes plugin uses, and has a setting called "Create file if it doesn't exist" inside the capture configuration. Enable this. If you also want the new file to start from your daily note template rather than a blank file, set the "Create file from template" option to point at your daily note template file. With both enabled, the first capture of the day generates a fully formatted daily note automatically rather than requiring you to open the note manually first.

**On related captures landing in different sections:**

If you fire General Capture and then Research Signal for two thoughts that are actually connected, they land in different headings of the same daily note with no link between them. This is fine. Do not try to solve it at capture time.

The connection between related captures is exactly the kind of thing the synthesis brief is built to find later. Trying to manually link captures as you make them reintroduces the evaluation pause that the whole point of QuickAdd is designed to eliminate. Capture fast, let the system find the relationships overnight.

## The Mobile Problem and How to Solve It

QuickAdd works on desktop. On mobile, the keyboard shortcut does not fire the same way and the interaction is slower.

The mobile capture solution is a Telegram bot connected to an N8N workflow. Any message sent to the bot lands in 00-Inbox within 30 seconds as a markdown note. The friction on mobile is: open Telegram, send message, done. Roughly the same as the desktop QuickAdd flow.

The full Telegram bot build is in the N8N automation article in this series. Build the desktop QuickAdd workflow first. Add the Telegram bot second. Together they cover every capture scenario: at the desk, away from it, walking, in a meeting, reading on a phone.

## One Habit That Makes the System Work

QuickAdd removes the friction. It does not remove the discipline of actually using it.

The habit that makes the difference: when an idea arrives, capture it before evaluating it.

The instinct is to pause and decide whether the idea is worth capturing. That pause is where ideas die. The evaluation takes longer than 90 seconds. By the time you decide it is worth saving, it has already degraded.

The habit is: capture first, evaluate never. If the idea was not worth having, the inbox processor will flag it for deletion tonight. If it was worth having, it is already in the vault.

Thirty days of this habit changes the contents of your vault more than any architectural change to the system. The synthesis brief produces better outputs when the vault contains a month of everything you thought, not just the ideas you decided were good enough to save.

## What Changed After Building This

The first change was volume. More ideas landed in the vault per day than in any previous week. Not because I was having more ideas. Because I was losing fewer of them.

The second change was quality distribution. The ideas I would have evaluated as "not worth saving" and lost turned out to contain the seeds of some of the best research threads I ran that month. Three of the captures I almost did not make became the parent notes for offspring ideas the synthesis brief surfaced weeks later.

The third change was invisible until the system had been running for six weeks. The daily brief started producing connections I had not seen coming because the vault contained enough material from different contexts and different moments. Ideas from walks connecting to ideas from reading sessions connecting to ideas from half-awake mornings. The cross-context collisions are only possible if the captures from all three contexts are actually in the vault.

QuickAdd is not a productivity tool. It is the mechanism that determines whether the rest of the system has anything to work with.

Three seconds is the window. The keyboard shortcut is what fits inside it.

Follow [@damidefi](https://x.com/@damidefi) on X for daily Claude AI tools, crypto analysis, and the full journey to 100K. Bookmark this. Share it with one person whose best ideas are living somewhere between their brain and a note-taking app they never opened.
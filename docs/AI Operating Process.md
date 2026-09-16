[00:00:00] So Anthropic engineers just said that they stopped building agents and they started building something completely different. So if you're still focused on building agents, you're probably wasting hours on something that'll never work the way that you actually want it to.
[00:00:13] But if you focus on what these engineers are actually building, you'll have a system that improves on its own. So in this video, I'm going to show you what they said to build instead and the four things that actually make it work so that you can start getting the same quality results that Anthropic engineers are getting.
[00:00:21] All right, so Anthropic isn't saying that agents are dead. Barry Zhang and Mahesh Murag, the two people who created agent skills at Anthropic, said that they basically stopped rebuilding a separate agent for every single job because the agent underneath had become way more general-purpose than they expected.
[00:00:37] The easiest way to understand this is to look at your phone. Your phone has a processor, an operating system, and then all the apps that you actually use every day. A few massive companies build the processor and the operating system; you probably aren't changing either one of those things, but you can choose the apps, and each app gives that same phone a very specific capability.
[00:00:52] The whole AI stack is starting to look pretty similar to that:
- The model is kind of like the processor.
- The agent runtime is like the operating system.
- Skills are the apps.
[00:01:02] Claude Code can already read files, write code, call tools, and work through a task. You don't need to necessarily rebuild all of that every time you want help creating a presentation, researching a company, or writing a LinkedIn post. You give the same general-purpose agent a skill that contains the process, the context, the scripts, and the examples for that specific job.

Four practical ways to make those skills work better:

1. Stop making Claude solve the same technical problem over and over [00:01:26]
The team kept watching Claude write basically the exact same Python script every time it needed to apply styling to a slide deck. It would spend tons of tokens recreating code that had already been written, and the results weren't consistent. So, they had Claude save that script inside the skill as a "tool for its future self." The next time it styles a presentation, it runs the proven version. Follow DRY (Don't Repeat Yourself). When Claude writes a working script, save it inside the skill's script folder, update skill.md so future runs call that file, and verify the output.

2. Progressive disclosure [00:03:02]
A mechanic doesn't dump hundreds of tools onto the bench before changing a tire. Skills work similarly: when Claude starts, it doesn't read full instructions, examples, and scripts from every skill (which wastes tokens and causes context rot). It starts with the name and description in the YAML front matter. Only when a prompt matches does it read the full skill.md file and supporting scripts. Descriptions must be clear and distinct so skills don't overlap or compete.

3. Turn corrections into durable instructions [00:04:54]
Every time you correct Claude and close the chat, that lesson is usually lost. If all you say is "fix it," the fix happens but the underlying process stays broken. When Claude fails, have it backtrack, identify why it failed, and update the skill.md instructions, add reference files, or introduce an explicit rule to prevent recurring mistakes. Skills become a living, durable record of procedural knowledge.

4. Built-in verification before returning final output [00:06:43]
Don't let a skill return its first attempt as the final output. Bake verification passes into the skill itself:
- Slide decks: Render slides as images, inspect screenshots, and fix layout/cropping issues.
- Research reports: Cross-reference primary sources and verify claims.
- Creative/subjective work: Have specialized sub-agent personas critique from different angles (e.g., beginner clarity, buyer skepticism).
Claude defines acceptance criteria, drafts, inspects against external evidence, fixes issues, and only hands over the finished, checked work.
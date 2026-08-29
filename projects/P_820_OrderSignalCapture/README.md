# P_820 Order Signal Capture

Thin utility project. No Python code by design -- the entire mechanism is
Claude writing structured signal-source data directly to the vault via
`write_to_vault("P820", {...})` at the moment Tony dictates a trade in
chat. No scanner, no evaluation logic, no CLI.

**Full operating rules, field list, and P_115 routing table:**
`<Hub>\.claude\skills\p820-project-context\SKILL.md`

**Purpose:** captures the signal source for trades that never touch a
Hub-built scanner (SNT, OIL/P_116, WSZ/P_117, Eddie Z/P_118) -- highest
priority in P_020's resolver chain (P_820 > ThinkLog > Tracker > default).

**Created:** 2026-08-16, P_020 session.

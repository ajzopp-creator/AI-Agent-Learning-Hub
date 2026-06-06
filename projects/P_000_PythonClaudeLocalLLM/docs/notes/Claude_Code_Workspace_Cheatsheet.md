# Claude Code Workspace — Cheatsheet
## Reference Document Converted From Image

---

| Field | Value |
|---|---|
| **Document ID** | CLAUDE-CODE-CHEAT-001 |
| **Source** | Image asset converted to markdown |
| **Created** | April 30, 2026 |
| **Owner** | Tony |
| **Status** | Reference — Read-Only |
| **Applies To** | Claude Code workspace planning |

---

## Section 1 — Project Overview

A complete Claude Code workspace combining Skills, Hooks, MCP Servers, Subagents, and Plugins for production AI-assisted development.

---

## Section 2 — Reference Folder Tree

```
my_project/
├── CLAUDE.md
├── .claude/
│   ├── settings.json
│   ├── settings.local.json
│   ├── commands/
│   │   ├── review.md
│   │   ├── deploy.md
│   │   ├── test-all.md
│   │   └── bootstrap.md
│   ├── skills/
│   │   ├── code-review/
│   │   │   ├── SKILL.md
│   │   │   ├── scripts/
│   │   │   ├── references/
│   │   │   └── assets/
│   │   ├── text-writer/
│   │   │   └── SKILL.md
│   │   ├── security-audit/
│   │   │   └── SKILL.md
│   │   └── refactor/
│   │       └── SKILL.md
│   ├── agents/
│   │   ├── code-reviewer.yml
│   │   ├── test-writer.yml
│   │   ├── security-auditor.yml
│   │   └── ops-sre.yml
│   └── plugins/
│       ├── manifest.json
│       └── my-plugin/
├── .mcp.json
├── src/
│   ├── components/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   └── shared/
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── database.ts
│   ├── utils/
│   │   ├── logger.ts
│   │   ├── validators.ts
│   │   └── helpers.ts
│   ├── types/
│   │   └── index.ts
│   └── index.ts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   └── onboarding.md
├── scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   └── seed-db.sh
├── package.json
├── tsconfig.json
├── .env.example
├── .gitignore
├── Dockerfile
└── README.md
```

---

## Section 3 — Key Components

| Component | Purpose |
|---|---|
| `CLAUDE.md` | Project memory |
| `.claude/` | Config and extensions |
| `commands/` | Slash commands |
| `skills/` | Auto-activated skills |
| `.mcp.json` | MCP server config |
| `agents/` | Subagent definitions |

---

## Section 4 — CLAUDE.md Essentials

The CLAUDE.md file is the project memory loaded by Claude Code on every session. It should cover:

1. Project conventions and style guide
2. Tech stack and architecture overview
3. Testing requirements and patterns
4. Git workflow and branch strategy
5. Security and compliance rules
6. File naming and folder conventions
7. Review checklist before commits

---

## Section 5 — Extension Types

| Extension | Behavior |
|---|---|
| **Skills** | Auto-activate on task match |
| **Hooks** | Lifecycle event scripts |
| **MCP** | External tool connections |
| **Subagents** | Isolated parallel work |
| **Agent Teams** | Multi-agent coordination |
| **Plugins** | Bundled distributable setups |

---

## Section 6 — Hook Events

| Event | Purpose |
|---|---|
| `PreToolUse` | Block before execution |
| `PostToolUse` | Auto-lint after writes |
| `SessionStart` | Load context on launch |
| `SessionEnd` | Save session summaries |
| `PreCommit` | Secret detection |
| `Notification` | Slack / webhook alerts |

---

## Section 7 — Skill Structure

| Folder / File | Purpose |
|---|---|
| `SKILL.md` | Instructions and metadata |
| `scripts/` | Executable automation |
| `references/` | Docs loaded on demand |
| `assets/` | Templates and static files |

---

## Section 8 — Popular MCP Servers

| Server | Function |
|---|---|
| GitHub | PRs, issues, repos |
| JIRA / Linear | Ticket workflows |
| Slack | Notifications and search |
| PostgreSQL | Direct queries |
| Playwright | Browser automation |
| Filesystem | Scoped file access |

---

## Section 9 — Getting Started (6 Steps)

1. `npm i -g @anthropic-ai/claude-code`
2. `cd` into your project and run `claude`
3. Create `CLAUDE.md` with conventions
4. Add slash commands in `.claude/commands/`
5. Configure MCP in `.mcp.json`
6. Add skills as workflows grow

---

## Section 10 — Context Management

| Context Usage | Action |
|---|---|
| 0–60% | Work freely |
| 50–70% | Monitor usage |
| 70–80% | Run `/compact` |
| 80%+ | `/clear` mandatory |

---

## Section 11 — Best Practices for Claude Code

- **Iterative Development** — Start small, test frequently
- **Clear Skill Documentation** — Describe skill purpose and usage
- **Modular Skill Design** — Break down complex tasks
- **Secure Secret Handling** — Use environment variables, not code
- **Regular Testing and Auditing** — Ensure skills remain reliable

---

## Section 12 — settings.json Structure

```json
{
  "permissions": {
    "allow": ["..."],
    "deny": ["..."]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "check-safety.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "npm run lint"
          }
        ]
      }
    ]
  },
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50"
  }
}
```

---

## Section 13 — .mcp.json Structure

```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-postgres"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

---

## Section 14 — CLAUDE.md Template

```markdown
# Project: My App

## Tech Stack
- Next.js 14, TypeScript, Tailwind
- Supabase for auth and database
- Prisma ORM, tRPC API layer

## Conventions
- Always write tests before code
- Use conventional commits
- Never commit directly to main
- Run lint and typecheck before PR

## Architecture
- src/components — React components
- src/services — Business logic
- src/utils — Shared helpers

## Security
- No secrets in code or logs
- Validate all user inputs
- Use parameterized queries only
```

---

*Source: image asset converted to markdown April 30, 2026.*
*OCR artifacts in original image (examples: "stale" → "stdio", "Tallwind" → "Tailwind", "wtila" → "utils", "Subegents" → "Subagents", "shoops-sre" → "ops-sre", "bockerfile" → "Dockerfile") have been corrected.*
*This is a reference document — not project-specific guidance. See `Claude_Environment_Gap_Analysis_V1.md` for application to the AI-Agent-Learning-Hub.*

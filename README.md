# job-search

Automated job search agent for remote backend/data/API engineering roles in Spain.

## Overview

This project uses [opencode](https://opencode.ai) with AI agent workflows to proactively search, evaluate, and track LinkedIn job listings. It runs as a CLI-driven assistant that follows strict filtering criteria.

## Features

- **Proactive daily search** — searches LinkedIn for new remote backend/data/API jobs in Spain each session
- **Auto-evaluation** — scores listings against CV (`cv/cv.png`) using the `job-matcher` skill
- **Strict filtering** — remote-only, product companies (no consultancies), full-time, posted within last week
- **Persistent tracking** — all evaluations saved to `data/jobs.csv`
- **Engram memory** — remembers past decisions, rejected companies, and application status across sessions

## Configuration

- `AGENTS.md` — agent instructions and workflow rules
- `opencode.json` — opencode config (Composio MCP integration)
- `.opencode/skills/` — custom skills (`linkedin-search`, `job-matcher`, `store-job`)
- `data/jobs.csv` — evaluation results log (48 entries as of 2026-07-06)

## Skills

| Skill | Description |
|---|---|
| `linkedin-search` | Searches LinkedIn via Composio MCP tools |
| `job-matcher` | Evaluates job fit against CV and filters |
| `store-job` | Persists evaluation summaries to CSV |

## Usage

```bash
# Start a session
opencode
```

Then ask the agent to search for jobs or provide a specific LinkedIn URL for evaluation.

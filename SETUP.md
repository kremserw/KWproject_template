# Project Setup Guide

This document explains how to set up this project on a new machine so that Claude Code
works identically to the original environment. (For configuring the project's *purpose* —
what it's about — run `/setup-project` once inside Claude Code; see README.md.)

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Claude Code** | recent | CLI agent (installed via `npm install -g @anthropic-ai/claude-code`) |
| **Anthropic subscription** | Max plan recommended | For a large-context model (1M window) |
| **Node.js** | v22.x (via nvm recommended) | Runtime for Claude Code + Firecrawl CLI |
| **Python 3** | ≥ 3.11 | Used by hook scripts for JSON parsing |
| **npm** | ≥ 10.x | Package manager (comes with Node.js) |
| **Git** | any recent | Version control |
| **GitHub CLI (`gh`)** | any recent | Optional, for PR/issue workflows |

---

## Step 1: Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Authenticate:
```bash
claude auth login
```

---

## Step 2: Install Firecrawl CLI

This project uses Firecrawl for all web research (search, scrape, crawl).

```bash
npm install -g firecrawl-cli
```

You need a Firecrawl API key. Get one at https://firecrawl.dev and set it:
```bash
export FIRECRAWL_API_KEY="your-key-here"
```

Add the export to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) so it persists.

---

## Step 3: Install Claude Code Plugins

These plugins provide skills used throughout the project. Install them from inside Claude Code:

```
/plugin add anthropic-agent-skills/document-skills
/plugin add claude-plugins-official/playwright
/plugin add claude-plugins-official/context7
/plugin add claude-plugins-official/firecrawl
```

(Add any others your workflow relies on, e.g. a planning/orchestration marketplace plugin.)

---

## Step 4: Configure Global Settings

Edit `~/.claude/settings.json` to enable the plugins and set the model:

```json
{
  "enabledPlugins": {
    "document-skills@anthropic-agent-skills": true,
    "playwright@claude-plugins-official": true,
    "context7@claude-plugins-official": true,
    "firecrawl@claude-plugins-official": true
  },
  "effortLevel": "high",
  "model": "<your preferred large-context model>"
}
```

---

## Step 5: Local Project Settings

The repo includes a tracked **`.claude/settings.json`** that wires all four hooks (`PreToolUse` for
the two file-protection hooks, `SessionStart` for the inbox converter, `SubagentStop` for the
inbox-cleared check). Commands resolve through `$CLAUDE_PROJECT_DIR`, so they work regardless of
where the repo is cloned. If a hook doesn't trigger, run `chmod +x .claude/hooks/*.sh`.

**The hooks only apply inside a Claude Code session started in this directory.** An assistant that
reads the repo from some other working directory never loads `.claude/` — run project work in the
repo, not next to it.

Anything machine-specific — a permission allowlist, extra entries such as `Bash(pdftoppm:*)` for PDF
rendering — belongs in an untracked `.claude/settings.local.json` of your own, which Claude Code
merges on top of the tracked file.

### Optional: `md-convert` for automatic inbox conversion

`convert-inboxes.sh` turns each new PDF / DOCX / PPTX / XLSX / HTML / EPUB file in `inbox/` into a
Markdown file beside it at session start. It needs a `md-convert` command on `PATH` (or the path in
the `MDCONVERT` environment variable) that takes a file and writes `<name>.md` next to it — typically
[MarkItDown](https://github.com/microsoft/markitdown) plus an OCR fallback (`ocrmypdf`, `tesseract`)
for scanned PDFs.

**This dependency is optional.** Without it the hook exits silently and you convert documents by hand
as before; nothing else in the project changes.

---

## Step 6: Configure the Project's Purpose (first run)

The first time you start Claude Code in a fresh copy of this template, a `.template-uninstantiated`
sentinel file is present. Run **`/setup-project`** (or just `/session-start`, which detects the sentinel
and routes you in). The interview asks for the project name, goal, type, outputs, knowledge domains,
collaborators, git remote, output language, and dashboard trajectories — then fills in every config
file and tailors the folder structure. After that, the project is yours; `/session-start` runs the
normal routine from then on.

---

## What's Already in the Repo

These components are tracked in git and work immediately after cloning.

### Agents (`.claude/agents/`)
| Agent | Purpose |
|-------|---------|
| `inbox-processor` | Ingests new files from `inbox/`, files to `knowledge/`, updates summaries |
| `knowledge-linter` | Health check: 10 criteria across all knowledge files |
| `report-reviewer` | Critiques the main output against quality criteria |
| `fact-checker` | Adversarial, read-only verification of cited claims |
| `project-initializer` | One-time bootstrap writer (used only by `/setup-project`) |

### Hooks (`.claude/hooks/`)
| Hook | Event | Purpose |
|------|-------|---------|
| `protect-inbox.sh` | `PreToolUse` | Blocks edits to `inbox/` originals (must move to `processed/` first) |
| `protect-archive.sh` | `PreToolUse` | Blocks edits to `outputs/reports/*/archive/` (archived outputs are immutable) |
| `convert-inboxes.sh` | `SessionStart` | Converts new inbox documents to Markdown beside the original (optional dependency, Step 5) |
| `verify-inbox-cleared.sh` | `SubagentStop` | Checks `inbox/` root is clear after an `inbox-processor` run |

### Skills (`.claude/skills/`)
| Skill | Trigger | Purpose |
|-------|---------|---------|
| `/setup-project` | First run | Configures the project's purpose; fills in config files |
| `/session-start` | Start of every session | Detects fresh template; else syncs git, reads INDEX, checks inbox |
| `/session-wrap` | End of every session | Updates logs + INDEX + ARTIFACTS + OPEN-QUESTIONS; files knowledge candidates |
| `/lint` | Periodically or on demand | Runs the knowledge base health check |
| `/file-back` | "file that back", "keep that" | Persists a finding into `knowledge/` with tagging |
| `/new-unit` | When adding a unit of work | Scaffolds a `{{UNIT_NOUN}}` knowledge + report structure |

### Project Instructions (`CLAUDE.md`)
The main instruction file. Defines the full workflow (Research → Plan → Write → Review),
folder structure, agent roles, file naming conventions, and session protocol. Claude
reads this automatically on every session start.

---

## Workflow Quick Start

Once set up, a typical session:

1. `cd` into the project directory
2. Run `claude` (or open in Claude Code desktop/IDE)
3. Claude automatically reads `CLAUDE.md` → `INDEX.md` → checks `inbox/`
4. Give your task — Claude follows the defined workflow
5. End with `/session-wrap` to update logs and project files

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Firecrawl commands fail | Check `FIRECRAWL_API_KEY` is set in your environment |
| Hooks don't trigger | Verify `.claude/settings.json` exists and hook paths resolve — and that the session's working directory IS this repo |
| Inbox files aren't converted to Markdown | `md-convert` is not on `PATH`; the hook is a deliberate no-op without it (Step 5) |
| Playwright browser fails | Run `npx playwright install chromium` for browser binaries |
| Plugins not loading | Restart Claude Code after plugin installation |
| "Permission denied" on hooks | Run `chmod +x .claude/hooks/*.sh` |

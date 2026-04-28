# imprint

A Claude Code plugin that trains a behavioral profile from your session history and injects it into all sessions.

## What it does

Imprint scans your Claude Code session transcripts, extracts patterns in how you work, communicate, and set quality expectations, then synthesizes a profile that every future Claude session will internalize.

## Installation

```
/plugin install n33kos/imprint
```

## Usage

### Train your profile

```
/imprint:train
```

This scans your session history in `~/.claude/projects/`, runs multi-pass LLM synthesis, and writes a profile to `~/.claude/.imprint`.

### How it works

Once a profile exists at `~/.claude/.imprint`, the plugin's `SessionStart` hook automatically injects the profile contents into every Claude session as additional context. No manual configuration needed — the hook fires on session start, resume, clear, and compact.

The hook is configured in `hooks/hooks.json` and the handler at `hooks-handlers/session-start.sh` reads `~/.claude/.imprint` and emits its contents via `hookSpecificOutput.additionalContext` — the supported mechanism for plugins to add persistent context to a session.

### Profile location

- **Profile**: `~/.claude/.imprint`
- The profile persists across plugin updates since it lives outside the plugin directory
- You can manually edit the profile to correct or refine it

## Profile sections

- **Communication Style** — Brevity, formality, voice usage, delegation patterns
- **Quality Standards** — Testing, type safety, accessibility, visual verification priorities
- **Review Instincts** — Code review approach, tone, conventional comments usage
- **Work Patterns** — Commit style, PR preferences, tool usage
- **Domain Expertise** — Areas of deep knowledge vs learning areas
- **Invariants** — Hard rules that are always enforced
- **Delegation Style** — Autonomy level, verification expectations

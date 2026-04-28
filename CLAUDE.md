# CLAUDE.md — Imprint plugin developer notes

This file is **developer documentation** for the imprint plugin source. It is **not** auto-injected into user sessions — Claude Code does not load plugin-level CLAUDE.md files into runtime context.

## How profile injection actually works

Profile loading is implemented as a `SessionStart` hook:

```
hooks/hooks.json                 # Hook config — fires on every session start
hooks-handlers/session-start.sh  # Reads ~/.claude/.imprint, emits JSON
```

The handler emits `hookSpecificOutput.additionalContext` containing the profile, which Claude Code then injects into the session as factual context. This is the only supported mechanism for a plugin to inject persistent instructions into a session.

## Why not CLAUDE.md?

Plugin-level CLAUDE.md files are conventionally used as developer documentation (see the slack, devin, notion-mcp plugins). They are not part of the runtime instruction surface. Earlier versions of imprint relied on this file to bootstrap profile loading, but that mechanism does not exist — the plugin was inert until v1.2.0 introduced the SessionStart hook.

## Layout

```
.claude-plugin/plugin.json   # Plugin manifest
hooks/hooks.json             # SessionStart hook registration
hooks-handlers/              # Hook scripts (run as ${CLAUDE_PLUGIN_ROOT}/hooks-handlers/...)
skills/train/SKILL.md        # /imprint:train skill
scripts/                     # Training pipeline (extract → synthesize → install)
templates/                   # Synthesis prompt template
```

## Profile location

The trained profile lives at `~/.claude/.imprint` — outside the plugin install dir so it survives plugin updates.

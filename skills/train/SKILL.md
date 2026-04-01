---
name: imprint:train
description: Train a behavioral profile from your Claude session history
---

# Train Behavioral Profile

Scan your Claude session history, extract behavioral patterns, and generate a profile at `~/.claude/.imprint`.

## Instructions

Before running anything, walk the user through the following configuration questions. Present them one at a time as multiple-choice prompts.

### Question 1: Sessions to include

> **How many sessions should I include in training?**
>
> 1. **All sessions** — most comprehensive profile, recommended for first run or full retrain
> 2. **Last 200 sessions** — solid coverage, faster extraction
> 3. **Last 50 sessions** — quick snapshot of recent behavior
> 4. **Custom number** — you specify
>
> *Default: 1 (All sessions)*

Map the choice to `--max-sessions`: all = `0`, otherwise the number they pick.

### Question 2: Model

> **Which model should I use for synthesis?**
>
> 1. **Opus** — highest quality, slowest, highest token usage. Best if you want the most thorough and nuanced profile.
> 2. **Sonnet** *(recommended)* — strong quality, moderate speed and cost. Best balance for most users.
> 3. **Haiku** — fastest and cheapest, but produces noticeably shorter and shallower profiles. Fine for a quick draft or if you're on a budget.
>
> *Weaker models will produce shorter, less nuanced profiles but will complete faster with lower token usage.*
>
> *Default: 2 (Sonnet)*

Map the choice to `--model`: `opus`, `sonnet`, or `haiku`.

### Question 3: Timeout

> **How long should each synthesis step be allowed to run before timing out?**
>
> 1. **10 minutes** — good for most users with <500 sessions
> 2. **20 minutes** *(recommended)* — safe default for large session histories
> 3. **30 minutes** — for very large histories or slower connections
> 4. **Custom (seconds)** — you specify
>
> *Each synthesis pass and the final merge step get their own timeout. If you have thousands of sessions or are using Opus, choose a longer timeout.*
>
> *Default: 2 (20 minutes)*

Map the choice to `--timeout`: 600, 1200, or 1800 seconds, or custom.

---

Once the user has answered all three questions (or accepted defaults), confirm their choices and run the pipeline.

### Step 1: Extract

```bash
cd "$PLUGIN_DIR/../.." && python3 scripts/extract-sessions.py --output /tmp/imprint-messages.json --max-sessions <N>
```

### Step 2: Synthesize

```bash
cd "$PLUGIN_DIR/../.." && python3 scripts/synthesize-profile.py /tmp/imprint-messages.json --model <MODEL> --timeout <SECONDS>
```

### Step 3: Report

After training completes:
1. Read `~/.claude/.imprint` and present a summary of what was learned
2. Report the number of sessions and messages analyzed
3. Note any sections with low confidence due to insufficient data
4. Clean up the temp file: `rm -f /tmp/imprint-messages.json`

If training fails at any step, report the error and suggest troubleshooting steps.

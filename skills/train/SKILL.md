---
name: imprint:train
description: Train a behavioral profile from your Claude session history
---

# Train Behavioral Profile

Scan your Claude session history, extract behavioral patterns, and generate a profile at `~/.claude/.imprint`.

## Instructions

Run the training pipeline:

```bash
cd "$PLUGIN_DIR/../.." && python3 scripts/extract-sessions.py --output /tmp/imprint-messages.json
```

If extraction succeeds, run synthesis:

```bash
cd "$PLUGIN_DIR/../.." && python3 scripts/synthesize-profile.py /tmp/imprint-messages.json
```

The synthesis script uses `claude --print` to analyze extracted messages in multiple passes and writes the final profile to `~/.claude/.imprint`.

After training completes:
1. Read `~/.claude/.imprint` and present a summary of what was learned
2. Report the number of sessions and messages analyzed
3. Note any sections with low confidence due to insufficient data
4. Clean up the temp file: `rm -f /tmp/imprint-messages.json`

If training fails at any step, report the error and suggest troubleshooting steps.

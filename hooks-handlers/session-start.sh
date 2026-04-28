#!/usr/bin/env bash
# Imprint plugin SessionStart hook.
#
# Reads ~/.claude/.imprint and emits its contents as additionalContext so the
# trained behavioral profile is loaded into every Claude Code session.
#
# When no profile exists yet, emits a brief notice pointing at /imprint:train.

set -euo pipefail

PROFILE_PATH="$HOME/.claude/.imprint"

emit_json() {
    # Encode the body as JSON-safe additionalContext. python3 is always present on macOS.
    python3 - "$1" <<'PY'
import json, sys
body = sys.argv[1]
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": body,
    }
}))
PY
}

if [[ ! -f "$PROFILE_PATH" ]]; then
    emit_json "The imprint plugin is installed but no behavioral profile has been trained yet. The user can run /imprint:train to generate one from their session history."
    exit 0
fi

PROFILE_CONTENT=$(cat "$PROFILE_PATH")

PREAMBLE="The following is a behavioral profile learned from this user's prior Claude Code sessions. It describes how they prefer to communicate, the quality standards they apply, the review instincts they've demonstrated, and the patterns they expect from Claude. Treat these as factual context about the user — adopt them as defaults for communication, decision-making, and quality gates. Items marked \"never\" or \"always\" are hard rules unless the user explicitly overrides them in this session.

--- BEGIN BEHAVIORAL PROFILE ---

"

POSTAMBLE="

--- END BEHAVIORAL PROFILE ---"

emit_json "${PREAMBLE}${PROFILE_CONTENT}${POSTAMBLE}"

#!/usr/bin/env bash
# Main training entrypoint: extract sessions → synthesize profile → install
#
# Usage:
#   scripts/train.sh [--max-sessions N] [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
TMP_MESSAGES="/tmp/imprint-messages.json"
PROFILE_PATH="$HOME/.claude/.imprint"

MAX_SESSIONS="${1:-50}"
DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --max-sessions=*) MAX_SESSIONS="${arg#*=}" ;;
    esac
done

echo "=== Imprint Profile Training ==="
echo ""

# Step 1: Extract
echo "Step 1/3: Extracting user messages..."
python3 "$SCRIPT_DIR/extract-sessions.py" --output "$TMP_MESSAGES" --max-sessions "$MAX_SESSIONS"

if [[ ! -f "$TMP_MESSAGES" ]]; then
    echo "Error: Extraction failed — no messages file produced" >&2
    exit 1
fi

# Step 2: Synthesize
echo ""
echo "Step 2/3: Synthesizing behavioral profile..."
python3 "$SCRIPT_DIR/synthesize-profile.py" "$TMP_MESSAGES"

# Step 3: Verify
echo ""
echo "Step 3/3: Verifying profile..."
if [[ -f "$PROFILE_PATH" ]]; then
    lines=$(wc -l < "$PROFILE_PATH")
    size=$(wc -c < "$PROFILE_PATH")
    echo "Profile written to $PROFILE_PATH ($lines lines, $size bytes)"
else
    echo "Error: Profile was not created at $PROFILE_PATH" >&2
    rm -f "$TMP_MESSAGES"
    exit 1
fi

# Cleanup
rm -f "$TMP_MESSAGES"

echo ""
echo "=== Training complete ==="
echo "The profile will be loaded automatically in new Claude sessions."

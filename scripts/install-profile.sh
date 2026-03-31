#!/usr/bin/env bash
# Install or verify the imprint profile at ~/.claude/.imprint
#
# Usage:
#   scripts/install-profile.sh              # Check if profile exists
#   scripts/install-profile.sh --remove     # Remove profile (with confirmation)

set -euo pipefail

PROFILE_PATH="$HOME/.claude/.imprint"

if [[ "${1:-}" == "--remove" ]]; then
    if [[ -f "$PROFILE_PATH" ]]; then
        read -p "Remove behavioral profile at $PROFILE_PATH? [y/N] " confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            rm "$PROFILE_PATH"
            echo "Profile removed."
        else
            echo "Cancelled."
        fi
    else
        echo "No profile found at $PROFILE_PATH"
    fi
    exit 0
fi

if [[ -f "$PROFILE_PATH" ]]; then
    lines=$(wc -l < "$PROFILE_PATH")
    size=$(wc -c < "$PROFILE_PATH")
    echo "Profile exists at $PROFILE_PATH ($lines lines, $size bytes)"
    echo "Run /imprint:train to regenerate."
else
    echo "No profile found. Run /imprint:train to generate one."
fi

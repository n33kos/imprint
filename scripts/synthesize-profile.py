#!/usr/bin/env python3
"""
Synthesize a behavioral profile from extracted session messages.

Uses `claude --print` for multi-pass LLM synthesis — no API key needed.

Usage:
    python3 scripts/synthesize-profile.py /tmp/imprint-messages.json [--passes N]
"""

import json
import subprocess
import sys
import textwrap
from pathlib import Path


PROFILE_PATH = Path.home() / ".claude" / ".imprint"
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

# Max messages per synthesis batch to stay within context limits
BATCH_SIZE = 200


def load_messages(input_path: Path) -> dict:
    data = json.loads(input_path.read_text())
    return data


def load_template() -> str:
    template_path = TEMPLATE_DIR / "synthesis-prompt.md"
    return template_path.read_text()


def sample_messages(messages: list[dict], batch_size: int = BATCH_SIZE) -> list[list[dict]]:
    """Split messages into batches, sampling evenly across projects."""
    if len(messages) <= batch_size:
        return [messages]

    # Group by project
    by_project: dict[str, list[dict]] = {}
    for msg in messages:
        proj = msg.get("project", "unknown")
        by_project.setdefault(proj, []).append(msg)

    # Sample proportionally from each project
    batches = []
    remaining = list(messages)

    while remaining:
        batch = remaining[:batch_size]
        batches.append(batch)
        remaining = remaining[batch_size:]

    return batches


def run_synthesis_pass(template: str, messages: list[dict], pass_label: str) -> str:
    """Run a single synthesis pass using claude --print."""
    message_text = "\n\n---\n\n".join(
        f"[Project: {m.get('project', 'unknown')}]\n{m['text']}"
        for m in messages
    )

    prompt = f"{template}\n\n## Messages\n\n{message_text}"

    print(f"  Running {pass_label} ({len(messages)} messages)...")

    result = subprocess.run(
        ["claude", "--print", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"  Warning: {pass_label} returned code {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"  stderr: {result.stderr[:200]}", file=sys.stderr)

    return result.stdout.strip()


def run_merge_pass(partial_profiles: list[str], metadata: dict) -> str:
    """Merge multiple partial profiles into a final one."""
    merge_prompt = textwrap.dedent(f"""\
        You are merging multiple partial behavioral profiles into a single coherent profile.

        Each partial profile was generated from a different batch of the same user's session history.
        Combine them into one unified profile, deduplicating insights and strengthening patterns
        that appear across multiple batches.

        Metadata:
        - Sessions analyzed: {metadata['session_count']}
        - Total messages: {metadata['message_count']}

        Rules:
        - Merge duplicate observations into single stronger statements
        - If a pattern appears in multiple batches, increase confidence
        - Resolve contradictions by favoring the more specific observation
        - Keep the same section structure (Communication Style, Quality Standards, etc.)
        - Add a header noting this was auto-generated and can be manually edited
        - Mark observations with [low confidence] if they only appeared in one batch
        - Start the file with: # User Behavioral Profile
        - Include a generation metadata line after the title

        ## Partial Profiles

    """)

    for i, profile in enumerate(partial_profiles):
        merge_prompt += f"### Batch {i + 1}\n\n{profile}\n\n"

    print(f"  Running merge pass ({len(partial_profiles)} batches)...")

    result = subprocess.run(
        ["claude", "--print", "-p", merge_prompt],
        capture_output=True,
        text=True,
        timeout=120,
    )

    return result.stdout.strip()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Synthesize behavioral profile")
    parser.add_argument("input", help="Path to extracted messages JSON")
    parser.add_argument("--passes", type=int, default=0, help="Override number of passes (0 = auto)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    data = load_messages(input_path)
    messages = data["messages"]
    metadata = {
        "session_count": data["session_count"],
        "message_count": data["message_count"],
    }

    print(f"Loaded {len(messages)} messages from {metadata['session_count']} sessions")

    template = load_template()
    batches = sample_messages(messages)
    num_passes = args.passes if args.passes > 0 else len(batches)

    print(f"Running {num_passes} synthesis pass(es)...")

    partial_profiles = []
    for i, batch in enumerate(batches[:num_passes]):
        profile = run_synthesis_pass(template, batch, f"pass {i + 1}/{num_passes}")
        if profile:
            partial_profiles.append(profile)

    if not partial_profiles:
        print("Error: All synthesis passes failed", file=sys.stderr)
        sys.exit(1)

    # If multiple batches, merge them
    if len(partial_profiles) > 1:
        final_profile = run_merge_pass(partial_profiles, metadata)
    else:
        final_profile = partial_profiles[0]

    if not final_profile:
        print("Error: Final profile is empty", file=sys.stderr)
        sys.exit(1)

    # Ensure header exists
    if not final_profile.startswith("# "):
        final_profile = (
            f"# User Behavioral Profile\n\n"
            f"> Auto-generated by imprint on {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}\n"
            f"> Based on {metadata['session_count']} sessions ({metadata['message_count']} messages)\n"
            f"> Edit this file to correct or refine the profile.\n\n"
            + final_profile
        )

    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(final_profile)
    print(f"\nProfile written to {PROFILE_PATH}")
    print(f"  Lines: {len(final_profile.splitlines())}")


if __name__ == "__main__":
    main()

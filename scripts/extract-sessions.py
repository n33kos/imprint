#!/usr/bin/env python3
"""
Extract user messages from Claude session history for profile training.

Scans JSONL session files in ~/.claude/projects/, extracts genuine user messages
(both typed and voice), and writes them to a JSON file for synthesis.

Usage:
    python3 scripts/extract-sessions.py --output /tmp/imprint-messages.json [--max-sessions N]
"""

import json
import re
import sys
from pathlib import Path


SKIP_PREFIXES = [
    "Base directory for this skill",
    "<command",
    "local-command",
    "task-notification",
    "[Request",
    "This session is being continued",
    "<system",
    "Async agent",
    "Shell cwd",
    "MCP error",
    "Continue from where you left off",
]


def _is_genuine_message(text: str) -> bool:
    text = text.strip()
    if len(text) < 15:
        return False
    for prefix in SKIP_PREFIXES:
        if text.startswith(prefix):
            return False
    return True


def _extract_voice_text(raw: str) -> str | None:
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            result = parsed.get("result", "")
            m = re.match(r"\[Voice from [^\]]+\]:\s*(.*)", result, re.DOTALL)
            if m:
                return m.group(1).strip()
    except (json.JSONDecodeError, TypeError):
        pass
    m = re.match(r"\[Voice from [^\]]+\]:\s*(.*)", raw, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def find_session_files(projects_dir: Path, max_files: int = 50) -> list[Path]:
    files = []
    for jsonl in projects_dir.rglob("*.jsonl"):
        try:
            stat = jsonl.stat()
            if stat.st_size > 50_000:
                files.append((jsonl, stat.st_mtime, stat.st_size))
        except OSError:
            continue

    files.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return [f[0] for f in files[:max_files]]


def extract_user_messages(session_file: Path) -> list[dict]:
    messages = []
    project = session_file.parent.name

    try:
        with open(session_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if entry.get("type") != "user":
                    continue

                content = entry.get("message", {}).get("content", "")
                texts = []

                if isinstance(content, str):
                    if _is_genuine_message(content):
                        texts.append(content.strip())
                elif isinstance(content, list):
                    for part in content:
                        if not isinstance(part, dict):
                            continue
                        ptype = part.get("type", "")

                        if ptype == "text":
                            text = part.get("text", "")
                            if _is_genuine_message(text):
                                texts.append(text.strip())
                        elif ptype == "tool_result":
                            inner = part.get("content", "")
                            if isinstance(inner, str):
                                voice = _extract_voice_text(inner)
                                if voice and len(voice) > 10:
                                    texts.append(voice)
                            elif isinstance(inner, list):
                                for ipart in inner:
                                    if isinstance(ipart, dict) and ipart.get("type") == "text":
                                        t = ipart.get("text", "")
                                        voice = _extract_voice_text(t)
                                        if voice and len(voice) > 10:
                                            texts.append(voice)

                for text in texts:
                    messages.append({
                        "text": text,
                        "project": project,
                    })

    except (OSError, UnicodeDecodeError):
        pass

    return messages


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract user messages from Claude sessions")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--max-sessions", type=int, default=50, help="Max sessions to scan")
    args = parser.parse_args()

    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        print(f"Error: {projects_dir} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning session transcripts in {projects_dir}...")
    session_files = find_session_files(projects_dir, max_files=args.max_sessions)
    print(f"Found {len(session_files)} session files to analyze")

    all_messages = []
    for i, sf in enumerate(session_files):
        if (i + 1) % 10 == 0:
            print(f"  Processing {i + 1}/{len(session_files)}...")
        messages = extract_user_messages(sf)
        all_messages.extend(messages)

    print(f"Extracted {len(all_messages)} user messages")

    if not all_messages:
        print("No user messages found — cannot generate profile", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_data = {
        "session_count": len(session_files),
        "message_count": len(all_messages),
        "messages": all_messages,
    }
    output_path.write_text(json.dumps(output_data, indent=2))
    print(f"Wrote {len(all_messages)} messages to {output_path}")


if __name__ == "__main__":
    main()

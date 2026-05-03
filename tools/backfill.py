#!/usr/bin/env python3
"""Idempotent backfill of wing/room frontmatter on memory files.

Reads classification.json and adds wing:/room: fields to each memory file's
YAML frontmatter. Skips files that already have both fields. Preserves all
other frontmatter and body content exactly.

Usage:
  backfill.py                              # auto-detect memory dir
  backfill.py --dir ./memory               # explicit path
  backfill.py --classification rules.json  # custom classification file
"""
import argparse
import json
import re
import sys
from pathlib import Path


def find_memory_dir() -> Path:
    candidates = [Path.cwd(), Path.cwd() / "memory"]
    projects_dir = Path.home() / ".claude" / "projects"
    if projects_dir.exists():
        for project in projects_dir.iterdir():
            mem = project / "memory"
            if mem.exists() and (mem / "MEMORY.md").exists():
                candidates.insert(0, mem)
    for c in candidates:
        if c.exists() and (c / "MEMORY.md").exists():
            return c
    print("Could not find memory directory. Pass --dir.", file=sys.stderr)
    sys.exit(1)


def backfill_one(path: Path, wing: str, room: str) -> str:
    """Returns: 'added', 'already_has', 'no_frontmatter', or 'error:...'."""
    try:
        text = path.read_text()
    except Exception as e:
        return f"error:{e}"

    m = re.match(r"^(---\n)(.*?\n)(---\n)", text, re.DOTALL)
    if not m:
        new_fm = f"---\nname: {path.stem}\nwing: {wing}\nroom: {room}\n---\n\n"
        path.write_text(new_fm + text)
        return "no_frontmatter"

    open_marker, fm_body, close_marker = m.group(1), m.group(2), m.group(3)
    has_wing = re.search(r"^wing\s*:", fm_body, re.MULTILINE)
    has_room = re.search(r"^room\s*:", fm_body, re.MULTILINE)

    if has_wing and has_room:
        return "already_has"

    new_fm_body = fm_body
    if not has_wing:
        new_fm_body = new_fm_body.rstrip("\n") + f"\nwing: {wing}\n"
    if not has_room:
        new_fm_body = new_fm_body.rstrip("\n") + f"\nroom: {room}\n"

    new_text = open_marker + new_fm_body + close_marker + text[m.end():]
    path.write_text(new_text)
    return "added"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=None)
    ap.add_argument("--classification", type=Path, default=None,
                    help="Path to classification.json (default: <dir>/classification.json)")
    args = ap.parse_args()

    mem_dir = args.dir or find_memory_dir()
    class_file = args.classification or mem_dir / "classification.json"

    if not class_file.exists():
        print(f"Classification file not found: {class_file}", file=sys.stderr)
        print("Create one manually or generate with classify.py first.", file=sys.stderr)
        sys.exit(1)

    classification = json.loads(class_file.read_text())
    counts = {"added": 0, "already_has": 0, "no_frontmatter": 0, "error": 0}
    errors = []

    for filename, meta in sorted(classification.items()):
        path = mem_dir / filename
        if not path.exists():
            continue
        result = backfill_one(path, meta["wing"], meta["room"])
        key = result.split(":")[0]
        counts[key] = counts.get(key, 0) + 1
        if key == "error":
            errors.append((filename, result))

    print(f"added: {counts['added']}")
    print(f"already_has: {counts['already_has']}")
    print(f"no_frontmatter (created): {counts['no_frontmatter']}")
    if errors:
        print(f"errors: {len(errors)}")
        for f, e in errors:
            print(f"  {f}: {e}")


if __name__ == "__main__":
    main()

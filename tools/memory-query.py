#!/usr/bin/env python3
"""Filter memory files by wing/room/type/text. Prints matching files with descriptions.

Usage:
  memory-query.py --wing infrastructure
  memory-query.py --wing backend --type feedback
  memory-query.py --room api-keys
  memory-query.py --text database
  memory-query.py --wing frontend --type project --paths    # paths only

Filters AND together. Reads YAML frontmatter from each .md file in the memory dir.
"""
import argparse
import re
import sys
from pathlib import Path

# Auto-detect memory directory: look for MEMORY.md in the current dir or parent dirs
def find_memory_dir() -> Path:
    # Check common locations
    candidates = [
        Path.cwd(),
        Path.cwd() / "memory",
        Path.home() / ".claude" / "memory",
    ]
    # Also check .claude/projects/*/memory/ pattern
    projects_dir = Path.home() / ".claude" / "projects"
    if projects_dir.exists():
        for project in projects_dir.iterdir():
            mem = project / "memory"
            if mem.exists() and (mem / "MEMORY.md").exists():
                candidates.insert(0, mem)

    for c in candidates:
        if c.exists() and (c / "MEMORY.md").exists():
            return c
    print("Could not find memory directory (no MEMORY.md found). Pass --dir.", file=sys.stderr)
    sys.exit(1)


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def main():
    ap = argparse.ArgumentParser(description="Filter memory files by wing/room/type/text")
    ap.add_argument("--wing", help="Filter by wing (e.g. infrastructure, backend)")
    ap.add_argument("--room", help="Filter by room (substring match)")
    ap.add_argument("--type", dest="hall", help="Filter by type/hall (feedback, project, reference, user)")
    ap.add_argument("--text", help="Substring match against name/description/body")
    ap.add_argument("--paths", action="store_true", help="Output file paths only (one per line)")
    ap.add_argument("--limit", type=int, default=0, help="Max results (0 = unlimited)")
    ap.add_argument("--dir", type=Path, default=None, help="Memory directory (auto-detected if omitted)")
    args = ap.parse_args()

    mem_dir = args.dir or find_memory_dir()

    matches = []
    for f in sorted(mem_dir.glob("*.md")):
        if f.name in ("MEMORY.md", "INDEX.md"):
            continue
        try:
            text = f.read_text()
        except Exception:
            continue
        fm = parse_frontmatter(text)
        if args.wing and fm.get("wing", "") != args.wing:
            continue
        if args.hall and fm.get("type", "") != args.hall:
            continue
        if args.room and args.room not in fm.get("room", ""):
            continue
        if args.text:
            hay = (fm.get("name", "") + " " + fm.get("description", "") + " " + text).lower()
            if args.text.lower() not in hay:
                continue
        matches.append((f, fm))

    if args.limit:
        matches = matches[: args.limit]

    if args.paths:
        for f, _ in matches:
            print(f)
    else:
        if not matches:
            print("(no matches)", file=sys.stderr)
            return
        from collections import defaultdict
        by_wing = defaultdict(list)
        for f, fm in matches:
            by_wing[fm.get("wing", "?")].append((f, fm))
        for wing in sorted(by_wing.keys()):
            print(f"\n## {wing} ({len(by_wing[wing])})")
            for f, fm in by_wing[wing]:
                room = fm.get("room", f.stem)
                hall = fm.get("type", "?")
                desc = fm.get("description", "").strip()
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                print(f"  [{hall}] {room} ({f.name})")
                if desc:
                    print(f"      {desc}")
        print(f"\n{len(matches)} match(es)")


if __name__ == "__main__":
    main()

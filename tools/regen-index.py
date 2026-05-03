#!/usr/bin/env python3
"""Regenerate the wing-grouped index in INDEX.md (sibling to MEMORY.md).

INDEX.md is a separate file so MEMORY.md can stay under the 200-line load budget.
MEMORY.md gets a one-line pointer to INDEX.md inside the AUTO markers.

Each entry is one line. Grouped by wing -> hall (type) -> entry, sorted alphabetically
within each group. Uses each file's `description:` frontmatter as the hook.

Usage:
  regen-index.py                  # auto-detect memory dir
  regen-index.py --dir ./memory   # explicit path
"""
import argparse
import re
import sys
from pathlib import Path
from collections import defaultdict

START_MARKER = "<!-- AUTO-START:wing-index -->"
END_MARKER = "<!-- AUTO-END:wing-index -->"

HALL_ORDER = ["feedback", "project", "reference", "user"]


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


def gather(mem_dir: Path) -> dict:
    """Returns: {wing: {hall: [(filename, room, description), ...]}}"""
    by_wing = defaultdict(lambda: defaultdict(list))
    for f in sorted(mem_dir.glob("*.md")):
        if f.name in ("MEMORY.md", "INDEX.md"):
            continue
        try:
            text = f.read_text()
        except Exception:
            continue
        fm = parse_frontmatter(text)
        wing = fm.get("wing", "general")
        hall = fm.get("type", "project")
        room = fm.get("room", f.stem)
        desc = fm.get("description", "").strip()
        by_wing[wing][hall].append((f.name, room, desc))
    return by_wing


def render_index(by_wing: dict) -> str:
    """Full wing index, written to INDEX.md."""
    lines = [
        "# Memory Wing Index",
        "",
        "Auto-generated from per-file `wing:` / `room:` / `type:` frontmatter.",
        "Regen with `python tools/regen-index.py`. **Do not hand-edit.**",
        "",
    ]

    for wing in sorted(by_wing.keys()):
        halls = by_wing[wing]
        total = sum(len(v) for v in halls.values())
        lines.append(f"### {wing.title()} ({total})")
        ordered_halls = [h for h in HALL_ORDER if h in halls] + sorted(
            h for h in halls if h not in HALL_ORDER
        )
        for hall in ordered_halls:
            entries = sorted(halls[hall], key=lambda e: e[1])
            lines.append(f"_{hall}_:")
            for filename, room, desc in entries:
                d = desc[:110] + "..." if len(desc) > 110 else desc
                lines.append(f"- [{room}]({filename}) -- {d}")
            lines.append("")
        lines.append("")

    return "\n".join(lines)


def render_pointer(by_wing: dict) -> str:
    """Slim pointer block for MEMORY.md -- wing counts + link to INDEX.md."""
    total = sum(sum(len(v) for v in halls.values()) for halls in by_wing.values())
    parts = []
    for wing in sorted(by_wing.keys()):
        n = sum(len(v) for v in by_wing[wing].values())
        parts.append(f"{wing.title()} ({n})")
    lines = [
        START_MARKER,
        f"## Memory Index -> [INDEX.md](INDEX.md) -- {total} files across {len(by_wing)} wings",
        "",
        "Wings: " + ", ".join(parts) + ".",
        "Read INDEX.md for the per-file map. Regen with `python tools/regen-index.py`.",
        END_MARKER,
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=None)
    args = ap.parse_args()

    mem_dir = args.dir or find_memory_dir()
    by_wing = gather(mem_dir)

    index_md = mem_dir / "INDEX.md"
    memory_md = mem_dir / "MEMORY.md"

    # Write full index
    index_md.write_text(render_index(by_wing) + "\n")

    # Write pointer into MEMORY.md
    new_block = render_pointer(by_wing)
    text = memory_md.read_text()

    if START_MARKER in text and END_MARKER in text:
        new_text = re.sub(
            re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
            new_block,
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        new_text = text.rstrip() + "\n\n" + new_block + "\n"

    memory_md.write_text(new_text)
    total = sum(sum(len(v) for v in halls.values()) for halls in by_wing.values())
    print(f"Indexed {total} entries across {len(by_wing)} wings -> {index_md}")


if __name__ == "__main__":
    main()

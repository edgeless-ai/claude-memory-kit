## Memory System

This project uses file-based persistent memory. Claude stores and retrieves memories
from `.claude/projects/<hash>/memory/` to maintain context across conversations.

**Memory types:**
- `user` -- Your role, preferences, and expertise
- `feedback` -- Corrections that prevent repeated mistakes
- `project` -- Decisions, constraints, and context not in the code
- `reference` -- Pointers to external resources and systems

**Organization (optional, recommended at 10+ files):**
- `wing` -- Top-level domain (e.g. infrastructure, backend, product)
- `room` -- Sub-topic within a wing (e.g. deployment-rules, api-keys)

**Rules:**
- Read `MEMORY.md` at session start to load the memory index
- Save memories when you learn important context about the user or project
- Update existing memories rather than creating duplicates
- Keep `MEMORY.md` under 200 lines (it gets truncated beyond that)
- Use absolute dates, not relative ones
- For feedback memories, always include **Why:** and **How to apply:** sections

**Tooling (when you have 10+ files):**
- `python tools/regen-index.py` -- regenerate INDEX.md from frontmatter
- `python tools/memory-query.py --wing X --type Y` -- filter and search memories
- `python tools/backfill.py` -- add wing/room to files missing them

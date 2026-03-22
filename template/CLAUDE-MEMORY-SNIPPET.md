## Memory System

This project uses file-based persistent memory. Claude stores and retrieves memories
from `.claude/projects/<hash>/memory/` to maintain context across conversations.

**Memory types:**
- `user` - Your role, preferences, and expertise
- `feedback` - Corrections that prevent repeated mistakes
- `project` - Decisions, constraints, and context not in the code
- `reference` - Pointers to external resources and systems

**Rules:**
- Read `MEMORY.md` at session start to load the memory index
- Save memories when you learn important context about the user or project
- Update existing memories rather than creating duplicates
- Keep `MEMORY.md` under 200 lines (it gets truncated beyond that)
- Use absolute dates, not relative ones

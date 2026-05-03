[![CI](https://github.com/edgeless-ai/claude-memory-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/edgeless-ai/claude-memory-kit/actions)
[![PyPI](https://img.shields.io/pypi/v/claude-memory-kit)](https://pypi.org/project/claude-memory-kit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# Claude Memory Kit

Persistent, file-based memory for [Claude Code](https://claude.ai/claude-code). Drop it into any project and Claude remembers who you are, what you've told it, and where things live -- across every conversation.

Based on a production system running 160+ memory files across 8 domains, managing multiple AI agents and 7,000+ documents.

## Quick Start

```bash
# Clone
git clone https://github.com/edgeless-ai/claude-memory-kit.git .claude-memory-kit

# Copy the memory template into your project's Claude config
mkdir -p .claude/projects/$(basename $(pwd))/memory
cp .claude-memory-kit/template/.claude/projects/example-project/memory/* \
   .claude/projects/$(basename $(pwd))/memory/

# Add the memory instructions to your CLAUDE.md
echo '' >> CLAUDE.md
cat .claude-memory-kit/template/CLAUDE-MEMORY-SNIPPET.md >> CLAUDE.md

# Copy the tooling scripts
cp -r .claude-memory-kit/tools ./memory-tools

# Clean up
rm -rf .claude-memory-kit
```

Or manually copy files from `template/` into `.claude/projects/<your-project>/memory/`.

> **Note:** Claude Code auto-creates the project directory at `.claude/projects/<hash>/memory/`. The exact hash varies. Check your `.claude/projects/` directory for the actual path, or let Claude create the first memory file and then copy the templates alongside it.

## How It Works

```
.claude/projects/<project>/memory/
  MEMORY.md              # Index (auto-loaded every session, <200 lines)
  INDEX.md               # Full wing-grouped index (auto-generated)
  user_role.md           # Who you are
  feedback_*.md          # Corrections and preferences
  project_*.md           # Decisions and constraints
  reference_*.md         # Pointers to external systems
```

`MEMORY.md` loads into Claude's context at the start of every conversation. It contains only links and one-line descriptions -- never full content. Individual memory files hold the detail.

## Memory Types

### User

```markdown
---
name: User Role
description: Senior Go engineer, new to React -- explain frontend via backend analogues
type: user
wing: user
room: role
---

Senior backend engineer with 8 years of Go experience.
New to the React frontend in this project.
Prefer concise explanations with code examples over prose.
```

### Feedback

Corrections Claude should never repeat. Always include **Why** and **How to apply**.

```markdown
---
name: No mocking in integration tests
description: Use real database in integration tests -- mocks caused prod incident Q4 2025
type: feedback
wing: backend
room: testing
---

Integration tests must hit a real database, not mocks.

**Why:** Mocked tests passed but the prod migration failed. Mocks diverged
from actual PostgreSQL behavior around NULL handling in JSONB columns.

**How to apply:** Always use the test database container. Never mock the
database connection, query builder, or ORM.
```

### Project

Context about ongoing work that isn't in the code.

```markdown
---
name: API Freeze
description: No breaking API changes until mobile release branch cut on 2026-03-15
type: project
wing: backend
room: api-freeze
---

Breaking API changes frozen until 2026-03-15 (mobile release cut).

**Why:** Mobile team pins integration tests against current API contract.

**How to apply:** New endpoints fine. Additive fields fine. Flag any PR
that removes fields, changes response shapes, or modifies status codes.
```

### Reference

Lookup tables, external pointers, config snippets.

```markdown
---
name: Infrastructure References
description: Where to find monitoring, docs, and tracking systems
type: reference
wing: infrastructure
room: external-systems
---

- **Bugs**: Linear project "PLATFORM"
- **Monitoring**: Grafana at grafana.internal/d/api-latency
- **Design**: Figma workspace "Product Design 2026"
```

## Organization: Wings and Rooms

At 1-10 files, you only need the 4 types above. At 10+, add **wings** (top-level domains) and **rooms** (sub-topics) to keep things navigable.

```yaml
# Frontmatter with full schema
---
name: deployment-rules
description: VPS deployment safety rules -- never hot-patch, always use staging first
type: feedback
wing: infrastructure      # top-level domain
room: deployment           # sub-topic within the wing
---
```

Choose wings that match your work. Examples:

| Solo Dev | Agent Operator | Data Team |
|----------|---------------|-----------|
| `backend` | `agents` | `pipelines` |
| `frontend` | `models` | `warehouse` |
| `infrastructure` | `knowledge` | `dashboards` |
| `product` | `product` | `governance` |
| `tools` | `creative` | `tools` |
| `user` | `user` | `user` |

See [docs/wing-taxonomy.md](docs/wing-taxonomy.md) for the full schema reference, writing guidelines, anti-patterns, and scaling advice.

## Tooling

Three Python scripts (zero dependencies, Python 3.8+) that become essential at 10+ files:

### Query memories

```bash
python tools/memory-query.py --wing backend
python tools/memory-query.py --wing infrastructure --type feedback
python tools/memory-query.py --text "database"
python tools/memory-query.py --room api-keys --paths
```

### Regenerate the index

```bash
python tools/regen-index.py
```

Reads frontmatter from every `.md` file, generates a wing-grouped `INDEX.md`, and inserts a summary pointer into `MEMORY.md` between the `AUTO-START` / `AUTO-END` markers.

### Backfill wing/room on older files

```bash
python tools/backfill.py
```

Reads a `classification.json` mapping (filename -> wing/room) and adds the fields to any file missing them. Idempotent, safe to re-run. Create `classification.json` manually or generate it with your own rules.

## Scaling

| Files | What you need |
|-------|--------------|
| 1-10 | Just the 4 types. MEMORY.md is your only index. |
| 10-30 | Add `wing:` and `room:` to frontmatter. Run `regen-index.py`. |
| 30-100 | `memory-query.py` becomes essential. `backfill.py` to retrofit older files. |
| 100+ | Monthly review. Archive aggressively. INDEX.md keeps MEMORY.md under 200 lines. |

## Best Practices

1. **Be specific in descriptions** -- Claude scans all descriptions to decide which files to open. "PostgreSQL connection pooling config and timeout tuning" beats "database stuff."

2. **Include why** -- For feedback and project memories, always explain the reason. Claude uses it to judge edge cases.

3. **Keep MEMORY.md under 200 lines** -- It gets truncated beyond that. Use INDEX.md for the full catalog.

4. **Update, don't duplicate** -- Check for existing memories before creating new ones.

5. **Use absolute dates** -- "2026-03-15", not "next Thursday."

6. **Prune regularly** -- Stale context confuses more than it helps.

## What NOT to Store

- Code patterns or architecture (derive from the codebase)
- Git history (use `git log` / `git blame`)
- Debugging solutions (the fix is in the code; the commit message has context)
- Anything already in CLAUDE.md
- Temporary task state (use Claude Code's task system)

## CLAUDE.md Integration

Add the snippet from `template/CLAUDE-MEMORY-SNIPPET.md` to your project's `CLAUDE.md`. It tells Claude:

- Where memory lives
- The 4 types + wing/room schema
- When to save vs. update
- How to use the tooling scripts

## Repo Structure

```
template/                   # Drop-in starter files
  CLAUDE-MEMORY-SNIPPET.md  # Paste into your CLAUDE.md
  .claude/projects/example-project/memory/
    MEMORY.md               # Index template
    user_role.md            # User memory template
    feedback_example.md     # Feedback memory template
    project_example.md      # Project memory template
    reference_example.md    # Reference memory template
tools/                      # Python scripts (zero dependencies)
  memory-query.py           # Filter memories by wing/room/type/text
  regen-index.py            # Auto-generate INDEX.md from frontmatter
  backfill.py               # Add wing/room to files missing them
docs/
  wing-taxonomy.md          # Full schema reference and writing guide
examples/                   # Realistic filled-in examples
  user_senior_engineer.md
  feedback_testing.md
  project_api_freeze.md
  reference_infrastructure.md
```

## License

MIT

---

Built by [Edgeless Labs](https://edgelesslab.com) -- a creative technology lab building AI agents, developer tools, and generative art.

# Wing Taxonomy -- Reference

This is the organizational schema that makes the memory system scale past a handful of files. Without it, 20+ memory files become an unsearchable pile. With it, 160+ files stay navigable.

## Concepts

### Wings

A **wing** is a top-level domain -- a coherent area of your work where knowledge belongs together. Wings are stable. You don't add new ones casually.

Example wings for a solo developer:

| Wing | Belongs here |
|---|---|
| `infrastructure` | Servers, deployment, CI/CD, monitoring, cron jobs |
| `backend` | API design, database, services, authentication |
| `frontend` | UI components, state management, styling, build tools |
| `product` | Business logic, feature specs, user feedback, roadmap |
| `tools` | Dev tools, CLI utilities, editor config, scripts |
| `user` | Your profile, preferences, working style |

Example wings for an AI/agent operator:

| Wing | Belongs here |
|---|---|
| `agents` | Agent configs, orchestration, dispatch, multi-agent coordination |
| `models` | LLM providers, model routing, prompt engineering, costs |
| `knowledge` | Knowledge base tools, ingestion pipelines, search, RAG |
| `product` | Brand, website, products, accounts, API keys |
| `creative` | Generative art, content creation, media tools |
| `user` | Your profile, preferences, design background |

**When to add a new wing**: if a domain has 10+ memory files, distinct vocabulary, and is independent of existing wings. Most "new" things are rooms in existing wings.

### Rooms

A **room** is a sub-area within a wing. It's a slug, not a sentence.

Rules:
- kebab-case, <=25 chars, descriptive
- The room is what you'd type if you wanted to filter for "this exact topic"
- One file per room is the default
- Filename should match room when possible: `deployment-rules.md` -> `room: deployment-rules`

Good rooms: `api-keys`, `deployment-rules`, `model-routing`, `database-migration`
Bad rooms: `stuff`, `notes`, `misc-from-january`, `config_v2_final_FINAL`

### Halls (Types)

The **type** field describes what *kind* of knowledge the entry holds:

| Type | Purpose | Body structure |
|---|---|---|
| `feedback` | Rules, corrections, preferences | Rule + **Why:** + **How to apply:** |
| `project` | Ongoing work, decisions, current state | Free-form with headings |
| `reference` | Pointers, configs, lookup tables | Tables, lists, code blocks |
| `user` | Profile facts about you | Free-form prose |

## Frontmatter Template

```yaml
---
name: short-slug-matching-filename
description: One-line hook (<=180 chars). Lead with the answer, not the topic.
type: feedback|project|reference|user
wing: your-wing-name
room: kebab-case-slug
---
```

### The description field matters

Future Claude scans all descriptions in INDEX.md and decides which files to open. If your description is generic ("This file documents the API"), you've wasted that decision.

Good: `"PostgreSQL connection pooling -- PgBouncer config, pool sizes, timeout tuning"`
Bad: `"Database stuff"`

## Body Structure by Type

**feedback** -- always 3 parts:

```markdown
Never run database migrations during peak hours.

**Why:** A migration on 2026-01-15 locked the users table for 8 minutes during lunch traffic.

**How to apply:** Schedule migrations for the maintenance window (2-4am UTC).
Check active connections before running. Alert oncall if migration takes >30s.
```

**project** -- free-form with headings. Lead with current state.

**reference** -- optimize for lookup, not narrative. Tables and code blocks.

**user** -- prose, read end-to-end. Keep under 200 lines.

## Decision Tree: Where Should This Go?

```
Q1: Is this a stable fact/preference that future sessions need?
    NO -> don't persist (ephemeral)
    YES -> continue

Q2: Is it <=200 lines?
    YES -> memory file
    NO -> consider splitting, or use a different storage layer
```

## Scaling Guide

### 1-10 files: Skip the taxonomy

Just use the 4 types (user, feedback, project, reference). MEMORY.md is your only index. No wings needed.

### 10-30 files: Add wings

You'll start losing track of which files exist. Add `wing:` and `room:` to frontmatter. Run `regen-index.py` to generate INDEX.md.

### 30-100 files: Add tooling

`memory-query.py` becomes essential for filtering. Run `regen-index.py` after every batch of changes. Consider `backfill.py` to retrofit wing/room on older files.

### 100+ files: Active maintenance

Review monthly. Archive aggressively. The INDEX.md auto-pointer in MEMORY.md keeps the loaded context under 200 lines even as the full index grows. Memory that's too long defeats the purpose -- Claude spends context window on stale instructions instead of your actual task.

## Anti-Patterns

- Don't bundle multiple topics in one file
- Don't tag a file with multiple wings -- pick the primary one
- Don't use the schema for ephemeral state (in-flight task progress, current chat context)
- Don't paste long file contents -- link to them
- Don't write descriptions longer than 180 chars (truncated in INDEX.md)
- Don't create a new wing for one file -- find the closest existing one

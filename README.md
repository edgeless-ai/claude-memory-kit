# Claude Memory Kit

A structured memory system for [Claude Code](https://claude.ai/claude-code) that persists context across conversations. Drop-in template for any project.

## What This Does

Claude Code conversations are ephemeral -- when a session ends, everything learned disappears. This kit gives Claude persistent, file-based memory that loads automatically at the start of every conversation.

**Before**: Claude forgets your preferences, project context, and past decisions every session.

**After**: Claude remembers who you are, what you're building, what feedback you've given, and where to find things.

## Quick Start

```bash
# Clone into your project
git clone https://github.com/edgeless-ai/claude-memory-kit.git .claude-memory-kit

# Copy the memory structure into your project
cp -r .claude-memory-kit/template/.claude/memory .claude/memory

# Add the memory loading instruction to your CLAUDE.md
echo '' >> CLAUDE.md
cat .claude-memory-kit/template/CLAUDE-MEMORY-SNIPPET.md >> CLAUDE.md

# Clean up
rm -rf .claude-memory-kit
```

Or manually copy the files from the `template/` directory.

## Memory Structure

```
.claude/
  projects/
    <project-hash>/
      memory/
        MEMORY.md          # Index file (auto-loaded by Claude)
        user_role.md       # Who you are
        feedback_*.md      # Corrections and preferences
        project_*.md       # Project context and decisions
        reference_*.md     # Pointers to external resources
```

## Memory Types

### User Memories
Store information about yourself that shapes how Claude works with you.

```markdown
---
name: User Role
description: Senior backend engineer experienced with Go and PostgreSQL
type: user
---

Senior backend engineer with 8 years of Go experience.
New to the React frontend in this project.
Prefer explanations that map frontend concepts to backend analogues.
```

### Feedback Memories
Corrections that prevent Claude from repeating mistakes.

```markdown
---
name: No mocking in integration tests
description: Use real database connections in integration tests, never mocks
type: feedback
---

Integration tests must hit a real database, not mocks.

**Why:** Last quarter, mocked tests passed but the prod migration failed.
Mocks diverged from actual database behavior.

**How to apply:** When writing or reviewing tests that touch the database,
always use the test database container, never mock the connection.
```

### Project Memories
Context about ongoing work that isn't in the code.

```markdown
---
name: API Migration Freeze
description: No breaking API changes until mobile release on March 15
type: project
---

Breaking API changes are frozen until 2026-03-15 (mobile release cut).

**Why:** Mobile team is cutting a release branch and can't absorb API changes.

**How to apply:** Any API endpoint modifications must be backwards-compatible.
New endpoints are fine. Flag any PR that modifies response shapes.
```

### Reference Memories
Pointers to where information lives outside the project.

```markdown
---
name: Bug Tracker
description: Production bugs tracked in Linear project PLATFORM
type: reference
---

Production bugs are tracked in Linear project "PLATFORM".
Feature requests go to "ROADMAP".
Design specs live in Figma workspace "Product Design 2026".
```

## MEMORY.md Index

The `MEMORY.md` file is automatically loaded into Claude's context at the start of every conversation. It should only contain links to memory files with brief descriptions -- never the memories themselves.

```markdown
# Memory Index

## User
- [user_role.md](user_role.md) - Senior Go engineer, new to React

## Feedback
- [feedback_no_mocks.md](feedback_no_mocks.md) - Use real DB in integration tests
- [feedback_terse_responses.md](feedback_terse_responses.md) - No trailing summaries

## Project
- [project_api_freeze.md](project_api_freeze.md) - API freeze until March 15

## Reference
- [reference_linear.md](reference_linear.md) - Bug tracking in Linear PLATFORM
```

## Best Practices

1. **Be specific in descriptions** -- The `description` field in frontmatter determines when Claude retrieves the memory. Make it specific enough to match relevant queries.

2. **Include why** -- For feedback and project memories, always explain *why*. This helps Claude judge edge cases instead of blindly following rules.

3. **Keep MEMORY.md short** -- Lines after ~200 get truncated. Link to files, don't inline content.

4. **Update, don't duplicate** -- Check for existing memories before creating new ones. Update in place.

5. **Use absolute dates** -- Convert "next Thursday" to "2026-03-15" so memories stay interpretable.

6. **Prune regularly** -- Remove memories that are no longer relevant. Stale context confuses more than it helps.

## What NOT to Store

- Code patterns or architecture (derive from the codebase)
- Git history (use `git log` / `git blame`)
- Debugging solutions (the fix is in the code)
- Anything already in CLAUDE.md
- Temporary task state (use Claude Code's task system instead)

## CLAUDE.md Integration

Add this snippet to your project's `CLAUDE.md` to activate the memory system:

```markdown
## Memory System

This project uses file-based persistent memory at `.claude/projects/<hash>/memory/`.
At session start, read MEMORY.md to load the memory index.
Save new memories when you learn important context about the user, receive feedback,
or discover project-specific information that will be useful in future conversations.
```

See `template/CLAUDE-MEMORY-SNIPPET.md` for a ready-to-paste version.

## License

MIT

---

Built by [Edgeless Labs](https://edgelesslab.com) -- a creative technology lab building AI agents, developer tools, and generative art.

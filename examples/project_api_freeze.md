---
name: API Breaking Change Freeze
description: No breaking API changes until mobile release branch cut on 2026-03-15
type: project
---

Breaking API changes are frozen until 2026-03-15 (mobile release branch cut).

**Why:** Mobile team is cutting release branch and their integration tests
pin against the current API contract. Breaking changes would require a
coordinated re-test cycle that delays the App Store submission deadline.

**How to apply:** Any API endpoint modifications must be backwards-compatible.
New endpoints are fine. Additive fields are fine. Flag any PR that removes
fields, changes response shapes, or modifies status codes. After March 15,
the freeze lifts and we can ship the v2 response format.

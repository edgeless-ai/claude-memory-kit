---
name: No mocking database in integration tests
description: Integration tests must use real database, never mocks -- learned from prod incident
type: feedback
wing: backend
room: testing
---

Integration tests must hit a real database, not mocks.

**Why:** Q4 2025, mocked tests passed but the prod migration failed because mocks
diverged from actual PostgreSQL behavior around NULL handling in JSONB columns.
Three hours of downtime.

**How to apply:** When writing or reviewing any test that touches the database layer,
always use the test database container (docker-compose.test.yml). Never mock the
database connection, query builder, or ORM. Unit tests for pure logic are fine to mock.

---
id: ARCH-064-COMMERCE-002
architecture_id: ARCH-064
title: correct production purpose membership reader
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: review
priority: 30
executor: codex
claimed_at: 2026-11-06T21:57:59Z
attempt: 1
depends_on: ["ARCH-064-COMMERCE-001", "ARCH-064-DATABASE-001", "ARCH-064-SHARED-004"]
enables: ["ARCH-064-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-06
---
# Correct production purpose membership reader

## Architecture
ARCH-064; docs/architecture/ARCH-064-published-initial-outreach-profile.md. Coordinator moda_architect.

## Objective
Make the production publication storage reader load immutable purpose memberships through actual generated Prisma relations.

## Context
After Commerce Attempt2 acceptance, MCP typed production-reader review demonstrated an adapter integration defect missed by custom storage test typing: accepted Commerce bef213b publication-storage.ts readState line108 uses CommerceRelease include purposeMemberships, but accepted Database379d563 CommerceRelease has no such relation. Actual joins are CommerceReleaseFeature.purposeMembers and CommerceReleaseCapability.purposeMemberships. Existing Complete task history remains unchanged; this independently reviewable production integration correction closes the newly demonstrated defect.

## Scope
src/commerce/integration/backend/publication-storage.ts readState/state projection and focused production query-shape/roundtrip tests. Use nested Feature purposeMembers (or separate exact release-key query) with deterministic position order, preserving complete immutable snapshot capability/release/feature IDs. Add generated Prisma type proof at query boundary to prevent custom port types hiding invalid relations.

## Out of Scope
Database schema changes, new relations, copied membership definitions, UI/seed redesign, runtime permissions, live migration/activation, main merge or MCP/Background code.

## Requirements
Production read must match accepted generated Prisma schema. Draft and immutable release membership stay distinct; no mutable draft fallback. Empty/foreign/missing membership continues fail-closed. No reset or rewrite of existing releases.

## Work Items
- [x] Correct actual production include/query and deterministic projection.
- [x] Prove query satisfies generated Prisma types and add reader-shaped fixture/roundtrip coverage.

## Interfaces / Contracts
Accepted DB379d563 joins; Shared5.5.0 purpose profile; existing PublicationState/ExactReleaseSnapshot contracts. No new cross-service wire contract.

## Dependencies
- ARCH-064-COMMERCE-001
- ARCH-064-DATABASE-001
- ARCH-064-SHARED-004

## Enables
- ARCH-064-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Generated Prisma client accepts production query; no nonexistent CommerceRelease.purposeMemberships include.
- [x] Production-shaped records preserve exact ordered release purpose links/feature behavior and immutable IDs across read/write/read; no draft lookup fallback.
- [x] Missing/foreign links remain rejected and ordinary release behavior unchanged.

## Validation
- [x] Focused production storage/reader and purpose publication tests, including generated Prisma query type proof.
- [x] Declared production typecheck; disposable integration if needed to prove real Prisma query execution. No live database.

## Stop Condition
Publish source/report and submit review, then STOP. Explicit developer completion required; no enabled task auto-start.

## Implementation Notes
MCP reader independently fixed its own analogous shape with a generated Prisma.CommerceReleaseInclude proof; reuse actual schema semantics, not sibling source imports. Do not add a direct database relation solely to make wrong include valid.

## Completion Report

### Status
Ready for Review — Attempt 1. Implementation and required local validation passed; architect review and explicit developer completion pending.

### Files Changed
- src/commerce/integration/backend/publication-storage.ts
- tests/publication-storage-release-delta.test.ts
- tests/publication-storage-audit-delta.test.ts

### Work Completed
Corrected production release query to nested features.purposeMembers, with generated Prisma.CommerceReleaseInclude type proof. Capability and membership position ordering is explicit; features have deterministic featureId order. Projection flattens immutable feature links and rejects foreign release/feature/capability identities. It preserves release feature behavior, revision/capability IDs and ordered membership without mutable draft fallback. Ordinary release handling remains intact.

Production-shaped fixture asserts the exact nested query and exercises write/read/no-op/read identity and behavior preservation. Missing immutable links stay empty despite draft membership and fail existing PROFILE_EMPTY validation. Foreign-link fixtures reject. Adjacent audit-delta fixture required its two already-existing delegates to be supplied.

### Validation Results
- `npm run prisma:generate`: passed using accepted Database 379d563 schema.
- `npx vitest run tests/publication-storage-release-delta.test.ts tests/publication-storage-audit-delta.test.ts tests/initial-outreach-publication.test.ts tests/initial-outreach-seed.test.ts`: 17 tests passed.
- `npm run typecheck:build`: passed, including generated Prisma query proof and production TypeScript compilation.
- `npx eslint src/commerce/integration/backend/publication-storage.ts tests/publication-storage-release-delta.test.ts tests/publication-storage-audit-delta.test.ts`: passed.
- `git diff --check`: passed.

### Deviations / Assistance
Material moda_commerce agent assistance implemented source/tests; root coordinated publication/report. No schema/dependency/generated tracked-file changes. Updated stale audit fixture delegates after focused test exposed missing fixture methods; no production scope expansion.

### Validation Limits / Unresolved Issues
Generated client type proof validates the production relation and local fixtures validate projection/roundtrip. No actual SQL, disposable PostgreSQL or deployed database execution claimed. No blocking scoped issue remains; integrated runtime completion remains owned by architecture/system validation.

### Git / VCS
Task branch: task/ARCH-064-COMMERCE-002.
Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-064-COMMERCE-002.
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-064-COMMERCE-002.
Both branches match task/ARCH-064-COMMERCE-002. Shared/default checkouts switched/mutated for task work: no. Other task worktree reused: no.
Start synchronization: parent remote fast-forward not-needed, origin/main already-current; implementation remote fast-forward not-needed, origin/main already-current. Initial parent a9809f1df90bf07a7323e52426ab4ad4cee8f67a; implementation bcc2d5dec2b8bcd3d37447fc6ab0860ada104afa.
Recursive implementation submodules: sync/update passed; database 379d563f6b9ee070305e284615dddbc0b97afeb0 initialized at recorded commit.
Dependency gate passed: COMMERCE-001, DATABASE-001, SHARED-004 Complete.
Durable claim: 18858bbccae861dda8745b1b558044891f785832; Attempt 1 codex at 2026-11-06T21:57:59Z, pushed.
Implementation: 92edcff3b3c344a8031cda18b452968a0161095c pushed origin/task/ARCH-064-COMMERCE-002.
Parent report committed/pushed on matching task branch; exact report commit available in Git history.
Submodule gitlink staged: no. Neither main branch merged/pushed. No enabled task started.

## Architect Review
### Review Status
Pending
### Review Notes
Exact source/schema mismatch verified; no implementation launched.
### Reviewed Files
Commerce bef213b publication-storage.ts:108; DB379d563 schema CommerceRelease and CommerceReleaseFeature/Capability relations.
### Validation Reviewed
Source/schema evidence only.
### Architecture Conformance
Bounded owning-repository production adapter correction; historical acceptance retained.
### Follow-up
None

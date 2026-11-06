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
status: in_progress
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
- [ ] Correct actual production include/query and deterministic projection.
- [ ] Prove query satisfies generated Prisma types and add reader-shaped fixture/roundtrip coverage.

## Interfaces / Contracts
Accepted DB379d563 joins; Shared5.5.0 purpose profile; existing PublicationState/ExactReleaseSnapshot contracts. No new cross-service wire contract.

## Dependencies
- ARCH-064-COMMERCE-001
- ARCH-064-DATABASE-001
- ARCH-064-SHARED-004

## Enables
- ARCH-064-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] Generated Prisma client accepts production query; no nonexistent CommerceRelease.purposeMemberships include.
- [ ] Production-shaped records preserve exact ordered release purpose links/feature behavior and immutable IDs across read/write/read; no draft lookup fallback.
- [ ] Missing/foreign links remain rejected and ordinary release behavior unchanged.

## Validation
- [ ] Focused production storage/reader and purpose publication tests, including generated Prisma query type proof.
- [ ] Declared production typecheck; disposable integration if needed to prove real Prisma query execution. No live database.

## Stop Condition
Publish source/report and submit review, then STOP. Explicit developer completion required; no enabled task auto-start.

## Implementation Notes
MCP reader independently fixed its own analogous shape with a generated Prisma.CommerceReleaseInclude proof; reuse actual schema semantics, not sibling source imports. Do not add a direct database relation solely to make wrong include valid.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Definition only.
### Deviations
None
### Assumptions
Accepted nested relation names remain canonical.
### Unresolved Issues
Production query defect above remains uncorrected.
### Architectural Concerns
Integrated ARCH-064 runtime must not be claimed complete until corrected reader validated.

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

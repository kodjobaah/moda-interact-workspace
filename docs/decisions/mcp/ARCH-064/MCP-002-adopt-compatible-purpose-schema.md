---
id: ARCH-064-MCP-002
architecture_id: ARCH-064
title: Adopt accepted database schema required by pinned purpose reader
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T04:58:14Z
attempt: 1
depends_on:
  - ARCH-064-MCP-001
  - ARCH-064-DATABASE-001
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Adopt accepted database schema required by pinned purpose reader

## Architecture

ARCH-064; docs/architecture/ARCH-064-published-initial-outreach-profile.md; moda_architect.

## Objective

Make the already-implemented typed pinned-purpose reader build and run against its compatible accepted canonical database schema.

## Context

User reports Render build failure src/capabilities/prisma-reader.ts24: purposeMembers missing from generated CommerceReleaseFeatureSelect. Read-only explorer and source inspection confirm MCP main ebbdc07 selects the correct accepted relation but nested Database pinbd2d090 predates it; canonical accepted Database2e14f8668346dfc135aa12f8d1fbc94e05c12ce7 contains purposeMembers and CommerceReleasePurposeCapability. This is dependency drift, not permission to remove scope authorization.

## Scope

MCP-owned nested database gitlink adoption of compatible accepted canonical commit2e14f8668346dfc135aa12f8d1fbc94e05c12ce7; generated-client build/type validation and meaningful existing pinned-purpose reader/auth/runtime tests. Minimal direct test/fixture correction only if genuine gap exposed.

## Out of Scope

Database schema/migration/seed edits, any live DDL/data/provider/Render/Admin operation, Shared release/adoption, removing purposeMembers selection, authorization weakening, unrelated refactor/dependency cleanup or main merge.

## Requirements

- Normal launcher dedicated parent/implementation worktrees and mirrored task branch; preserve all primary untracked files, especially session_export.json/private local data. Do not read/publish sensitive ad-hoc exports or copy them into task source. Primary unrelated staged ARCH069 parent file must remain untouched.
- Reproduce the generated-client/schema mismatch on exact old pin via bounded build/type evidence where practical, then adopt exact accepted Database2e14f8668346dfc135aa12f8d1fbc94e05c12ce7 as nested gitlink, no source migration edits. If current origin main already fixed, report evidence instead of duplicate change.
- Preserve releaseInclude satisfies Prisma.CommerceReleaseInclude, actual immutable Feature.purposeMembers relation and same-release projection. Do not replace typed selection with any/casts/omission or query draft memberships. Existing shop/platform/current release/plan/preference/purpose/capability/revision authority remains fail-closed.
- Fresh normal npm install/client generation must resolve accepted schema and compile purposeMembers. Do not commit generated client/node_modules/dist, inferred Prisma types or copied schema. No database/runtime credentials in logs/report.
- Meaningful runtime validation should exercise actual generated Prisma reader against disposable accepted schema, including pinned purpose subset and denied wrong-release/tenant/permission cases through existing integration harness. Prefer existing coverage; no contrived test merely mirroring gitlink hash.
- Use repository-declared scripts/task validation; inspect actual package.json. Fix only directly related test/fixture mismatch if exposed; report unrelated baseline failures honestly and return wider issues rather than broad cleanup. No new deployment topology/telemetry/publication mechanism.
- Commit/push exact implementation and parent report with ready PR links and remote CI/check evidence. Root owns final source/main and parent actualgitlink merges; no live operations by agent.

## Work Items

- [ ] Verify bounded old generated-client failure and accepted dependency relation.
- [ ] Adopt exact compatible accepted database gitlink without changing authorization/source semantics.
- [ ] Run declared build/types/lint/unit and meaningful disposable pinned-purpose runtime checks.
- [ ] Push exact source/report/PR/check evidence and stop for review.

## Interfaces / Contracts

Existing ARCH064 canonical database purpose membership model and MCP trusted-purpose/current release contract. Existing Shared5.12.5 remains unchanged; no new package release needed. Database adoption consumes accepted source, not a new migration task.

## Dependencies

ARCH-064-MCP-001 and ARCH-064-DATABASE-001 Complete. Exact current accepted canonical Database2e14f8668346dfc135aa12f8d1fbc94e05c12ce7 is root-supplied and already integrated in parent; no new DDL permission.

## Enables

Root source/parent integration and separately owned deployment verification. No application task depends on a system-test task.

## Acceptance Criteria

- [ ] Clean generated Prisma/client build/types recognize purposeMembers and immutable same-release membership.
- [ ] Pinned-purpose subset and tenant/release/auth fail-closed behavior preserved in meaningful runtime tests.
- [ ] Changes bounded to nested pin and necessary direct validation; no Shared/schema/auth weakening.
- [ ] Mirrored clean isolated commits/reports/PRs/remote checks ready for root; primary private files preserved.

## Validation

- [ ] Bounded old-pin failure and new generated-schema/build proof.
- [ ] Declared npm run build,typecheck,lint,test:unit and typecheck:integration where relevant to actual runtime harness.
- [ ] Existing disposable PostgreSQL integration runner covering real purpose reader and denial cases (no hosted DB); report exact executed subset/flags and skips.
- [ ] Diff/privacy/no-generated-file scan, canonical preparation/isolation/synchronization and final remote CI review.

## Stop Condition

When required checks pass, push both task branches, set review and return Completion Report; STOP. Do not merge main, deploy or begin adjacent capabilities.

## Implementation Notes

You are not alone; preserve all other work. Existing reader relation is correct; update dependency rather than weakening query. No new observability or Gateway task identified because build/schema dependency only, no runtime topology change.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root owns final integration/deployment; exact accepted database commit supplied.

### Unresolved Issues

None known beyond dependency drift.

### Architectural Concerns

Return genuine schema/runtime contract gaps before widening.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

No architecture/live completion claim.

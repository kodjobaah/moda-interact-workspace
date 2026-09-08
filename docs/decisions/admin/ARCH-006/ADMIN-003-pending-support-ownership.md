---
id: ARCH-006-ADMIN-003
architecture_id: ARCH-006
title: Implement pending-support queries and exclusive ownership commands
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 65
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-006-ADMIN-001
enables:
  - ARCH-006-ADMIN-004
created: 2026-09-05
updated: 2026-09-06T18:01:08Z
---
# ARCH-006-ADMIN-003: Implement pending-support queries and exclusive ownership commands

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Implement the durable pending-work queue queries and atomic take/release/SUPER_ADMIN reassignment server operations without UI.

## Context

This retains the previously confirmed product rule: assignment survives logout and remains until explicit release; all active Admins read every thread; only owner sends via ADMIN-001.

## Scope

Admin server queries/commands and focused concurrency/authorization tests for pending-support ownership.

## Out of Scope

- React/Admin visual experience (`ADMIN-004`).
- Message compose implementation (ADMIN-001).
- Redis locks/session ownership.
- Automatic claim on open/send.

## Requirements

Pending query returns bounded/paginated shops where `needsAdminResponse=true`, with filters `all`, `unassigned`, `assigned-to-me`, `assigned-to-others`, safe shop identity, lastMerchantMessageAt and owner summary; no full body in cross-shop list.

Take ownership must be atomic compare-and-set on `assignedPlatformAdminId IS NULL`; two concurrent admins yield exactly one winner. Losing claimant reloads actual owner.

Assigned admin may release only their own thread. SUPER_ADMIN may reassign to another active PlatformAdmin or release. SUPER_ADMIN still must own/reassign to self before sending; do not change ADMIN-001 send check.

Assignment persists independently of read state, pending clearing, logout and worker/server restart.

## Work Items

- [x] Implement bounded pending-support query/filter/order.
- [x] Implement atomic unassigned->current-admin claim.
- [x] Implement owner-only release.
- [x] Implement SUPER_ADMIN active-admin reassign/release.
- [x] Add concurrency and privilege tests, including no auto-claim behavior.

## Interfaces / Contracts

Uses DB001 thread assignment/pending fields. ADMIN-001 remains the send authorization boundary.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-ADMIN-004`

## Acceptance Criteria

- [x] All active Admins can list/read pending threads.
- [x] Pending/read states remain independent.
- [x] Exactly one concurrent claimant wins.
- [x] Assignment survives pending becoming false.
- [x] Ordinary admin cannot release/steal another owner.
- [x] SUPER_ADMIN reassign validates target active admin and does not bypass send ownership.
- [x] Queries are bounded/paginated.

## Validation

Focused concurrency/auth/query tests plus repository-declared validation and `git diff --check`.

## Implementation Notes

No UI in this task; keeping it server-only makes ownership correctness independently reviewable.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/src/app/actions/merchant-support.ts`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`

### Work Completed

- Added bounded, paginated pending-support reads with all four filters, safe Shop domain identity, owner summary, and no message body.
- Added atomic unassigned-to-current-admin compare-and-set claims; losing claimants reload the durable owner.
- Added owner-only release for ordinary admins and SUPER_ADMIN release/reassignment with active-target validation.
- Added authenticated server actions for take, release, and reassign without adding UI or changing ADMIN-001 send authorization.
- Added focused behavior coverage for bounded queries, no auto-claim reads, one-winner concurrency, owner reload, release privileges, and reassignment.

### Validation Results

- `node --test tests/security/admin-merchant-support.test.mjs`: 10 passed.
- `npm test`: 91 passed, 1 failed due the known stale `0.7.0` internationalization assertion; current accepted Shared dependency is `0.7.1`.
- `npx tsc --noEmit --pretty false`: passed.
- `npm run lint`: 0 errors, 2 pre-existing React Hook warnings in `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed, with existing Next workspace-root and optional BullMQ `@valkey/valkey-glide` warnings.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- Touched-file diagnostics reported no errors.

### Deviations

No schema, UI, worker, shared-contract, or cross-repository changes were made. The full-suite stale `0.7.0` assertion was not changed because it is outside ADMIN-003 scope.

### Assumptions

The ownership commands rely on the existing support schema and active PlatformAdmin records supplied by DATABASE-001/ADMIN-001.

### Unresolved Issues

The repository-wide suite retains one unrelated stale internationalization assertion until its owning task corrects it.

### Architectural Concerns

No architectural concerns identified within ADMIN-003. Ownership state remains durable in PostgreSQL and ADMIN-001 remains the send authorization boundary.

## Architect Review

### Review Status

Accepted — Complete.

### Independent Review

`moda_architect` independently reviewed Attempt 1 against the task contract and implementation snapshot. The pending-support query is bounded/paginated, exposes safe shop/owner metadata without message bodies, and preserves pending/read independence. Ownership claim uses an atomic compare-and-set on `assignedPlatformAdminId IS NULL`, so concurrent claimants cannot both win; the losing claimant reloads the durable owner. Ordinary release is owner-scoped, SUPER_ADMIN may release or reassign, and reassignment validates an active PlatformAdmin. Assignment remains PostgreSQL-durable and ADMIN-001 remains the exclusive send-authorization boundary.

Focused validation passed 10/10 plus typecheck, build, Prisma validation and `git diff --check`. The known stale Shared `0.7.0` full-suite assertion remains an unrelated baseline failure and does not block acceptance. No UI, schema, worker, shared-contract or downstream implementation was introduced.

### Coordination Decision

`ARCH-006-ADMIN-003` is Complete. `ARCH-006-ADMIN-004` remains Pending because its other declared dependency, `ARCH-006-BACKGROUND-007`, is not yet Complete. No downstream Admin task is promoted by this acceptance.

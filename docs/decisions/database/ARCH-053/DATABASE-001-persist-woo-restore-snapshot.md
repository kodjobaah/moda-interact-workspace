---
id: ARCH-053-DATABASE-001
architecture_id: ARCH-053
title: Persist generation-specific Woo restoration snapshot
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-053-API-002
- ARCH-053-BACKGROUND-002
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-DATABASE-001 — Persist generation-specific Woo restoration snapshot

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Persist generation-specific Woo restoration snapshot. One bounded outcome in `moda-interact-database` owned by `moda_database`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Ready** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Modify only `moda-interact-database/prisma/schema.prisma` and one new migration under `moda-interact-database/prisma/migrations/<timestamp>_arch053_woo_restore_snapshot/migration.sql`; appropriate schema/migration tests in this repository.
- Add `wooRestoreSnapshot Json?` to `model CheckoutRecovery` adjacent to `lineItems`, in `@@schema("commerce")`; preserve existing `checkoutUrl String?`, `lineItems Json?`, `generation` and `@@unique([shopId, checkoutToken, generation])` without modification.
- Add a nullable JSONB column to the existing `commerce."CheckoutRecovery"` table, no defaults/backfill and no row rewrites. Existing rows continue to mean `wooRestoreSnapshot = null` = restoration evidence unavailable.

## Out of Scope

No URL generation, API, Woo PHP, Background code, database triggers, publication or unrelated schema cleanup.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- No storage of bearer token in a new table, no WordPress transient, no update to unrelated coupon/catalogue models. The new JSON field records the immutable, validated capture snapshot at **recovery admission**, not cart state across subsequent generations.
- Do not add an index on arbitrary JSON content without a demonstrated query: resolution selects by recovery ID/shop and generation, not JSON scanning. Preserve all existing foreign keys and multitenant uniqueness.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [ ] Add nullable Prisma field and corresponding DDL.
- [ ] Add schema/migration compatibility check; compare existing vs migrated recovery with/without the field.
- [ ] Document database rollback/data preservation limitations.

## Interfaces / Contracts

Consumer: Background `ARCH-053-BACKGROUND-002` writes at admission; API `ARCH-053-API-002` reads. Structural JSON schema is `ARCH-053-SHARED-001`, not defined by Prisma. `null` and unsupported snapshots never produce a URL.

## Dependencies

None — independently executable after materialisation / launcher gate.

## Enables

- `ARCH-053-BACKGROUND-002`
- `ARCH-053-API-002`

## Acceptance Criteria

- [ ] Add nullable Prisma field and corresponding DDL.
- [ ] Add schema/migration compatibility check; compare existing vs migrated recovery with/without the field.
- [ ] Document database rollback/data preservation limitations.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] `npx prisma validate --schema prisma/schema.prisma` and Prisma client generation where available
- [ ] Migration SQL apply/rollback review against isolated Postgres and legacy recovery row
- [ ] No extra constraints or new tables; `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

Before migration, verify the actual database schema name/table casing and existing migration naming. Do not edit nested database submodule copies in consumer repositories; they adopt the accepted database commit through their normal task worktrees.

## Completion Report

### Status

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

Not Started.

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design reconciled against uploaded 2026-10-30 07:59 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.

---
id: ARCH-040-DATABASE-004
architecture_id: ARCH-040
title: Persist platform-controlled human messaging suspension and audit
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-040-ADMIN-001
  - ARCH-040-BACKGROUND-004
  - ARCH-040-API-004
  - ARCH-040-SHOPIFY-001
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-API-002
  - ARCH-040-API-003
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-040-DATABASE-004 — Persist platform-controlled human messaging suspension and audit

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. Portable task definition; no branch, worktree, commit, push or implementation is claimed.

## Objective

Add durable shop-wide platform authority to suspend/restore HUMAN messaging without changing shop installation status, AI operation, conversation mode, or recovery credits.

## Context

The existing `Shop.status=SUSPENDED` stops too much; merchant-editable `ShopFeaturePreference` cannot enforce platform sanctions. Inbound WhatsApp abuse admission protects customer-to-agent traffic, not merchant-originated human sends. Use PostgreSQL as source of truth.

## Scope

- Add `ShopHumanMessagingRestriction` (one current record per shop) and `ShopHumanMessagingRestrictionEvent` (append-only history) in the canonical `commerce` schema, with Prisma relations from `Shop` and `PlatformAdmin`.
- Add a fresh-development Prisma migration and constraints/indexes; avoid historical migration or compatibility work.
- Provide typed, transaction-safe status checks/updates usable by Admin, Shopify server, Woo API and Background without duplicating persistent state.

## Out of Scope

- Do not change existing AI/automation entitlement or full-shop `Shop.status` rules; this is a platform-controlled HUMAN-only restriction.
- No merchant-facing toggle to restore a suspension, no per-employee permission system, no new Conversation or duplicated follow-up credit.
- Do not add new ARCH-040 Shared package publication, Shopify-to-Woo/API dependencies or `docs/decisions/**/_index.md` files.
- No speculative new service, queue platform or third-party AI moderation provider.

## Requirements

### Explicit data model

- `HumanMessagingRestrictionStatus = ACTIVE | SUSPENDED`; absent restriction row means ACTIVE (existing shops allowed by default). Do not derive this status from billing entitlements, user preferences, or `Shop.status`.
- `ShopHumanMessagingRestriction`: `shopId` primary/unique FK to `Shop`, `status`, `revision` (integer, monotonic), `reasonCode` (bounded), `reasonNote` (bounded, nullable, admin-only), `suspendedAt`, `restoredAt`, `updatedAt`. Once created, **never delete the row on restoration**; this prevents revision reset and stale replay.
- `ShopHumanMessagingRestrictionEvent`: immutable event ID, `shopId`, `fromStatus`, `toStatus`, `revision`, `reasonCode`, optional bounded `reasonNote`, `platformAdminId` FK to `PlatformAdmin`, `createdAt`; indexed by `(shopId, createdAt, id)`. No individual merchant staff identifiers. Existing administrative principal is legitimate because this is a *platform* action.
- Enforce only supported status values, unique shop restriction, unique `(shopId, revision)` event, bounded reasons and any nullable/timestamp invariants supported by Prisma/SQL. The event records the reason for **both** suspension and restoration.
- Updates use atomic compare-and-set plus event insertion in one PostgreSQL transaction and serialize the initial absent-row creation (e.g., lock the Shop row). A concurrent admin update yields a stable stale-revision conflict. `ACTIVE -> SUSPENDED -> ACTIVE -> SUSPENDED` revisions keep increasing.
- Use an explicit scoped lookup keyed by server-authenticated shop ID. Reads reveal only public status to merchant boundaries; admin-only notes and events must never reach merchant API DTOs.
- No irreversible deletion of records/receipts or conversion of existing `Conversation.controlMode`.

## Work Items

- [ ] Implement the restriction enum, one-row-per-shop model, immutable admin audit model, FK/index/uniqueness constraints.
- [ ] Implement fresh database migration and keep existing recovery, message, and billing models intact.
- [ ] Prove atomic upsert/CAS monotonic revision and event insertion under concurrent admins and restore/re-suspend.
- [ ] Test default ACTIVE for legacy/fresh shops and absence of merchant-visible admin reason notes.

## Interfaces / Contracts

Prisma is the canonical persistence contract. `ADMIN-001` owns the administrative command; Shopify/Woo API and Background enforce the same persisted decision. No Shared contract publication or shop preference toggle.

## Dependencies

None.

## Enables

- ARCH-040-ADMIN-001
- ARCH-040-BACKGROUND-004
- ARCH-040-API-004
- ARCH-040-SHOPIFY-001
- ARCH-040-SYSTEM-TEST-001
- ARCH-040-API-002
- ARCH-040-API-003

## Acceptance Criteria

- [ ] One shop has at most one current restriction and a complete immutable audit trail.
- [ ] An absent row is treated as ACTIVE; restoration does not reset revision or delete history.
- [ ] Concurrent conflicting admin updates cannot silently overwrite each other.
- [ ] Suspension state is independent of AI/HUMAN conversation mode, shop status, subscription and credits.

## Validation

- [ ] Prisma validate plus fresh-db migration replay
- [ ] PostgreSQL race/constraints/foreign-key tests
- [ ] Read/restore/re-suspend audit and privacy tests
- [ ] git diff --check and task worktree evidence

## Stop Condition

After defined work, acceptance criteria and required validation are complete, record Completion Report, set task to review, return control to moda_architect and STOP. Do not begin another task.

## Implementation Notes

Use only the canonical database submodule; no cached Redis-only authority. Record database-owned shapes, not separate app-local shadow models. Use the canonical task preparation/worktree protocol. Check actual repository scripts before running tests; use the published shared logger for structured telemetry without message contents or credentials. No `_index.md` updates until the user explicitly confirms architectural-session completion.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The initiative is proposed; work has not begun.

### Unresolved Issues
None recorded.

### Architectural Concerns
None recorded.

## Architect Review

### Review Status
Pending

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.

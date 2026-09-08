---
id: ARCH-007-ADMIN-004
architecture_id: ARCH-007
title: Add controlled billing-event retry and compensating correction operations
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: pending
priority: 130
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-007-ADMIN-003
  - ARCH-007-BACKGROUND-008
enables: 
  - ARCH-007-SYSTEM-TEST-002
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-07
---

# ARCH-007-ADMIN-004: Add controlled billing-event retry and compensating correction operations

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Provide narrowly authorized operational actions to retry eligible failed App Events and create auditable negative corrections without editing historical usage.

## Context

App Event delivery directly affects revenue and merchant invoices. Support needs safe recovery tools, but actions must preserve permanent idempotency and append-only ledger semantics.

## Scope

Admin server actions/UI confirmations/audit/tests for retry and correction only.

## Out of Scope

- Direct provider HTTP calls from Admin.
- Editing/deleting UsageEvent rows.
- Changing Shopify plan price/tier.
- Bulk automatic correction based only on reconciliation mismatch.

## Requirements

- Retry action is SUPER_ADMIN-only and permitted only for a UsageEvent in RETRYABLE or explicitly recoverable NEEDS_ATTENTION after configuration has been corrected. It changes durable state/nextReportAt so the billing worker republishes; Admin never POSTs App Events directly.
- Retry preserves original quantity, occurredAt, shopifyEventHandle and permanent shopifyIdempotencyKey.
- Correction action is SUPER_ADMIN-only, requires one original positive reportable UsageEvent and human reason, and appends a linked negative UsageEvent with a new deterministic permanent idempotency key. It never edits/deletes original.
- Prevent correction beyond net original quantity unless architect-approved semantics explicitly allow it; repeated form submit must be idempotent and cannot create multiple identical corrections.
- Every action writes BillingAuditEvent with actor/reason/original/correction/retry before-after state in same DB transaction where practical.
- UI includes clear confirmation that financial billing may change; do not expose an arbitrary numeric event editor unless task validation proves bounded correction semantics.
- Worker remains sole App Events network publisher.

## Work Items

- [ ] Implement retry state-reset action with authorization and immutable event-field checks.
- [ ] Implement linked negative correction creation with replay protection/net-bound validation.
- [ ] Add confirmation/status UI from ADMIN-003 event detail.
- [ ] Write audit events.
- [ ] Add security, repeated-submit, over-correction and field-immutability tests.

## Interfaces / Contracts

Admin mutation -> PostgreSQL durable state -> BACKGROUND-008 worker -> Shopify. No Admin -> Shopify direct network path.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-SYSTEM-TEST-002
- ARCH-007-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Retry preserves permanent App Event identity.
- [ ] Correction is append-only and linked; original stays unchanged.
- [ ] Repeated correction request cannot double-credit.
- [ ] Unauthorized roles/actions are rejected.
- [ ] Every financial action is audited.
- [ ] Tests/validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Do not run `git commit` or `git push`.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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

None

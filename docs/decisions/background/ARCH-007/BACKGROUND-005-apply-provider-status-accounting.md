---
id: ARCH-007-BACKGROUND-005
architecture_id: ARCH-007
title: Apply normalized Meta provider status to durable message and usage accounting
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: in_progress
priority: 100
executor: copilot
claimed_at: 2026-09-08T15:32:26Z
attempt: 1
depends_on: 
  - ARCH-007-BACKGROUND-004
  - ARCH-007-MESSAGING-001
  - ARCH-007-SHARED-004
enables: 
  - ARCH-007-BACKGROUND-008
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-08T15:32:26Z
---

# ARCH-007-BACKGROUND-005: Apply normalized Meta provider status to durable message and usage accounting

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Consume the Shared normalized provider-status event idempotently and apply delivered/read/failed lifecycle plus delivered-message usage/provider metadata without making Meta status alter Shopify conversation billing incorrectly.

## Context

ARCH-007 tracks outbound safety at send admission and provider lifecycle separately. Messaging owns webhook ingress; Background owns durable ConversationMessage and usage/accounting state.

## Scope

Messaging queue consumer/handler and durable Background service/tests for normalized provider status. Reuse existing messaging worker router topology; do not create competing Workers on the same queue.

## Out of Scope

- Raw Meta webhook parsing.
- Shopify App Events publishing.
- Exact Meta pricing-rate engine.

## Requirements

- Validate Shared normalized status schema at consumer boundary.
- Resolve the durable outbound ConversationMessage by `providerMessageId`; derive the owning shop only from durable local message/usage/recovery state created by BACKGROUND-004, never from a producer-supplied `shopId`. Unknown ID is a bounded no-op/operational warning, not a cross-tenant guess.
- Consume provider-status schema v2 from exact Shared `0.7.4`: `providerAccountId`, `providerPhoneNumberId`, and `providerMessageId` are observed provider identities. They may be used for bounded consistency/diagnostic checks, but MUST NOT select or guess a different tenant.
- Make status transitions monotonic/idempotent: duplicate DELIVERED/READ does not create duplicate usage; READ may imply delivered timestamp only according to existing message semantics; FAILED must not regress an already DELIVERED/READ message.
- On first delivered transition create exactly one DELIVERED_WHATSAPP_MESSAGE UsageEvent with deterministic message identity. Shopify report state is NOT_APPLICABLE.
- Persist bounded provider pricing/category metadata only in schema fields/provider response locations already accepted; if exact cost is unavailable leave cost unknown rather than calculating from hard-coded rates.
- Use existing messaging worker process/router; no dedicated competing Worker on the same queue name.
- Emit structured domain outcome through shared logger without full customer payload.

## Work Items

- [ ] Implement status consumer handler/service.
- [ ] Add monotonic/idempotent transition logic.
- [ ] Create delivered usage once.
- [ ] Persist optional bounded metadata.
- [ ] Add duplicate/out-of-order/unknown-provider-id/cross-tenant focused tests.

## Interfaces / Contracts

Input is exactly Shared provider-status schema v2 published as `@modainteract/moda-interact-shared@0.7.4` and produced by the architect-accepted MESSAGING-001 Attempt 3. The event contains no `shopId`. Background resolves the owning shop from durable local outbound message/usage state using `providerMessageId`. Output is durable ConversationMessage lifecycle + NOT_APPLICABLE delivered usage.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-BACKGROUND-008
- ARCH-007-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Duplicate/out-of-order statuses cannot duplicate delivered usage or regress final state.
- [ ] Unknown provider ID cannot update another shop.
- [ ] No producer-supplied or fabricated `shopId` is required for provider-status routing.
- [ ] No raw webhook parsing exists in Background.
- [ ] No exact Meta monetary amount is fabricated.
- [ ] Tests and worker validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes

Exact provider-status Shared dependency for this task: `@modainteract/moda-interact-shared@0.7.4`.


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Do not run `git commit` or `git push`.


## Completion Report

### Status

In Progress

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

---
id: ARCH-007-BACKGROUND-005
architecture_id: ARCH-007
title: Apply normalized Meta provider status to durable message and usage accounting
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: review
priority: 100
executor: copilot
claimed_at: 2026-09-08T16:15:07Z
attempt: 2
depends_on: 
  - ARCH-007-BACKGROUND-004
  - ARCH-007-MESSAGING-001
  - ARCH-007-SHARED-004
enables: 
  - ARCH-007-BACKGROUND-008
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-08T16:21:49Z
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

- [x] Implement status consumer handler/service.
- [x] Add monotonic/idempotent transition logic.
- [x] Create delivered usage once.
- [x] Persist optional bounded metadata.
- [x] Add duplicate/out-of-order/unknown-provider-id/cross-tenant focused tests.

## Interfaces / Contracts

Input is exactly Shared provider-status schema v2 published as `@modainteract/moda-interact-shared@0.7.4` and produced by the architect-accepted MESSAGING-001 Attempt 3. The event contains no `shopId`. Background resolves the owning shop from durable local outbound message/usage state using `providerMessageId`. Output is durable ConversationMessage lifecycle + NOT_APPLICABLE delivered usage.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-BACKGROUND-008
- ARCH-007-SYSTEM-TEST-003

## Acceptance Criteria

- [x] Duplicate/out-of-order statuses cannot duplicate delivered usage or regress final state.
- [x] Unknown provider ID cannot update another shop.
- [x] No producer-supplied or fabricated `shopId` is required for provider-status routing.
- [x] No raw webhook parsing exists in Background.
- [x] No exact Meta monetary amount is fabricated.
- [x] Tests and worker validation pass.

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

Ready for Review (Attempt 2)

### Files Changed

src/services/whatsapp-provider-status.service.ts
src/workers/whatsapp.worker.ts
tests/unit/services/whatsapp-provider-status.service.test.ts

### Work Completed

Added the schema-validated `message-status` consumer to the existing `whatsapp-events` worker. The consumer resolves ownership from the durable outbound message relation, applies monotonic SENT/DELIVERED/READ/FAILED lifecycle updates, creates one deterministic NOT_APPLICABLE delivered usage event, and stores bounded accepted provider metadata in `providerResponseSummary`. Unknown and unowned messages are bounded no-ops with structured operational logging.

Attempt 2 addressed every Architect Review correction: lifecycle writes now use serializable transactions, conditional status CAS updates, and bounded `P2034`/CAS retries; provider status is rejected for matching inbound messages; and focused tests cover concurrent READ/DELIVERED and DELIVERED/FAILED races, inbound-boundary isolation, and provider-identity versus durable-shop accounting.

### Validation Results

Focused: `npm exec vitest run tests/unit/services/whatsapp-provider-status.service.test.ts` passed (10 tests).
Build: `npm run build` passed.
Prisma: `npm run prisma:validate` passed.
Full suite: `npm test` reported 369 passed, 7 skipped, and 2 pre-existing failures in `tests/unit/services/pending-recovery-candidate.service.test.ts` (null-context preservation/merge cases); no provider-status tests failed.
Formatting/diff: `git diff --check` passed.
Diagnostics: no errors reported for the changed source files.

### Deviations

The task Implementation Notes name Shared `0.7.4`, while the current architecture and Background package consume the accepted Shared `0.8.0` release. The provider-status v2 billing exports used here are present in `0.8.0`; no dependency downgrade was made.

### Assumptions

None.

### Unresolved Issues

The two unrelated `pending-recovery-candidate` baseline failures remain for architect/developer follow-up.

### Git / VCS

Task branch: task/ARCH-007-BACKGROUND-005

Implementation repository:
  repository: moda-interact-background
  commit: de619dc
  remote branch: origin/task/ARCH-007-BACKGROUND-005
  pushed: yes

Parent workspace:
  task file: docs/decisions/background/ARCH-007/BACKGROUND-005-apply-provider-status-accounting.md
  commit: pending
  remote branch: origin/task/ARCH-007-BACKGROUND-005
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested — Attempt 1

### Review Notes

1. Make provider-status lifecycle transitions concurrency-safe. The current implementation reads the message status and then performs an unconditional `conversationMessage.update` inside a normal transaction. Because the existing WhatsApp worker processes jobs concurrently, two statuses for the same `providerMessageId` can both read the same weaker state and then overwrite each other. A concurrent READ/DELIVERED pair can finish as DELIVERED, and a concurrent DELIVERED/FAILED pair can finish as FAILED. Replace the read/compute/unconditional-write pattern with a conditional/CAS transition (or an equivalent serializable retry design) so a weaker state can never overwrite a stronger durable state. Concurrent delivery/read handling must still create exactly one `DELIVERED_WHATSAPP_MESSAGE` UsageEvent.

2. Enforce the task's outbound-message boundary. `ConversationMessage.providerMessageId` is also used by persisted inbound CUSTOMER messages, but the new service resolves only by `providerMessageId` and does not verify `direction`. A provider-status job must only mutate a durable `OUTBOUND` message. A matching inbound message must be treated as a bounded ignored/invalid ownership case and must not create delivered usage.

3. Add the missing focused regressions required by this task. The Attempt 1 test file covers sequential duplicate/out-of-order handling, invalid/unknown ids and bounded metadata, but it does not contain the checked-off cross-tenant case and it does not exercise the concurrency race above. Add tests proving: (a) concurrent READ/DELIVERED and DELIVERED/FAILED cannot regress final state and delivered usage remains exactly-once; (b) an inbound message cannot be updated/accounted as outbound delivery; and (c) providerAccountId/providerPhoneNumberId (or any rejected producer `shopId`) cannot redirect accounting away from the shop derived from the durable outbound message.

### Reviewed Files

Implementation commit `2bdbe865415feab303e0f17a40cdab1a62c19b1d`:

- `src/services/whatsapp-provider-status.service.ts`
- `src/workers/whatsapp.worker.ts`
- `tests/unit/services/whatsapp-provider-status.service.test.ts`

Cross-checked against the current inbound `ConversationMessage.providerMessageId` persistence path and the accepted Shared provider-status v2 contract.

### Validation Reviewed

- Focused provider-status tests reported passed: 6 tests.
- `npm run build` reported passed.
- `npm run prisma:validate` reported passed.
- targeted formatting and `git diff --check` reported passed.
- full suite reported 365 passed, 7 skipped, with the same 2 unrelated `pending-recovery-candidate` failures already present in prior accepted ARCH-007 Background reviews.
- GitHub exposes no commit status checks for implementation commit `2bdbe865`.

### Architecture Conformance

Not accepted on Attempt 1. Shared schema validation, tenant derivation from durable local state, existing-worker routing, bounded provider metadata, NOT_APPLICABLE delivered usage and no fabricated monetary cost are directionally correct. Concurrency-safe monotonic lifecycle state and the explicit outbound-message boundary remain incomplete.

### Follow-up

Return the same task to `ready`, clear the claim, preserve `attempt: 1`, and reclaim it as Attempt 2. `ARCH-007-BACKGROUND-008` remains Pending until BACKGROUND-005 is architect-accepted Complete. Do not create a separate correction task.

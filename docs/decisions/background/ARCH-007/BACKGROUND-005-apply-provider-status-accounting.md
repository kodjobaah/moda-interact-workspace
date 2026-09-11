---
id: ARCH-007-BACKGROUND-005
architecture_id: ARCH-007
title: Apply normalized Meta provider status to durable message and usage accounting
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 100
executor: null
claimed_at: null
attempt: 2
depends_on: 
  - ARCH-007-BACKGROUND-004
  - ARCH-007-MESSAGING-001
  - ARCH-007-SHARED-004
enables: 
  - ARCH-007-BACKGROUND-008
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

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
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-BACKGROUND-005` branch and the mirrored parent-workspace `task/ARCH-007-BACKGROUND-005` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


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
  commit: 77ece72
  remote branch: origin/task/ARCH-007-BACKGROUND-005
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is architect-accepted Complete.

All Changes Requested from Attempt 1 are resolved:

1. Provider lifecycle transitions are now concurrency-safe. Status writes use a conditional CAS on the durable message id, `OUTBOUND` direction, and previously observed status inside a Prisma `Serializable` transaction. CAS losers and Prisma `P2034` conflicts retry the whole transaction with a bounded retry policy, so a weaker concurrent status cannot overwrite a stronger durable state.

2. Provider-status accounting is now explicitly outbound-only. A matching inbound `ConversationMessage` is a bounded ignored case and cannot be lifecycle-mutated or create `DELIVERED_WHATSAPP_MESSAGE` usage.

3. Focused regression coverage now exercises concurrent READ/DELIVERED and DELIVERED/FAILED races, exactly-once delivered usage during those races, inbound-message isolation, and provider-identity versus durable-shop ownership.

The accepted Attempt 1 behavior remains intact: Shared provider-status v2 validation occurs at the consumer boundary; tenant ownership is derived only from durable local message/conversation/recovery state; unknown/unowned ids are bounded no-ops; the existing `whatsapp-events` Worker remains the single queue consumer topology; delivered usage is deterministic and `NOT_APPLICABLE` for Shopify; provider metadata is bounded; and no exact Meta monetary amount is fabricated.

The repository's accepted Shared `0.8.0` dependency is retained. The older `0.7.4` wording in this task's Implementation Notes is superseded by the current accepted ARCH-007 Shared release and is not a reason to downgrade.

### Reviewed Files

Implementation branch cumulative task surface:

- `moda-interact-background/src/services/whatsapp-provider-status.service.ts`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/tests/unit/services/whatsapp-provider-status.service.test.ts`

Attempt 2 implementation commit:

- `de619dc7dd49756598d9e853f4b2555cf754bf34`

Parent task-report commit reviewed:

- `77ece727ac4b7fc4d7f9b5cd50fb1724b0079a8d`

### Validation Reviewed

- Focused provider-status suite reported passed: 10/10.
- `npm run build` reported passed.
- `npm run prisma:validate` reported passed.
- `git diff --check` reported passed.
- Full suite reported 369 passed, 7 skipped, with the same 2 unrelated existing `pending-recovery-candidate` failures; no provider-status regression failed.
- GitHub exposes no commit status checks for `de619dc7dd49756598d9e853f4b2555cf754bf34`.
- The supplied archive does not contain the Background submodule working tree; the pushed implementation commit and exact source/tests were therefore independently reviewed from GitHub.

### Architecture Conformance

Accepted. The implementation now satisfies the ARCH-007 provider-status ownership, monotonic lifecycle, idempotent delivered-usage, bounded metadata, and existing-worker-topology requirements.

### Follow-up

`ARCH-007-BACKGROUND-005` is Complete. `ARCH-007-BACKGROUND-008` remains Pending until its other incomplete dependency or dependencies are architect-accepted Complete. System-test work remains manual/terminal-gated and is not automatically started by this acceptance.

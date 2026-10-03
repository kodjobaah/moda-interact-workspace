---
id: ARCH-028-BACKGROUND-001
architecture_id: ARCH-028
title: Adopt WhatsApp provider-status v3 and persist failure evidence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-DATABASE-001
  - ARCH-028-SHARED-002
enables: []
created: 2026-10-03
updated: 2026-10-03
---

# Adopt WhatsApp provider-status v3 and persist failure evidence

## Architecture

Architecture ID:

`ARCH-028`

Architecture document:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator:

`moda_architect`

## Objective

Adopt the exact published ARCH-028 dual-version WhatsApp provider-status contract in `moda-interact-background` and persist bounded provider-failure evidence on outbound `ConversationMessage` rows while preserving all existing status-ordering, delivered-usage and retry semantics.

This is a **consumer-compatibility and evidence-persistence task only**. It must make Background safe to receive either legacy v2 or current v3 status events before Messaging begins producing v3, without yet changing recovery, billing, follow-up, reachability or merchant-notification behaviour.

## Context

The current Background provider-status consumer imports:

```text
safeParseNormalizedWhatsAppStatus
NormalizedWhatsAppStatus
```

from `@modainteract/moda-interact-shared/billing`, then applies the normalized status inside a Serializable transaction in:

```text
src/services/whatsapp-provider-status.service.ts
```

Current durable behaviour includes:

- strict runtime validation before database access;
- outbound-message ownership checks;
- monotonic `PENDING -> SENT -> DELIVERED -> READ` progression;
- `PENDING|SENT -> FAILED`;
- late `FAILED` cannot regress `DELIVERED`/`READ`;
- later `DELIVERED` may advance an earlier `FAILED`;
- one idempotent `DELIVERED_WHATSAPP_MESSAGE` usage event;
- Serializable retry/CAS handling for concurrent status delivery.

`ARCH-028-DATABASE-001` adds nullable:

```text
ConversationMessage.providerFailureCode
ConversationMessage.failedAt
```

and the tenant-scoped reachability table. This task uses only the two message fields. It must **not** write reachability state yet.

`ARCH-028-SHARED-001` defines a canonical parser that accepts both legacy v2 and current v3 status events, and `ARCH-028-SHARED-002` publishes the exact accepted package revision. Background must install that published version before Messaging emits v3.

## Scope

Authorised `moda-interact-background` implementation surface:

```text
package.json
package-lock.json
database                         # nested database submodule/gitlink only
src/services/whatsapp-provider-status.service.ts
tests/unit/services/whatsapp-provider-status.service.test.ts
```

`tests/unit/workers/whatsapp.worker.test.ts` may be changed only if a focused worker-level v2/v3 compatibility assertion is genuinely required; do not alter unrelated inbound-message coverage.

The task owns:

1. adoption of the exact Shared version published by SHARED-002;
2. adoption of the accepted DATABASE-001 schema in the nested database dependency;
3. dual-version v2/v3 provider-status consumption through the canonical Shared parser;
4. bounded `FAILED` evidence persistence on `ConversationMessage`;
5. idempotent enrichment of an already-FAILED legacy/v2 row when later v3 evidence supplies a missing provider code;
6. focused regression coverage proving existing status ordering/accounting remains unchanged.

## Out of Scope

- Parsing Meta webhook `statuses[].errors`; Messaging owns producer normalization later.
- Emitting provider-status v3 from Messaging.
- Defining a provider-code classification table.
- Deciding whether a code means terminal-recipient, temporary-provider, configuration or ambiguous failure.
- Writing `WhatsAppRecipientReachability`.
- Choosing suppression TTL.
- Changing `RecoveryOutreachAttempt`, `CheckoutRecovery` or follow-up scheduling.
- Releasing/compensating recovery usage or restoring recovery capacity.
- Creating merchant SYSTEM notifications.
- Changing synchronous outbound-send rejection classification.
- Changing delivered usage accounting or `providerResponseSummary` semantics.
- Modifying database schema/migrations directly from the Background repository.
- Copying/redefining the Shared v2/v3 schemas locally.
- Modifying `docs/architecture/_index.md`.

## Requirements

### R1 — Consume the exact published Shared revision

Read the exact package version published and recorded by `ARCH-028-SHARED-002`. Update `moda-interact-background/package.json` and `package-lock.json` to that exact version.

Do not use:

```text
workspace links
file: dependencies
local npm links
copied Shared source
range/wildcard substitution for the ARCH-028 release
```

The Background source must continue importing the canonical parser/type from:

```text
@modainteract/moda-interact-shared/billing
```

### R2 — Consume the accepted DATABASE-001 schema

The prepared implementation worktree must resolve the nested `database` dependency to the accepted/merged DATABASE-001 implementation containing:

```text
ConversationMessage.providerFailureCode
ConversationMessage.failedAt
```

Update only the Background repository's database gitlink/submodule dependency as required by the normal workspace workflow. Do not edit Prisma schema/migrations from this task.

If the accepted DATABASE-001 implementation is not available through the prepared dependency state, STOP and return the dependency gap to `moda_architect`.

### R3 — Continue accepting legacy v2 statuses

After the Shared upgrade, existing v2 provider-status payloads must continue through the same `safeParseNormalizedWhatsAppStatus(...)` path and retain all current lifecycle/accounting behaviour.

Do not coerce v2 into v3 or invent a provider code.

### R4 — Accept v3 and persist bounded FAILED evidence

For a valid v3 `FAILED` event carrying:

```text
failure.providerCode
```

when the durable outbound message is currently `PENDING` or `SENT`, the same Serializable transaction that applies the FAILED lifecycle transition must persist:

```text
status = FAILED
failedAt = event.occurredAt when failedAt is currently null
providerFailureCode = event.failure.providerCode when providerFailureCode is currently null
```

For a valid v2 FAILED event, persist `failedAt` when missing but leave `providerFailureCode` null.

Do not persist raw provider text/details/body/metadata.

### R5 — Allow evidence enrichment for an already-FAILED legacy row

A message already in `FAILED` may have been produced from a v2 event or an earlier v3 event without failure evidence. A later valid v3 FAILED duplicate may fill a currently-null `providerFailureCode` without changing status.

Rules:

- preserve an existing non-null `providerFailureCode`; never overwrite it with a later different code in this task;
- preserve an existing non-null `failedAt`;
- if durable evidence is newly added, return the service outcome as `applied`;
- an exact duplicate/no-op remains `ignored`;
- duplicate/concurrent enrichment remains retry-safe/idempotent under the existing Serializable/CAS mechanism.

### R6 — Late FAILED must not contaminate delivered/read messages

If the durable message is already `DELIVERED` or `READ`, a later FAILED event remains ignored exactly as today. It must not:

```text
regress status
set failedAt
set providerFailureCode
create reachability state
create compensation state
```

This requirement preserves the current monotonic delivery authority.

### R7 — Later delivery may still advance FAILED while retaining history

The current service allows a later `DELIVERED`/`READ` event to advance an earlier FAILED message. Preserve that behaviour.

If the message already contains `failedAt`/`providerFailureCode`, later successful delivery does not erase that historical message-level evidence in BACKGROUND-001. Later reachability tasks may use positive delivery evidence to clear **recipient suppression**, but they must not rewrite this task's historical message evidence.

### R8 — Preserve delivered usage accounting

Do not change:

```text
DELIVERED_WHATSAPP_MESSAGE usage-event identity
whatsapp-delivered:<messageId> idempotency key
shop ownership derivation
providerResponseSummary for delivered usage
```

A FAILED event never creates a delivered-usage event. Provider failure evidence must not be appended to unrelated delivered usage summaries.

### R9 — Preserve transaction/retry/ownership semantics

Retain:

- runtime validation before database access;
- outbound-only enforcement;
- durable Shop ownership derivation from the Conversation/CheckoutRecovery;
- Serializable transaction isolation;
- bounded retry on existing CAS/P2034 conflicts;
- no Shop execution-eligibility lookup for provider-status finalization.

Do not move provider-status handling behind merchant lifecycle/execution admission. Provider statuses must continue finalizing already-created outbound messages even if the Shop later becomes inactive.

### R10 — No ARCH-028 policy side effects yet

BACKGROUND-001 must not classify `providerFailureCode` or perform any downstream action based on its value. In particular it must not:

```text
mark recipient suppressed
write WhatsAppRecipientReachability
fail RecoveryOutreachAttempt
cancel/suppress follow-up
compensate usage
restore merchant capacity
notify merchant
```

Those behaviours require later explicit Background tasks.

## Work Items

- [ ] Update the nested database dependency to the accepted DATABASE-001 implementation.
- [ ] Install the exact Shared package version published by SHARED-002 and update the lockfile deterministically.
- [ ] Extend the provider-status consumer to persist bounded failure code/time evidence under the existing transaction/CAS semantics.
- [ ] Preserve legacy v2 status processing unchanged except for recording `failedAt` on an accepted FAILED transition when missing.
- [ ] Support idempotent v3 enrichment of an already-FAILED row with a missing provider code.
- [ ] Add focused tests for v2/v3 parsing, persistence, enrichment, late-failure suppression and later-delivery progression.
- [ ] Preserve all existing delivered-usage/idempotency/ownership/concurrency tests.
- [ ] Run the required Background validation.
- [ ] Complete the Completion Report and return to `moda_architect` at `status: review`.

## Interfaces / Contracts

Shared contract owner:

`ARCH-028-SHARED-001`

Publication gate:

`ARCH-028-SHARED-002`

Published package:

`@modainteract/moda-interact-shared@<SHARED-002 published version>`

Published subpath:

`@modainteract/moda-interact-shared/billing`

Database owner:

`ARCH-028-DATABASE-001`

Durable fields consumed:

```text
whatsapp.ConversationMessage.providerFailureCode
whatsapp.ConversationMessage.failedAt
```

Consumer:

`moda-interact-background/src/services/whatsapp-provider-status.service.ts`

Compatibility:

```text
v2 event -> accepted
v3 event -> accepted
Messaging v3 producer -> MUST remain gated until this consumer task is Complete/deployed
```

## Dependencies

- `ARCH-028-DATABASE-001`
- `ARCH-028-SHARED-002`

Both dependencies must be Complete and architect-accepted. SHARED-002's exact published version and DATABASE-001's accepted database implementation are execution inputs, not values to guess from conversation history.

## Enables

None materialised yet.

After architect acceptance, the next safe rollout step is the Messaging producer task that begins emitting v3 failure evidence. That producer must depend on BACKGROUND-001.

## Acceptance Criteria

- [ ] Background depends on the exact Shared package revision published by SHARED-002.
- [ ] Background's nested database dependency contains the accepted DATABASE-001 fields.
- [ ] Existing valid v2 provider-status events still parse and retain current status/accounting semantics.
- [ ] A v3 FAILED event on PENDING/SENT persists FAILED status, missing `failedAt` and missing `providerFailureCode` atomically.
- [ ] A v2 FAILED event on PENDING/SENT persists missing `failedAt` without inventing a provider code.
- [ ] A v3 FAILED duplicate can enrich an already-FAILED row only when its provider code is currently null.
- [ ] Existing non-null provider failure code/time evidence is never overwritten by later duplicate FAILED events.
- [ ] Newly persisted evidence makes the provider-status outcome `applied`; an exact duplicate remains `ignored`.
- [ ] Late FAILED on DELIVERED/READ does not persist failure evidence or regress state.
- [ ] Later DELIVERED/READ may advance an earlier FAILED message while historical failure evidence remains.
- [ ] Delivered usage-event identity, provider summary, shop derivation and exactly-once accounting remain unchanged.
- [ ] Invalid/unknown/inbound/unowned status handling remains unchanged.
- [ ] Existing Serializable retry/CAS behaviour remains horizontally safe.
- [ ] No provider-code policy classification, reachability, recovery, follow-up, billing-compensation or merchant-notification behaviour is introduced.
- [ ] No local duplicate of the Shared provider-status contract is created.

## Validation

Run from `moda-interact-background` using the scripts actually declared by the current repository:

- [ ] `npm run prisma:generate`
- [ ] `npm run prisma:validate`
- [ ] focused `vitest run tests/unit/services/whatsapp-provider-status.service.test.ts`
- [ ] `npm run test:unit`
- [ ] `npm test`
- [ ] `npm run build` (includes Prisma generation + TypeScript compilation)
- [ ] `git diff --check`

Also verify:

- [ ] `package.json` and `package-lock.json` resolve the exact SHARED-002 version with no local/workspace/file override;
- [ ] the nested `database` dependency resolves to the accepted DATABASE-001 implementation;
- [ ] changed-file/source inspection shows no reachability/compensation/recovery/follow-up/merchant-notification behaviour was added.

Do not invent standalone lint/typecheck commands; this repository currently exposes no such npm scripts, and `npm run build` is the declared TypeScript compilation gate.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

Do not begin the Messaging v3 producer, provider-code classification, recovery convergence, compensation, reachability or merchant-notification tasks.

## Implementation Notes

Keep the existing `WhatsAppProviderStatusService` as the canonical status consumer. Do not introduce a second status worker/service merely for v3.

The current unit test file is a strong regression asset. At definition time it contains 11 tests and SHA-256:

```text
c052c0101ee37c930b056e227c07fe108fc33f97e76ce0e4cbf306f7e70464e4
```

Existing assertions must not be weakened or deleted merely to accommodate v3. Add focused cases to the same suite or an adjacent focused ARCH-028 suite following repository conventions.

The current implementation intentionally permits `FAILED -> DELIVERED/READ` progression but rejects `DELIVERED/READ -> FAILED` regression. Preserve this asymmetry exactly. Historical `providerFailureCode`/`failedAt` on a message that later delivers is evidence about that message lifecycle; it is not by itself authority for continuing recipient suppression.

For evidence enrichment on an already-FAILED row, preserve the first durable non-null provider code/time. The existing Serializable transaction/retry mechanism should remain the concurrency boundary; do not add global locks or serialize all WhatsApp status handling.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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

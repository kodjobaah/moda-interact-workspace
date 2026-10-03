---
id: ARCH-028-MESSAGING-001
architecture_id: ARCH-028
title: Emit WhatsApp provider-status v3 with bounded failure evidence
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-SHARED-002
  - ARCH-028-BACKGROUND-001
enables: []
created: 2026-10-03
updated: 2026-10-03
---

# Emit WhatsApp provider-status v3 with bounded failure evidence

## Architecture

Architecture ID:

`ARCH-028`

Architecture document:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator:

`moda_architect`

## Objective

Upgrade `moda-interact-messaging` to the exact Shared release published by `ARCH-028-SHARED-002`, emit canonical provider-status **v3** events from verified Meta status webhooks, and preserve only bounded provider failure-code evidence for FAILED statuses while retaining existing webhook security, routing, pricing metadata and queue semantics.

This task is the **producer side of the consumer-first rollout**. It must not begin until `ARCH-028-BACKGROUND-001` has proven that Background accepts both v2 and v3 and persists bounded FAILED evidence safely.

## Context

The current verified webhook route is:

```text
moda-interact-messaging/app/routes/whatsapp.tsx
```

It currently:

- verifies `x-hub-signature-256` against the exact raw body before parsing;
- derives provider account identity from `entry.id`;
- derives provider phone-number identity from `change.value.metadata.phone_number_id`;
- derives provider message identity/status/timestamp from `value.statuses[]`;
- normalizes SENT / DELIVERED / READ / FAILED;
- retains bounded optional pricing `{billable, category, model}` without monetary invention;
- validates the candidate through Shared `safeParseNormalizedWhatsAppStatus(...)`;
- publishes `message-status` jobs to the existing `whatsapp-events` BullMQ queue;
- derives a deterministic status job ID from provider account, phone-number ID, message ID and normalized status.

Current Messaging depends on an older exact Shared package revision (`0.12.0` in the supplied baseline) and emits schema version 2. The current normalizer drops `statuses[].errors[]` completely.

`ARCH-028-SHARED-001` defines canonical v3 failure evidence:

```text
failure?: {
  providerCode: string   # trimmed, non-empty, <= 64 characters
}
```

valid only on `FAILED` statuses. `ARCH-028-SHARED-002` publishes the accepted dual-version parser/schema. `ARCH-028-BACKGROUND-001` consumes that release before this producer is allowed to emit v3.

There is one rollout-sensitive queue detail: current status job identity excludes schema version and failure evidence. A retained legacy v2 FAILED BullMQ job can therefore have the same job ID as a later v3 FAILED redelivery that finally carries provider failure evidence. If that later job is deduplicated by BullMQ, Background cannot enrich the durable message with the provider code. This task must refine FAILED evidence job identity without changing normal non-failure identity.

Current source baseline used to define this task:

```text
app/routes/whatsapp.tsx
  430 lines
  SHA-256 9515d857d9f61f00bcbd4271ea6615cdde9e1272857c8d4d43233d089bd6662b

tests/whatsapp-provider-status.test.mjs
  148 lines
  SHA-256 fdbf8c3ac3a8dfefc05aa7e14aa340bb484022e369dba633f0fd94b891ef5018

package.json
  SHA-256 c7a6ee8ff7eaeadfc7e7eaaf73998cee083a2bef51bc47083201fb1e0df40690

package-lock.json
  SHA-256 2183c48ef71f5f9f86e10229a8bd07be41f5e90f7f1a4a41e36104bfb2c3b6a3
```

These hashes are evidence for the task-definition baseline, not an instruction to reject legitimate prerequisite version changes made by SHARED-002 adoption.

## Scope

Repository-owned changes in `moda-interact-messaging`:

- install the **exact** `@modainteract/moda-interact-shared` version published by `ARCH-028-SHARED-002` and update the lockfile deterministically;
- consume the canonical WhatsApp provider-status contract from `@modainteract/moda-interact-shared/billing`;
- change verified provider-status production from schema v2 to schema v3;
- extract bounded provider error-code evidence from the already-verified Meta `status.errors` structure;
- attach canonical `failure.providerCode` only for normalized FAILED statuses and only when a valid bounded code is actually present;
- refine deterministic FAILED job identity so new v3 failure evidence cannot be suppressed by a retained legacy FAILED job while exact evidence duplicates still deduplicate;
- extend focused Messaging tests and the existing Shared-version startup assertion;
- preserve all existing ingress security, inbound-message normalization, queue topology, telemetry and bounded pricing behaviour.

Expected primary implementation/test files:

```text
moda-interact-messaging/package.json
moda-interact-messaging/package-lock.json
moda-interact-messaging/app/routes/whatsapp.tsx
moda-interact-messaging/tests/whatsapp-provider-status.test.mjs
moda-interact-messaging/tests/startup-contract.test.mjs
```

Additional Messaging-owned focused test files may be added only when directly necessary to prove this bounded producer behaviour.

## Out of Scope

- Any edit to `moda-interact-shared`; consume only the exact SHARED-002 registry release.
- Any edit to `moda-interact-background` or database schema.
- Shop/tenant lookup in Messaging.
- Provider-code policy classification such as terminal recipient, temporary provider, configuration or ambiguous failure.
- Asserting that a customer does or does not have a WhatsApp account.
- Recipient reachability/suppression writes.
- RecoveryOutreachAttempt / CheckoutRecovery / follow-up changes.
- Usage release/compensation or recovery-capacity restoration.
- Merchant support notification.
- Synchronous outbound-send HTTP error classification; this task is only the Meta webhook status producer path.
- Raw provider error text/title/message/error-data persistence or logging.
- New queue/channel/topic creation.
- Changes to webhook HMAC verification, inbound customer-message normalization or ingress telemetry semantics.
- `docs/architecture/_index.md` updates; ARCH-028 remains absent from the global index until initiative completion.

## Requirements

### R1 — Adopt the exact published Shared release

Install the exact package version recorded by the architect-accepted `ARCH-028-SHARED-002` Completion Report:

```text
@modainteract/moda-interact-shared@<SHARED-002 published version>
```

Update `package.json` and `package-lock.json` deterministically. Do not use workspace/file/link overrides and do not guess the version from this task definition.

Update the existing startup-contract dependency assertion to the exact published version.

Consume provider-status runtime/type exports from:

```text
@modainteract/moda-interact-shared/billing
```

rather than introducing any Messaging-local copy of the v3 schema.

### R2 — Emit canonical v3 for supported provider statuses

After adoption, every successfully normalized provider status emitted by this producer uses the canonical current schema version from Shared (v3 at the time this task was defined).

Preserve the current supported status set exactly:

```text
sent      -> SENT
delivered -> DELIVERED
read      -> READ
failed    -> FAILED
```

Do not add queued/deleted/warning/unknown statuses in this task.

Preserve current identity/timestamp/pricing normalization and strict Shared validation before queue publication.

### R3 — Extract only bounded provider-code evidence

For normalized `FAILED` statuses only, inspect Meta's `status.errors` value as untrusted input.

Deterministic extraction contract:

1. If `status.errors` is not an array, emit FAILED v3 without `failure`.
2. Inspect error entries in their provider-supplied array order.
3. For each object-like entry, inspect only its `code` field.
4. Accept a code when it is either:
   - a finite integer number; or
   - a string which, after trim, is non-empty and at most 64 characters.
5. Convert an accepted numeric code to its base-10 string representation; trim an accepted string code.
6. Use the **first valid bounded code** in array order and stop scanning.
7. If no valid bounded code exists, emit FAILED v3 without `failure` rather than rejecting the otherwise-valid status event.

Do not retain or inspect for product semantics:

```text
title
message
error_data
href
raw details
raw metadata
```

Do not attach `failure` to SENT / DELIVERED / READ even if a malformed provider payload contains an `errors` array there. Shared v3 validation remains authoritative.

### R4 — Preserve safe failure when identities/status/timestamp are invalid

Continue returning `null` for missing/invalid provider account identity, provider phone-number identity, provider message identity, unsupported status, or invalid occurred-at value exactly as today.

Malformed optional failure evidence must not turn an otherwise valid FAILED status into a webhook-level rejection. Omit invalid evidence and preserve the normalized FAILED event.

### R5 — Preserve bounded pricing behaviour

Retain current optional pricing normalization exactly:

```text
billable
category <= existing bound
model <= existing bound
```

Do not fabricate monetary amount/cost and do not mix provider failure evidence into pricing.

### R6 — Refine deterministic job identity only when new FAILED evidence exists

Preserve the current legacy job-identity material for:

- SENT;
- DELIVERED;
- READ;
- FAILED v3 **without** `failure.providerCode`.

For a canonical v3 FAILED event with bounded `failure.providerCode`, include that normalized provider code in the deterministic hash input in addition to the existing provider account/phone/message/status identity.

Required properties:

- exact duplicate FAILED v3 events carrying the same provider code produce the same bounded job ID;
- different provider codes for the same provider message/status may produce different jobs, allowing Background to receive new evidence while its persistence policy remains first-evidence-wins;
- a v3 FAILED event carrying new failure evidence must not be suppressed solely because a retained legacy v2/no-evidence FAILED job has the old identity;
- non-failure status job IDs remain byte-for-byte compatible with the existing identity algorithm for the same normalized event values;
- job IDs remain within BullMQ's existing bounded identity convention (current `ws-` prefix and maximum 64-character result).

Do not add timestamps to status job identity; repeated Meta delivery of the same evidence must remain deduplicated.

### R7 — Preserve webhook and queue boundaries

Retain:

- HMAC verification over the exact raw request body before JSON processing;
- existing loader verification behaviour;
- existing `messages` field routing;
- existing `whatsapp-events` queue;
- existing `message-status` job name;
- existing attempts/backoff;
- no shop/tenant identity fabrication in Messaging;
- existing bounded ingress telemetry semantics.

Do not add a database lookup merely to classify or route failure evidence.

### R8 — No provider-failure policy in Messaging

Messaging is an evidence producer only.

The task must not decide whether a provider code means:

```text
terminal recipient failure
not registered on WhatsApp
temporary provider failure
configuration failure
ambiguous failure
```

Those decisions belong to later Background policy tasks.

### R9 — Sensitive-data boundary

No new log/metric/trace attribute may contain:

- raw webhook bodies;
- full provider error objects;
- provider error message/title/details;
- customer message content;
- credentials/tokens.

Focused diagnostics/tests may assert bounded provider code only.

## Work Items

- [ ] Verify SHARED-002 and BACKGROUND-001 are Complete and architect-accepted before claiming the task.
- [ ] Install the exact SHARED-002 package revision and update lockfile/startup dependency assertion.
- [ ] Move provider-status imports to the canonical `/billing` subpath where required.
- [ ] Emit canonical v3 normalized provider-status events.
- [ ] Add bounded deterministic `status.errors[].code` extraction for FAILED only.
- [ ] Refine FAILED evidence job identity without changing non-failure identities.
- [ ] Extend focused tests for v3 statuses, numeric/string/bounded/malformed provider codes and absence of raw error data.
- [ ] Extend deterministic job-ID tests for legacy/no-evidence vs evidence-bearing FAILED delivery.
- [ ] Preserve all existing realistic Meta webhook identity/pricing/malformed-input tests.
- [ ] Run required Messaging validation.
- [ ] Complete the Completion Report and return to `moda_architect` at `status: review`.

## Interfaces / Contracts

Shared contract owner:

`ARCH-028-SHARED-001`

Publication gate:

`ARCH-028-SHARED-002`

Consumer-first gate:

`ARCH-028-BACKGROUND-001`

Published package:

`@modainteract/moda-interact-shared@<SHARED-002 published version>`

Published subpath:

`@modainteract/moda-interact-shared/billing`

Producer:

`moda-interact-messaging/app/routes/whatsapp.tsx`

Queue:

```text
whatsapp-events
job name: message-status
```

Consumer:

`moda-interact-background/src/services/whatsapp-provider-status.service.ts`

Compatibility:

```text
old queued v2 -> accepted by Background
new Messaging output -> v3
v3 FAILED may carry bounded failure.providerCode
v3 non-FAILED never carries failure
```

## Dependencies

- `ARCH-028-SHARED-002`
- `ARCH-028-BACKGROUND-001`

Both tasks must be Complete and architect-accepted. BACKGROUND-001 is a deliberate deployment-safety gate, not merely a source-code dependency.

## Enables

None materialised yet.

After architect acceptance, later Background provider-code classification and lifecycle-convergence tasks may safely assume that new verified Meta statuses carry canonical v3 evidence where the provider actually supplies it.

## Acceptance Criteria

- [ ] Messaging resolves the exact SHARED-002 package revision in both manifest and lockfile.
- [ ] The startup dependency-pin regression asserts that exact published version.
- [ ] Provider-status imports use the canonical Shared runtime contract rather than a local schema copy.
- [ ] SENT / DELIVERED / READ normalize to valid v3 without `failure`.
- [ ] FAILED normalizes to valid v3 with no failure evidence when Meta supplies no valid bounded code.
- [ ] A numeric provider error code is normalized to bounded decimal text in `failure.providerCode`.
- [ ] A bounded string provider code is trimmed and retained.
- [ ] Invalid/blank/over-bound provider codes are omitted without dropping the otherwise-valid FAILED status.
- [ ] Multiple error entries select the first valid bounded code in provider array order.
- [ ] Raw provider title/message/error-data/details are absent from the normalized event and from new logs/telemetry.
- [ ] Non-FAILED statuses never carry failure evidence even if the raw status object contains `errors`.
- [ ] Existing provider identity, timestamp and bounded pricing semantics are unchanged.
- [ ] Missing identities/unsupported statuses/invalid timestamps still return null safely.
- [ ] Exact duplicate v3 FAILED evidence produces the same deterministic job ID.
- [ ] Evidence-bearing v3 FAILED has distinct identity from the same FAILED event without evidence, preventing retained legacy job suppression.
- [ ] Non-failure job identity remains unchanged for the same provider identity/status.
- [ ] Existing webhook HMAC verification, queue name/job name/retry policy and inbound-message normalization are unchanged.
- [ ] No tenant lookup, provider-code classification, reachability, compensation, recovery/follow-up or merchant-notification behaviour is added.
- [ ] Existing Messaging tests remain active and assertions are not weakened merely to accommodate v3.

## Validation

Inspect the current `package.json` before execution and use only repository-declared scripts.

From `moda-interact-messaging` run:

- [ ] focused `node --import tsx --test tests/whatsapp-provider-status.test.mjs`
- [ ] focused `node --import tsx --test tests/startup-contract.test.mjs`
- [ ] `npm test`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `npm ls @modainteract/moda-interact-shared --depth=0` confirms the exact SHARED-002 version
- [ ] `git diff --check`

The repository currently declares no standalone lint or Prisma-validation script. Do not invent one unless the repository declares it at execution time.

Also inspect the changed source to confirm no raw Meta failure object/text is logged or copied into the normalized event.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin Background classification/convergence work.

## Implementation Notes

Prefer one small pure helper for provider failure-code extraction rather than scattering `errors` parsing across the webhook route. Keep it Messaging-local because it normalizes Meta's raw webhook shape into the Shared provider-neutral contract; do not move raw Meta structure into Shared.

The Shared runtime validator is authoritative after candidate construction. Local normalization should omit malformed optional failure evidence rather than reproduce the complete Shared schema.

Do not interpret provider code `131026` or any other specific value in this task. ARCH-028 intentionally separates evidence transport from Background policy classification.

The v3 evidence-bearing FAILED job-ID refinement is a rolling-deployment mechanism, not a new business identity. Background remains responsible for durable first-evidence-wins/idempotent persistence when multiple evidence-bearing jobs are delivered.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

- Meta provider-status `errors` may be absent or malformed; failure evidence is optional and must never be required for accepting an otherwise-valid supported status.
- Provider error `code` is the only raw failure field ARCH-028 permits Messaging to carry across the service boundary.

### Unresolved Issues

None for this task. Provider-code classification and recipient-suppression policy remain intentionally deferred to later Background tasks.

### Architectural Concerns

Any implementation pressure to add shop lookup, billing/recovery decisions, raw Meta error text or a second provider-status contract must be returned to `moda_architect` rather than implemented here.

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

Pending.

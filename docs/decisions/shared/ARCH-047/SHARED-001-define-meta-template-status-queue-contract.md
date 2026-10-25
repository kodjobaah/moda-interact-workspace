---
id: ARCH-047-SHARED-001
architecture_id: ARCH-047
title: Define canonical Meta template status queue event v2
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-047-SHARED-002
created: 2026-10-25
updated: 2026-10-25
---

# Define canonical Meta template status queue event v2

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`.

This is a **portable task definition**; it is not materialised on a Git task branch. The old documentation-only `v1` content-hash-based observation ID is **superseded before production**. There is no deployed v1 producer/consumer requiring a compatibility adapter. This narrow task does **not** reinstate a Shared AST/translation/template compiler package.

## Objective

Publish one type-safe, strictly validated cross-repository contract for authenticated Meta template-status observations sent from Messaging to the existing `whatsapp-events` BullMQ consumer in Background, with distinct occurrence identity and reproducible job ID formatting.

## Context

The earlier R3 contract derived a job ID from WABA, template, status and reason. An APPROVED → PAUSED → APPROVED sequence can therefore repeat the first ID and be suppressed while BullMQ retains the completed job. Delivery of a new observation must not depend on removal of older jobs. A content fingerprint is not an event occurrence ID. Messaging and Background are different repositories and must not maintain duplicate wire schemas.

## Scope

Only `moda-interact-shared/`. Add a browser-safe module `src/whatsapp-template-events.ts`, export `./whatsapp-template-events` through `package.json` and the `tsup` build entrypoints, and write focused tests and a checked-in compatibility fixture. Reuse installed Zod and established package conventions; no Node-only dependencies in this browser-safe entrypoint.

## Out of Scope

No AST format, translation segments, Meta Graph API, queues/workers, webhooks, provider reconciliation, Prisma schema, release/publication, scheduling, consent/STOP logic or package publication. No duplicate generic hashing, logging or validation framework.

## Requirements

### R1 — Exact event and queue contract

Expose `META_TEMPLATE_STATUS_QUEUE = "whatsapp-events"`, `META_TEMPLATE_STATUS_JOB = "meta-template-status-update"`, `META_TEMPLATE_STATUS_SCHEMA_VERSION = 2`, `MetaTemplateStatusObservationV2Schema` and its inferred TypeScript type. Validate **exactly nine own JSON keys**, reject unknown keys, accept unknown well-formed Meta statuses as text (never infer approval). Size of `JSON.stringify(job.data)` MUST be ≤4096 UTF-8 bytes, enforced at ingress and consumer boundaries. Required payload:

```json
{
  "schemaVersion": 2,
  "eventIdentity": "meta-template-status:v2:550e8400-e29b-41d4-a716-446655440000",
  "wabaId": "123456789",
  "providerTemplateId": "987654321",
  "providerTemplateName": "checkout_recovery_initial_v2",
  "providerLanguageCode": "en_GB",
  "providerStatus": "APPROVED",
  "reasonCode": "NONE",
  "receivedAt": "2026-10-25T19:00:00.000Z"
}
```

`wabaId` and non-null `providerTemplateId` are decimal strings 1–32 chars; optional ID/reason are explicit `null` when absent. `providerTemplateName` is 1–255 chars; provider language 1–16; provider status 1–32; non-null reason 1–128; preserve validated provider strings, with no case rewriting. `receivedAt` must be canonical UTC ISO-8601 including milliseconds and trailing `Z`; it records receipt, **not** Meta event ordering. No raw webhook, customer fields, tokens or Meta headers. `eventIdentity` must use the exact prefix/UUID syntax in R2.

### R2 — New event occurrence versus identical content

Messaging generates a fresh cryptographically random **UUID v4 for every matching change after authenticated, whole-batch preflight**. Shared has **no randomness source**: export pure `formatMetaTemplateStatusEventIdentity(observationId)` and `formatMetaTemplateStatusJobId(observationId)` that validate a lowercase UUID v4 and return respectively:

```text
meta-template-status:v2:550e8400-e29b-41d4-a716-446655440000
meta-template-status-v2-550e8400-e29b-41d4-a716-446655440000
```

`eventIdentity` and job ID use the **same occurrence UUID**. A retry of the **same already-created job** keeps its ID. A distinct authenticated webhook delivery, including a later identical APPROVED after PAUSED, receives a fresh ID; a redelivery of the same provider bytes may also create a new job. Background's current-state reconciliation is idempotent; **neither the UUID nor `receivedAt` orders provider status**. Do not reconstruct the occurrence ID from six provider-content fields. A separate content fingerprint may be computed for diagnostics, but MUST NOT be the queue job ID or the unique database event identity. Never depend on completed-job removal for correctness. A stable Meta occurrence ID is not available in this source payload.

### R3 — Strict schema and compatible fixture

Use pure Zod validation and deterministic formatting; no network/environment/DB access. Export one fixture with the exact JSON object above and expected job ID. Fixtures for a second UUID + identical six Meta values must generate distinct identities; fixtures for APPROVED, PAUSED, APPROVED and two separate identical HTTP deliveries must all be admissible. Assert exact nine fields, round-trip parse, numeric ID rejection, unsafe ID rejection (normalisation is producer-owned), wrong version, malformed UUID, oversized payload, extra keys, invalid/null required fields, bad timestamp and unknown status handling. Write a minimal package export/build-entrypoint test. Error messages must not dump untrusted payloads.

### R4 — Consumption boundaries

Messaging maps signed Meta webhook values and generates UUIDs; Background parses the same published event and interprets provider state. No Shared parser of Admin ASTs, template content or provider policy; no Shared responsibility for DB transitions or final-send gating. New consumers import the published `@modainteract/moda-interact-shared/whatsapp-template-events` subpath, never source from sibling worktrees. The producer's existing HMAC verification/queue retry policy and Background admission behaviour remain their owning repositories' responsibilities.

## Work Items

- [ ] Implement the strict nine-field v2 Zod schema, exported constants/types and deterministic UUID-based formatters.
- [ ] Add browser-safe subpath export, build entry, canonical compatibility fixture and exact unit tests.
- [ ] Verify the repeated-APPROVED transition is not coalesced by occurrence identity and that content fingerprint is not used as queue identity.
- [ ] Run repository-declared typecheck, build, focused/full unit tests and `git diff --check`; document changed files and validation evidence.

## Interfaces / Contracts

Export exactly the public v2 contract specified in R1–R2 from `@modainteract/moda-interact-shared/whatsapp-template-events`. The shape is consumed unchanged by `ARCH-047-MESSAGING-001` and `ARCH-047-BACKGROUND-003`. The preceding six-field v1 SHA vector remains **historical documentation only**, not a runtime dependency or v2 test vector.

## Dependencies

None. This bounded Shared contract can be implemented independently of DB001 because it has no database access.

## Enables

- `ARCH-047-SHARED-002` (publication only). Consumer implementation tasks become eligible only after SHARED-002 is published/accepted and their other dependencies are Complete.

## Acceptance Criteria

- [ ] v2 schema/formatters/fixture exact and independently importable through package subpath.
- [ ] Different authenticated observations with identical Meta fields receive distinct occurrence identities and do not depend on queue retention/removal.
- [ ] Zod rejects all malformed/oversized/unknown-key inputs and preserves well-formed unknown statuses.
- [ ] Only cross-repository transport/schema mechanics are implemented; no template AST, provider status business policy or database operations.
- [ ] Tests, typecheck and production build pass; `git diff --check` clean.

## Validation

- [ ] `npm run typecheck` (if provided in repository `package.json`).
- [ ] Focused tests using the repository's `tsx --test` mechanism plus `npm test`.
- [ ] `npm run build` and package subpath import/fixture validation.
- [ ] `git diff --check` and completion/worktree branch evidence.

## Stop Condition

Complete the task's Work Items, Acceptance Criteria, Validation and Completion Report; set task to `review` and STOP. Do not publish the package from this implementation task or start consumer tasks.

## Implementation Notes

Follow the repository's published entrypoint patterns and the canonical task launcher with dedicated parent/implementation worktrees. No `docs/decisions/**/_index.md` edits. This contract is pre-production and may replace the earlier unimplemented v1 envelope without backward adapters; if a live v1 job is discovered, stop and report the deployment compatibility issue to `moda_architect` before consumer cutover.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

No production v1 template-status job exists; check deployment state during implementation.

### Unresolved Issues

None known.

### Architectural Concerns

None known.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.

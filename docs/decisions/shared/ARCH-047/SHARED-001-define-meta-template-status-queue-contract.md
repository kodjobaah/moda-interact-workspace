---
id: ARCH-047-SHARED-001
architecture_id: ARCH-047
title: Define canonical Meta template status queue event v2
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 15
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-047-SHARED-002
created: 2026-10-25
updated: 2026-10-25
---

# Define canonical Meta template status queue event v2

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`.

This definition was supplied as a **portable task definition** and is now materialized on the canonical parent task branch. The old documentation-only `v1` content-hash-based observation ID is **superseded before production**. There is no deployed v1 producer/consumer requiring a compatibility adapter. This narrow task does **not** reinstate a Shared AST/translation/template compiler package.

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

- [x] Implement the strict nine-field v2 Zod schema, exported constants/types and deterministic UUID-based formatters.
- [x] Add browser-safe subpath export, build entry, canonical compatibility fixture and exact unit tests.
- [x] Verify the repeated-APPROVED transition is not coalesced by occurrence identity and that content fingerprint is not used as queue identity.
- [x] Run repository-declared typecheck, build, focused/full unit tests and `git diff --check`; document changed files and validation evidence.

## Interfaces / Contracts

Export exactly the public v2 contract specified in R1–R2 from `@modainteract/moda-interact-shared/whatsapp-template-events`. The shape is consumed unchanged by `ARCH-047-MESSAGING-001` and `ARCH-047-BACKGROUND-003`. The preceding six-field v1 SHA vector remains **historical documentation only**, not a runtime dependency or v2 test vector.

## Dependencies

None. This bounded Shared contract can be implemented independently of DB001 because it has no database access.

## Enables

- `ARCH-047-SHARED-002` (publication only). Consumer implementation tasks become eligible only after SHARED-002 is published/accepted and their other dependencies are Complete.

## Acceptance Criteria

- [x] v2 schema/formatters/fixture exact and independently importable through package subpath.
- [x] Different authenticated observations with identical Meta fields receive distinct occurrence identities and do not depend on queue retention/removal.
- [x] Zod rejects all malformed/oversized/unknown-key inputs and preserves well-formed unknown statuses.
- [x] Only cross-repository transport/schema mechanics are implemented; no template AST, provider status business policy or database operations.
- [x] Tests, typecheck and production build pass; `git diff --check` clean.

## Validation

- [x] `npm run typecheck` (if provided in repository `package.json`).
- [x] Focused tests using the repository's `tsx --test` mechanism plus `npm test`.
- [x] `npm run build` and package subpath import/fixture validation.
- [x] `git diff --check` and completion/worktree branch evidence.

## Stop Condition

Complete the task's Work Items, Acceptance Criteria, Validation and Completion Report; set task to `review` and STOP. Do not publish the package from this implementation task or start consumer tasks.

## Implementation Notes

Follow the repository's published entrypoint patterns and the canonical task launcher with dedicated parent/implementation worktrees. No `docs/decisions/**/_index.md` edits. This contract is pre-production and may replace the earlier unimplemented v1 envelope without backward adapters; if a live v1 job is discovered, stop and report the deployment compatibility issue to `moda_architect` before consumer cutover.

## Completion Report

### Status

Developer Completed and Architect Review Accepted — explicit developer completion was recorded on 2026-10-25 for workflow Attempt 1, followed by architect acceptance on 2026-10-25. Implementation commits and all focused/full validation are published and passing. Attempt 0 review history is retained below.

### Files Changed

Implementation repository `moda-interact-shared` (8 files in the original implementation commit):

- `README.md`
- `fixtures/README.md`
- `fixtures/meta-template-status-v2.json`
- `package.json`
- `scripts/validate-whatsapp-template-events-entrypoint.mjs`
- `src/whatsapp-template-events.ts`
- `src/whatsapp-template-events.test.ts`
- `tsup.config.ts`

The follow-up TypeScript-only correction changes `src/whatsapp-template-events.test.ts`, replacing a `delete` expression with `Reflect.deleteProperty`; it is committed and published in `6a01cba02351ebb7c0ea56be8d5f6eb20fdb121e`.

Implementation commits `b9a14730dad04df7cce8e3665783af663a284dae` and `6a01cba02351ebb7c0ea56be8d5f6eb20fdb121e` are both published to `origin/task/ARCH-047-SHARED-001`.

### Work Completed

- Added strict, size-bounded Meta template status v2 observations with nine required own JSON keys and canonical receipt timestamps.
- Added pure event-identity and BullMQ job-ID formatters using the same validated lowercase UUID v4 occurrence identity; Meta content and time are not used to deduplicate occurrences.
- Added a browser-safe package subpath and tsup build entry, checked-in canonical fixture, package-export validator and contract tests.
- Exercised repeat APPROVED/PAUSED/APPROVED observations, identical provider payloads with distinct UUIDs, unknown statuses, malformed values, timestamps, extra keys and 4096-byte size bounds.
- Corrected the test-only required-property deletion using `Reflect.deleteProperty`, then reran the complete validation sequence successfully.

### Validation Results

Fresh canonical-worktree verification on 2026-10-25 (`typescript(20261025-214030)`):

- **PASS** — `npm run typecheck`, after the test-only TS2790 correction.
- **PASS** — `npx tsx --test src/whatsapp-template-events.test.ts`: 9 passed, 0 failed, 0 skipped.
- **PASS** — `npm test`: 375 passed, 0 failed, 1 skipped (376 total).
- **PASS** — `npm run build`; generated ESM output and declarations for `whatsapp-template-events`.
- **PASS** — `npm run validate:arch047-whatsapp-template-events`; package subpath, fixture and npm tarball validated.
- **PASS** — `git diff --check origin/main...HEAD`; no whitespace errors.
- `npm ci` previously succeeded (211 packages installed). npm audit reported 3 dependency vulnerabilities (1 low, 2 high); dependency remediation is outside this contract task and was not performed.
- Canonical launcher resolved parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-SHARED-001` and implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-SHARED-001`, both on `task/ARCH-047-SHARED-001`.
- Parent task worktree was clean at `02ac1f6b60411f63a4275e9457219c28f83a24be`, equal to its origin task branch, and contains current workspace `origin/main` (`c90273ccee9301374390ad8fca625c0561698e15`).
- Implementation worktree was clean at `6a01cba02351ebb7c0ea56be8d5f6eb20fdb121e`, equal to `origin/task/ARCH-047-SHARED-001`; its task diff is based on Shared `origin/main` `7e7448506987624cb634c1df0b39887251f34405`. No submodules are registered for this package.

### Deviations

None in production-contract scope. One test-only TS2790 correction was made and validated before review.

### Assumptions

This remains a pre-production replacement for the former unimplemented v1 content-hash contract; no existing production v1 jobs requiring compatibility are assumed. Verify this before consumer deployment.

### Unresolved Issues

- No task-scoped validation failures remain. npm audit findings are noted above and remain outside this task's scope.
- The package is not published by this task. SHARED-002 remains the separate publication gate; no consumer implementation or cutover is authorized here.

### Architectural Concerns

None identified in the v2 transport contract. SHARED-002 remains the separate publication gate; consumer tasks use the published subpath only.

## Architect Review

### Review Status

Accepted — 2026-10-25. The v2 Shared contract conforms to the task requirements and is accepted for the separate publication gate. This acceptance does not itself publish the package.

### Review Notes

The implementation is limited to the strict transport schema, deterministic UUID v4 identity/job-ID formatting, browser-safe package subpath, fixture and tests. It does not add provider policy, queue production/consumption, database transitions or template AST responsibilities. The previously failing TS2790 test typing issue was corrected and the complete validation sequence passed. No blocking architecture or behavior issue remains in the reviewed task scope.

### Reviewed Files

- `src/whatsapp-template-events.ts`
- `src/whatsapp-template-events.test.ts`
- `fixtures/meta-template-status-v2.json`
- `package.json`
- `tsup.config.ts`
- `scripts/validate-whatsapp-template-events-entrypoint.mjs`
- `README.md`
- `fixtures/README.md`

### Validation Reviewed

- `npm run typecheck` — passed.
- `npx tsx --test src/whatsapp-template-events.test.ts` — 9 passed.
- `npm test` — 375 passed, 0 failed, 1 skipped.
- `npm run build` — passed.
- `npm run validate:arch047-whatsapp-template-events` — passed; package subpath, fixture and npm tarball validated.
- `git diff --check origin/main...HEAD` — passed.

### Architecture Conformance

Accepted. The implementation preserves the Messaging producer and Background consumer ownership boundaries and leaves package publication to SHARED-002.

### Follow-up

SHARED-002 is now materialized and `ready` at Attempt 0 on its own parent task branch. Do not publish from SHARED-001 or start consumer work before package publication is verified.

## Execution Ownership Amendment

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_shared`, coordinator, repository, dependency set, task scope, acceptance criteria and validation requirements.
- Materialization: The existing portable architect definition was published on parent branch `task/ARCH-047-SHARED-001` in commit `ae96dda2`; no implementation or unrelated local-main history was copied.
- Claim state: This amendment does not claim an implementation attempt; the canonical launcher records the claim after implementation worktree preparation and dependency verification.

## Developer Self-Review Passed/Accepted

### Review Decision

Developer self-review of Attempt 1 passed on 2026-10-25. All task Work Items and Acceptance Criteria are complete, implementation changes are committed and pushed, and focused/full tests, typecheck, production build, package-entrypoint validation and diff checks pass. The canonical parent and implementation worktrees are clean, their task branches are published, and the parent branch contains current workspace `origin/main`. No task-scoped blocker was found.

### Review Scope and Residual Boundaries

Reviewed the strict nine-field schema, UUID v4 event/job identity formatters, browser-safe package export, canonical fixture and tests, and package build/tarball validation. Production deployment, package publication, consumer wiring, and verification of any live v1 jobs remain outside this task's implementation scope; SHARED-002 is the publication gate.

### State Transition

The self-review initially left `status: review`, `executor: null`, `claimed_at: null`, `attempt: 1`, with explicit developer completion pending.

## Developer Completion Decision

On 2026-10-25, the developer explicitly invoked `/moda_developer_update ARCH-047-SHARED-001 complete`. The durable passing review is present, all required Work Items and Acceptance Criteria are complete, implementation commits `b9a14730dad04df7cce8e3665783af663a284dae` and `6a01cba02351ebb7c0ea56be8d5f6eb20fdb121e` are published, and the parent task/report change is publishable. The task is now `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`. This does not constitute architect acceptance or a merge to `main`.

### Dependency Frontier

`ARCH-047-SHARED-002` is `ready` at Attempt 0 because SHARED-001 is complete and its Architect Review is accepted. SHARED-002 has not been claimed and no package publication is claimed. Consumer tasks remain gated on actual package publication and their other explicit dependencies.

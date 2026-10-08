---
id: ARCH-028-SHARED-001
architecture_id: ARCH-028
title: Define versioned WhatsApp provider-failure status contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: copilot
claimed_at: 2026-10-08T12:26:01Z
attempt: 1
depends_on: []
enables:
  - ARCH-028-SHARED-002
created: 2026-10-03
updated: 2026-10-08
---

# Define versioned WhatsApp provider-failure status contract

## Architecture

Architecture ID:

`ARCH-028`

Architecture document:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator:

`moda_architect`

## Objective

Define one canonical, runtime-safe Shared WhatsApp provider-status contract that can carry bounded provider failure evidence without breaking queued v2 status events during rolling deployment.

The task must leave Messaging and Background able to adopt the same published contract later; it must not implement producer extraction, consumer classification, persistence, suppression, billing compensation or merchant notification.

## Context

The current published Shared billing contract uses:

```text
WHATSAPP_PROVIDER_STATUS_SCHEMA_VERSION = 2
NormalizedWhatsAppStatusSchema
```

and strictly validates:

```text
providerAccountId
providerPhoneNumberId
providerMessageId
status = SENT | DELIVERED | READ | FAILED
occurredAt
pricing?
```

`moda-interact-messaging` currently emits literal `schemaVersion: 2`, and `moda-interact-background` validates every queued status through `safeParseNormalizedWhatsAppStatus(...)`. The current strict v2 schema drops/forbids provider failure evidence.

Mutating v2 in place is not safe: an old strict consumer would reject a v2 payload carrying a newly added field. Conversely, a producer that starts emitting a new schema version before the consumer upgrade would also be rejected.

ARCH-028 therefore uses a dual-version rolling contract:

```text
v2 legacy event
    exact existing shape

v3 current event
    exact existing shape
    + optional bounded failure.providerCode

canonical Shared parser
    accepts v2 OR v3
```

This lets Background upgrade first while continuing to consume queued/current v2 events. Messaging may emit v3 only after that consumer adoption.

The definition order is iterative, but SHARED-001 has no runtime dependency on DATABASE-001. Do not add an artificial dependency merely to serialize the architecture. DATABASE-001's 64-character provider-code persistence bound is, however, the matching durability boundary for this contract.

## Scope

Authorised implementation surface in `moda-interact-shared`:

```text
src/billing.ts
src/billing.test.ts
scripts/validate-billing-entrypoint.mjs
```

Directly equivalent focused test/validation files may be added only if required by the repository's existing conventions; record any substitution in the Completion Report.

The task owns:

1. the legacy/current schema-version constants required to distinguish v2 and v3;
2. the bounded `WhatsAppProviderFailureEvidence` runtime schema/type;
3. explicit v2 and v3 normalized provider-status schemas;
4. one canonical `NormalizedWhatsAppStatusSchema`/type/parser that accepts both versions;
5. strict v3 rules tying failure evidence to FAILED statuses only;
6. focused contract tests for compatibility, strictness and bounds;
7. billing-subpath export/declaration validation for the new public runtime symbols.

## Out of Scope

- Changing `moda-interact-messaging` webhook normalization or queue publication.
- Changing `moda-interact-background` provider-status processing.
- Persisting `ConversationMessage.providerFailureCode` / `failedAt`.
- Reading/writing `WhatsAppRecipientReachability`.
- Provider-code classification such as terminal-recipient vs temporary/configuration/ambiguous.
- Defining which Meta code means a recipient currently cannot receive WhatsApp.
- Suppression duration/policy.
- Recovery/outreach/follow-up transitions.
- Usage release/compensation or merchant notification.
- Raw provider error text, provider webhook bodies, error details, access tokens or arbitrary metadata.
- Publishing `@modainteract/moda-interact-shared`; publication belongs to a later `task_kind: publication` task.
- Modifying consumer dependency versions/lockfiles.
- Modifying `package.json`/`package-lock.json` unless a validation-only metadata change is genuinely necessary; no new dependency is expected.

## Requirements

### R1 — Preserve v2 exactly

Define/export an explicit legacy v2 normalized provider-status schema whose accepted payload shape remains exactly the current contract:

```text
schemaVersion = 2
providerAccountId
providerPhoneNumberId
providerMessageId
status
occurredAt
pricing?
```

v2 must continue rejecting unknown fields, including `failure`. Existing v2 messages already present in a queue must remain parseable through the canonical parser after SHARED-001.

### R2 — Introduce v3 as the current producer version

Advance the current `WHATSAPP_PROVIDER_STATUS_SCHEMA_VERSION` to `3` and retain an explicitly named/exported legacy-v2 version constant. Use clear names consistent with the existing billing entrypoint.

The exact accepted exported names are:

```ts
WHATSAPP_PROVIDER_STATUS_V2_SCHEMA_VERSION
WHATSAPP_PROVIDER_STATUS_SCHEMA_VERSION
```

with values `2` and `3` respectively.

### R3 — Bounded failure evidence

Export:

```ts
WhatsAppProviderFailureEvidenceSchema
WhatsAppProviderFailureEvidence
```

with exactly this logical payload:

```ts
{
  providerCode: string;
}
```

`providerCode` must be trimmed, non-empty and at most 64 characters. A numeric Meta code is represented as text.

Do not add provider error title/message/details/category/raw metadata in SHARED-001. If later source evidence proves another bounded field is required, return to `moda_architect`; do not broaden the envelope opportunistically.

### R4 — v3 failure semantics

Define/export an explicit v3 normalized provider-status schema with the existing identity/status/time/pricing fields plus:

```ts
failure?: WhatsAppProviderFailureEvidence
```

Rules:

- `failure` is allowed only when `status === "FAILED"`;
- `FAILED` without `failure` remains valid because provider evidence can be absent/legacy/ambiguous;
- `SENT`, `DELIVERED` and `READ` carrying `failure` are invalid;
- the v3 schema remains strict and rejects all unknown fields.

The exact accepted exported schema names are:

```ts
NormalizedWhatsAppStatusV2Schema
NormalizedWhatsAppStatusV3Schema
NormalizedWhatsAppStatusSchema
```

### R5 — Canonical parser accepts both versions

`NormalizedWhatsAppStatusSchema`, `NormalizedWhatsAppStatus`, `parseNormalizedWhatsAppStatus(...)` and `safeParseNormalizedWhatsAppStatus(...)` must accept the union of valid v2 and valid v3 events.

Do not silently coerce a v2 event into v3 or synthesize failure evidence. Preserve the received `schemaVersion` so Background can reason about evidence presence explicitly where needed.

### R6 — Preserve all current fields/semantics

Do not change:

- provider account/phone/message identifier bounds;
- provider status literals;
- timestamp validation;
- pricing metadata shape/bounds;
- strict rejection of extra customer/shop/provider payload fields.

### R7 — Rolling deployment is consumer first

Document/test the compatibility invariant:

```text
new Shared parser accepts old v2 and new v3
old Shared parser does not accept v3
```

This task does not change consumers/producers. The later architecture must deploy/adopt the published Shared version in Background before Messaging begins emitting v3.

### R8 — No policy classification in Shared

Shared carries provider evidence only. It must not export enums/functions such as:

```text
TERMINAL_RECIPIENT_FAILURE
NOT_ON_WHATSAPP
TEMPORARY_PROVIDER_FAILURE
SUPPRESS_RECIPIENT
```

Those are Background policy decisions to be defined from provider/source evidence later.

## Work Items

- [x] Add explicit v2/current provider-status schema-version constants.
- [x] Add bounded `WhatsAppProviderFailureEvidenceSchema` and type.
- [x] Preserve exact strict v2 schema behaviour.
- [x] Add strict v3 schema with failure evidence allowed only on FAILED.
- [x] Make the canonical normalized-status schema/parser accept both v2 and v3 without coercion.
- [x] Add focused tests covering v2 compatibility, v3 success/failure cases, failure bounds and strict rejection.
- [x] Extend billing-entrypoint validation for the new public runtime/type exports.
- [x] Run all required Shared validation.
- [x] Complete the task Completion Report and return to `moda_architect` at `status: review`.

## Interfaces / Contracts

Contract owner:

`ARCH-028-SHARED-001`

Package/subpath after the later publication task:

`@modainteract/moda-interact-shared/billing`

Legacy schema:

```text
NormalizedWhatsAppStatusV2Schema
schemaVersion = 2
```

Current schema:

```text
NormalizedWhatsAppStatusV3Schema
schemaVersion = 3
optional failure.providerCode only for FAILED
```

Canonical consumer schema:

```text
NormalizedWhatsAppStatusSchema = v2 | v3
```

Producer:

`moda-interact-messaging` (later ARCH-028 task)

Consumer:

`moda-interact-background` (later ARCH-028 task)

Runtime validation:

`safeParseNormalizedWhatsAppStatus(...)` / `parseNormalizedWhatsAppStatus(...)`

Compatibility:

Background must adopt the published dual-version parser before Messaging emits v3. Existing queued v2 events remain valid throughout rollout.

## Dependencies

None.

DATABASE-001 is an independent durable-persistence task, not a prerequisite for defining/testing this runtime contract. The 64-character provider-code bound deliberately matches DATABASE-001's planned persistence boundary.

## Enables

None materialised yet.

After architect acceptance, the next Shared step will be a separate publication-only task. Messaging and Background adoption tasks must consume that published package rather than unpublished task-branch source.

## Acceptance Criteria

- [x] Existing valid v2 provider-status payloads continue to parse through the canonical parser unchanged.
- [x] v2 rejects `failure` as an unknown field.
- [x] Valid v3 SENT/DELIVERED/READ payloads without failure parse.
- [x] Valid v3 FAILED payloads parse both with and without bounded failure evidence.
- [x] v3 non-FAILED payloads containing failure evidence are rejected.
- [x] Empty/whitespace/over-64-character provider codes are rejected.
- [x] Failure evidence cannot carry raw message/details/category/metadata fields.
- [x] Existing provider identity/status/timestamp/pricing strictness is unchanged.
- [x] `NormalizedWhatsAppStatus` preserves the received v2/v3 schema version and exposes failure evidence only where valid.
- [x] No provider-failure classification/suppression/billing policy is introduced into Shared.
- [x] Existing Shared tests remain passing and are not weakened to accommodate the new contract.
- [x] The billing subpath build/declaration exports the new runtime schemas/types/constants.
- [x] No package publication or consumer-repository changes occur in SHARED-001.

## Validation

Run from `moda-interact-shared` using the scripts actually declared by its current `package.json`:

- [x] `npm test`
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `npm run validate:billing-entrypoint`
- [x] `npm pack --dry-run --json --ignore-scripts` confirms the billing runtime/declaration remain in the package
- [x] `git diff --check`

Also run a focused test command for `src/billing.test.ts` when practical and record the exact command/result. Do not invent lint commands that the repository does not declare.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not publish the Shared package and do not begin Messaging or Background adoption.

## Implementation Notes

Prefer a strict union of explicit v2/v3 schemas rather than mutating the v2 object schema. This makes rolling compatibility inspectable and prevents an old-version event from carrying new evidence under the same schema version.

The current `billing.ts` contract is already the canonical producer/consumer boundary. Keep ARCH-028 additions there rather than creating a second WhatsApp-status entrypoint solely for this field.

No new dependency is expected; Zod is already used by the module.

When extending `scripts/validate-billing-entrypoint.mjs`, validate both runtime exports and declaration/type exports for the new contract without weakening existing billing-export checks.

Do not update package version metadata in this implementation task. Publication/versioning belongs to the later publication-only task after architect acceptance.

## Completion Report

### Status

Ready for Review. No architect acceptance decision has been made by this agent.

### Files Changed

- `src/billing.ts`
- `src/billing.test.ts`
- `scripts/validate-billing-entrypoint.mjs`
- This task report in the parent worktree.

### Work Completed

- Added `WHATSAPP_PROVIDER_STATUS_V2_SCHEMA_VERSION = 2` and advanced the current
  `WHATSAPP_PROVIDER_STATUS_SCHEMA_VERSION` to `3`.
- Preserved the exact strict v2 payload shape in
  `NormalizedWhatsAppStatusV2Schema`; added strict v3 and bounded
  `WhatsAppProviderFailureEvidenceSchema` with trimmed non-empty codes capped at
  64 characters.
- The v3 schema accepts failure evidence only on `FAILED` events, while allowing
  legacy/ambiguous FAILED events without evidence. The canonical schema and both
  parser helpers accept v2 or v3 without changing the received version.
- Added focused compatibility, failure semantics, bounds, and strictness tests;
  existing identity/status/time/pricing tests remain intact.
- Extended billing entrypoint validation for the new runtime and declaration
  exports. No producer, consumer, package metadata, or publication changes.

### Validation Results

- Initial focused baseline before editing: `npx tsx --test src/billing.test.ts`,
  14 passed. Dependencies were absent in the fresh implementation worktree;
  `npm ci --no-audit --no-fund` installed 210 lockfile packages. No lockfile
  change was made.
- Focused post-change command: `npx tsx --test src/billing.test.ts`, 17 passed.
- `npm test`: 216 passed, 1 skipped, 0 failed. The existing BullMQ telemetry
  test skipped because `TEST_REDIS_URL` is not configured.
- `npm run typecheck`: passed.
- `npm run build`: passed through `npm run validate:billing-entrypoint`; ESM and
  declaration builds succeeded.
- `npm run validate:billing-entrypoint`: passed, validating runtime exports,
  declaration type exports, and package export targets.
- `npm pack --dry-run --json --ignore-scripts`: passed; package file list
  includes `dist/billing.js` and `dist/billing.d.ts`.
- `git diff --check`: passed.

Physical worktree isolation and launcher evidence:

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-SHARED-001
parent branch: task/ARCH-028-SHARED-001
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-SHARED-001
implementation branch: task/ARCH-028-SHARED-001
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
parent prepared head: ef7f9078d2ecb9c550b1e75d9d4a1f828f816586
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
implementation prepared head: 21903fb0b8ebe538ebce96e5683ee949fe8dccda
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
recorded recursive submodules: none (entries: [])
claim: attempt 1, executor copilot, committed and pushed
claim commit: d653bc81fe9db79d10b340ed244dace8b93d43b7
claim timestamp: 2026-10-08T12:26:01Z
```

### Deviations

No scope deviation. The first focused-test invocation was issued from the prior
task's terminal directory and could not locate this task's file; it was rerun
from the launcher-supplied implementation worktree. The implementation
worktree initially had no installed dependencies; the lockfile installation
allowed all required validation to run.

### Assumptions

- The current Shared package continues to expose provider-status contracts through `./billing`.
- Provider numeric error codes can be normalized safely to bounded text without preserving raw provider error content.

### Unresolved Issues

None within this task. Provider-code policy classification remains intentionally
deferred to Background architecture.

### Architectural Concerns

No new concerns. Provider-code policy classification remains intentionally
deferred to Background; this change carries only bounded evidence.

## Architect Review

### Review Status

Pending

### Review Notes

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.

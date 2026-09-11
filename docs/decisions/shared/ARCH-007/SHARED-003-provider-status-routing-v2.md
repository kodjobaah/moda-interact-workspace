---
id: ARCH-007-SHARED-003
architecture_id: ARCH-007
title: Correct normalized WhatsApp provider-status routing contract to schema v2
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 62
executor:
claimed_at:
attempt: 1
depends_on:
  - ARCH-007-SHARED-002
enables:
  - ARCH-007-SHARED-004
created: 2026-09-07
updated: 2026-09-07T22:20:00+01:00
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-SHARED-003: Correct normalized WhatsApp provider-status routing contract to schema v2

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Correct the provider-status cross-repository contract so Messaging can normalize
real verified Meta status webhooks without fabricating a Moda tenant/shop ID.

## Context

`@modainteract/moda-interact-shared@0.7.3` provider-status schema v1 requires:

```text
shopId
providerAccountId
providerMessageId
status
occurredAt
pricing?
```

Architect review of MESSAGING-001 established that the real Meta status webhook
does not supply `shopId`. The verified payload supplies WABA identity via
`entry.id` and the business phone-number identity via
`metadata.phone_number_id`.

Messaging owns ingress normalization but has no durable tenant lookup. Background
owns the database and can resolve the local outbound message by
`providerMessageId`, then derive the owning shop from durable local state.

ARCH-007 is pre-production/breaking. Do not preserve the erroneous v1 status
shape merely for theoretical compatibility.

## Scope

Shared provider-status constants, Zod schema/types, focused tests and exports
already owned by the existing `./billing` package entrypoint.

Do not change unrelated accepted billing-plan, merchant-system-message or
Shopify-idempotency contracts.

## Out of Scope

- npm publication/version bump; SHARED-004 owns publication.
- Meta webhook parsing; MESSAGING-001 owns producer logic.
- Database/shop resolution; BACKGROUND-005 owns durable consumer resolution.
- New provider-account persistence.

## Requirements

### Canonical v2 contract

Set:

```ts
WHATSAPP_PROVIDER_STATUS_SCHEMA_VERSION = 2
```

The strict normalized event must contain exactly:

```text
schemaVersion: 2
providerAccountId: string
providerPhoneNumberId: string
providerMessageId: string
status: SENT | DELIVERED | READ | FAILED
occurredAt: offset-aware ISO datetime
pricing?: {
  billable?: boolean
  category?: bounded non-empty string
  model?: bounded non-empty string
}
```

`shopId` MUST NOT be part of provider-status v2.

Semantics:

- `providerAccountId` = Meta `entry.id` / WABA identity.
- `providerPhoneNumberId` = Meta `value.metadata.phone_number_id`.
- `providerMessageId` = Meta outbound message/status `id`.
- no tenant/shop ID is invented at ingress.
- Background resolves the shop from durable local state using
  `providerMessageId`; provider identities remain observed metadata and must
  never cause a cross-tenant guess.

### Runtime/type rules

- strict Zod validation;
- preserve existing provider status enum;
- preserve bounded pricing metadata semantics;
- preserve exact literal TypeScript inference;
- reject blank/oversized provider identities;
- reject v1 payloads containing `shopId` under the strict v2 schema;
- do not create a local compatibility union accepting both v1 and v2.

### Regression tests

Add/update focused tests proving:

1. a valid v2 event parses;
2. `schemaVersion: 1` is rejected;
3. missing/blank `providerAccountId` is rejected;
4. missing/blank `providerPhoneNumberId` is rejected;
5. missing/blank `providerMessageId` is rejected;
6. an object containing the removed `shopId` field is rejected by the strict v2
   schema;
7. all four status literals remain accepted;
8. pricing metadata remains optional, bounded and monetary amounts remain absent;
9. unrelated accepted billing exports/helpers remain type/build compatible.

## Work Items

- [x] Replace provider-status v1 schema/version with canonical v2.
- [x] Add `providerPhoneNumberId`.
- [x] Remove `shopId` from the normalized status contract.
- [x] Add focused runtime/type regression tests.
- [x] Run Shared typecheck/build/full tests and `git diff --check`.
- [x] Return only SHARED-003 to `review` and STOP.

## Interfaces / Contracts

Owner: `moda_shared`

Package entrypoint:

```text
@modainteract/moda-interact-shared
@modainteract/moda-interact-shared/billing
```

Producer after publication: `moda_messaging`

Consumer after publication: `moda_background`

Schema version: `v2`

## Dependencies

SHARED-002 is architect-accepted Complete and published `0.7.3`. This task
amends only the provider-status contract discovered invalid during
MESSAGING-001 review.

## Enables

- ARCH-007-SHARED-004

## Acceptance Criteria

- [x] Real Meta routing identities can satisfy the Shared event without `shopId`.
- [x] Provider-status v2 is strict/versioned and no v1 compatibility shim exists.
- [x] Accepted unrelated billing contracts are unchanged.
- [x] Tests/typecheck/build/`git diff --check` pass.

## Validation

Inspect `package.json`, then run the repository-declared typecheck/build/full
tests plus focused billing/provider-status tests and `git diff --check`.

## Implementation Notes

Do not bump/publish the package version in this task. SHARED-004 owns the
release.

Luna deterministic-execution guardrails:

- This task exists because Architect Review found a real cross-repository
  contract defect; do not reintroduce `shopId`.
- Do not add database access to Shared.
- Do not change unrelated billing semantics.
- Do not start SHARED-004.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SHARED-003` branch and the mirrored parent-workspace `task/ARCH-007-SHARED-003` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/src/billing.ts`
- `moda-interact-shared/src/billing.test.ts`

### Work Completed

- Set `WHATSAPP_PROVIDER_STATUS_SCHEMA_VERSION` to literal `2`.
- Replaced the required `shopId` with required `providerPhoneNumberId` in the strict normalized event schema.
- Preserved provider status literals, bounded pricing metadata, strict unknown-field rejection, and unrelated billing exports/helpers.
- Added regression coverage for v1 rejection, removed `shopId`, blank/oversized identity validation, all four statuses, optional pricing, and monetary metadata rejection.

### Validation Results

- Focused `./node_modules/.bin/tsx --test src/billing.test.ts` — 6 passed.
- `npm run typecheck` — passed.
- `npm test` — 104 passed, 1 skipped because `TEST_REDIS_URL` is not configured.
- `npm run build` — passed, including ESM and declaration builds.
- `git diff --check` — passed.
- `git status --short` — only `src/billing.ts` and `src/billing.test.ts` modified in the owned repository.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

SHARED-003 is architect-accepted Complete.

Direct source comparison against the published/accepted Shared `0.7.3`
`src/billing.ts` confirms the provider-status contract changed only in the
intended bounded ways:

```text
WHATSAPP_PROVIDER_STATUS_SCHEMA_VERSION: 1 -> 2
remove: shopId
add:    providerPhoneNumberId
```

The accepted unrelated ARCH-007 billing plan, usage metric, SYSTEM-message,
merchant source-key and Shopify idempotency contracts are unchanged.

The canonical provider-status v2 event is now:

```text
schemaVersion: 2
providerAccountId
providerPhoneNumberId
providerMessageId
status: SENT | DELIVERED | READ | FAILED
occurredAt
pricing?
```

There is deliberately no Moda `shopId` in the ingress contract. Messaging will
publish only verified provider identities from Meta. Background remains
responsible for resolving the owning shop from durable local outbound state by
`providerMessageId`.

### Reviewed Files

- `moda-interact-shared/src/billing.ts`
- `moda-interact-shared/src/billing.test.ts`
- `moda-interact-shared/package.json`
- `docs/decisions/shared/ARCH-007/SHARED-003-provider-status-routing-v2.md`
- SHARED-003 Completion Report

### Validation Reviewed

The submitted task reports:

- focused provider-status/billing tests: 6 passed;
- full Shared suite: 104 passed, 1 expected Redis-dependent skip;
- typecheck: passed;
- build including declarations: passed;
- `git diff --check`: passed.

The focused tests prove:

- valid schema v2 parsing;
- schema v1 rejection;
- required/bounded WABA, phone-number and message identities;
- strict rejection of removed `shopId`;
- all four normalized statuses;
- optional bounded pricing metadata;
- rejection of monetary amount metadata;
- preservation of unrelated accepted billing helpers.

### Architecture Conformance

Conformant. The cross-repository provider-status routing defect discovered
during MESSAGING-001 review is corrected at the Shared contract boundary.

### Follow-up

SHARED-004 may now publish the accepted contract as exact
`@modainteract/moda-interact-shared@0.7.4`.

MESSAGING-001 remains Blocked until SHARED-004 is architect-accepted Complete.
Do not unblock it merely because SHARED-003 source is accepted; consumers must
use the published artifact.

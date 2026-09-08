---
id: ARCH-007-SHARED-001
architecture_id: ARCH-007
title: Define canonical ARCH-007 billing and provider-status contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 6
depends_on: 
  - ARCH-007-DATABASE-003
enables: 
  - ARCH-007-SHARED-002
created: 2026-09-07
updated: 2026-09-07T20:59:00+01:00
---

# ARCH-007-SHARED-001: Define canonical ARCH-007 billing and provider-status contracts

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Define and test the cross-repository types, Zod schemas, system codes and deterministic key helpers required by ARCH-007 consumers.

## Context

ARCH-007 crosses App, Background, Messaging and Admin. Lower-capability agents must not independently invent billing metrics, message codes, provider-status event shapes or idempotency-key formats.

## Scope

Add a bounded billing export surface to `@modainteract/moda-interact-shared` using existing package/export conventions. Include only semantics actually shared by two or more repositories.

## Out of Scope

- Database Prisma schema.
- Shopify/Meta HTTP clients.
- Business services or Admin UI.
- Publication/version bump (SHARED-002).

## Requirements

- Export exact canonical values for plan kind, usage metrics and merchant billing SYSTEM message codes used cross-repository; values must align with accepted DATABASE-003 schema and architecture.
- Initial merchant billing system codes: `BILLING_FREE_ALLOWANCE_WARNING`, `BILLING_FREE_ALLOWANCE_EXHAUSTED`, `BILLING_PLAN_UPGRADED`, `BILLING_PLAN_DOWNGRADE_SCHEDULED`, `BILLING_SUBSCRIPTION_ENDED`, `BILLING_SAFETY_LIMIT_REACHED`.
- Define a versioned normalized WhatsApp provider-status contract for Messaging producer -> Background consumer with: schemaVersion, shop identity needed to route, providerMessageId, status (`SENT|DELIVERED|READ|FAILED` as actually supported), occurredAt, and optional bounded pricing/category metadata only when present in Meta. Never include full customer payload/access token.
- Define runtime validation schema for that provider-status event.
- Provide deterministic helpers for merchant SYSTEM source keys and recovery/billing idempotency identities used across repositories. Keys destined for Shopify App Events must be guaranteed <=64 characters and stable; do not use random UUID generation.
- Define schema-version constants for new cross-service event contracts.
- Do not export Prisma-generated model types as the cross-service API. Shared contracts must be repository-neutral.

## Work Items

- [x] Inspect current shared export/package conventions and existing merchant-communications/WhatsApp contracts.
- [x] Implement billing/provider-status constants/types/Zod schemas/helpers.
- [x] Add unit tests for valid/invalid provider status and key determinism/length.
- [x] Update package exports/build metadata only as required for implementation, not publication version.

## Interfaces / Contracts

Canonical package:

```text
@modainteract/moda-interact-shared
```

Producer/consumer:

```text
NormalizedWhatsAppStatus: moda_messaging -> moda_background
BillingSystemMessageCode/key helpers: moda_background/moda_app/admin as needed
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-SHARED-002

## Acceptance Criteria

- [x] No duplicate local definition is necessary for consumers after publication.
- [x] Provider-status schema rejects malformed status/timestamp/missing providerMessageId and accepts only bounded optional metadata.
- [x] Billing key helpers are deterministic and Shopify-targeted keys are <=64 chars.
- [x] No customer-identifying payload is added to App Events/shared billing event attributes.
- [x] Package tests/build and `git diff --check` pass.

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

Ready for Review

### Files Changed

`src/billing.ts`, `src/billing.test.ts`, `src/index.ts`, `tsup.config.ts`, and `package.json`.

### Work Completed

- Added canonical ARCH-007 plan kinds, usage metrics, merchant billing SYSTEM message codes, schema-version constants, and normalized WhatsApp provider-status types.
- Added strict Zod parsing with bounded tenant/provider identity, timestamps, supported statuses, and optional Meta pricing metadata; customer payloads and credentials are not part of the contract.
- Added deterministic merchant SYSTEM source-key, recovery idempotency, and Shopify usage idempotency helpers. Shopify-targeted keys are guaranteed to be at most 64 characters without random UUIDs.
- Added the browser-safe `./billing` package export and root re-export without changing the publication version.

### Validation Results

`npm run typecheck` — passed.
`npm run build` — passed; billing entrypoint emitted.
`npm test` — passed; 103 tests passed, 1 pre-existing Redis-dependent test skipped, 0 failed.
`git diff --check` — passed.

### Deviations

The Redis-dependent BullMQ telemetry test remains skipped because `TEST_REDIS_URL` is not configured; this is unrelated to the billing contract changes.

### Assumptions

The normalized status contract uses `shopId` plus `providerAccountId` for tenant/provider routing and accepts only bounded `billable`, `category`, and `model` pricing metadata when present.

### Unresolved Issues

None

### Architectural Concerns

None

## Attempt 6 Implementation

### Architect Review Checklist

- [x] Exact billing SYSTEM-code union: `src/billing.ts` now uses an explicit six-value readonly tuple for Zod, and `src/billing.test.ts` contains a compile-time assertion that `string` does not extend `BillingSystemMessageCode`; typecheck passed.
- [x] Lifecycle-scoped source keys: `createMerchantBillingSystemSourceKey(shopId, code, eventIdentity, version?)` now includes the durable event identity and contract version while preserving the 255-character bound.
- [x] Replay and distinct-event semantics: focused tests prove same-identity replay stability and different identities produce different keys.
- [x] Version semantics: focused tests prove the default version is `1` and an explicit version `2` produces a distinct key for the same event identity.
- [x] Input validation: focused tests prove blank and whitespace event identities are rejected; existing validation continues to cover shop, code, and version.
- [x] Bounded long identities: focused tests prove long event identities remain deterministic and produce keys no longer than 255 characters.
- [x] Validation and handoff: focused tests, typecheck, build, full tests, and `git diff --check` are required before returning this task to `review`; only SHARED-001 is being returned.

### Attempt 6 Files Changed

`src/billing.ts`, `src/billing.test.ts`, and this task record.

## Attempt 2 Correction Requirements

Architect review found two cross-repository contract defects inside the original SHARED-001 scope. Attempt 2 MUST correct only these defects, rerun the focused/full repository validation already required by this task, update the Completion Report, return this same task to `review`, and STOP. Do not start SHARED-002.

1. Preserve the merchant billing SYSTEM code as an exact compile-time literal union. The current `z.enum(Object.values(... ) as [string, ...string[]])` widens `BillingSystemMessageCode` to `string`, allowing downstream code to compile with arbitrary non-canonical codes. Refactor the exported values/schema/type so:
   - runtime validation still accepts exactly the six architecture-approved codes;
   - `BillingSystemMessageCode` is the exact six-value TypeScript union, not `string`;
   - downstream helpers accept only that exact union at compile time;
   - add a type-level or compile-time assertion that would fail if the type widens to `string`.

2. Make merchant SYSTEM source keys lifecycle/event scoped. The current helper uses only `shopId + code + version`, but `MerchantSupportMessage.sourceKey` is globally unique and plan-change/safety events can legitimately recur. Refactor the helper contract to include a required deterministic durable `eventIdentity`/`lifecycleIdentity` in addition to shop, code and version. The helper MUST:
   - deduplicate replay of the same durable event/transition;
   - produce a different key for a later distinct lifecycle event using the same shop/code/version;
   - reject an empty lifecycle/event identity;
   - remain bounded to the existing MerchantSupportMessage source-key allowance;
   - use no random UUID.

   Downstream semantics are deliberately generic: callers supply a durable identity appropriate to the event (for example an entitlement transition identity, subscription transition identity, or safety incident identity). Shared must not invent repository-specific database lookups.

Add focused tests proving identical lifecycle identity is stable, different lifecycle identities do not collide in ordinary deterministic cases, long identities stay bounded, and empty identities are rejected.

## Architect Review

### Review Status

Accepted — Attempt 6

### Review Notes

The Attempt 2 submission cannot be accepted. Direct comparison of the submitted workspace against Attempt 1 shows that `src/billing.ts` and `src/billing.test.ts` are byte-for-byte unchanged. Both original contract defects therefore remain present:

1. `BillingSystemMessageCodeSchema` still uses `z.enum(Object.values(BILLING_SYSTEM_MESSAGE_CODES) as [string, ...string[]])`, preserving the compile-time widening defect identified in Attempt 1.
2. `createMerchantBillingSystemSourceKey` still has the old `(shopId, code, version)` contract and therefore still cannot distinguish replay of one lifecycle event from a later legitimate repeat of the same billing SYSTEM code.

The task record was advanced to Attempt 2/review, but the required implementation and focused tests were not changed. Validation of the unchanged implementation does not satisfy the Attempt 2 correction requirements.

### Attempt 3 Required Changes

Reclaim this same task as Attempt 3. Implement **only** the two already-defined correction requirements in this task and update the Completion Report to describe the actual Attempt 3 code/test delta. Concretely:

- Replace the widened billing SYSTEM-code schema/type construction with an implementation whose exported `BillingSystemMessageCode` remains the exact six-value literal union at compile time while runtime Zod validation accepts exactly those six values. Add a compile-time/type assertion that fails if `string extends BillingSystemMessageCode` becomes true.
- Change `createMerchantBillingSystemSourceKey` to require a non-empty deterministic durable lifecycle/event identity in addition to `shopId`, canonical `BillingSystemMessageCode`, and version. Same lifecycle identity must replay to the same key; a different lifecycle identity for the same shop/code/version must produce a different key in ordinary deterministic cases; long identities must remain bounded to 255 characters; empty identities must throw; random UUID generation is prohibited.
- Update focused tests so they would fail against the current Attempt 2 implementation.
- Run repository typecheck, build, full test suite and `git diff --check`.
- Return **only SHARED-001** to `review` and STOP. Do not start SHARED-002.

### Reviewed Files

- `src/billing.ts`
- `src/billing.test.ts`
- `src/index.ts`
- `package.json`
- `tsup.config.ts`
- `docs/decisions/shared/ARCH-007/SHARED-001-define-billing-contracts.md`
- Attempt 1 and Attempt 2 submitted Shared workspace archives

### Validation Reviewed

The agent reported successful typecheck/build/tests/`git diff --check`, but those validations were run against source/test files unchanged from Attempt 1. They therefore do not demonstrate closure of the requested corrections.

### Architecture Conformance

Changes Requested — same-task bounded rework only.

### Follow-up

Task is returned to `ready` with `attempt: 2`, cleared claim metadata, so the next repository-agent claim becomes Attempt 3. SHARED-002 remains Pending until SHARED-001 is architect-accepted Complete.

### Attempt 3 Review

**Changes Requested — Attempt 3 did not implement the required corrections.**

The submitted Attempt 3 workspace was inspected directly. `src/billing.ts` and
`src/billing.test.ts` still contain the same rejected contracts and test coverage:

1. `BillingSystemMessageCodeSchema` still uses
   `z.enum(Object.values(BILLING_SYSTEM_MESSAGE_CODES) as [string, ...string[]])`.
   The task explicitly requires a construction that preserves the exact six-value
   `BillingSystemMessageCode` compile-time literal union and a compile-time
   assertion that fails if the type widens to `string`.

2. `createMerchantBillingSystemSourceKey` still has the old contract:

   `createMerchantBillingSystemSourceKey(shopId, code, version?)`

   There is still no required deterministic durable lifecycle/event identity.
   Therefore a later legitimate event for the same shop/code/version can still
   collide with the globally unique `MerchantSupportMessage.sourceKey`.

3. `src/billing.test.ts` still calls the old source-key helper and does not contain
   the focused tests required by the Attempt 2/3 correction:
   - same lifecycle identity replays to the same key;
   - different lifecycle identities produce different keys;
   - empty lifecycle identity is rejected;
   - long lifecycle identities remain bounded;
   - compile-time protection against `BillingSystemMessageCode` widening.

The Attempt 3 report states that no source changes were needed. That is incorrect:
the source still violates the explicit Attempt 3 Required Changes already present
in this task. Passing the existing repository suite only proves that the unchanged
Attempt 1 implementation still passes its original tests; it does not satisfy the
architect review.

### Attempt 4 Required Changes

Reclaim this same task as Attempt 4 and implement **only** the two existing
correction requirements. Do not reinterpret, waive, or merely revalidate them.

#### A. Exact billing SYSTEM-code type

Refactor the billing SYSTEM-code values/schema/type so all of the following are
true simultaneously:

- runtime Zod validation accepts exactly the six architecture-approved billing
  SYSTEM codes;
- exported `BillingSystemMessageCode` is the exact six-value TypeScript literal
  union, not `string`;
- `createMerchantBillingSystemSourceKey` accepts only that exact union;
- add a compile-time/type assertion in touched source/test/type-test code that
  fails if `string extends BillingSystemMessageCode` becomes `true`.

Do not use the existing `[string, ...string[]]` widening cast.

#### B. Lifecycle-scoped merchant SYSTEM source keys

Change the helper contract to require a non-empty deterministic durable lifecycle
or event identity, conceptually:

`createMerchantBillingSystemSourceKey(shopId, code, eventIdentity, version?)`

Requirements:

- `eventIdentity` is mandatory and trimmed/non-empty;
- replay of the same shop/code/eventIdentity/version returns the same key;
- a later distinct eventIdentity for the same shop/code/version returns a
  different key in ordinary deterministic cases;
- long identities are bounded to the existing 255-character source-key limit;
- no random UUIDs or timestamps generated by Shared;
- Shared performs no repository/database lookup; callers supply the durable
  identity.

Add focused tests that **would fail against the submitted Attempt 3 code**.

#### Mandatory validation and handoff

Run the task's existing typecheck, build, full test suite, focused billing tests,
and `git diff --check`. Update the Completion Report with the actual Attempt 4
source/test delta. Return **only ARCH-007-SHARED-001** to `review` and STOP.
Do not start SHARED-002.

### Attempt 4 Review

**Changes Requested — the submitted source still does not implement the active Architect Review contract.**

The authoritative Attempt 4 task metadata reached `review`, but direct inspection
of `src/billing.ts` and `src/billing.test.ts` shows the old contracts remain:

- `BillingSystemMessageCodeSchema` is still constructed with
  `Object.values(...) as [string, ...string[]]`, so the task still lacks the
  required compile-time guarantee that `BillingSystemMessageCode` is the exact
  six-value literal union.
- `createMerchantBillingSystemSourceKey` still accepts
  `(shopId, code, version = 1)` and has no durable lifecycle/event identity.
- the focused tests still call the two-argument helper and do not prove
  occurrence identity separately from message-contract version.

The task runner also emitted a progress label naming
`ARCH-007-DATABASE-003` while executing `ARCH-007-SHARED-001`. Under the updated
agent protocol, task-identity mismatches must be corrected before implementation.

### Attempt 5 Required Changes

This section is the authoritative rework contract for Attempt 5. It MUST be read
in full before source inspection. Attempt 5 MUST modify `src/billing.ts` and
`src/billing.test.ts`; a no-source-change revalidation is not acceptable.

#### 1. Preserve the exact billing SYSTEM-code literal union

Keep the existing exported `BILLING_SYSTEM_MESSAGE_CODES` object if desired, but
construct the Zod enum from an explicitly typed readonly tuple of the six exact
values rather than casting `Object.values(...)` to `[string, ...string[]]`.

Required compile-time invariant:

`BillingSystemMessageCode` must be the exact six-code literal union; `string`
must NOT be assignable to it.

Add a compile/type-level regression assertion that fails if this type widens to
`string`.

#### 2. Separate business occurrence identity from message-contract version

Change the helper contract to:

```ts
createMerchantBillingSystemSourceKey(
  shopId: string,
  code: BillingSystemMessageCode,
  eventIdentity: string,
  version = 1,
): string
```

Semantics are fixed:

- `eventIdentity` identifies WHICH durable business occurrence/transition is
  being notified;
- `version` identifies WHICH SYSTEM-message contract/content version is used;
- `version` is NOT an occurrence counter;
- callers own and supply the deterministic durable `eventIdentity`; Shared must
  not generate random UUIDs or timestamps.

The generated source key must include both dimensions (directly or through the
existing bounded deterministic hashing behaviour) and remain <=255 characters.

The helper must reject blank/whitespace `shopId`, `code`, and `eventIdentity`,
and reject non-positive/non-integer `version`.

#### 3. Mandatory focused tests

Replace/update the old source-key test so it proves all of the following:

1. same shop/code/eventIdentity with default version replay -> same key;
2. different eventIdentity with same shop/code/version -> different key;
3. same eventIdentity with version `1` vs explicit version `2` -> different key;
4. default version is `1`;
5. empty/whitespace eventIdentity is rejected;
6. long deterministic eventIdentity remains stable and source key <=255;
7. the compile-time SYSTEM-code type assertion is enforced.

A suitable readable unbounded case may be asserted explicitly, e.g. the key
contains shop, code, event identity and version. Do not require callers to use a
random identifier.

#### 4. Completion Report discipline

The Attempt 5 Completion Report MUST contain an Architect Review checklist with
one row/item for each requirement above, identifying:

- implementation status;
- files changed;
- focused test/typecheck evidence.

Run the task's required typecheck, build, tests and `git diff --check`, return
ONLY `ARCH-007-SHARED-001` to `review`, and STOP. Do not start SHARED-002.

### Attempt 6 Review

**Accepted.**

Direct architect review of the submitted Attempt 6 workspace confirms that the
active rework contract is implemented in source and focused tests.

Accepted corrections:

1. `BillingSystemMessageCodeSchema` is now constructed from an explicit readonly
   tuple of the six architecture-approved values. `BillingSystemMessageCode`
   therefore remains the exact literal union, and the compile-time assertion in
   `src/billing.test.ts` fails if the type widens so that `string extends
   BillingSystemMessageCode` becomes true.
2. `createMerchantBillingSystemSourceKey` now requires
   `(shopId, code, eventIdentity, version?)`. `eventIdentity` represents the
   durable business occurrence, while `version` remains the independent
   SYSTEM-message contract/content version with default `1`.
3. Focused tests prove same-event replay stability, distinct lifecycle identity,
   explicit version `2` distinction, default version `1`, blank event-identity
   rejection, deterministic bounded long identities and the compile-time code
   type invariant.
4. The accepted implementation preserves the existing browser-safe `./billing`
   export, strict provider-status validation, deterministic recovery identity and
   <=64-character Shopify usage idempotency helper.

The agent reported successful typecheck, build, full tests (103 passed, one
expected Redis-dependent skip), diagnostics and `git diff --check`. Source/test
inspection is consistent with that validation evidence.

### Reviewed Files — Attempt 6

- `src/billing.ts`
- `src/billing.test.ts`
- `src/index.ts`
- `package.json`
- `tsup.config.ts`
- `docs/decisions/shared/ARCH-007/SHARED-001-define-billing-contracts.md`

### Architecture Conformance — Attempt 6

Accepted. SHARED-001 is architect-complete. The canonical contract is ready for
the publication-only SHARED-002 gate; consumer repositories remain blocked until
SHARED-002 itself is architect-accepted Complete.

### Follow-up — Attempt 6

Mark `ARCH-007-SHARED-002` Ready with `attempt: 0`. Do not unblock SHOPIFY,
MESSAGING, BACKGROUND or ADMIN consumers until the Shared publication task has
completed and been architect-accepted.


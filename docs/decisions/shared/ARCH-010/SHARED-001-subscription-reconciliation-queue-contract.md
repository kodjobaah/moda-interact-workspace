---
id: ARCH-010-SHARED-001
architecture_id: ARCH-010
title: Define subscription reconciliation BullMQ contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-007-SHARED-006
enables:
  - ARCH-010-SHARED-002
  - ARCH-010-SHARED-003
created: 2026-09-11
updated: 2026-09-11T16:01:47Z
---

# ARCH-010-SHARED-001: Define subscription reconciliation BullMQ contract

## Objective

Define the one canonical cross-repository queue contract used by `moda-interact` producers and `moda-interact-background` consumers for durable subscription reconciliation.

## Repository / files

Inspect:

```text
src/billing.ts
src/index.ts
package.json
tsup.config.ts
```

Follow existing Zod/runtime contract patterns. Do not create a duplicate generic queue-contract mechanism.

## Required exports

Add canonical exports from the billing entrypoint for:

```text
BILLING_SUBSCRIPTION_RECONCILE_SCHEMA_VERSION = 1
BILLING_SUBSCRIPTION_RECONCILE_QUEUE_NAME = "billing-subscription-reconcile"
BILLING_SUBSCRIPTION_RECONCILE_JOB_NAME = "reconcile-subscription"
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS = 300000
BillingSubscriptionReconcileJobSchema
BillingSubscriptionReconcileJob
parseBillingSubscriptionReconcileJob(...)
safeParseBillingSubscriptionReconcileJob(...)
createBillingSubscriptionReconcileJobId(subscriptionId, expectedNextReconcileAt)
```

Payload v1 must be strict and contain exactly:

```ts
{
  schemaVersion: 1;
  shopId: string;
  subscriptionId: string;
  expectedNextReconcileAt: string; // offset-aware ISO datetime
}
```

Use bounded non-empty identifier validation consistent with existing Shared billing contracts.

The deterministic job ID must be derived solely from the canonical subscription ID and expected reconciliation timestamp. It must contain no `:` characters and must remain within BullMQ/custom-ID practical limits. Identical inputs must always produce an identical ID; changing the timestamp must change the ID.

The payload must not carry plan IDs, credit balances, entitlement decisions or provider tokens. PostgreSQL/Shopify remain authoritative.

`APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` is a cross-repository Shopify App Pricing billing policy constant, not queue payload data. It must equal exactly five minutes (`300000`). It is used for any action that would create an App Event near a Shopify monthly billing-cycle boundary, including Paid normal-recovery billing events and Free/Paid recovery-credit-pack top-up billing events. Paid recovery admission may use the same window because its included recovery creates a billing App Event; Free lifetime recovery admission does not create an App Event and MUST NOT be paused merely because the Free Shopify billing cycle is draining. Do not create service-local copies with different values.

## Required tests

Prove at least:

1. valid payload parses;
2. wrong/missing schema version is rejected;
3. missing/blank shopId is rejected;
4. missing/blank subscriptionId is rejected;
5. invalid timestamp is rejected;
6. unknown payload fields are rejected;
7. job ID is deterministic;
8. job ID changes when expected timestamp changes;
9. job ID contains no colon;
10. public package billing entrypoint exports all required symbols;
11. `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` is exported from the billing entrypoint and equals `300000`;
12. the generic App Pricing drain constant is not serialized into the v1 queue payload.

## Validation

Inspect `package.json`; run only declared relevant tests/build/typecheck plus `git diff --check`.

## Non-goals

Do not publish in this task. Do not edit consumers/producers, Prisma, Render, billing periods or credits. Defining the canonical drain constant is in scope; implementing its timing behaviour is not.

## Completion Report

### Status
Ready for Review

### Files Changed
- `src/billing.ts`
- `src/billing.test.ts`

### Work Completed
- Added the strict v1 subscription reconciliation payload schema, parser, safe parser, and inferred type.
- Added canonical queue/job names, schema version, and the five-minute App Pricing billing-period drain-window constant.
- Added a deterministic, colon-free, bounded BullMQ job ID derived from subscription ID and expected reconciliation timestamp.
- Exported all contract symbols through the existing public billing entrypoint.
- Added rejection and determinism coverage, including proof that the drain constant is not serialized into the payload.

### Validation Results
- `npm run test -- src/billing.test.ts` passed: 109 passed, 0 failed, 1 skipped because `TEST_REDIS_URL` is not configured; the declared test glob runs the repository test suite.
- `npm run typecheck` passed.
- `npm run build` passed, including public billing declarations.
- `git diff --check` passed.
- `npm ci` installed the repository lockfile dependencies in the new worktree; npm reported one low-severity audit finding and pending install-script approvals, with no task-source impact.

### Git / VCS
- Task branch: `task/ARCH-010-SHARED-001`.
- Physical worktree isolation:
  - canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
  - parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHARED-001`;
  - parent branch: `task/ARCH-010-SHARED-001`;
  - implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHARED-001`;
  - implementation branch: `task/ARCH-010-SHARED-001`;
  - shared workspace checkout switched/mutated for task work: no;
  - shared implementation checkout switched/mutated for task work: no;
  - another task worktree reused: no.
- Start-of-attempt synchronization:
  - parent remote task branch fast-forwarded: not-needed; branch created from current `origin/main`;
  - parent `origin/main` incorporated: already-current;
  - implementation remote task branch fast-forwarded: not-needed; branch created from current `origin/main`;
  - implementation `origin/main` incorporated: already-current.
- Implementation repository: `moda-interact-shared`, commit `6ba830d`, remote `origin/task/ARCH-010-SHARED-001`, pushed: yes.
- Parent workspace task file: this file, claim commit `5ef8118`, review commit `3729dc1`, pushed: yes.
- Submodule gitlink staged: no.
- Merged to implementation main: no.
- Merged to workspace main: no.

### Architect Review

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested (public-entrypoint proof only)

The ARCH-010-SHARED-001 runtime contract is architecturally correct. No queue
schema, job-ID, queue-name, job-name, drain-window, or parser redesign is
requested.

Architect review verified:

- `BILLING_SUBSCRIPTION_RECONCILE_SCHEMA_VERSION` is exactly `1`;
- queue name is exactly `billing-subscription-reconcile`;
- job name is exactly `reconcile-subscription`;
- `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` is exactly `300000`;
- the v1 payload is a strict Zod object containing only `schemaVersion`, `shopId`,
  `subscriptionId`, and offset-aware `expectedNextReconcileAt`;
- shop/subscription identifiers are trimmed, non-empty and bounded consistently
  with existing Shared billing identifiers;
- unknown fields and invalid/missing required values are rejected;
- `createBillingSubscriptionReconcileJobId(...)` is derived only from the trimmed
  subscription ID and expected timestamp, is deterministic, changes when the
  timestamp changes, contains no colon, and is comfortably within the practical
  BullMQ custom-ID bound;
- the drain-window constant is module policy and is not payload data;
- the existing `package.json` `./billing` export and `tsup` billing entry remain
  correctly configured;
- the Completion Report contains the required dedicated parent/implementation
  worktree evidence and all four start-of-attempt synchronization outcomes;
- the skipped Redis integration test is unrelated to this contract and is
  legitimately skipped because `TEST_REDIS_URL` is unset.

One explicit Required Tests item is not directly proven by the submitted test.

##### Required correction — prove the public package `./billing` entrypoint

Required Test 10 says:

```text
public package billing entrypoint exports all required symbols
```

The new `billing.test.ts` imports from:

```ts
"./billing.js"
```

That proves the source module exports the values, but it does not prove that a
consumer of the package subpath:

```text
@modainteract/moda-interact-shared/billing
```

can obtain the complete contract through the package export/build surface.

Add a focused public-entrypoint smoke assertion after build, or an equivalent
deterministic package-export validation, that proves the built/package `./billing`
entrypoint exposes all runtime symbols required by this task:

```text
BILLING_SUBSCRIPTION_RECONCILE_SCHEMA_VERSION
BILLING_SUBSCRIPTION_RECONCILE_QUEUE_NAME
BILLING_SUBSCRIPTION_RECONCILE_JOB_NAME
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
BillingSubscriptionReconcileJobSchema
parseBillingSubscriptionReconcileJob
safeParseBillingSubscriptionReconcileJob
createBillingSubscriptionReconcileJobId
```

Also prove the generated declaration for the public billing entrypoint exposes the
`BillingSubscriptionReconcileJob` type. A small build-time validation script is
acceptable if that matches existing Shared entrypoint-validation patterns.

Do not duplicate the contract in another module merely for testing.

##### Validation

After normal Attempt 2 synchronization/claim, rerun the repository-declared
relevant validation, including:

```text
npm run test -- src/billing.test.ts
npm run typecheck
npm run build
git diff --check
```

and run the new public-billing-entrypoint smoke validation if implemented as a
separate declared command.

The existing Redis integration skip remains acceptable unless this task itself
changes that integration path.

##### Scope guard

This is a validation/export-proof correction only.

Do not change the accepted payload shape, queue/job identity, job-ID algorithm,
drain-window value, billing semantics, consumers/producers, Prisma, Render or
credit logic.

Do not publish the package in this task. Publication remains owned by
`ARCH-010-SHARED-002`.

Return the same task to `review`.


## Stop conditions

STOP and return to `moda_architect` if an integrated/published Shared contract already owns the same queue/job identity with an incompatible payload or deterministic job-ID rule. Do not create a second reconciliation queue to avoid resolving that conflict.

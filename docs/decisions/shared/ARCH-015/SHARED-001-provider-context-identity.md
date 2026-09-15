---
id: ARCH-015-SHARED-001
architecture_id: ARCH-015
title: Canonical Shopify provider-context identity
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
- ARCH-015-SHOPIFY-002
- ARCH-015-BACKGROUND-001
- ARCH-015-BACKGROUND-002
- ARCH-015-SHOPIFY-003
- ARCH-015-BACKGROUND-003
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015-SHARED-001

## Objective

Publish one deterministic Shared contract used by `moda-interact` and `moda-interact-background` to derive and compare Shopify provider billing contexts.

Do not add database, Shopify API, ARCH-014, pricing, entitlement or refund logic.

## Authorized implementation surface

```text
src/billing.ts
src/billing.test.ts
package.json
package-lock.json
# package export/build files only if current package convention requires
```

Prefer the existing billing entrypoint instead of creating a second billing package surface.

## Required API

Implement and export functions equivalent to:

```ts
deriveShopifyProviderContextIdentity(input): string
isSameShopifyPurchaseProviderContext(purchase, current): boolean
```

Use current repository naming/type conventions but preserve the exact semantics below.

### Identity derivation

Input facts:

```text
providerSubscriptionId: string | null
planHandle: string
currentPeriodStart: Date|string|null
currentPeriodEnd: Date|string|null
```

Rules:

1. trim `providerSubscriptionId`;
2. if non-empty, return the trimmed provider id unchanged for backward compatibility with existing snapshots;
3. otherwise require non-empty trimmed `planHandle`;
4. otherwise require valid period start/end;
5. require start < end;
6. normalize dates with `Date.toISOString()`;
7. encode the trimmed plan handle with `encodeURIComponent`;
8. return exactly:

app-pricing:v1:<encodedPlanHandle>:<startIso>:<endIso>

Invalid/missing fallback evidence throws a bounded deterministic error beginning:

```text
SHOPIFY_PROVIDER_CONTEXT_INVALID:
```

Do not use current wall-clock time.

### Context comparison

Purchase facts:

```text
providerContextIdentity
shopifyPlanHandleSnapshot
billingPeriodId
```

Current facts:

```text
providerContextIdentity
shopifyPlanHandle
billingPeriodId
```

Return `true` only when all three trimmed/string identities match exactly.

Do not compare eventHandle inside this generic helper; callers must separately validate the meter required by their operation.

## Tests

Cover:

- raw legacy id returned unchanged after trim;
- two identical native inputs generate identical identity;
- different plan handles differ;
- different period starts differ;
- different period ends differ;
- malformed/missing fallback facts throw;
- start >= end throws;
- comparison requires identity + plan + billingPeriod;
- event handle is deliberately not part of generic context comparison;
- existing Shared billing exports remain unchanged.

## Publication

Read the current package version. Bump exactly one patch version. Do not choose a minor/major version.

Run package validation, publish the patch release using existing repository publication procedure, and verify the published billing export contains both functions.

## Validation

Inspect package scripts, then run applicable exact equivalents of:

```text
npm test
npm run typecheck
npm run build
npm pack --dry-run
git diff --check
```

## Stop conditions

STOP and return to `moda_architect` if:

- existing public billing API already defines a conflicting provider-context identity contract;
- publication would require a breaking package/API change;
- implementation requires Prisma/database/provider network access.

## Completion protocol

Record published version in Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Status: Review; implementation complete and returned to `moda_architect`.

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-SHARED-001` on `task/ARCH-015-SHARED-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-SHARED-001` on `task/ARCH-015-SHARED-001`.
- Shared/default checkout switched or mutated: no.
- Another task worktree reused: no.

### Start-of-Attempt Synchronization

- Parent remote task branch fast-forwarded: not-needed.
- Parent `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed.
- Implementation `origin/main` incorporated: already-current.
- Recursive submodules: none; sync and initialization passed.
- Launcher claim commit: `401ba7e2504f30b73be6b9ed7c62f29d61c855b5`.

### Implementation

- Added and exported `deriveShopifyProviderContextIdentity` with legacy ID
	compatibility, deterministic native fallback identity derivation, strict date
	validation, and bounded `SHOPIFY_PROVIDER_CONTEXT_INVALID:` errors.
- Added and exported `isSameShopifyPurchaseProviderContext`, comparing only the
	trimmed provider context identity, plan handle, and billing period ID.
- Added coverage for deterministic identity generation, differing plan/period
	inputs, malformed fallback evidence, ordering errors, comparison requirements,
	event-handle independence, and existing billing exports.
- Bumped exactly one patch version from `0.11.0` to `0.11.1`.

### Validation and Publication

- `npm test`: 112 passed, 1 skipped.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `npm run validate:billing-entrypoint`: passed; runtime and declaration exports
	are present.
- `npm pack --dry-run`: passed for `@modainteract/moda-interact-shared@0.11.1`.
- `git diff --check`: passed.
- Published `@modainteract/moda-interact-shared@0.11.1` to npm with public
	access. npm accepted the publication; registry metadata was still propagating
	when checked immediately afterward and returned a temporary 404, so the
	published-registry export verification remains propagation-pending.
- Implementation commit: `882fefc`.

### Architect Review

The bounded shared contract is implemented without database, Shopify API,
pricing, entitlement, or refund logic. Review the implementation and complete
the final registry propagation check before promoting the task.

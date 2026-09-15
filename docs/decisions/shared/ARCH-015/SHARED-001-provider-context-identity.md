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
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-09-15T12:44:02Z
attempt: 2
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

## Architect Review — Attempt 1

### Status

**Changes Requested — one functional fail-closed provider-context comparison correction plus corrected patch publication**

This review uses the ARCH-015 v1.1 architecture and task definition from the
supplied 2026-09-15 workspace snapshot as the binding contract. It intentionally
prioritises runtime/provider-context correctness over expanding test coverage for its
own sake.

Attempt 1 is otherwise accepted. In particular, preserve the implemented behavior
for:

```text
legacy providerSubscriptionId -> trimmed raw provider id unchanged
native App Pricing fallback -> deterministic app-pricing:v1 identity
trimmed + encoded plan handle
exact ISO-normalised period start/end
start < end validation
bounded SHOPIFY_PROVIDER_CONTEXT_INVALID: failures
no wall-clock fallback
no event-handle comparison in the generic context helper
no database / Shopify API / pricing / entitlement / refund logic in Shared
```

The published `0.11.1` artifact must be treated as immutable. Do not attempt to
republish or overwrite it.

### Finding — blank required context facts compare as the same provider context

`isSameShopifyPurchaseProviderContext(...)` currently evaluates each pair using:

```ts
purchaseValue.trim() === currentValue.trim()
```

without requiring the trimmed values to be non-empty.

Therefore malformed or incomplete inputs such as:

```text
purchase.providerContextIdentity = ""
current.providerContextIdentity  = "   "

purchase.shopifyPlanHandleSnapshot = ""
current.shopifyPlanHandle           = ""

purchase.billingPeriodId = "   "
current.billingPeriodId  = ""
```

can satisfy the corresponding equality checks. If all three pairs are blank, the
helper returns `true`.

That contradicts the task contract:

```text
comparison requires identity + plan + billingPeriod
```

and is unsafe for ARCH-015 downstream consumers. `BACKGROUND-002` uses this shared
comparison concept to classify current-context lots, while `SHOPIFY-003` uses current
provider-context matching as a prerequisite to the normal monetary refund path. A
missing provider identity, plan handle or billing period must never be interpreted as
positive evidence that two contexts are the same.

This is a functional fail-open defect, not a request for broader test exhaustiveness.

### Required Attempt-2 correction

Modify only the original Shared task surface required for this correction:

```text
moda-interact-shared/src/billing.ts
moda-interact-shared/src/billing.test.ts
moda-interact-shared/package.json
moda-interact-shared/package-lock.json
```

No consumer repository changes are authorised in this task.

#### 1. Fail closed on blank comparison facts

In `src/billing.ts`, preserve the existing three-field comparison and trimming, but
return `false` unless **both** values in **every** required pair are non-empty after
trimming.

Required semantics for each pair are exactly:

```text
purchase value is a string
current value is a string
trim(purchase value) is non-empty
trim(current value) is non-empty
trim(purchase value) === trim(current value)
```

The three required pairs remain exactly:

```text
purchase.providerContextIdentity   <-> current.providerContextIdentity
purchase.shopifyPlanHandleSnapshot <-> current.shopifyPlanHandle
purchase.billingPeriodId           <-> current.billingPeriodId
```

Do not add `eventHandle` to this helper.

Do not throw for a blank comparison field. This helper is a predicate; malformed or
incomplete comparison evidence must produce `false`.

A deterministic implementation is equivalent to:

```ts
return pairs.every(([purchaseValue, currentValue]) => {
  if (typeof purchaseValue !== "string" || typeof currentValue !== "string") {
    return false;
  }

  const normalizedPurchaseValue = purchaseValue.trim();
  const normalizedCurrentValue = currentValue.trim();

  return normalizedPurchaseValue.length > 0
    && normalizedCurrentValue.length > 0
    && normalizedPurchaseValue === normalizedCurrentValue;
});
```

Preserve the already-correct identity derivation function unchanged unless a purely
mechanical formatting/import adjustment is required.

#### 2. Focused regression evidence

In `src/billing.test.ts`, retain the existing positive match, mismatching
identity/plan/billing-period cases, and event-handle-independence test.

Add focused assertions proving the predicate returns `false` when either side of any
required field is empty or whitespace-only. At minimum cover:

```text
blank purchase providerContextIdentity
blank current providerContextIdentity
blank purchase shopifyPlanHandleSnapshot
blank current shopifyPlanHandle
blank purchase billingPeriodId
blank current billingPeriodId
```

No broader test expansion is required.

### Publication correction

Attempt 1 already published `@modainteract/moda-interact-shared@0.11.1`. npm package
versions are immutable, so the corrected runtime contract cannot be published again
as `0.11.1`.

For Attempt 2:

```text
package.json      0.11.1 -> 0.11.2
package-lock.json 0.11.1 -> 0.11.2
```

Update both canonical root-version declarations in `package-lock.json` and do not
change dependency versions solely for this correction.

Publish **exactly**:

```text
@modainteract/moda-interact-shared@0.11.2
```

once, using the repository's existing public npm publication procedure. Do not use
`--force`, do not attempt to overwrite `0.11.1`, and do not choose a minor/major
version.

Before publishing, verify `0.11.2` does not already exist. If it unexpectedly exists,
STOP and return to `moda_architect`; do not invent another version.

### Required exact-version registry smoke

The Attempt-1 Completion Report explicitly records that published-registry export
verification was still propagation-pending. Attempt 2 must close that original task
requirement for the corrected release.

After npm reports successful publication and registry metadata resolves, verify at
minimum:

```text
npm view @modainteract/moda-interact-shared@0.11.2 version dist.tarball dist.shasum
npm view @modainteract/moda-interact-shared dist-tags.latest
```

Then install **exactly `0.11.2`** into an isolated clean temporary consumer and import:

```text
@modainteract/moda-interact-shared/billing
```

Prove the registry-installed artifact exports both runtime functions:

```text
deriveShopifyProviderContextIdentity
isSameShopifyPurchaseProviderContext
```

and prove the installed `isSameShopifyPurchaseProviderContext` returns `false` for a
blank required comparison fact and `true` for a valid matching three-field context.

A transient propagation miss may be retried. Do not mark the task `review` until the
exact corrected registry artifact can be resolved and smoke-tested, or return the
exact external blocker without claiming publication verification.

### Attempt-2 validation

Run the task's normal Shared validation against the corrected source:

```bash
cd moda-interact-shared

npm test
npm run typecheck
npm run build
npm run validate:billing-entrypoint
npm pack --dry-run

git diff --check
```

Then perform the exact-version registry smoke above after publishing `0.11.2`.

### Accepted Attempt-1 work — do not churn

Do not redesign or widen:

```text
Shopify provider-context identity format
legacy provider-id compatibility
period normalisation rules
error prefix
billing entrypoint
existing Shared billing contracts
ARCH-014 pricing semantics
purchase admission
purchase reconciliation
cross-plan consumption
refund eligibility/correction
Prisma schema
consumer repositories
```

`0.11.1` remains historical publication evidence only. Downstream ARCH-015 tasks must
consume the corrected architect-accepted Shared release after Attempt 2, not rely on
the defective comparator from `0.11.1`.

### Workflow / Completion Report

Return the **same** task through:

```text
/moda-task ARCH-015-SHARED-001
```

Preserve before reclaim:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next authorised claim increments this task to Attempt 2 exactly once.

The Attempt-2 Completion Report must record:

```text
implementation correction commit
0.11.2 package + lock versions
successful local validation
successful npm publication
registry version/tarball/shasum/latest evidence
clean exact-version consumer import
runtime export smoke for both provider-context functions
blank-context fail-closed smoke
parent report commit
clean parent + implementation worktrees
```

### Review evidence

The developer-reported implementation commit resolves in the connected Shared
repository as:

```text
882fefcb4fccd47cf492f0ff8259fd0c8fb592e7
feat: add Shopify provider context identity
```

and changes only the expected implementation/test/package-version files.

The developer-reported parent Completion Report commit resolves as:

```text
06f41f6adfd789c567499a47dcbeca85828edef0
docs: complete provider context identity task
```

The supplied implementation archive confirms the source shown in that commit and the
parent task is at `status: review`, `attempt: 1`, with its claim cleared.

No new ARCH-015 task is created. No dependant is promoted from Pending while
`ARCH-015-SHARED-001` remains unaccepted.

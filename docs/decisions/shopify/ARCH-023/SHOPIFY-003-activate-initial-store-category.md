---
id: ARCH-023-SHOPIFY-003
architecture_id: ARCH-023
title: Activate initial pending Store Category after authoritative subscription activation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 51
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHOPIFY-002
enables: []
created: 2026-09-29
updated: 2026-09-30
---

# Activate initial pending Store Category after authoritative subscription activation

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Activate the initial pending Store Category only after Moda has durably established that the shop's **current** Subscription is `ACTIVE` or `TRIALING` with a current `planId`.

The plan-selection return/configure signal is not itself activation authority. If the synchronous Shopify-side path observes and commits an active/trialing subscription, it may invoke the activation immediately. If subscription activation is established later by the existing Background billing reconciler, that Background path must invoke the same idempotent activation contract in a separate bounded task.

This task has **no Merchant Knowledge activation behaviour**. Subscription activation only makes plan-backed Merchant Knowledge configuration available; explicit merchant opt-in is owned by SHOPIFY-004/ADMIN-004 and later Background/Commerce follow-ups.

## Context

A `CommerceShopProfile` with:

```text
activeCategoryId = null
pendingCategoryId != null
pendingPromptRevisionId != null
```

represents initial onboarding category state.

Receiving a plan handle, welcome/configure return, or marking onboarding complete does not prove the subscription is active. The only activation gate is the durable current Subscription projection.

After initial activation, any later pending category is a post-onboarding change and must wait for Admin publication.

## Scope

Primary authorized implementation surface:

```text
app/services/store-profile/commerce-environment.server.ts
app/services/store-profile/store-category-activation.server.ts

app/routes/app/billing/callback/route.tsx   # only where this existing path actually commits ACTIVE/TRIALING

existing subscription-sync integration point in moda-interact, if required

tests/unit/store-category-activation.test.ts
tests/unit/routes/billing-callback.test.ts
tests/integration/store-category-activation.integration.test.ts
```

Do not create a new subscription webhook or a second subscription reconciler.

## Out of Scope

- Background subscription-reconciliation fallback implementation.
- later category-change Admin publication.
- Store Category selection.
- plan materialisation logic except consuming the existing durable projection.
- Merchant Knowledge activation, source processing or queue publication.
- Commerce runtime prompt composition.

## Requirements

### R1 — exact environment mapping

Create `resolveShopifyCommerceEnvironment(): CommerceEnvironment` using existing `resolveDeploymentEnvironmentName()` and map exactly:

```text
local -> LOCAL
test -> TEST
development -> DEVELOPMENT
staging -> STAGING
production -> PRODUCTION
```

Unknown values throw `Commerce environment is unavailable.`

### R2 — idempotent activation entrypoint

Create:

```ts
activateInitialPendingStoreCategoryIfEligible({
  shopId,
  expectedPendingSelectionGeneration?,
}): Promise<
  | { kind: "ACTIVATED"; categoryId: string; promptRevisionId: string }
  | { kind: "ALREADY_ACTIVE" }
  | { kind: "NO_PENDING" }
  | { kind: "SUBSCRIPTION_NOT_ACTIVE" }
>
```

### R3 — exact transaction eligibility

In one transaction:

1. lock Shop/CommerceShopProfile scope for `shopId`;
2. load the current Subscription;
3. require `status IN (ACTIVE, TRIALING)` and `planId != null`;
4. no profile -> `NO_PENDING`;
5. `activeCategoryId != null` -> `ALREADY_ACTIVE`;
6. require `pendingCategoryId`, `pendingPromptRevisionId`, `pendingSelectedAt`;
7. if expected generation is supplied, require exact equality;
8. load the pending category and exact pending revision;
9. require DRAFT, SHOP scope, same shop, non-null template provenance;
10. require the revision's `sourceTemplateId` matches the selected category's pinned default-template identity;
11. never re-read current template text.

Structural inconsistency throws bounded `STORE_CATEGORY_PENDING_STATE_CONFLICT` and rolls back.

### R4 — publish the exact pending DRAFT

Use one transaction timestamp and lowercase SHA-256 of exact UTF-8 `promptText`. Require non-empty trimmed text. Publish the existing revision only; do not create a replacement.

### R5 — set current Shop prompt atomically

Resolve current Commerce environment, find/create the one SHOP `CommerceAgentConfiguration`, set `activePromptRevisionId`, increment `promptEditVersion`, and preserve existing `modelId` / `modelEditVersion`.

### R6 — promote profile atomically

In the same transaction:

```text
activeCategoryId          = pendingCategoryId
activeCategoryActivatedAt = now
pendingCategoryId         = null
pendingPromptRevisionId   = null
pendingSelectedAt         = null
```

Preserve `pendingSelectionGeneration`.

### R7 — later changes never auto-activate

If `activeCategoryId != null`, return `ALREADY_ACTIVE` even when another pending category exists.

### R8 — integrate only after durable subscription activation

The Shopify-side integration may call R2 only **after** the existing billing/subscription synchronization path has committed:

```text
Subscription.status IN (ACTIVE, TRIALING)
Subscription.planId != null
```

Do not call merely because a plan handle/configure/welcome return was received. If that return records onboarding/plan intent but the durable subscription is not yet active, leave Store Category pending and let the existing Background billing reconciliation path establish subscription state later.

Category activation failure must not roll back an already-committed billing projection.

### R9 — onboarding milestone is separate

Preserve existing `ShopSettings.onboardingCompleted` semantics. It is neither proof of subscription activation nor the category activation gate.

### R10 — idempotency

Repeated invocation after successful activation returns `ALREADY_ACTIVE`, does not republish, does not increment versions again, and never clears a later post-onboarding pending category.

### R11 — audit

Use existing authorised Commerce audit helpers if available. Do not invent a PlatformAdmin/system actor solely for this task; record any audit-actor gap for architect follow-up.

### R12 — tests

Prove at minimum:

```text
plan/configure/welcome signal without durable ACTIVE/TRIALING -> no activation
NO_CONTRACT -> no activation
ACTIVE -> exact pending DRAFT activates
TRIALING -> exact pending DRAFT activates
activeCategoryId already set -> later pending remains untouched
current template edits after selection do not alter pinned prompt
configuration pointer + publication + profile promotion are atomic
mid-transaction failure rolls all three back
repeated activation is idempotent
billing projection remains committed if category activation fails afterward
no Merchant Knowledge preference/source/queue state is mutated
```

## Work Items

- [x] Add exact environment mapper.
- [x] Implement idempotent initial activation transaction.
- [x] Integrate only after an authoritative durable Shopify-side subscription activation commit.
- [x] Preserve later-category Admin boundary.
- [x] Add transaction/idempotency/subscription-gate tests.
- [x] Record the existing Background billing-reconciliation fallback as a separate unresolved implementation boundary if still absent.

## Interfaces / Contracts

Consumes SHOPIFY-002 pending state, current Subscription projection and Commerce prompt/configuration tables.

## Dependencies

- `ARCH-023-SHOPIFY-001`
- `ARCH-023-SHOPIFY-002`

## Acceptance Criteria

- [x] Only durable current ACTIVE/TRIALING subscription state can activate the initial category.
- [x] Initial category/prompt activation is exact, atomic and idempotent.
- [x] Later category changes remain Admin-owned.
- [x] No plan-handle/onboarding signal is treated as subscription-active authority.
- [x] No Merchant Knowledge activation or processing is coupled to subscription activation.

## Validation

- [x] focused activation tests
- [x] billing/subscription integration regressions
- [ ] transaction integration test execution (suite added; blocked because no container runtime is available and local PostgreSQL does not respond)
- [x] `npm run typecheck`
- [x] changed-file lint/diagnostics
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Attempt 1 implementation complete; returned for Architect Review.
### Files Changed
`app/services/store-profile/store-category-activation.server.ts`, `app/routes/app/billing/callback/route.tsx`, `tests/unit/store-category-activation.test.ts`, `tests/unit/routes/billing-callback.test.ts`, and `tests/integration/store-category-activation.integration.test.ts`.
### Work Completed
Added the exact deployment environment mapper and an atomic, idempotent initial activation transaction. It locks the Shop scope used by category selection, requires the current subscription to be ACTIVE/TRIALING with a plan, validates the complete pending profile/revision/template provenance, publishes the existing pinned DRAFT with lowercase SHA-256 of its exact UTF-8 text, updates or creates the one SHOP configuration while preserving model settings, and promotes/clears only the initial pending profile state. Existing active categories return `ALREADY_ACTIVE` without touching later pending selections. The billing callback invokes activation only after a successful durable Paid projection, successful Free completion, or a fresh `syncSubscription` result with a current active/trialing plan. Configure/welcome intent and onboarding completion alone do not invoke activation. No Merchant Knowledge preference/source/queue state or Background worker/reconciler was changed.
### Validation Results
Focused activation, billing callback, Store Category selection and action regressions: 60 passed; the two disposable PostgreSQL activation tests were skipped in the default run. `npm run typecheck`: passed. Changed-file ESLint: passed (emitted the repository's TypeScript 5.9.3 versus typescript-estree supported-version warning). Changed-file diagnostics: clean. `npm run build`: passed. `git diff --check`: passed. The activation PostgreSQL suite was also explicitly enabled, but Testcontainers failed before provisioning with `Could not find a working container runtime strategy`; the available local PostgreSQL probe reported no response at `/tmp:5432`. Thus the database-backed transaction assertions are implemented but could not be executed in this environment.
### Deviations
The requested live transaction validation could not run because this environment has neither a working container runtime nor a responding local PostgreSQL server; the disposable PostgreSQL suite is present and opt-in using the repository's existing integration convention.
### Assumptions
The existing billing callback may invoke the activation service only after the current projection transaction returns; a later Background reconciliation activation hook is a separate repository-owned task and remains outside SHOPIFY-003 scope.
### Unresolved Issues
The existing Background billing reconciler does not yet invoke this activation contract when subscription activation is established after the Shopify callback; a separate bounded Background task must add that hook. An activation transaction error currently propagates from the callback after the billing projection has committed; callback response and retry policy should be decided with the Background fallback boundary. No authorized Commerce audit helper/actor exists in this repository, so this task does not fabricate a system actor or audit event; the audit-actor gap is recorded for architect follow-up. The disposable PostgreSQL transaction suite remains unexecuted in this environment as noted above.
### Architectural Concerns
The callback path is covered here, but the missed-callback/background-reconciliation path remains a cross-repository follow-up. Activation errors are not swallowed: they can fail the Shopify callback response, although the prior billing projection commit remains durable. Decide whether that response behavior is desired and how retry/reconciliation will guarantee eventual activation. The existing Commerce audit schema accepts only PlatformAdmin or MerchantAccess actors and this activation has neither; an authorized actor/audit contract needs architect direction before audit records are added.

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-SHOPIFY-003`
  parent branch: `task/ARCH-023-SHOPIFY-003`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-SHOPIFY-003`
  implementation branch: `task/ARCH-023-SHOPIFY-003`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded submodule commit: `database` at `2eb17ee910491e8f9df82736fc0a843844415947`

Launcher claim:
  attempt: 1
  dependency gate: passed (`ARCH-023-SHOPIFY-001`, `ARCH-023-SHOPIFY-002`)
  executor: `copilot`
  claimed at: `2026-09-30T19:07:21Z`
  claim commit: `9388d1a8fc532eb6aa6a0f3234c60c2b826d4ded` (pushed)

Implementation commit:
  `be279948ff7421e9f5edfa567b58fd1ffe55e680` (pushed to `origin/task/ARCH-023-SHOPIFY-003`)

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes

The submitted implementation is substantively architecture-conformant by source inspection. The activation service uses the durable current `Subscription` projection as the only activation gate, locks the Shop scope, validates the exact pending Store Category/DRAFT/provenance, publishes that existing revision, updates the SHOP prompt configuration and promotes the profile inside one Prisma transaction. The billing callback invokes that service only after an ACTIVE/TRIALING projection with a current `planId`; onboarding/configure intent alone does not activate the category. No Merchant Knowledge preference/source/queue state is coupled to this lifecycle.

Acceptance is withheld for one bounded validation item only.

**A1-R1 — execute the required real PostgreSQL transaction proof.** The task's `transaction integration test execution` item remains unchecked. This proof is material because the implementation relies on the accepted PostgreSQL schema, raw `SELECT ... FOR UPDATE`, Prisma transaction rollback and database constraints for the core atomicity contract. The authored `tests/integration/store-category-activation.integration.test.ts` covers the correct cases, but both cases were skipped in the focused run and the explicit Testcontainers attempt stopped before PostgreSQL provisioning.

The same repository already proved the working Colima/Testcontainers invocation during accepted `ARCH-023-SHOPIFY-002`. Attempt 2 must rerun the existing SHOPIFY-003 integration suite from the canonical implementation worktree with the known repository-local Docker endpoint before changing production code:

```text
DOCKER_HOST="unix:///Users/kwadwoadomafriyie/.colima/default/docker.sock" \
TESTCONTAINERS_RYUK_DISABLED=true \
MODA_DISPOSABLE_INTEGRATION=1 \
npm test -- tests/integration/store-category-activation.integration.test.ts
```

Required durable evidence:

```text
all accepted migrations apply to fresh pgvector/pgvector:pg17
2/2 activation PostgreSQL cases pass
pinned DRAFT publication + configuration pointer + profile promotion commit atomically
forced profile-promotion failure rolls publication/configuration/profile back
pre-existing ACTIVE billing projection remains committed after that activation rollback
replay remains idempotent
disposable container is removed after the run
```

Do not change the database schema or production activation implementation merely to manufacture this evidence. If the live proof exposes a real defect, correct that defect inside this same task and rerun the focused validation.

The reported callback error propagation is **not an Attempt 1 defect**. R8 requires category activation to execute after, and outside, the durable billing projection transaction; it does not require the Shopify callback to swallow a Store Category activation failure. Keep the current separation for Attempt 2 unless the PostgreSQL proof exposes a correctness problem. A future UX/retry-policy change, if desired, is separate from proving this transaction.

The missing Background billing-reconciliation activation hook is also non-blocking for this Shopify task because it is explicitly out of scope and already required by D11 as a separate bounded Background integration before final ARCH-023 system acceptance. Likewise, R11 explicitly forbids fabricating a PlatformAdmin/system Commerce audit actor; the recorded audit-actor gap does not block SHOPIFY-003.

### Reviewed Files

Reviewed the task contract/report and submitted implementation surfaces, including:

```text
app/services/store-profile/store-category-activation.server.ts
app/routes/app/billing/callback/route.tsx
tests/unit/store-category-activation.test.ts
tests/unit/routes/billing-callback.test.ts
tests/integration/store-category-activation.integration.test.ts
database/prisma/schema.prisma
docs/architecture/ARCH-023-merchant-knowledge.md
```

### Validation Reviewed

Submitted evidence records 60 focused tests passing with 2 opt-in PostgreSQL activation tests skipped, plus passing TypeScript, production build, changed-file lint/diagnostics and `git diff --check`. The Completion Report also records canonical parent/implementation worktrees, start-of-attempt synchronization, recursive submodule preparation and the accepted database gitlink.

The review archive does not contain installed dependencies or a runnable Git worktree, so the architect did not claim to rerun the Node/Testcontainers suite from the archive. The missing acceptance evidence is specifically the task-owned real PostgreSQL execution above.

### Architecture Conformance

Conformant by source inspection. Initial activation is gated only by durable ACTIVE/TRIALING subscription state with a current plan; later pending category changes remain untouched once an active category exists; the exact pinned DRAFT is published without rereading current template text; prompt configuration model state is preserved; and Merchant Knowledge activation remains independent.

### Follow-up

Return this same task to `ready` for Attempt 2 with `attempt: 1` preserved and the execution claim cleared. Attempt 2 should be limited to the existing PostgreSQL integration proof plus any correction that proof actually demonstrates is necessary. Do not begin another Shopify task.

Before final ARCH-023 system acceptance, moda_architect must separately materialise the already-documented Background billing-reconciliation hook that calls this same idempotent activation contract when Background establishes ACTIVE/TRIALING after a missed callback. The Commerce automatic-actor/audit question remains a non-blocking architecture follow-up.

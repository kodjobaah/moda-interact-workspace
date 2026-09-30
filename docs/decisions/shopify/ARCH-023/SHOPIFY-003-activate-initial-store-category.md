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
status: in_progress
priority: 51
executor: copilot
claimed_at: 2026-09-30T20:33:16Z
attempt: 3
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
10. treat `sourceTemplateId` / `sourceTemplateEditVersion` as selection-time provenance only; do **not** compare `sourceTemplateId` with the category's current `defaultTemplateId`;
11. never re-read current template text or current default-template identity.

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
category default-template reassignment after selection does not invalidate or reseed the pinned prompt
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
- [x] transaction integration test execution
- [x] `npm run typecheck`
- [x] changed-file lint/diagnostics
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Attempt 2 completed the sole Architect-Requested correction (A1-R1); returned for Architect Review.
### Files Changed
`app/services/store-profile/store-category-activation.server.ts`, `app/routes/app/billing/callback/route.tsx`, `tests/unit/store-category-activation.test.ts`, `tests/unit/routes/billing-callback.test.ts`, and `tests/integration/store-category-activation.integration.test.ts`.
### Work Completed
Added the exact deployment environment mapper and an atomic, idempotent initial activation transaction. It locks the Shop scope used by category selection, requires the current subscription to be ACTIVE/TRIALING with a plan, validates the complete pending profile/revision/template provenance, publishes the existing pinned DRAFT with lowercase SHA-256 of its exact UTF-8 text, updates or creates the one SHOP configuration while preserving model settings, and promotes/clears only the initial pending profile state. Existing active categories return `ALREADY_ACTIVE` without touching later pending selections. The billing callback invokes activation only after a successful durable Paid projection, successful Free completion, or a fresh `syncSubscription` result with a current active/trialing plan. Configure/welcome intent and onboarding completion alone do not invoke activation. No Merchant Knowledge preference/source/queue state or Background worker/reconciler was changed.
### Validation Results
Attempt 1 focused activation, billing callback, Store Category selection and action regressions: 60 passed; the two disposable PostgreSQL activation tests were skipped in the default run. `npm run typecheck`: passed. Changed-file ESLint: passed (emitted the repository's TypeScript 5.9.3 versus typescript-estree supported-version warning). Changed-file diagnostics: clean. `npm run build`: passed. `git diff --check`: passed.

Attempt 2 A1-R1 exact architect-requested command, run from the canonical implementation worktree:

```text
DOCKER_HOST="unix:///Users/kwadwoadomafriyie/.colima/default/docker.sock" TESTCONTAINERS_RYUK_DISABLED=true MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/store-category-activation.integration.test.ts
```

Result: 1 test file passed; 2/2 PostgreSQL integration cases passed. The suite provisioned the disposable `pgvector/pgvector:pg17` database, applied accepted migrations, proved exact pinned DRAFT publication/configuration pointer/profile promotion, proved forced profile-promotion failure rolls all activation writes back while the separately committed Subscription remains ACTIVE, and proved replay idempotency. A post-run Colima `docker ps -a --filter ancestor=pgvector/pgvector:pg17` check returned no matching containers. No production implementation or schema change was needed. The implementation worktree remained clean at `be279948ff7421e9f5edfa567b58fd1ffe55e680`, matching its remote task branch.
### Deviations
None. The Attempt 1 container limitation was resolved for the architect-requested rerun by using the known Colima Docker endpoint; the live transaction proof passed in Attempt 2.
### Assumptions
The existing billing callback may invoke the activation service only after the current projection transaction returns; a later Background reconciliation activation hook is a separate repository-owned task and remains outside SHOPIFY-003 scope.
### Unresolved Issues
The existing Background billing reconciler does not yet invoke this activation contract when subscription activation is established after the Shopify callback; a separate bounded Background task must add that hook. No authorized Commerce audit helper/actor exists in this repository, so this task does not fabricate a system actor or audit event; the audit-actor gap is recorded for architect follow-up. These are non-blocking/out-of-scope boundaries per the Architect Review.
### Architectural Concerns
The callback path is covered here, but the missed-callback/background-reconciliation path remains a cross-repository follow-up. Activation errors are not swallowed: they can fail the Shopify callback response, although the prior billing projection commit remains durable. Per the Attempt 1 Architect Review, this is not a defect in the required transaction separation; any future callback UX/retry-policy change is separate. The existing Commerce audit schema accepts only PlatformAdmin or MerchantAccess actors and this activation has neither; an authorized actor/audit contract needs architect direction before audit records are added.

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

Attempt 2 launcher claim:
  status before/after: `ready` -> `in_progress`
  attempt: 2 (previous attempt: 1)
  dependency gate: passed (`ARCH-023-SHOPIFY-001`, `ARCH-023-SHOPIFY-002`)
  executor: `copilot`
  claimed at: `2026-09-30T19:40:30Z`
  claim commit: `c6ade4e5c336cb28fc9c729615437a1c14514949` (pushed)

Implementation commit:
  `be279948ff7421e9f5edfa567b58fd1ffe55e680` (pushed to `origin/task/ARCH-023-SHOPIFY-003`)

Attempt 2 implementation change: none; the architect-requested correction was validation-only.

## Architect Review

### Review Status
Changes Requested — Attempt 2

### Review Notes

Attempt 1 A1-R1 is closed. Attempt 2 executed the exact architect-requested disposable PostgreSQL proof against `pgvector/pgvector:pg17`: all accepted migrations applied, both activation integration cases passed, rollback left the separately committed ACTIVE Subscription intact, replay remained idempotent, and the disposable container was removed. No production change was needed for that validation correction.

Full conformance review nevertheless identified one task-scoped production defect that is inconsistent with the parent ARCH-023 snapshot/provenance contract and with accepted ADMIN-002 default-template management.

**A2-R1 — do not revalidate pinned template provenance against the category's current default template.** `CommerceAgentPromptRevision.sourceTemplateId` and `sourceTemplateEditVersion` record the template identity/version **at copy time**. `CommercePromptTemplateCategory.defaultTemplateId` is independently mutable by Admin after the merchant has made a pending Store Category selection. Therefore a valid sequence is:

```text
merchant selects Category A while Template A is its default
    -> pending DRAFT stores sourceTemplateId = Template A
Admin later changes Category A.defaultTemplateId to Template B
subscription becomes ACTIVE/TRIALING
    -> activation must still publish the exact already-pinned Template-A DRAFT
```

The current activation service instead loads the category's current `defaultTemplateId` and rejects when:

```text
revision.sourceTemplateId !== category.defaultTemplateId
```

That turns selection-time provenance into a live constraint and can make a legitimate pending onboarding selection impossible to activate after an unrelated Admin default-template reassignment.

Attempt 3 must make exactly this bounded correction:

1. In `app/services/store-profile/store-category-activation.server.ts`, continue loading/validating the pending category identity and exact pending DRAFT, SHOP scope, same shop, non-null `sourceTemplateId`, non-null `sourceTemplateEditVersion`, and non-empty pinned `promptText`.
2. Do **not** require `revision.sourceTemplateId === category.defaultTemplateId` and do not re-read/reseed the current default template.
3. Keep publication of the existing pending revision, SHOP configuration update/create, profile promotion, subscription gate, locking, idempotency and later-category behaviour unchanged.
4. Update the unit regression that currently treats a changed `defaultTemplateId` as inconsistent. A changed current default must be accepted; null/missing provenance must still fail closed.
5. Strengthen the PostgreSQL activation case so the fixture pins Template A, then changes the category's current `defaultTemplateId` to a distinct enabled Template B before calling the production activation service. Prove activation still publishes the existing Template-A DRAFT and retains its original `sourceTemplateId` / `sourceTemplateEditVersion`.
6. Rerun the focused activation/billing tests, the same disposable PostgreSQL integration suite, `npm run typecheck`, changed-file lint/diagnostics, `npm run build` and `git diff --check`.

Do not change database schema/migrations, billing projection semantics, onboarding milestones, Background reconciliation, Commerce audit actors, Merchant Knowledge preference/source/queue state, or another Shopify task. If the bounded correction exposes a different architectural conflict, return it to `moda_architect` rather than expanding scope.

### Reviewed Files

Reviewed the task/report, parent architecture and submitted implementation/test surfaces including:

```text
app/services/store-profile/store-category-activation.server.ts
app/services/store-profile/store-category-selection.server.ts
app/routes/app/billing/callback/route.tsx
tests/unit/store-category-activation.test.ts
tests/unit/routes/billing-callback.test.ts
tests/integration/store-category-activation.integration.test.ts
docs/decisions/admin/ARCH-023/ADMIN-002-manage-store-categories-default-templates.md
docs/architecture/ARCH-023-merchant-knowledge.md
```

### Validation Reviewed

Accepted the submitted Attempt 2 validation evidence: the exact Colima/Testcontainers command ran the production integration suite against a fresh `pgvector/pgvector:pg17` database with accepted migrations and passed 2/2 cases; teardown evidence reports no remaining test container. Attempt 1 also records 60 focused tests plus passing TypeScript, build, changed-file lint/diagnostics and `git diff --check`.

The uploaded review archive is a source snapshot rather than the developer's runnable worktree, so the architect did not claim to independently rerun Docker/Testcontainers from the archive.

### Architecture Conformance

Conformant except for A2-R1. The durable Subscription projection remains the only activation authority; publication/configuration/profile promotion remain one transaction; later category changes remain Admin-owned; Merchant Knowledge activation remains independent. The current-default-template comparison conflicts with ARCH-023's selection-time provenance semantics and accepted Admin ability to change `defaultTemplateId` without rewriting pending profiles.

### Follow-up

Return this same task to `ready` for Attempt 3 with `attempt: 2` preserved and the claim cleared. Attempt 3 is limited to A2-R1, its focused regressions and required validation. Do not begin another Shopify task.

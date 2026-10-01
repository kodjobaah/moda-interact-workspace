---
id: ARCH-023-SHOPIFY-004
architecture_id: ARCH-023
title: Activate and manage Merchant Knowledge web-page sources
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 51
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHARED-002
  - ARCH-023-ADMIN-004
enables:
  - ARCH-023-SHOPIFY-005
created: 2026-09-29
updated: 2026-10-01
---

# Activate and manage Merchant Knowledge web-page sources

## Objective

Implement the Merchant Knowledge control plane on the existing Recovery Settings page.

The current plan grants **configuration access**. Merchant Knowledge is an ordinary `MERCHANT_OPT_IN` Feature and the merchant explicitly enables/disables it through the existing Recovery Settings `FeaturePreferences` control / `ShopFeaturePreference` model.

Canonical invariant:

```text
effectiveMerchantKnowledgeEnabled = planEntitled && merchantEnabled
```

Source configuration is allowed while the feature is OFF, within current plan limits. OFF is non-destructive: source/revision data remains stored, no new processing is started, and Commerce retrieval is separately denied by COMMERCE-004.

This task also implements WEB_PAGE source lifecycle and generic ordering/read models reused by SHOPIFY-005.

## Scope

```text
app/services/merchant-knowledge/merchant-knowledge-entitlement.server.ts
app/services/merchant-knowledge/merchant-knowledge.server.ts
app/services/merchant-knowledge/merchant-knowledge-queue.server.ts

app/routes/app/recovery-settings/route.tsx
app/routes/app/recovery-settings/RecoverySettingsView.tsx
app/components/settings/FeaturePreferences.tsx             # tests/labels only if required; reuse existing control
app/components/settings/MerchantKnowledgeSection.tsx

app/routes/app/merchant-knowledge/source/route.ts
app/routes/app/merchant-knowledge/reorder/route.ts
app/routes/app/merchant-knowledge/refresh/route.ts
app/routes/app/merchant-knowledge/delete/route.ts

existing feature-preference save route/service only where needed to prove canonical activation behavior

tests/unit/merchant-knowledge-entitlement.test.ts
tests/unit/merchant-knowledge-actions.test.ts
tests/unit/merchant-knowledge-section.test.tsx
tests/integration/merchant-knowledge-source-lifecycle.integration.test.ts
```

Do not create a second Merchant Knowledge toggle or preference table.

## Out of Scope

- CSV/XLSX/R2 upload mechanics (SHOPIFY-005).
- Background ingestion.
- Commerce retrieval enforcement (COMMERCE-004).
- changing Feature activation mode (ADMIN-004).
- subscription activation logic.

## Requirements

### R1 — commercial entitlement is current-plan only

Implement/retain:

```ts
loadCurrentMerchantKnowledgeEntitlement(shopId)
```

Require current Subscription `ACTIVE|TRIALING`, current `planId`, active BillingPlan, enabled BillingPlanFeature, active `Feature.key=merchant_knowledge`, and `Feature.activationMode=MERCHANT_OPT_IN`. Parse C2 with Shared schema. Ignore pending future plans.

This resolver answers **plan entitlement/configuration access only**. It does not require the merchant preference to be enabled.

### R2 — canonical merchant activation state

Resolve the exact `ShopFeaturePreference` for the current `merchant_knowledge` Feature using the same semantics as the existing generic feature-preference service:

```text
missing preference -> false
enabled=false       -> false
enabled=true        -> true
```

Expose section-level:

```ts
{
  planEntitled: boolean;
  merchantEnabled: boolean;
  effectiveEnabled: boolean; // planEntitled && merchantEnabled
}
```

The existing `FeaturePreferences` checkbox is the only activation control. Do not add another toggle inside `MerchantKnowledgeSection`.

### R3 — active catalogue and source read model

Intersect active Purpose/Data Format compatibility with current C2 `allowedSourceTypes`. Load all shop sources ordered `(position ASC,id ASC)`.

For each source expose commercial/source state separately:

```ts
currentlyPlanEntitled
processingEligible // currentlyPlanEntitled && merchantEnabled
dormantReason: null | "MERCHANT_DISABLED" | "SOURCE_TYPE" | "SOURCE_COUNT" | "NO_CURRENT_PLAN"
```

Disabled Merchant Knowledge does not delete or hide configured sources.

### R4 — public HTTPS syntax validation

Require URL length <=2048, parseable `https:`, no username/password, persist `url.toString()`. Network SSRF checks remain Background-owned.

### R5 — create WEB_PAGE source while ON or OFF

Validate plan entitlement and exact currently allowed Purpose/Data Format pair; **do not require merchantEnabled**.

In one Shop-locked transaction enforce source-count rules, allocate position, create source generation 1 and one `CREATE/PENDING` revision.

After commit:

```text
merchantEnabled=true  -> enqueue C4 best effort
merchantEnabled=false -> do not enqueue; leave durable PENDING
```

No second reconciliation job is introduced. Existing Background periodic PENDING reconciliation will observe the preference after it becomes enabled.

### R6 — edit URL/metadata

Plan-entitled source remains configurable while feature is OFF. Purpose/Data Format stay immutable. URL change creates `URL_CHANGE/PENDING`; metadata-only edit creates no revision. Post-commit enqueue follows R5 activation rule.

### R7 — Refresh

Owned, currently plan-entitled WEB_PAGE source may create `REFRESH/PENDING` while ON or OFF. Post-commit enqueue follows R5.

### R8 — delete

Delete owned source and collision-safely compact positions. Deletion is allowed while OFF.

### R9 — reorder

Require exact set equality and collision-safe rewrite to `0..N-1`. Reorder is allowed while OFF and for dormant/excess sources.

### R10 — queue helper

Use existing Shared C4 queue constants/schema/job-id. Queue publication is an optimisation, not source of truth.

Before immediate post-commit enqueue, use the committed activation snapshot or safely re-read it. If OFF, skip enqueue without error. Races where the merchant disables after enqueue are handled by BACKGROUND-006/004 re-checks.

Enabling Merchant Knowledge itself does **not** enumerate/enqueue sources in Shopify. The existing periodic Background PENDING reconciliation is the repair/activation mechanism.

### R11 — Recovery Settings UI

Order remains:

```text
Conversation Features
  existing generic Merchant Knowledge checkbox (canonical ON/OFF)
Store Profile
Merchant Knowledge
Existing recovery settings
```

When plan-entitled but OFF, Merchant Knowledge section remains configurable and clearly indicates that ingestion/retrieval are disabled until the merchant enables the feature.

Show configured/max, source list/order, entitlement/dormancy, localized Purpose/Data Format, language, URL, revision status, active usage/truncation/last processed.

### R12 — source language

Default from `resolveModaConfigurationLocale(ShopSettings.defaultLanguageTag)`; allow exact Shared supported tags.

### R13 — authentication/tenant boundary

Every Merchant Knowledge action must derive `shopId` from the authenticated Shopify session/access boundary. Browser input must never supply `shopId`. Ownership is checked before mutation or external calls.

### R14 — concurrency

Lock Shop for ordering/count and source for generation. Concurrent creates cannot exceed current commercial allowance; revision generation increments once per committed revision.

### R15 — tests

Prove at minimum:

```text
Feature is MERCHANT_OPT_IN
missing/false ShopFeaturePreference -> merchantEnabled=false
true preference -> effectiveEnabled=true when plan entitled
plan entitled + OFF -> source create/edit/refresh/reorder/delete allowed
plan entitled + OFF -> new PENDING revision is NOT enqueued
plan entitled + ON -> new PENDING revision gets best-effort enqueue
activation toggle uses existing FeaturePreferences/ShopFeaturePreference only
turning OFF deletes/mutates no source/revision/chunk data
no current plan -> configuration unavailable
malformed C2 -> fail closed
disallowed pair rejected
source type filtering precedes source-count limit
queue failure leaves PENDING
no extracted content/vector returned to UI
shopId cannot be supplied by browser
```

## Work Items

- [x] Implement current commercial entitlement + merchant activation read model.
- [x] Reuse existing FeaturePreferences as the sole Merchant Knowledge activation control.
- [x] Implement activation-aware WEB_PAGE source lifecycle and queue decision.
- [x] Add Recovery Settings Merchant Knowledge section.
- [x] Add tenant/authentication/concurrency tests.

## Dependencies

- `ARCH-023-SHOPIFY-001`
- `ARCH-023-SHARED-002`
- `ARCH-023-ADMIN-004`

Resolved Shared release: `@modainteract/moda-interact-shared@1.0.1`.

## Enables

- `ARCH-023-SHOPIFY-005`

## Acceptance Criteria

- [x] Subscription/current plan grants configuration access but does not activate Merchant Knowledge.
- [x] Existing ShopFeaturePreference is the sole merchant activation state.
- [x] OFF permits non-destructive source configuration but no immediate processing.
- [x] ON permits Background ingestion; Commerce enforcement remains independently owned by COMMERCE-004.
- [x] WEB_PAGE lifecycle remains revisioned and queue-loss safe.
- [x] No duplicate preference/toggle mechanism exists.

## Validation

- [x] focused entitlement/activation/action tests
- [x] DB concurrency integration tests
- [x] Recovery Settings component/route tests
- [x] `npm run typecheck`
- [x] changed-file lint/diagnostics
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin SHOPIFY-005.

## Completion Report

### Status
Attempt 2 corrections implemented and submitted to `moda_architect` for review. This is not an architect acceptance decision.
### Files Changed
- `app/routes.ts`
- `app/routes/app/recovery-settings/route.tsx`
- `app/routes/app/recovery-settings/RecoverySettingsView.tsx`
- `app/components/settings/MerchantKnowledgeSection.tsx`
- `app/routes/app/merchant-knowledge/{source,reorder,refresh,delete}/route.ts`
- `app/services/merchant-knowledge/merchant-knowledge-entitlement.server.ts`
- `app/services/merchant-knowledge/merchant-knowledge.server.ts`
- `app/services/merchant-knowledge/merchant-knowledge-queue.server.ts`
- `tests/unit/merchant-knowledge-{entitlement,actions,queue,read-model,section,url-validation}.test.*`
- `tests/integration/merchant-knowledge-source-lifecycle.integration.test.ts`
### Work Completed
- Added current-subscription/current-plan entitlement resolution using the Shared C2 schema and `MERCHANT_OPT_IN` Feature state; plan entitlement grants configuration access independently from the merchant preference.
- Read the canonical `ShopFeaturePreference` and expose plan, activation and effective state. Recovery Settings reuses its existing `FeaturePreferences` checkbox as the only activation control and presents Store Profile, Merchant Knowledge, then existing recovery controls in the required order.
- Added WEB_PAGE source create/edit/refresh/delete/reorder actions and metadata read model. Operations use the authenticated `settingsAccess` shop, Shop/source row locks, exact ownership checks, current allowed source types, supported language tags, HTTPS syntax validation, revision generations, and collision-safe position rewrites.
- OFF-state create/edit/refresh leaves durable PENDING revisions and does not enqueue; ON-state revisions use the existing Shared C4 job contract. Queue construction/publication failures are contained after commit. Preference changes do not enumerate sources or enqueue work.
- The UI remains configurable while OFF, shows plan/source/dormancy and revision/active usage state, and does not expose extracted content or embeddings.
- Implementation commits: `d2815f8b22a9f906276c45fce64e4a8abea9cd58` and `a33dc681d8e26adefd9b0ce5b759016d5baed5ce`.
### Launcher Evidence
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-SHOPIFY-004`, branch `task/ARCH-023-SHOPIFY-004`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-SHOPIFY-004`, branch `task/ARCH-023-SHOPIFY-004`.
- Both worktrees were newly created for this task; no other task worktree was reused. Shared workspace/source checkouts were not switched or mutated for task implementation.
- Start-of-attempt synchronization: parent remote task branch fast-forward `not-needed`, parent `origin/main` `already-current`; implementation remote task branch fast-forward `not-needed`, implementation `origin/main` `already-current`.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` initialized at `2eb17ee910491e8f9df82736fc0a843844415947`.
### Validation Results
- Focused Merchant Knowledge plus existing feature-preference/Recovery Settings tests: 9 files, 31 tests passed.
- Disposable PostgreSQL lifecycle/concurrency proof: `tests/integration/merchant-knowledge-source-lifecycle.integration.test.ts`, 5/5 passed. It verified OFF/ON queue behavior, non-destructive opt-out, OFF-state refresh remaining PENDING/un-enqueued, ownership isolation, plan/source validation, concurrent source-cap enforcement and serialized generation increments. Testcontainers used one owned `pgvector/pgvector:pg17` instance, deployed migrations, and removed the container. Colima required per-command `DOCKER_HOST=unix:///Users/kwadwoadomafriyie/.colima/default/docker.sock` and `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock`; no global Docker configuration was changed.
- `npm run typecheck` — passed after the final implementation/test changes.
- Changed-file ESLint — passed. ESLint emitted its existing warning that the installed TypeScript 5.9.3 is newer than the parser's declared supported range; no lint findings were reported.
- `npm run build` — passed. Build emitted dependency annotation/externalization and large-chunk warnings, with no build errors.
- Changed-file diagnostics — no errors. `git diff --check HEAD~2 HEAD` — passed.
- Implementation task branch `task/ARCH-023-SHOPIFY-004` was pushed and verified at `a33dc681d8e26adefd9b0ce5b759016d5baed5ce`; implementation worktree is clean.
### Deviations
The integration proof needed explicit per-command Colima socket settings for Testcontainers. No product-scope or architecture deviations were made.
### Assumptions
Durable OFF-state PENDING revisions are activated by the existing Background periodic reconciliation after merchant opt-in; Shopify does not add an enqueue-on-enable path, as required by R10.
### Unresolved Issues
None within this task's scope.
### Architectural Concerns
None identified. Commerce retrieval enforcement remains owned by COMMERCE-004; ingestion remains Background-owned.

### Attempt 2
#### Files Changed
- `app/services/merchant-knowledge/merchant-knowledge.server.ts`
- `tests/integration/merchant-knowledge-source-lifecycle.integration.test.ts`
- `tests/unit/merchant-knowledge-url-validation.test.ts`

#### Corrections Implemented
- Delete and reorder now resolve current entitlement immediately after locking the Shop and deny before mutation without a valid entitlement. They do not require merchant opt-in or source-count eligibility; existing OFF-state operations under entitlement remain covered and passing.
- Edit and refresh compute the R3 eligible source window under the Shop lock: active Purpose/Data Format, pair in current C2 `allowedSourceTypes`, position then id order, first `maxKnowledgeSources`. An excess source is denied before metadata, generation, revision or enqueue changes; reorder can move a source into the window.
- URL validation checks raw and canonical URL lengths and returns only the validated canonical value. A Unicode path regression proves a raw input shorter than 2,048 characters is rejected when `URL.toString()` exceeds 2,048, before transaction entry.
- PostgreSQL regressions cover a two-source downgrade to `maxKnowledgeSources: 1` (second source denied on edit/refresh without revision/enqueue; reorder moves it into the window and refresh succeeds) and no-entitlement delete/reorder denial with source rows and positions unchanged.

#### Launcher and Worktree Evidence
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-SHOPIFY-004`, `task/ARCH-023-SHOPIFY-004`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-SHOPIFY-004`, `task/ARCH-023-SHOPIFY-004`.
- Shared workspace checkout switched/mutated for task work: no. Shared implementation checkout switched/mutated for task work: no. Another task worktree reused: no.
- Prepared launcher synchronized both task worktrees; parent sync was current and implementation began at `a33dc681d8e26adefd9b0ce5b759016d5baed5ce`. Read-only verification confirmed both task branches contain `origin/main`; no startup preparation or resynchronization was repeated.
- Dependency gate passed: SHOPIFY-001, SHARED-002 and ADMIN-004 complete. Recursive implementation submodules were ready; `database` was at `2eb17ee910491e8f9df82736fc0a843844415947`.
- Parent claim commit `b2336d9cb1ae8302dd0f8b2498d23dbe4f23cc41` and implementation commit `d17cfffc6c03dec77632d3e9cae5770ca2fc74d8` were pushed on their respective task branches.

#### Validation Results
- Focused Merchant Knowledge, activation and Recovery Settings suites: 9 files, 36 tests passed.
- Disposable PostgreSQL lifecycle/concurrency suite: 1 file, 7 tests passed. Per-command environment: `DOCKER_HOST=unix:///Users/kwadwoadomafriyie/.colima/default/docker.sock`, `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock`, `MODA_DISPOSABLE_INTEGRATION=1`; global Docker configuration was not changed.
- `npm run typecheck`: passed.
- Changed-file ESLint: passed; existing parser warning notes TypeScript 5.9.3 is outside its declared `<5.4.0` support range. Changed-file diagnostics: no errors.
- `npm run build`: passed with existing dependency annotation/externalization and large-chunk warnings; no build errors.
- `git diff --check`: passed.

#### Deviations and Unresolved Issues
No scope deviations or unresolved issues. No schema, migration, shared contract, Background, Commerce, or SHOPIFY-005 changes were made.

## Architect Review

### Review Status
Changes Requested

### Review Notes
Attempt 1 is substantially aligned with the Merchant Knowledge control-plane design, including reuse of the existing `ShopFeaturePreference`, OFF-state durability, authenticated shop derivation, revisioned WEB_PAGE lifecycle, queue-loss tolerance and Shop/source locking. Three bounded corrections remain before acceptance.

**A1-R1 — current-plan configuration access is not enforced by delete/reorder.** `deleteMerchantKnowledgeSource(...)` and `reorderMerchantKnowledgeSources(...)` lock the authenticated Shop and validate ownership/set equality, but neither calls `loadCurrentMerchantKnowledgeEntitlement(...)`. A merchant whose current plan no longer entitles `merchant_knowledge` can therefore still mutate stored Merchant Knowledge state through these resource actions whenever Recovery Settings remains reachable for other plan features. R1 and R15 require current-plan entitlement for configuration access; OFF-state permission is not permission to mutate without a current Merchant Knowledge plan mapping.

**A1-R2 — edit/refresh do not enforce the R3 `currentlyPlanEntitled` source-count boundary.** Both operations validate the source Purpose/Data Format pair, but neither verifies that the source is within the first `maxKnowledgeSources` currently allowed sources ordered by `(position ASC, id ASC)`. After a source-count downgrade, a `SOURCE_COUNT`-dormant source can therefore create `URL_CHANGE`/`REFRESH` revisions and, when merchant opt-in is ON, receive an immediate C4 enqueue even though R3 marks it not currently plan-entitled and R7 limits refresh to a currently plan-entitled source. Reorder/delete may still operate on dormant/excess sources under a valid current entitlement.

**A1-R3 — URL length is checked before canonicalisation, not on the value persisted.** `parsePublicHttpsUrl(...)` checks the raw input length and then returns `url.toString()`. Percent-encoding can expand an input below 2,048 characters beyond the `MerchantKnowledgeSourceRevision.requestedUrl VARCHAR(2048)` bound, causing a database failure instead of deterministic `INVALID_INPUT`. The canonical `url.toString()` value must also be `<= 2048` before opening the transaction/persisting it.

### Reviewed Files
- `moda-interact/app/services/merchant-knowledge/merchant-knowledge-entitlement.server.ts`
- `moda-interact/app/services/merchant-knowledge/merchant-knowledge.server.ts`
- `moda-interact/app/services/merchant-knowledge/merchant-knowledge-queue.server.ts`
- `moda-interact/app/routes/app/merchant-knowledge/{source,reorder,refresh,delete}/route.ts`
- `moda-interact/app/routes/app/recovery-settings/route.tsx`
- `moda-interact/app/routes/app/recovery-settings/RecoverySettingsView.tsx`
- `moda-interact/app/components/settings/MerchantKnowledgeSection.tsx`
- `moda-interact/app/services/feature-preferences/{access,feature-preferences}.server.ts`
- focused Merchant Knowledge unit/integration tests listed in the Completion Report
- accepted ARCH-023 database schema/migrations relevant to source positions/revisions

### Validation Reviewed
The Completion Report records 31/31 focused tests, 5/5 disposable PostgreSQL lifecycle/concurrency cases, typecheck, changed-file lint/diagnostics, build and diff checks as passing. The test suite does not currently exercise the three correction cases above. The review archive does not contain a runnable installed dependency environment, so these dependency-backed commands were inspected from durable evidence rather than independently rerun.

### Architecture Conformance
Conformant on merchant opt-in reuse, OFF-state non-destruction, tenant identity, source locking/generation, queue-loss safety, UI ordering and WEB_PAGE ownership boundaries. Not yet conformant on the current-plan configuration gate, R3/R7 source-count eligibility for edit/refresh, and deterministic canonical URL-length validation.

### Follow-up
Return the same task through `/moda-task ARCH-023-SHOPIFY-004` for Attempt 2. Preserve the current implementation and make only these bounded corrections:

1. **Gate delete/reorder on current Merchant Knowledge entitlement.** After acquiring the existing Shop lock, call the current-plan entitlement resolver. If it is not `kind: "entitled"`, fail with `DENIED` before deleting or rewriting positions. Do not require `merchantEnabled`; delete/reorder remain allowed while OFF. Do not require the target source itself to be within the current source-count allowance; deletion/reordering must remain available for dormant/excess sources while the shop has a valid current Merchant Knowledge entitlement.
2. **Enforce `currentlyPlanEntitled` for edit/refresh.** Under the existing Shop lock, compute the ordered currently allowed source set using the same semantics as the R3 read model: active Purpose/Data Format, pair present in current C2 `allowedSourceTypes`, ordered `(position ASC,id ASC)`, then first `maxKnowledgeSources`. The edited/refreshed source must be in that first-N set. Otherwise fail `DENIED` without changing metadata/generation, creating a revision or enqueueing C4. Preserve immutable Purpose/Data Format.
3. **Keep reorder as the way to move an excess source into/out of the first-N entitlement window.** Add a PostgreSQL regression with at least two currently allowed sources and a downgraded `maxKnowledgeSources: 1`: the second source must read as `SOURCE_COUNT`, edit/refresh must be denied without a new revision/enqueue; after reordering it into position 0 it becomes currently plan-entitled and refresh succeeds, while the displaced source becomes `SOURCE_COUNT`.
4. **Prove no-plan mutation denial.** Add integration coverage showing that once the current Merchant Knowledge mapping/qualifying plan entitlement is absent, delete and reorder are denied and source rows/positions remain unchanged. Existing OFF-state delete/reorder behavior under a valid entitled plan must continue to pass.
5. **Validate the canonical URL length.** Parse as today, compute `const canonical = url.toString()`, reject with `INVALID_INPUT` when `canonical.length > 2048`, and persist/compare only the validated canonical value. Add a unit regression using an input shorter than 2,048 characters whose Unicode/path canonicalisation expands beyond 2,048; assert rejection occurs before the database transaction.
6. Rerun the existing focused Merchant Knowledge unit/component/action suites and disposable PostgreSQL lifecycle/concurrency suite, plus `npm run typecheck`, changed-file lint/diagnostics, `npm run build` and `git diff --check`. Record exact counts/results and normal Attempt 2 launcher/worktree/synchronisation evidence.
7. Return the task to `review`, clear the claim, leave this Architect Review history intact, and STOP. Do not begin SHOPIFY-005.

No schema/migration, Shared-contract, Background, Commerce, feature-preference redesign, second activation control, or SHOPIFY-005 implementation is authorised by this correction.

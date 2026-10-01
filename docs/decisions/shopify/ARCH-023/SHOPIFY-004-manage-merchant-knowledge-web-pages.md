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
executor: copilot
claimed_at: 2026-09-30T22:53:18Z
attempt: 1
depends_on:
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHARED-002
  - ARCH-023-ADMIN-004
enables:
  - ARCH-023-SHOPIFY-005
created: 2026-09-29
updated: 2026-09-30
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
Implemented for Attempt 1 and submitted to `moda_architect` for review. This is not an architect acceptance decision.
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

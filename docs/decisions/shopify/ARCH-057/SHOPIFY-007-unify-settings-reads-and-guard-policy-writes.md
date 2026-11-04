---
id: ARCH-057-SHOPIFY-007
architecture_id: ARCH-057
title: Unify settings reads and guard merchant policy writes
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-057-SHOPIFY-001
enables:
- ARCH-057-SHOPIFY-008
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-007: Unify settings reads and guard merchant policy writes

## Architecture

Architecture ID: `ARCH-057`. Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Mandatory execution/logging/validation contract: `docs/architecture/ARCH-057/task-contract.md`. This task is materialised in its canonical parent and implementation worktrees on `task/ARCH-057-SHOPIFY-007`. Attempt 1 is published, architect-accepted and Complete. The Completion Report records the claim, implementation commit, worktree paths, synchronization and validation evidence. Current lifecycle state is recorded in the task frontmatter; the acceptance record below states the review decision.

## Objective

Compose merchant settings from one request-local read projection, perform no discount writes for unchanged policy, and require ACTIVE Shop state under the existing category-selection lock before committing a category change.

## Context

Review F11 identifies overlapping settings/subscription/feature reads and a settings guard that fetches a row mutation callers discard. F12 identifies discount deselect/reselect writes before the no-op check. F18 identifies a category lifecycle check performed before preparation but not under the later Shop lock. The architect now selects **ACTIVE at category-selection commit** as a requirement. This decision does not move or redefine the separate onboarding milestone.

SHOPIFY-001 supplies scalar Shop/Subscription/ShopSettings facts. This task owns the additional settings-specific plan/features/preference projection and freezes its interface for SHOPIFY-008. It does not put heavy relation includes into the global merchant context.

## Scope

Paths are relative to `moda-interact`.

| Existing path | Required edit |
|---|---|
| `app/services/feature-preferences/access.server.ts` | Add the explicit no-settings-read mutation guard; retain existing settingsAccess contract and policy |
| `app/services/feature-preferences/feature-preferences.server.ts` | Extract a pure feature projection consumed by page reads and the existing fresh transactional loader; preserve feature revision bytes |
| `app/routes/app/recovery-settings/route.tsx` | Pass framework context, construct one settings read context, reuse it for features/policy; keep knowledge invocation for SHOPIFY-008 to migrate |
| `app/services/recovery-policy/recovery-policy.server.ts` | Accept supplied settings for read composition; implement prewrite no-op and added/removed discount sets; preserve atomic revision fencing |
| `app/routes/app/settings-save/route.ts` | Use the mutation guard, retain bounded form handling and all current intents, complete operational diagnostics for every intent |
| `app/services/store-profile/store-category-selection.server.ts` | Enforce ACTIVE and existing Shop under FOR UPDATE; preserve preparation/current-template validation/generation CAS; retain actual render failure cause |
| `app/routes/app/store-profile/category/route.ts` | Consume request context, map the new lifecycle denial, log operational errors and retain existing safe response shape |
| `app/components/settings/StoreProfileSection.tsx` | Extend only the typed result union for SHOP_UNAVAILABLE; use the existing localized saveFailed presentation |
| `tests/unit/recovery-policy-save.test.ts`, `tests/unit/recovery-policy-snapshot.test.ts` | Change true no-op expectations to zero UPDATEs and cover supplied settings/delta writes |
| `tests/unit/settings-save-recovery-route.test.ts`, `tests/unit/merchant-settings-action.test.ts`, `tests/unit/ai-response-delay-loader.test.ts` | Verify guard/context reuse and unchanged form/error/revision behavior |
| `tests/unit/store-category-selection.test.ts` | Verify ACTIVE-under-lock and generation/provenance behavior |
| `tests/integration/shopify-recovery-discounts.postgres.integration.test.ts` | Preserve selected-field ownership tests; remove any fixture assumption that every save always makes exactly two updates |
| `tests/integration/merchant-feature-preferences.test.ts` | Preserve existing feature/revision integration cases; use pgvector/pgvector:pg17 instead of its obsolete postgres:15-alpine fixture |
| `tests/integration/store-category-selection.postgres.integration.test.ts` | Retain existing initial/active selection, provenance and concurrency cases |
| `package.json` | Register the exact focused scripts below |

New files:

- `app/services/feature-preferences/settings-read-context.server.ts`: the settings-specific server-only read projection below.
- `app/services/feature-preferences/merchant-settings-observability.server.ts`: thin Shared-based settings/category semantic diagnostics.
- `tests/unit/settings-read-context.test.ts`: scalar reuse, plan/preference read and pure-selector cases.
- `tests/unit/merchant-settings-observability.test.ts`: actual Shared output, code/cause/redaction/sink checks.
- `tests/integration/merchant-settings-writes.postgres.test.ts`: true no-op/selection deltas/concurrent policy revisions.
- `tests/integration/store-category-lifecycle.postgres.test.ts`: explicit lifecycle/selection lock race.
- `tests/helpers/merchant-settings-postgres.ts`: small PG17 migration/client/fixture helpers for the two new suites; no generic runner.

New files remain below 300 lines. Existing large suites need only focused edits; do not undertake unrelated test reorganization. `ai-response-delay.server.ts`, category activation service, onboarding callbacks/resume and locale catalogues are preservation/read-only touchpoints.

## Out of Scope

No onboarding milestone reorder, category-activation/Background hook, new subscription admission policy, knowledge processing implementation, global cache, schema/index/migration, discount synchronization change, provider call, per-source queue change, locale rewrite or generic repository framework. SHOPIFY-008 migrates the eight knowledge actions to the new guard. Do not change feature no-op/stale-revision semantics merely to make them match recovery policy.

## Requirements

### R1 — one presentation projection, separate mutation access

1. Add `settingsMutationAccess(request, context?)` with the exact contract below. It performs authenticated local context resolution and the same Shop lifecycle/RECOVERY_SETTINGS policy as current settingsAccess, including the old active/trialing subscription filtering. For an established tenant with valid prerequisites it does not call `readSettings` or query ShopSettings. Retain SHOPIFY-001's authenticated missing-prerequisite bootstrap/repair; this exceptional recovery is outside the guard-only zero-read budget. All production callers owned here pass actual framework context.
2. Keep `settingsAccess(request, context?)` returning `{shop, settings, session, merchant}`. Reuse one private authorization path and obtain settings only for this read-oriented method. Do not duplicate authentication/subscription I/O between the two methods.
3. Add `loadSettingsReadContext(merchant, client=db)`. Obtain scalar subscription/settings through `merchant.readSubscription()` and `merchant.readSettings()`. For a non-null planId, read its BillingPlan with current Feature mappings/Feature scalar fields in one explicit Prisma call, ordered exactly as the current feature loader. Read ShopFeaturePreference once with its existing featureId ordering. Use the already authenticated Shop's status/default language. A missing plan remains null; no replacement plan or provider sync is allowed. A missing settings row is represented as null and retains the policy reader's existing SETTINGS_NOT_FOUND failure, not a fabricated authorization denial.
4. Extract `projectFeaturePreferences` as a pure function over the settings read facts. Preserve filtering, editable/effective feature semantics and exact `revisionOf` input shape/order. The page uses this selector rather than `loadFeaturePreferences` rereading Subscription/preferences. Keep `loadFeaturePreferences(shopId, transaction)` for mutations: it still loads current transaction facts and calls the same pure selector. `saveFeaturePreferences` retains Shop lock, fresh read, no-change early return, revision check, per-changed-feature upserts and fresh returned revision.
5. Extend `loadRecoveryPolicySnapshot` with an optional supplied-settings argument below. If present, including `{settings:null}`, do not query ShopSettings. Continue reading the current override and discount catalogue, and preserve every returned field, sorting, selected dormant discounts and effective/merchant distinction. The page supplies `readContext.settings` and uses that same row for AI delay. Do not serialize the read context.
6. Expose the read context for SHOPIFY-008, but do not alter knowledge services/actions here. After this task, the settings-specific path reads subscription/settings only through memoized scalar getters and performs one plan/features plus one preference-list read. Its remaining knowledge duplicate reads are explicitly assigned to SHOPIFY-008, not hidden in a global heavy projection.

### R2 — no-op and delta discount persistence

7. Keep parsing, active Shop FOR UPDATE, current settings lookup, expected-revision comparison, selected-ID uniqueness/50 limit and same-Shop ownership validation before writes. Compute the old/new selected-ID sets and compare the full desired policy plus notification preference before any UPDATE.
8. If nothing changes, return the current settings revision with **zero discount UPDATE calls, zero settings UPDATE calls and unchanged row timestamps**. If only settings/notification fields change, leave all discount rows untouched.
9. For changed selection, issue only a nonempty removed-ID update to false and a nonempty added-ID update to true, each constrained by shopId/IDs and expected current availability. Verify affected counts against those sets; a concurrent disappearance/state mismatch raises the existing DISCOUNT_SELECTION_CHANGED error and rolls back. Retained selected IDs are never toggled. Do not filter ownership by provider ACTIVE/selectability: existing dormant/expired selections remain legitimate merchant-owned preferences.
10. Persist changed settings once in the same transaction, including changed selected-set semantics even if other fields are identical. Advance updatedAt monotonically using the existing AI-delay pattern `new Date(Math.max(Date.now(), current.updatedAt.getTime() + 1))`, so two changes cannot retain the same millisecond revision. Preserve fixedShopifyDiscountId compatibility, sorted first selection, admin override separation and provider sync ownership of provider fields. Do not remove fresh mutation checks because a page read passed.

### R3 — category ACTIVE under lock

11. Change the existing Shop lock to `WHERE id = shopId AND status = 'ACTIVE' FOR UPDATE`, inspect returned rows and fail before profile/prompt/configuration writes if no row qualifies. Add `SHOP_UNAVAILABLE` to StoreCategorySelectionError and map it to HTTP403 with `{ok:false,error:'SHOP_UNAVAILABLE'}`. Missing/inactive Shop have the same safe response. Existing CONFLICT409 and CATEGORY_UNAVAILABLE400 remain unchanged.
12. Keep prompt rendering/preparation outside the transaction, then current category/template/mapping checks under the existing lock, expected pending-generation CAS, active-category immediate publication, configuration preservation and selected draft provenance. A lifecycle update that wins the Shop lock first prevents category writes; if category selection wins first, it completes atomically before the lifecycle writer proceeds. Prove both orders with separate PostgreSQL connections and explicit barriers.
13. Keep existing onboarding/callback/resume/category activation semantics and tests unchanged. An authenticated callback milestone is not moved after billing/category success. This task adds a commit-time guard to category selection only.

### R4 — logging and failure ownership

Use the mandatory Shared error contract, actual original safe error/code/cause and existing `resolveDeploymentEnvironmentName`. The semantic adapter may expose settings/category event functions; it must not implement a generic serializer/redactor. Never log form values, selected discount titles/code text, rendered prompts/source contexts, taxonomy payloads, customer information or credentials.

| Failure/injection | Diagnostic owner | Required result |
|---|---|---|
| SHOPIFY-001 auth/scalar context failure | SHOPIFY-001 source owner | Propagate; no duplicate source error at rethrow-only settings caller |
| Settings-specific plan/features/preferences/override/catalogue read fails | The owning settings read function | Original safe DB message/code/cause once; no fabricated empty features/catalogue |
| Policy/feature/AI-delay transaction fails unexpectedly | settings-save action, with actual intent/stage | Original error once for every intent, including features; preserve rollback and safe HTTP behavior |
| Expected invalid input, revision conflict, inactive Shop, invalid feature/discount ownership | Existing typed business outcome | Preserve current 400/403/409/422 mapping; do not invent provider errors |
| Category rendering throws | Preparation boundary | Log original safe cause once before wrapping CATEGORY_UNAVAILABLE with `cause`; do not log prompt/context |
| Category transaction/preflight DB fails | Category action | Original DB error/code/cause; no partial publication/profile/config change |
| ACTIVE-under-lock finds no Shop | Typed SHOP_UNAVAILABLE | 403, no write; not an invented database outage |
| Throwing Shared sink | Shared isolation | Read failure, revision winner, rollback and public response unchanged |

## Work Items

- [x] Add the minimal mutation guard and settings read context/selector contracts.
- [x] Wire the settings page/save/category route with actual framework context and existing DTOs.
- [x] Move complete no-op checks before writes and implement nonempty selection deltas plus monotonic revision.
- [x] Enforce ACTIVE under the existing category lock and preserve onboarding/activation semantics.
- [x] Complete original-error diagnostics for settings/category operational branches.
- [x] Implement/register/run focused unit/UI and real PostgreSQL cases; publish accurate count/row/log evidence in the report.

## Interfaces / Contracts

Consumes `ARCH-057-SHOPIFY-001`'s exact `MerchantRequestContext` and `getMerchantRequestContext` contracts. GET/HEAD scalar reads may be memoized; non-GET and all write transactions use fresh admission. SHOPIFY-008 consumes these new contracts without copying their queries:

```ts
settingsMutationAccess(request: Request, context?: RouterContextProvider): Promise<{
  shop: Shop;
  session: MerchantRequestContext["authentication"]["session"];
  merchant: MerchantRequestContext;
}>;

type SettingsPlan = Prisma.BillingPlanGetPayload<{
  include: { features: { include: { feature: true } } };
}>;
type SettingsReadContext = Readonly<{
  shop: Pick<Shop, "id" | "status" | "defaultLanguageTag">;
  settings: ShopSettings | null;
  subscription: Subscription | null;
  plan: SettingsPlan | null;
  preferences: readonly ShopFeaturePreference[];
}>;

loadSettingsReadContext(
  merchant: MerchantRequestContext,
  client?: PrismaClient,
): Promise<SettingsReadContext>;

projectFeaturePreferences(
  facts: Pick<SettingsReadContext, "shop" | "subscription" | "plan" | "preferences">,
): ExistingFeaturePreferencesSnapshot;

loadRecoveryPolicySnapshot(
  shopId: string, now?: Date, client?: PrismaClient,
  supplied?: { settings: ShopSettings | null },
): Promise<ExistingRecoveryPolicySnapshot>;
```

Use imported concrete Prisma/SDK/router types and existing output aliases; the `Existing...` names above refer to the unchanged inferred DTOs, not additional public wire schemas. The plan read includes the Feature metadata/configuration SHOPIFY-008 needs, including inactive mappings; it must not discard them before the pure selector applies its policy. No context object enters browser data.

Add exact package scripts:

```json
{
  "test:merchant-settings:unit": "vitest run tests/unit/settings-read-context.test.ts tests/unit/merchant-settings-observability.test.ts tests/unit/recovery-policy-save.test.ts tests/unit/recovery-policy-snapshot.test.ts tests/unit/settings-save-recovery-route.test.ts tests/unit/merchant-settings-action.test.ts tests/unit/ai-response-delay-loader.test.ts tests/unit/ai-response-delay.test.ts tests/unit/store-category-selection.test.ts",
  "test:merchant-settings:postgres": "MODA_DISPOSABLE_INTEGRATION=1 MODA_SETTINGS_POSTGRES=1 vitest run tests/integration/merchant-settings-writes.postgres.test.ts tests/integration/store-category-lifecycle.postgres.test.ts tests/integration/shopify-recovery-discounts.postgres.integration.test.ts tests/integration/store-category-selection.postgres.integration.test.ts tests/integration/merchant-feature-preferences.test.ts"
}
```

## Dependencies

- ARCH-057-SHOPIFY-001

## Enables

- ARCH-057-SHOPIFY-008
- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [x] For an established tenant with valid prerequisites the mutation guard performs no settings read; authenticated missing-prerequisite repair and the old surface/lifecycle policy remain intact.
- [x] The page reuses scalar Subscription/ShopSettings, one plan/features read and one preference list; pure feature revision/output remains identical for the same facts.
- [x] Identical policy saves issue no UPDATEs and leave timestamps unchanged; settings-only changes do not touch discounts; only added/removed selections change.
- [x] Real concurrent policy writers using one revision have one changed-state winner, and provider synchronization does not overwrite merchant availability selections.
- [x] Category writes require ACTIVE under the Shop lock, with no partial state if lifecycle changes first; the selected first-writer order is proven on PG17.
- [x] Existing initial/active category publication, pinned provenance, config preservation, stale-generation handling and onboarding ordering remain intact.
- [x] Every operational failure in the matrix emits safe original error/code/cause through Shared; business-denial behavior and localization remain unchanged.

## Validation

- [x] `npm run test:merchant-settings:unit` — named cases for cached getter reuse, null settings, inactive/absent plan, pure revision parity, transaction freshness, true no-op, added/removed/retained IDs, changed same-millisecond revision, lifecycle denial and log ownership.
- [x] `npm run test:merchant-settings:postgres` — all suites use task-owned `pgvector/pgvector:pg17` with canonical forward migrations. New cases use distinct clients and explicit lock barriers, not sleeps/mocks, for two stale policy writers and both category/lifecycle lock orders. Assert physical rows/timestamps and no partial prompt/profile/configuration writes. Existing source-sync fixture must still prove actual selection ownership after the changed update shape. Skips block acceptance.
- [x] `npm test -- tests/unit/recovery-settings-discounts.test.tsx tests/unit/recovery-settings-submit-guard.test.tsx tests/unit/ai-response-delay-settings.test.tsx tests/unit/recovery-settings-i18n.test.ts tests/unit/onboarding-store-category.test.jsx tests/unit/store-category-activation.test.ts` — preserve UI, locale and deliberate activation/milestone behavior.
- [x] `npm run typecheck` and `npm run build`.
- [x] `npx --no-install eslint app/services/feature-preferences app/services/recovery-policy/recovery-policy.server.ts app/services/store-profile/store-category-selection.server.ts app/routes/app/recovery-settings/route.tsx app/routes/app/settings-save/route.ts app/routes/app/store-profile/category/route.ts app/components/settings/StoreProfileSection.tsx tests/unit/settings-read-context.test.ts tests/unit/merchant-settings-observability.test.ts tests/unit/recovery-policy-save.test.ts tests/unit/recovery-policy-snapshot.test.ts tests/unit/settings-save-recovery-route.test.ts tests/unit/merchant-settings-action.test.ts tests/unit/ai-response-delay-loader.test.ts tests/unit/store-category-selection.test.ts tests/integration/merchant-settings-writes.postgres.test.ts tests/integration/store-category-lifecycle.postgres.test.ts tests/integration/shopify-recovery-discounts.postgres.integration.test.ts tests/integration/store-category-selection.postgres.integration.test.ts tests/integration/merchant-feature-preferences.test.ts tests/helpers/merchant-settings-postgres.ts`.
- [x] `git diff --check`; same-fixture before/after call/SQL/affected-row evidence and actual Shared JSON/cause/redaction/sink evidence; exact installed versions, canonical pins and task-owned cleanup.

## Stop Condition

After required work, acceptance and validation, set review and return the Completion Report to `moda_architect`. Stop for a changed context contract, required schema modification, non-current source or a proposed onboarding/activation policy change. Do not implement knowledge processing, modify downstream state, mark Complete or begin enabled tasks.

## Implementation Notes

A request read context is not a transaction snapshot. Preserve the existing fresh `loadFeaturePreferences` call inside mutations. The policy no-op must be checked after current revision/ownership validation, before any write. Use the new selected-set deltas rather than broad false/true updates. Category lifecycle enforcement fits its existing Shop lock and needs no new synchronization mechanism.

## Completion Report

### Status

Attempt 1 accepted and Complete on 2026-11-04. Implementation committed and pushed as `e1533e4658e7e69eeb33e7efd6516211f0bcbe2e` on `task/ARCH-057-SHOPIFY-007`. All required gates passed; the Architect Acceptance record below states the decision.

### Files Changed

25 implementation files, including the seven declared new files; all new files are below 300 lines (29–81 lines). Source changes stay within the settings/access, policy, category selection and typed result paths in Scope. Registered both exact scripts. Updated the existing request-context router fixture for the new feature projection and verified its settings/recovery GET regression cases. No Database, Shared, locale, knowledge implementation, onboarding callback or activation source changed.

### Work Completed

- R1: Both settings access methods use one private authorization path. Mutation access does not read settings for a valid established tenant; ACTIVE/TRIALING filtering and request-context bootstrap remain intact. Settings-specific read facts use memoized scalar getters, one ordered plan/features read and one ordered preference list. The pure selector retains revision input order and output semantics. Fresh transactional feature reads, early denial, no-change and stale-revision behavior remain intact. The page passes framework context, supplies settings to policy loading (including explicit null), and reuses the same row for AI delay. No server context is serialized.
- R2: Revision and same-Shop ownership checks precede the no-op decision. Identical saves issue no UPDATE; settings-only changes leave discounts untouched. Only nonempty removed/added sets are updated with their previous availability predicates and checked counts. Retained and dormant selections are preserved. Settings update once with a strictly increasing millisecond revision. Existing provider synchronization ownership remains verified.
- R3: Category selection checks ACTIVE under its existing Shop FOR UPDATE lock before publication writes. Missing/inactive rows produce SHOP_UNAVAILABLE and route HTTP403; existing 409/400 mappings remain unchanged. Prompt preparation, current template/mapping checks, generation CAS, initial DRAFT, active immediate publication and configuration/provenance behavior are preserved.
- R4: The new thin settings adapter reuses the existing safe boundary diagnostic helper and real Shared logger with resolveDeploymentEnvironmentName. Read composition, every save intent and category failures preserve safe original message, database code and cause. Scalar-context failures remain with their original owner. Rendering errors are diagnosed before typed wrapping and retain their actual cause. Business denials do not fabricate operational errors.

### Physical Worktree and Provenance Evidence

Launcher-prepared topology; no repeated preparation or claim:

```text
canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-057-SHOPIFY-007
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-057-SHOPIFY-007
both branches: task/ARCH-057-SHOPIFY-007
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
parent remote task fast-forward: not-needed
parent origin/main incorporation: already-current
implementation remote task fast-forward: not-needed
implementation origin/main incorporation: already-current
parent prepared start: 2be472de3a91d2ba8f35aa21f13f1d886b92594f
implementation start: 042ab0f7c762767ae9597d21a3a7ea318a8e2514
claim: 7496bb3790667aab31714a1d07069af0a5dde0e9
claim pushed: yes; Attempt 1, codex, 2026-11-04T20:07:53Z
implementation end: e1533e4658e7e69eeb33e7efd6516211f0bcbe2e
recursive submodule sync/update/init/verification: passed by launcher
Database recorded/working pin, unchanged: 8e74634ff92be9900f693c0c449ffce888e7d617
```

Installed locked versions: Node 24.19.0, npm 11.17.0, Shared 3.1.0, Prisma/client 6.19.3, React Router 7.18.2, Shopify React Router SDK 1.2.1, Zod 4.5.4 and Vitest 4.1.11. Used workspace Node bootstrap, npm ci and pinned-schema Prisma generation; no dependency/version or schema upgrade.

### Validation Results

| Gate | Final result |
|---|---|
| `npm run test:merchant-settings:unit` | 9 files, 106 passed, zero failed/skipped |
| `npm run test:merchant-settings:postgres -- --maxWorkers=1 --no-file-parallelism --testTimeout=30000 --hookTimeout=60000` | 5 files, 23 passed, zero failed/skipped |
| Exact six-suite UI/onboarding command in Validation | 6 files, 29 passed, zero failed/skipped |
| `npm run test:merchant-request:router` | 9 passed, zero failed/skipped; actual settings/recovery route chains retain one authentication and Shop resolution per GET |
| `npm run typecheck` | Passed |
| Exact focused eslint command in Validation | Passed, no diagnostics |
| `npm run build` | Passed; existing large-chunk advisory only |
| `git diff --check` and staged equivalent | Passed |
| Temporary same-fixture before/after evidence harness | 2 passed; temporary baseline source and harness removed before final validation/commit |

PostgreSQL uses task-owned pgvector/pgvector:pg17 and canonical forward migrations, never db push. Distinct connections plus explicit barriers and pg_stat_activity lock-wait observation establish the one stale-policy-writer winner and both category/lifecycle lock orders without sleeps. Tests assert physical selections, timestamps, prompt/profile/configuration state, and rollback on both count mismatch and a genuine P2010 database error after profile/lineage writes.

Initial environment attempts could not discover Docker and then used an invalid host-side socket mount. The successful runs set DOCKER_HOST from `docker context inspect` and TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock, only in the test process. An initial parallel run exposed a fixture slug constraint and contention-related transaction/test deadlines; fixed the slug and ran files sequentially with larger test deadlines, leaving production transaction limits unchanged. These initial failures/skips are superseded by the final fully enabled 23/23 run, not counted as passes. All task-owned PostgreSQL and Ryuk containers were removed; the two pre-existing PostgreSQL containers and Portainer were left untouched.

### Same-Fixture Call, SQL and Affected-Row Evidence

Comparison used the task start source above for the old policy implementation, the same migrated disposable database/Shop/discount fixture, and exact restoration of initial settings/discount timestamps before each branch. Counts include transaction controls separately and zero provider calls throughout.

| Branch | Before | After |
|---|---|---|
| Identical save | 2 discount updateMany calls; 2 discount UPDATE SQL; 2 affected discount rows across those statements; 0 settings UPDATE; 8 total SQL including BEGIN/COMMIT; retained timestamp changed | 0 discount/settings UPDATE calls or SQL; 0 affected rows; 6 total SQL including BEGIN/COMMIT; all timestamps unchanged |
| Settings-only save | 2 discount updateMany plus 1 settings update; affected discount rows 2, settings rows 1; 9 SQL including BEGIN/COMMIT | 0 discount updates, 1 settings update; affected discount rows 0, settings rows 1; 7 SQL including BEGIN/COMMIT; retained discount timestamp unchanged |
| Settings read composition, same active plan facts | Subscription.findUnique 2, ShopSettings.findUnique 2, preference list 1, override 1, catalogue 1; 10 SELECT SQL | Subscription.findUnique 1, ShopSettings.findUnique 1, BillingPlan.findUnique 1, preference list 1, override 1, catalogue 1; 7 SELECT SQL; feature output/revision identical |
| Selection delta | Broad deselect/reselect shape | One removed ID becomes false; one added ID becomes true; retained expired selection and timestamp unchanged; exactly 2 bounded discount UPDATEs and one settings revision update |

The read comparison includes request scalar acquisition and settings composition, excludes unchanged knowledge reads assigned to SHOPIFY-008, and uses no provider refresh. These are fixture-level call/row observations, not capacity or latency claims. Temporary local evidence: `/tmp/shopify007-sql-evidence.json`, `/tmp/shopify007-read-evidence.json`, `/tmp/shopify007-before-after.log`. The durable results are recorded above.

### Actual Shared Diagnostic Evidence

`merchant-settings-observability.test.ts` captures real Shared sink records, not mocked logger calls. The emitted JSON retains the multiline `constraint failure marker`, actual P2021 and `original-cause`, with database origin and redactionApplied=true; credential, email and connection-URL sentinels are absent from raw captured JSON. Read-group injections cover plan, preferences, override and catalogue; scalar failures generate no duplicate settings diagnostic. All three save intents retain original rejection and diagnostics. Category rendering retains original cause before CATEGORY_UNAVAILABLE wrapping, never emitting the template sentinel. Category database failure retains the original code; SHOP_UNAVAILABLE/CONFLICT/CATEGORY_UNAVAILABLE keep 403/409/400 and emit no invented failure. The same failures with a genuinely throwing Shared sink preserve their original rejection/public outcome; real PostgreSQL tests separately verify rollback and revision winners.

### Deviations

No architecture or ownership deviation. The existing router regression fixture required a focused adaptation to the new settings selector. PostgreSQL validation adds runner-only serialization/timeouts for the local host; exact registered package scripts remain as specified. New helper/suites remain below the 300-line limit. Temporary baseline comparison files were not published as production code.

### Assumptions

Launcher dependency gate proves SHOPIFY-001 Complete. No new context contract, schema, persisted revision format, provider or queue contract is introduced. Remaining knowledge duplication belongs to SHOPIFY-008.

### Unresolved Issues

None identified within this task's bounded scope. Architect acceptance is recorded below.

### Architectural Concerns

No new concerns identified. Downstream task states and parent implementation gitlinks were not changed. Neither task branch was merged to main.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable task definition only; no implementation accepted.

### Reviewed Files

Definition and latest unchanged settings/category touchpoints.

### Validation Reviewed

Definition inspection only.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

Return for review; do not begin SHOPIFY-008 or another enabled task.

## Architect Acceptance — Attempt 1 (2026-11-04)

**Accepted and Complete.** Reviewed implementation `e1533e4658e7e69eeb33e7efd6516211f0bcbe2e` and parent submission with documentation correction `2562e5efa`. No blocking findings remain. The current submission has no implementation change since the passing review; the stale materialization statement is fixed. Historical Pending/awaiting-review entries above are superseded by this decision.

The settings-specific projection preserves scalar getter reuse, ordered feature/preference revision inputs and fresh mutation reads. The minimal mutation guard retains independent access policy without unnecessary settings reads. Recovery policy validates revision and tenant ownership before the no-op, performs only nonempty added/removed discount updates, checks affected counts and advances settings revisions monotonically. Category selection requires ACTIVE under its existing Shop lock, preserving both lifecycle lock orders, generation CAS, prompt/configuration provenance and onboarding/activation behavior. Original-error diagnostics and expected business-denial mappings remain intact. No schema, dependency, locale, knowledge-processing or provider-policy change was introduced.

Independent validation in the canonical implementation worktree: **106 focused unit tests plus 29 UI/onboarding/activation tests passed**, zero failures/skips. Logs: `/tmp/arch057-shopify007-review-unit.log` and `/tmp/arch057-shopify007-review-ui.log`. Reviewed recorded **23/23 passing migrated PostgreSQL tests** across five suites, including separate-connection barriers, physical timestamps/selection ownership, stale-revision winner, both category/lifecycle lock orders and rollback after actual database errors. Reviewed passing typecheck/build/scoped lint, router regression and same-fixture SQL/call evidence. PostgreSQL/build/typecheck/lint were not independently rerun in this review. No tests were repeated for the documentation-only correction; prior independent checks apply to identical implementation bytes.

Canonical parent and implementation worktrees were verified clean on `task/ARCH-057-SHOPIFY-007`; implementation HEAD matches its remote task ref. The Completion Report records launcher claims, worktree synchronization, source/Database pins, installed versions and owned fixture cleanup. Automatic completion applies; Attempt remains 1, executor/claim remain null. The developer explicitly authorized this completion-report update, commit and push. No main merge, implementation edit or parent gitlink update is included.

Dependency reconciliation: SHOPIFY-001 is Complete, so SHOPIFY-008 now has both prerequisites satisfied and becomes ready, unclaimed, at Attempt 0. SHOPIFY-011 remains pending on remaining prerequisites. No downstream task is executed by acceptance; ARCH-057 remains in progress.

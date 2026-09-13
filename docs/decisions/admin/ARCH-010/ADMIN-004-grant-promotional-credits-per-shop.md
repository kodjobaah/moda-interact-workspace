---
id: ARCH-010-ADMIN-004
architecture_id: ARCH-010
title: Create and activate GLOBAL, PLAN and SHOP promotion campaigns
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 84
executor: copilot
claimed_at: '2026-09-13T13:31:36Z'
attempt: 3
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-ADMIN-010
enables:
- ARCH-010-ADMIN-005
- ARCH-010-SHOPIFY-021
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-ADMIN-004: Create and activate GLOBAL, PLAN and SHOP promotion campaigns

## Objective

Replace the old direct one-shop credit-grant concept with a SUPER_ADMIN-only campaign-authoring workflow. Admin creates an optional merchant offer with exactly one targeting scope (`GLOBAL`, `PLAN`, `SHOP`), a fixed recovery-credit quantity and a bounded running window. Creating/activating a campaign does **not** grant credits to merchants.

Merchants never access `moda-interact-admin`.

## Inspect before editing

```text
src/app/(protected)/**
src/components/admin/**
src/app/actions/**
src/lib/admin/**
src/lib/auth/platform-admin.ts
database/prisma/schema.prisma
```

Use the integrated Admin navigation/component conventions rather than assuming the prototype files still exist under the same names.

## Required behaviour

Provide SUPER_ADMIN campaign create/edit-before-activation support for:

```text
name
merchantDescription?       # merchant-facing campaign copy
scope = GLOBAL | PLAN | SHOP
quantity > 0
startsAt
expiresAt
```

Target controls:

```text
GLOBAL -> no target field
PLAN   -> exact BillingPlan.id selected from durable plan mapping
SHOP   -> exact Shop.id selected from tenant directory/search
```

Server validation must reject mixed/missing target shapes even if the client is bypassed.

## Activation

Activation must:

1. re-read campaign state in the transaction/action;
2. require DRAFT;
3. require valid target/quantity/window;
4. set `status=ACTIVE` and the activation/start state according to the DATABASE-010 contract;
5. append the required `PromotionCampaignEvent` audit evidence;
6. never create `PromotionalCreditGrant`, `MerchantPromotionSelection`, Shopify App Event, BillingAllowanceAdjustment or entitlement counter mutation.

After first activation, scope/target/quantity are immutable. The Admin UI must not imply that those can be changed later; a materially different offer is a new campaign.

## Security

- SUPER_ADMIN only;
- use existing platform-admin session/authorization conventions;
- no merchant Shopify session path;
- no raw Prisma error/stack leakage;
- exact Shop/BillingPlan IDs are resolved server-side.

## Required tests

At minimum prove:

1. non-SUPER_ADMIN cannot create/activate;
2. GLOBAL validates with no target;
3. PLAN requires exact BillingPlan;
4. SHOP requires exact Shop;
5. mixed target shape is rejected;
6. quantity/window validation is server-side;
7. activation writes audit event;
8. activation creates zero merchant grants/selections/counter changes;
9. post-activation target/quantity edits are rejected;
10. no Shopify/App Event call exists.

Run focused security/action/UI tests plus repository typecheck/lint/build/full tests as normally required and `git diff --check`.

## Non-goals

Do not implement merchant selection, consumption, campaign reopen/close/history, usage reporting, email/WhatsApp marketing delivery, campaign codes or automatic enrolment.

## Stop conditions

Stop if DATABASE-010 has not landed or if current Admin authorization/tenant-plan lookup cannot resolve exact durable IDs without inventing a second identity system.

## Completion Report

### Status
Review.

### Files Changed
- `src/app/(protected)/promotions/page.tsx`
- `src/components/admin/sidebar.tsx`
- `tests/security/admin-promotions.test.mjs`

### Work Completed
- Preserved the accepted Attempt 2 CAS, persisted-term activation validation, no-grant/no-selection/no-counter/no-Shopify boundaries, and existing campaign authoring behaviour.
- Added a SUPER_ADMIN page boundary that retains the platform principal, redirects non-SUPER_ADMIN roles before loading campaign or target data, and preserves unauthenticated handling in `requirePlatformAdminPage()`.
- Restricted the Promotions sidebar entry to SUPER_ADMIN while leaving all other navigation visibility unchanged.
- Added deterministic security coverage for page role gating, redirect ordering, sidebar discoverability, and all existing ADMIN-004 mutation boundaries.

### Validation Results
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `node --experimental-strip-types --test tests/unit/promotion-validation.test.ts`: passed, 4 tests.
- `node --test tests/security/admin-promotions.test.mjs`: passed, 9 tests.
- `node --test tests/unit/promotion-validation.test.ts`: passed, 4 tests.
- `npm test`: passed, 157 tests; existing observability tests that require a prior build were skipped as designed.
- `npm run lint`: passed with two pre-existing warnings in `src/components/admin/queue-monitor.tsx`.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed; existing BullMQ optional-dependency/critical-dependency warnings remain.
- `git diff --check`: passed.

### Git / VCS
Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-004`
  parent branch: `task/ARCH-010-ADMIN-004`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-004`
  implementation branch: `task/ARCH-010-ADMIN-004`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

database submodule initialized: yes
database gitlink expected: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`
database submodule HEAD: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`
database gitlink staged/changed: no

Parent claim commit: `934a768`, pushed to `origin/task/ARCH-010-ADMIN-004` in `moda-interact-workspace`.
Implementation commit: `b0fc432`, pushed to `origin/task/ARCH-010-ADMIN-004` in `moda-interact-admin`.
Parent report commit: pending publication.
The implementation worktree was clean after publication; main branches were not modified.

### Architect Review

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested

Attempt 1 is **not accepted**. The overall ADMIN-004 implementation is within scope and the campaign authoring model is correct, but the mutation path does not yet enforce the post-activation immutability invariant under concurrent requests.

The accepted parts of Attempt 1 should be preserved:

- the `/promotions` Admin route and existing Admin navigation integration;
- SUPER_ADMIN mutation authorization;
- GLOBAL / PLAN / SHOP target-shape validation;
- exact durable `BillingPlan.id` and `Shop.id` lookup;
- positive bounded quantity and ordered start/expiry validation;
- transactional `CREATED` and `ACTIVATED` lifecycle events;
- zero `PromotionalCreditGrant`, `MerchantPromotionSelection`, entitlement-counter, Shopify App Event or compatibility-model mutation;
- the existing UI rule that non-DRAFT campaigns are not editable;
- the existing full-repository validation baseline.

This is an **Attempt 2 correction on the same task**. Do not create a replacement task and do not redesign the promotion architecture.

##### Attempt 2 production scope — exact files

Production/test changes are limited to:

- `moda-interact-admin/src/app/actions/promotions.ts`
- `moda-interact-admin/src/components/admin/promotion-campaign-form.tsx`
- `moda-interact-admin/src/lib/admin/promotion-validation.ts` only if a reusable persisted-campaign validation helper is required
- `moda-interact-admin/tests/security/admin-promotions.test.mjs`
- `moda-interact-admin/tests/unit/promotion-validation.test.ts` only if the validation helper above is added
- this ADMIN-004 task file for execution metadata and Completion Report evidence only

Do **not** modify Prisma schema/migrations, Shared contracts, merchant-facing Shopify code, Background code, promotion grant/selection models, another task file, or architecture documents.

##### Correction 1 — make DRAFT edit and activation a compare-and-set transition

The current implementation does:

```text
findUnique(id)
require status == DRAFT
update(where: { id })
```

for both activation and draft editing.

That is not race-safe. Two transactions may both read the same DRAFT row. A draft edit may then update the row after another transaction has activated it, changing scope/target/quantity after first activation. Two activation requests may also both append `ACTIVATED` events.

Use the existing `PromotionCampaign.version` field and persisted `DRAFT` state as the compare-and-set authority. No schema change is required.

For **activation**, after re-reading the campaign and validating the persisted campaign values, perform a conditional update equivalent to:

```ts
const result = await transaction.promotionCampaign.updateMany({
  where: {
    id: existing.id,
    status: PromotionCampaignStatus.DRAFT,
    version: existing.version,
  },
  data: {
    status: PromotionCampaignStatus.ACTIVE,
    version: { increment: 1 },
  },
});

if (result.count !== 1) {
  throw new Error("Promotion campaign changed; reload and retry.");
}
```

Create the `PromotionCampaignEventType.ACTIVATED` event **only after** that conditional update wins inside the same transaction.

For **draft editing**, use the same conditional authority:

```text
id = existing.id
status = DRAFT
version = existing.version
```

and update the requested draft fields plus `version += 1` only when exactly one row matches. If the conditional update loses, throw the same bounded stale-state/reload error. Do not retry with stale submitted data and do not fall back to an unconditional `update({ where: { id } })`.

The resulting invariant must be:

```text
once any transaction wins DRAFT -> ACTIVE,
no concurrent or later ADMIN-004 draft edit can mutate campaign terms.
```

Do not use a force update, last-write-wins behaviour, or an in-memory mutex.

##### Correction 2 — activation must use only the persisted re-read campaign as commercial authority

The current activation form submits hidden copies of:

```text
name
scope
quantity
targetPlanId
targetShopId
startsAt
expiresAt
```

and `parsePromotionCampaignForm()` parses those client values before the transaction, even though activation subsequently re-reads the database row.

For activation, the client must submit only command identity required to request the transition:

```text
intent=activate
id=<campaign id>
```

Do not require or trust hidden commercial values for activation.

Inside the transaction:

1. re-read the campaign by `id`;
2. require `status === DRAFT`;
3. validate the **persisted** target shape and exact target existence;
4. validate the persisted quantity is a positive bounded integer using the same ADMIN-004 quantity rule;
5. validate `expiresAt > startsAt` using the persisted values;
6. perform the version/status CAS from Correction 1;
7. append `ACTIVATED` evidence only after the winning CAS.

It is acceptable to factor the quantity/window/target checks into a reusable helper in `src/lib/admin/promotion-validation.ts`. Do not duplicate a second, different validation policy for activation.

Do not calculate activation state from current pricing, merchant balances, promotion grants or merchant selections.

##### Correction 3 — add deterministic regression coverage for the immutable transition boundary

Extend the existing ADMIN-004 focused tests. At minimum prove all of the following:

1. activation uses a conditional mutation containing `id`, `status: DRAFT`, and `version: existing.version`;
2. draft editing uses the same `id + DRAFT + version` conditional authority;
3. both conditional mutations require exactly one affected row and reject a stale/lost transition;
4. the `ACTIVATED` event is written only after the activation CAS succeeds;
5. the activation form submits `intent` and `id` but no hidden `name`, `scope`, `quantity`, target, start, or expiry commercial authority;
6. activation validates the persisted target, quantity, and window after re-read;
7. the existing non-SUPER_ADMIN, GLOBAL/PLAN/SHOP, mixed-target, quantity/window, no-grant/no-selection/no-counter/no-Shopify assertions remain green.

The tests may use the repository's existing source/security-test style. If a helper is introduced in `promotion-validation.ts`, add direct unit tests for the helper as appropriate.

Do not add a database integration harness solely for this task if the repository does not already have one.

##### Correction 4 — preserve the existing security and scope boundaries

Attempt 2 must not broaden access or behaviour:

- mutations remain SUPER_ADMIN-only;
- no merchant Shopify session path is introduced;
- exact Shop/BillingPlan IDs remain server-resolved;
- no raw Prisma object is intentionally returned to the client;
- no merchant grant, selection, reservation, entitlement counter, purchased-credit, lifetime-Free, or Shopify App Event write is added;
- campaign close/reopen/expiry-change lifecycle remains ADMIN-005 scope.

Do not change the database schema or add a new campaign status.

##### Correction 5 — record mandatory Attempt 2 worktree/synchronisation evidence prospectively

Attempt 1's Completion Report records the implementation worktree and commits but does not contain the complete mandatory physical-isolation/start-of-attempt evidence structure.

Do **not** invent missing Attempt 1 evidence.

When Attempt 2 is actually claimed, use the canonical dedicated ADMIN-004 worktrees and perform the normal start-of-attempt synchronization. Record the actual Attempt 2 results using this exact structure:

```text
Physical worktree isolation:
  canonical workspace root: <actual launcher-resolved workspace root>
  parent worktree: <actual canonical ADMIN-004 parent worktree>
  parent branch: task/ARCH-010-ADMIN-004
  implementation worktree: <actual canonical ADMIN-004 implementation worktree>
  implementation branch: task/ARCH-010-ADMIN-004
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Record only outcomes actually observed during Attempt 2. Stop under `docs/agent-worktree-isolation-policy.md` if the canonical worktrees cannot be used cleanly.

##### Correction 6 — required Attempt 2 validation

From the canonical ADMIN-004 implementation worktree, initialize the already-recorded database submodule/gitlink as required by the Admin repository without changing the gitlink, then run:

```bash
npm run prisma:validate
npm run prisma:generate
node --experimental-strip-types --test tests/unit/promotion-validation.test.ts
node --test tests/security/admin-promotions.test.mjs tests/unit/promotion-validation.test.ts
npm test
npm run lint
npx tsc --noEmit
npm run build
git diff --check
```

All task-owned/focused tests must pass.

Repository-wide warnings may be reported only when they are demonstrably pre-existing and unrelated to ADMIN-004. Do not suppress or rewrite unrelated baseline files merely to make this task green.

The Completion Report must record:

- each command and outcome;
- the new implementation commit;
- the parent Completion Report commit;
- the unchanged database submodule gitlink;
- the exact Attempt 2 worktree/synchronisation evidence above.

##### Attempt 2 stop conditions

STOP and return this same task to `moda_architect` without inventing an alternative design if:

1. enforcing the DRAFT/version CAS requires a Prisma/schema change;
2. the accepted `PromotionCampaign.version` field is not available at the recorded database gitlink;
3. exact durable Shop/BillingPlan target validation cannot be performed inside the existing transaction;
4. satisfying the correction requires merchant grant/selection/counter mutation or another repository;
5. canonical worktree isolation/synchronization cannot be satisfied;
6. a required focused validation fails because of the Attempt 2 change.

After the corrections and validation pass, set this same task back to `status: review`, update the Completion Report, push both task branches, and STOP for `moda_architect` review. Do not start `ADMIN-005` or `SHOPIFY-021`.

#### Attempt 2 — Changes Requested

Attempt 2 is **accepted in substance for the campaign transition implementation**, but this task is not yet architect-accepted Complete. Keep the same task and reclaim it as Attempt 3. Do not redesign the CAS/activation implementation.

The following Attempt 2 work is accepted and must be preserved unchanged unless a required test proves a defect:

- versioned `id + DRAFT + version` compare-and-set for draft editing;
- versioned `id + DRAFT + version` compare-and-set for activation;
- stale/lost transitions require `count === 1` and otherwise fail with the bounded reload/retry error;
- `ACTIVATED` audit evidence is appended only after the activation CAS succeeds in the same transaction;
- activation submits only `intent=activate` and the campaign `id`;
- activation re-reads persisted campaign terms and validates persisted target/quantity/window state;
- no merchant grant, selection, reservation, entitlement-counter, purchased-credit, lifetime-Free or Shopify App Event mutation was introduced;
- implementation commit `6683e190c28536f768dd9fafa4e4ccfed38c4aae` is the accepted-in-substance Attempt 2 source baseline.

Attempt 3 is intentionally narrow. Do not change the accepted CAS logic or persisted-term validation unless one of the required focused tests fails because that implementation is genuinely wrong.

##### Correction 1 — enforce the original `SUPER_ADMIN only` contract at the page boundary

The task's Security section says `SUPER_ADMIN only`. The mutation action is correctly SUPER_ADMIN-gated, but the `/promotions` page currently calls only `requirePlatformAdminPage()`, which permits any authorized platform-admin role to read campaign history/targets and see campaign authoring controls.

File:

```text
moda-interact-admin/src/app/(protected)/promotions/page.tsx
```

Required behaviour:

1. call `requirePlatformAdminPage()` and retain the returned principal;
2. before calling `getPromotionTargets()` or `getPromotionCampaigns()`, require `principal.role === "SUPER_ADMIN"`;
3. for any authenticated non-SUPER_ADMIN, redirect to `/` using the repository/Next.js page convention;
4. do not query promotion campaigns or target lists before that role check;
5. unauthenticated behaviour remains owned by `requirePlatformAdminPage()` and must continue to redirect to `/login`;
6. do not create a second auth/session system.

A conforming shape is conceptually:

```ts
const principal = await requirePlatformAdminPage();
if (principal.role !== "SUPER_ADMIN") redirect("/");

const [{ plans, shops }, campaigns] = await Promise.all([...]);
```

Use `redirect` from `next/navigation`. Do not expose a raw authorization/Prisma error to the page.

##### Correction 2 — hide the Promotions navigation entry from non-SUPER_ADMIN roles

File:

```text
moda-interact-admin/src/components/admin/sidebar.tsx
```

The sidebar already receives `administratorRole`. Render the `/promotions` link only when:

```text
administratorRole === "SUPER_ADMIN"
```

Do not change the visibility of tenant directory, billing, merchant-support or observability navigation. This is UI discoverability only; the page-level role check from Correction 1 remains mandatory and is the security boundary.

##### Correction 3 — add deterministic security regression coverage

File:

```text
moda-interact-admin/tests/security/admin-promotions.test.mjs
```

Extend the existing source/security tests to prove all of the following:

1. the Promotions page retains the principal returned by `requirePlatformAdminPage()`;
2. the page checks `principal.role !== "SUPER_ADMIN"` before campaign/target data is loaded;
3. a non-SUPER_ADMIN page request follows the bounded `/` redirect path;
4. the Sidebar renders the `/promotions` link only behind `administratorRole === "SUPER_ADMIN"`;
5. the existing mutation-level `requirePlatformAdminMutation()` + SUPER_ADMIN guard remains present;
6. all Attempt 2 CAS/persisted-authority/no-grant/no-Shopify assertions remain green.

Use the repository's existing source/security-test style. Do not introduce a browser/system-test harness for this correction.

##### Correction 4 — exact Attempt 3 production scope

Attempt 3 production/test changes are limited to:

```text
moda-interact-admin/src/app/(protected)/promotions/page.tsx
moda-interact-admin/src/components/admin/sidebar.tsx
moda-interact-admin/tests/security/admin-promotions.test.mjs
```

plus this task file for execution metadata and Completion Report evidence.

Do **not** change:

```text
src/app/actions/promotions.ts
src/components/admin/promotion-campaign-form.tsx
src/lib/admin/promotion-validation.ts
tests/unit/promotion-validation.test.ts
database/prisma/**
```

unless a required Attempt 3 test demonstrates a concrete defect in the accepted-in-substance Attempt 2 implementation. If that occurs, STOP and return the exact failing test and reason to `moda_architect` before editing those files.

No other repository, task file, architecture document, Shared contract, merchant-facing Shopify code or Background code is in scope.

##### Correction 5 — task lifecycle and worktree evidence

The published parent branch at Attempt 2 incorrectly remained:

```yaml
status: in_progress
executor: copilot
claimed_at: '2026-09-13T12:58:24Z'
attempt: 2
```

while its Completion Report said `Review.`. This overlay deliberately returns the same task to the reclaimable state:

```yaml
status: ready
executor: null
claimed_at: null
attempt: 2
```

The next authorized `/moda-task ARCH-010-ADMIN-004` claim must increment exactly once to Attempt 3. At the end of Attempt 3, the repository agent must actually set the task frontmatter to `status: review` before publishing the parent report. A Completion Report that merely says Review while YAML remains `in_progress` is not sufficient.

Attempt 3 must again record the real canonical worktree and start-of-attempt synchronization evidence using the mandatory structure. Do not fabricate or rewrite Attempt 2 history.

##### Correction 6 — required Attempt 3 validation

From the canonical ADMIN-004 implementation worktree, with the recorded database submodule initialized and gitlink unchanged, run:

```bash
npm run prisma:validate
npm run prisma:generate
node --experimental-strip-types --test tests/unit/promotion-validation.test.ts
node --test tests/security/admin-promotions.test.mjs
npm test
npm run lint
npx tsc --noEmit
npm run build
git diff --check
```

Expected:

- the ADMIN-004 focused security tests pass;
- the existing promotion validation tests pass;
- full repository tests pass under the same accepted baseline;
- lint/typecheck/build pass subject only to already-documented unrelated warnings;
- no changed Attempt 3 file introduces formatting/diff-check failures;
- database submodule HEAD remains `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`;
- no database gitlink change is staged.

The Completion Report must list the Attempt 3 implementation commit and parent report commit, exact command outcomes, exact worktree/synchronization evidence, and confirm only the three authorized implementation/test files changed.

##### Attempt 3 stop conditions

STOP and return to `moda_architect` if:

1. enforcing SUPER_ADMIN page access requires a new authentication system or cross-repository contract;
2. the existing page principal does not expose a reliable `role`;
3. satisfying this correction requires a schema/migration change;
4. a required focused test demonstrates the accepted Attempt 2 CAS implementation is actually defective;
5. canonical worktree isolation/synchronization cannot be satisfied.

After the corrections pass, set this same task to `status: review`, push the implementation and parent task branches, and STOP. Do not start `ADMIN-005` or `SHOPIFY-021`.


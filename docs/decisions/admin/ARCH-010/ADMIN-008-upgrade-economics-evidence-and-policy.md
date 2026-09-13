---
id: ARCH-010-ADMIN-008
architecture_id: ARCH-010
title: Manage verified Shopify economics evidence, upgrade edges and guardrail policy
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 88
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-ADMIN-001
- ARCH-010-ADMIN-010
enables:
- ARCH-010-ADMIN-009
created: 2026-09-12
updated: '2026-09-13'
---

# ARCH-010-ADMIN-008: Manage verified Shopify economics evidence, upgrade edges and guardrail policy

## Objective

Add SUPER_ADMIN controls for the durable evidence consumed by the upgrade-economics guardrail while preserving Shopify App Pricing as monetary authority.

This task records **verified Shopify economics evidence**; it does not create/change Shopify prices.

## Inspect before editing

```text
src/app/(protected)/billing/**
src/components/admin/billing-*.tsx
src/app/actions/billing-controls.ts
src/app/actions/billing-plan.ts
src/lib/admin/billing-control-validation.ts
src/lib/admin/billing-plan*.ts
tests/security/admin-billing-*.test.mjs
database/prisma/schema.prisma
```

## Required Admin capabilities

### A. Platform policy

Expose:

```text
Minimum stay+top-up premium above next-plan upgrade
```

bound to:

```text
PlatformBillingPolicy.minimumUpgradePremiumBps
```

Default display = 20.00% for 2000 bps.

Server validation: integer bps `0..10000`. Audit through existing `PLATFORM_POLICY_CHANGED`; no second policy subsystem.

### B. Explicit upgrade ladder

SUPER_ADMIN can configure exact edges using durable plan IDs, e.g.:

```text
Free -> Starter
Starter -> Growth
Growth -> Scale
```

Do not infer next plan from name, price or creation order.

Server-side reject:

- self-edge;
- duplicate lower successor;
- duplicate higher predecessor;
- missing/inactive plan IDs where current conventions require active mappings.

### C. Record Shopify economics snapshot

Provide a bounded form/action to record the exact Shopify Partner Dashboard/App Pricing evidence verified by the SUPER_ADMIN:

```text
billingPlanId
shopifyPlanHandleSnapshot
monthlyRecurringAmountMinor
currency
recoveryCreditPackEnabledSnapshot
recoveryCreditsPerPackSnapshot
shopifyRecoveryCreditPackEventHandleSnapshot
usagePricingSnapshot
verificationReason
```

`usagePricingSnapshot` UI may use explicit fields rather than raw JSON, but server output must normalize to the DATABASE-013 shape.

Supported pricing:

```text
FIXED
GRADUATED
VOLUME
```

For tier modes, allow ordered tiers with:

```text
upTo?                 # final tier null/open-ended
amountPerUnitMinor
flatAmountMinor
```

The UI must label this evidence clearly:

> Verified Shopify App Pricing economics used by Moda's Admin guardrail. Shopify remains the charging authority.

Do not claim the snapshot itself changes merchant pricing.

### D. Drift checks

Before storing the snapshot, re-read local `BillingPlan` and require:

- exact `shopifyPlanHandle` match;
- pack-enabled flag/pack size match the local mapping;
- exact local pack-meter handle when packs enabled;
- no pack-pricing evidence when packs disabled unless retained as historical evidence outside the active snapshot flow.

Do not call Shopify Partner API in this task unless an already-approved Admin connector/service exists. Manual verification against Partner Dashboard is acceptable and must be audited.

## Required tests

Implement integration scenarios 43–47 plus snapshot-management portions of 61–64 from:

```text
docs/contracts/ARCH-010-upgrade-economics-guardrail-test-matrix.md
```

Also prove:

1. only SUPER_ADMIN can mutate threshold/edges/snapshots;
2. threshold before/after audit is durable;
3. snapshot creation is append-only;
4. existing snapshots cannot be silently overwritten;
5. normalized tiers reject malformed/non-open-ended configuration;
6. snapshot contains no secret/token fields;
7. no Shopify mutation/API call is introduced;
8. plan catalogue still does not own monetary price fields.

## Non-goals

Do not implement the guardrail calculation (ADMIN-007), hard enforcement (ADMIN-009), automatic Partner API price discovery, merchant UI, profitability checks or provider price changes.

## Stop conditions

Stop if DATABASE-013 is unavailable or if implementation would require putting monthly/top-up money columns back on `BillingPlan`.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-admin/src/app/(protected)/billing/controls/page.tsx`
- `moda-interact-admin/src/app/(protected)/billing/page.tsx`
- `moda-interact-admin/src/app/actions/billing-controls.ts`
- `moda-interact-admin/src/app/actions/billing-economics.ts`
- `moda-interact-admin/src/components/admin/billing-controls.tsx`
- `moda-interact-admin/src/lib/admin/billing-control-validation.ts`
- `moda-interact-admin/src/lib/admin/billing-economics-validation.ts`
- `moda-interact-admin/src/lib/admin/billing-economics.ts`
- `moda-interact-admin/tests/security/admin-billing-economics.test.mjs`
- `moda-interact-admin/tests/unit/billing-economics-behavior.test.ts`
- `moda-interact-admin/tests/unit/billing-economics-validation.test.ts`

### Work Completed
- Added the bounded `minimumUpgradePremiumBps` platform policy field with a 2000 bps default and existing `PLATFORM_POLICY_CHANGED` audit path.
- Added SUPER_ADMIN-only exact durable-plan upgrade-edge creation/deactivation with self-edge, active-plan, duplicate predecessor/successor, and increasing-allowance checks.
- Added SUPER_ADMIN-only append-only verified Shopify economics snapshots with normalized FIXED, GRADUATED, and VOLUME pricing evidence.
- Added exact local Shopify handle, pack enablement, pack size, and pack-meter drift checks before snapshot persistence.
- Corrected edge lifecycle handling for permanent DATABASE-013 unique keys: exact inactive pairs reactivate, inactive conflicting declarations reject before Prisma, and repeated deactivation is idempotent.
- Added the required percentage display (`20.00% (2000 bps)` by default) while retaining integer bps persistence, and bounded persisted Prisma `Int` economics fields to `0..2147483647`.
- Added bounded Admin controls and the required Shopify charging-authority disclaimer. No Shopify API calls, provider mutations, merchant UI, or monetary fields on `BillingPlan` were introduced.
- Added focused behavior coverage for scenarios 43–47 and snapshot-management boundaries, alongside parser and source/security coverage for authorization, drift, append-only storage, tier validation, no-secret evidence, and no-Shopify-mutation boundaries.

### Validation Results
- PASS: `npm run prisma:validate` and `npm run prisma:generate`.
- PASS: focused unit/parser and behavior tests, 6/6; focused security tests, 13/13.
- PASS: `npm test`, 161/161; `npm run test:unit`, 42/42.
- PASS: `npm run lint` (two pre-existing warnings in `src/components/admin/queue-monitor.tsx`, zero errors).
- PASS: `npx tsc --noEmit --pretty false` and `npm run build`.
- PASS: focused Prettier check for all six changed implementation/test files and `git diff --check`.
- EXPECTED BASELINE DEVIATION: repository-wide `npm run format:check` reports 87 pre-existing unformatted files; none of the six ADMIN-008 files are among the reported files.
- PASS: database submodule initialized and gitlink verified. Expected and actual SHA: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.
- PASS: exact removed-symbol search has only intentional negative assertions in existing tests; exact `billing.adjustments` search has only the intentional negative assertion in `tests/security/admin-billing-visibility.test.mjs`.

### Git / VCS
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-008
  parent branch: task/ARCH-010-ADMIN-008
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-008
  implementation branch: task/ARCH-010-ADMIN-008
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: yes
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: yes

Database submodule:
  database submodule initialized: yes
  database gitlink expected: 5443afdd8f0c816dc16e1f3e93f9906c5ca31d94
  database submodule HEAD: 5443afdd8f0c816dc16e1f3e93f9906c5ca31d94
  database gitlink staged/changed: no

### Attempt 2 Git / VCS
- Parent claim commit: `bf0ae72`, pushed to `origin/task/ARCH-010-ADMIN-008`.
- Implementation branch: `task/ARCH-010-ADMIN-008`; implementation changes are ready to commit and push.

### Architect Review
Changes Requested

#### Attempt 1 — Changes Requested

Attempt 1 is **not accepted**. Keep this same task and return it to `ready` for Attempt 2. Do not create a replacement task and do not start `ARCH-010-ADMIN-009`.

The following Attempt 1 implementation is retained unless a required regression test proves it wrong:

- SUPER_ADMIN mutation guards;
- `PlatformBillingPolicy.minimumUpgradePremiumBps` persisted through the existing `PLATFORM_POLICY_CHANGED` audit path;
- append-only `BillingEconomicsSnapshot.create(...)`;
- Shopify plan-handle / pack-enable / pack-size / pack-meter drift checks;
- normalized FIXED / GRADUATED / VOLUME snapshot parsing;
- manual Partner Dashboard evidence marker;
- no Shopify provider mutation/API call;
- no monetary price fields added back to `BillingPlan`.

Attempt 2 is intentionally bounded to the corrections and evidence below.

##### Correction 1 — make upgrade-edge deactivate/reactivate compatible with DATABASE-013 uniqueness

Files:

```text
moda-interact-admin/src/app/actions/billing-economics.ts
moda-interact-admin/src/lib/admin/billing-economics-validation.ts   # only if form intent/types need a bounded adjustment
moda-interact-admin/src/components/admin/billing-controls.tsx       # only if UI needs reactivation/reason wiring
```

DATABASE-013 has permanent uniqueness:

```prisma
@@unique([lowerPlanId])
@@unique([higherPlanId])
```

The Attempt 1 create path checks only `lowerEdge?.active` / `higherEdge?.active`. Therefore, after an edge is deactivated, the row still owns both unique keys and a later `create()` for the same pair reaches Prisma `P2002`. The Admin UI currently exposes deactivation, so the ladder can be placed into a state that cannot be restored through the same control.

Required behavior for `intent=create`:

```text
load current durable lower plan and higher plan
load any declared row by lowerPlanId
load any declared row by higherPlanId

if either requested plan is missing/inactive:
  reject

if lowerPlanId == higherPlanId:
  reject

if higher monthly included allowance <= lower monthly included allowance:
  reject

if an ACTIVE lower or higher declaration conflicts:
  reject with the existing bounded branching error

if the SAME exact lowerPlanId -> higherPlanId row exists and is inactive:
  reactivate that existing row
  do NOT create a second row
  write one BillingAuditEvent with beforeValue + afterValue

if an INACTIVE lower/higher declaration exists but belongs to a DIFFERENT pair:
  reject with a bounded declared-edge conflict
  do NOT fall through to Prisma unique-constraint failure
  do NOT delete historical rows in this task

only when neither unique key is already declared:
  create the new row
  audit the create
```

The same exact inactive row may be detected through both the lower and higher lookups; compare by durable row `id`.

For `intent=deactivate`:

- re-read by durable edge id;
- transition only an ACTIVE row to inactive;
- avoid appending duplicate deactivation audit evidence for an already-inactive row;
- the audit must contain the actual persisted before/after edge, not client-hidden lower/higher IDs.

Do not change DATABASE-013 schema or its unique constraints in ADMIN-008.

##### Correction 2 — present the premium as the required percentage, while persisting bps

File:

```text
moda-interact-admin/src/components/admin/billing-controls.tsx
```

The task contract requires:

```text
Minimum stay+top-up premium above next-plan upgrade
Default display = 20.00% for 2000 bps
```

Attempt 1 currently exposes only:

```text
Minimum upgrade premium (basis points)
2000
```

Keep the durable/form value in basis points, but the UI must visibly explain the percentage.

Required initial/current display:

```text
20.00% (2000 bps)
```

when the current/default value is 2000.

Use the current policy value when present:

```text
percentage = minimumUpgradePremiumBps / 100
```

and render it with exactly two decimal places for this control. Do not change durable storage to floating point.

The visible label/help must use the task meaning:

```text
Minimum stay+top-up premium above next-plan upgrade
```

A bps input may remain, provided the corresponding percentage is plainly visible.

##### Correction 3 — bound persisted Prisma `Int` economics values before database execution

File:

```text
moda-interact-admin/src/lib/admin/billing-economics-validation.ts
```

`BillingEconomicsSnapshot.monthlyRecurringAmountMinor` and
`BillingEconomicsSnapshot.recoveryCreditsPerPackSnapshot` are Prisma `Int`
fields. Attempt 1 accepts any JavaScript safe integer, including values larger
than PostgreSQL/Prisma `Int`, so form validation can pass and persistence can
fail later.

For fields persisted into Prisma `Int`, validate against:

```text
0 .. 2147483647
```

with pack size still strictly positive when present.

At minimum prove:

```text
monthlyRecurringAmountMinor = 2147483647 -> accepted
monthlyRecurringAmountMinor = 2147483648 -> rejected

recoveryCreditsPerPackSnapshot = 2147483647 -> accepted when packs enabled
recoveryCreditsPerPackSnapshot = 2147483648 -> rejected
```

Do not arbitrarily apply the 32-bit bound to JSON-only tier fields unless the
accepted evaluator/database contract requires it.

##### Correction 4 — replace source-only assertions with behavior evidence for scenarios 43–47 and snapshot portions of 61–64

Attempt 1's `admin-billing-economics.test.mjs` mainly proves source text is
present. Keep useful source-boundary assertions, but the task explicitly
requires behavior for integration scenarios 43–47 and snapshot-management
portions of 61–64.

Add focused behavior tests. Use existing repository test conventions. If the
Next server action itself is awkward to import without the full Next runtime,
extract only the smallest pure/testable decision helpers from the action path;
the server action must call those exact helpers.

Required behavior proofs:

```text
43:
  non-SUPER_ADMIN mutation remains rejected at the server-action boundary
  for threshold, edge and snapshot mutations

44:
  matching durable plan/Shopify handles succeeds
  mismatched current plan handle rejects
  mismatched enabled pack size rejects
  mismatched enabled pack meter handle rejects

45:
  lowerPlanId == higherPlanId rejects

46:
  active branching lower successor rejects
  active branching higher predecessor rejects
  exact inactive pair reactivates instead of create/P2002
  inactive conflicting declaration rejects deterministically before create

47:
  higher monthly included allowance <= lower allowance rejects

snapshot append-only:
  record path creates a new snapshot
  no snapshot update/upsert/delete path is used

61:
  snapshot recording does not mutate Subscription, Shop, BillingPeriod,
  merchant entitlement/reservation state, promotion state or Shopify billing

62:
  no appSubscriptionCreate, appPurchaseOneTimeCreate, App Events or other
  Shopify billing mutation is invoked by snapshot/edge/policy evidence work

63:
  persisted providerEvidence/audit data contains no token, secret, cookie,
  password, access token or raw Partner credential field

64:
  no merchant billing or promotional-credit mutation is introduced
```

The tests do not need to invent a new live database test infrastructure. A
small deterministic decision/helper test plus existing source security checks
is acceptable where the repository has no server-action harness, but **source
regex alone is not sufficient** for the edge lifecycle, drift validation and
numeric boundary behavior.

Do not implement ADMIN-007 evaluator behavior or ADMIN-009 hard enforcement in
these tests.

##### Correction 5 — run the required toolchain validation from the isolated worktree

The Completion Report says Prisma, ESLint and TypeScript were unavailable
because dependencies were not installed. Missing `node_modules` in a new
worktree is setup state, not evidence that the required validation itself is
unavailable.

At Attempt 2 start, after synchronization and submodule initialization:

```bash
cd /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-008

git submodule sync -- database
git submodule update --init --recursive database

EXPECTED_DATABASE_GITLINK="$(git rev-parse HEAD:database)"
ACTUAL_DATABASE_HEAD="$(git -C database rev-parse HEAD)"
test "$EXPECTED_DATABASE_GITLINK" = "$ACTUAL_DATABASE_HEAD"

npm ci
```

Do not edit the database gitlink or database schema for this task.

Then run:

```bash
npm run prisma:validate
npm run prisma:generate

node --experimental-strip-types --test \
  tests/unit/billing-economics-validation.test.ts

node --test \
  tests/security/admin-billing-economics.test.mjs \
  tests/security/admin-billing-controls.test.mjs

# Include the new Attempt 2 behavior test file(s) explicitly here.
npm test
npm run lint
npx tsc --noEmit --pretty false
npm run build
git diff --check
```

All ADMIN-008 focused tests, Prisma validate/generate, lint, typecheck, build
and `git diff --check` must pass.

If `npm ci` itself fails because of a real external registry/network/tooling
outage, record the exact command/error and return the task as **blocked** rather
than claiming required validation passed.

Existing unrelated warnings may be recorded exactly; do not fix them in this task.

##### Correction 6 — mandatory physical-worktree and synchronization evidence

Attempt 1 records worktree paths but not the mandatory exact physical-isolation
and start-of-attempt synchronization evidence.

Attempt 2 must begin with synchronization in both canonical task worktrees
before editing. If a remote task branch already exists, fast-forward it first,
then incorporate current `origin/main`. Stop on divergence or unresolved
conflict rather than inventing history.

The Completion Report must contain this exact-shaped evidence using actual
Attempt 2 observations:

```text
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-008
  parent branch: task/ARCH-010-ADMIN-008
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-008
  implementation branch: task/ARCH-010-ADMIN-008
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Database submodule:
  database submodule initialized: yes
  database gitlink expected: <full SHA>
  database submodule HEAD: <full SHA>
  database gitlink staged/changed: no
```

Do not reconstruct or rewrite Attempt 1 history. Record only what is actually
observed during Attempt 2.

##### Attempt 2 scope boundary

Production changes are limited to ADMIN-008 economics/policy surfaces:

```text
src/app/actions/billing-economics.ts
src/components/admin/billing-controls.tsx
src/lib/admin/billing-economics-validation.ts
src/lib/admin/billing-economics.ts        # only if a testable helper belongs here
src/app/actions/billing-controls.ts       # only if needed to preserve threshold wiring
src/lib/admin/billing-control-validation.ts
```

Focused test changes are allowed under:

```text
tests/security/admin-billing-economics.test.mjs
tests/security/admin-billing-controls.test.mjs
tests/unit/billing-economics-validation.test.ts
tests/unit/<new narrowly-scoped ADMIN-008 behavior test>.ts
```

Do not:

- modify Prisma schema/migrations;
- add monetary authority to `BillingPlan`;
- implement ADMIN-007 evaluator calculations;
- implement ADMIN-009 hard enforcement;
- call Shopify Partner/Admin/App Billing APIs;
- modify merchant subscriptions, purchases, refunds, promotions or entitlement accounting;
- broaden into unrelated Admin UI cleanup.

##### Stop conditions

STOP and return to `moda_architect` if:

1. current DATABASE-013 schema differs materially from the permanent lower/higher unique-key contract described above;
2. making a deactivated exact edge restorable would require a database schema change;
3. behavior testing requires changing a cross-repository contract;
4. current `origin/main` introduces a conflicting economics architecture that cannot be reconciled within the files above;
5. required validation cannot run after successful dependency installation for a reason that would require unrelated repository repair.

After the corrections:

1. set this same task to `review`;
2. update the Completion Report with the new implementation commit and parent report commit;
3. push both `task/ARCH-010-ADMIN-008` branches;
4. STOP.

Do not execute `ARCH-010-ADMIN-009`.

#### Attempt 2 — Accepted

**Decision: Accepted / Complete.**

Accepted implementation:

```text
94d4fbb08f294b6e34cdf04c065949d82c19c519
```

Accepted parent review report:

```text
97495746b4699d8840fa924f3aedfe5c4e7484af
```

Attempt 2 satisfies the implementation corrections requested after Attempt 1:

- exact inactive upgrade-edge pairs reactivate the existing durable row rather than colliding with DATABASE-013 permanent unique keys;
- inactive conflicting declarations reject deterministically before Prisma persistence;
- repeated deactivation is idempotent;
- edge audit before/after evidence is retained;
- `minimumUpgradePremiumBps` remains integer basis points and the Admin UI renders the required `20.00% (2000 bps)` default presentation;
- persisted Prisma `Int` economics fields are bounded to `0..2147483647`;
- append-only economics snapshots, SUPER_ADMIN mutation guards, Partner Dashboard evidence and no-Shopify-mutation boundaries are preserved;
- canonical worktree, synchronization and database-submodule evidence is complete;
- Prisma validation/generation, focused tests, 161 full tests, 42 unit tests, lint, typecheck, build, focused formatting and `git diff --check` passed; the repository-wide 87-file formatting deviation is accepted as unrelated baseline evidence.

The final scenario-44 mapping-drift evidence was supplied manually against the exact accepted implementation SHA without changing the repository. A temporary Vitest harness imported the real production `recordEconomicsSnapshotAction()` and executed five cases:

```text
ADMIN-008: exact durable-plan snapshot mapping is accepted
ADMIN-008: changed shopifyPlanHandle is rejected
ADMIN-008: changed recoveryCreditPackEnabled is rejected
ADMIN-008: changed enabled recoveryCreditsPerPack is rejected
ADMIN-008: changed enabled shopifyRecoveryCreditPackEventHandle is rejected
```

Result:

```text
Test Files  1 passed (1)
Tests       5 passed (5)
```

The temporary evidence test/config were then removed; `git status --short` and `git diff --check` were clean and implementation HEAD remained `94d4fbb08f294b6e34cdf04c065949d82c19c519`. The temporary Vitest harness is acceptance evidence only and is not required to become a repository dependency.

No Attempt 3 implementation is required. The previously proposed evidence-only Attempt 3 overlay is superseded by this acceptance decision and must not be applied.


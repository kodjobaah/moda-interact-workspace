---
id: ARCH-010-ADMIN-007
architecture_id: ARCH-010
title: Implement the supplied upgrade economics guardrail as a deterministic pure evaluator
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 87
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
- ARCH-010-ADMIN-009
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-ADMIN-007: Implement the supplied upgrade economics guardrail as a deterministic pure evaluator

## Objective

Implement the user-supplied **Upgrade Economics Guardrail** as a pure, deterministic Admin library with exhaustive tests. Luna must **not redesign the algorithm**.

The supplied source established these binding semantics:

- find the cheapest lower-plan top-up path needed to reach the next plan's included capacity;
- lower monthly subscription + cheapest top-ups must be at least 20% more expensive than upgrading by default;
- fail when stay+top-up is as cheap/cheaper than upgrade;
- fail when the premium is positive but below policy;
- show the exact calculation to Admin.

ARCH-010 adds fail-closed `UNVERIFIED` states and a current single-pack Shopify usage-meter adapter.

## Binding reference implementation

**Read and copy/adapt the full implementation from:**

```text
docs/contracts/ARCH-010-upgrade-economics-guardrail.reference.ts
```

That reference is intentionally complete. Do not reconstruct the dynamic-programming algorithm, tier mathematics, result codes or threshold arithmetic from prose.

Target implementation location should be:

```text
src/lib/admin/upgrade-economics-guardrail.ts
```

unless the repository already has a directly equivalent canonical utility location.

The implementation must preserve these exported capabilities from the reference:

```text
findCheapestTopUpCombination
summarisePurchases
evaluateUpgradeEconomicsCost
validateUpgradeEconomics
calculateUsagePricingCostMinor
validateSinglePackShopifyEconomics
```

## Current Moda integration rule

Current `BillingPlan` has one configured pack size/meter per plan. Therefore the production path uses:

```text
validateSinglePackShopifyEconomics(...)
```

The generic fixed-multi-offer `validateUpgradeEconomics(...)` is retained because it is the supplied guardrail algorithm and supports future multiple fixed offers without redesign.

## Shopify tier semantics

The reference implements normalized pricing snapshots for:

- FIXED;
- GRADUATED — units charged through each tier they pass through;
- VOLUME — all units charged at the tier containing final quantity.

Do not query Shopify in this task. ADMIN-008 supplies audited normalized pricing snapshots.

## Mandatory Free-plan correction

The supplied example uses `Free included=2`. That example is retained as a regression fixture for the supplied algorithm, but ARCH-010 production integration MUST pass:

```text
Free.monthlyIncludedConversations = 0
```

regardless of the one-time lifetime-Free grant.

## Required tests — no omissions

Implement **every applicable pure-evaluator scenario** in:

```text
docs/contracts/ARCH-010-upgrade-economics-guardrail-test-matrix.md
```

Specifically sections A–E (tests 1–42) are mandatory in this task.

Use exact source fixture values for the three supplied examples so regressions are obvious.

Tests must be deterministic and must not make network/database calls.

## Non-goals

Do not edit Prisma, Admin actions/UI, Shopify provider code, BillingPlan mutations, promotions, refunds or profitability policy.

## Stop conditions

Stop if the repository runtime cannot support the reference implementation without changing its economics semantics. Report the exact incompatibility rather than simplifying the algorithm.

## Completion Report

### Status
Review.

### Files Changed

Attempt 1 established the evaluator implementation and test command. Attempt 2 changed only:

- `tests/unit/upgrade-economics-guardrail.test.ts`

### Work Completed

- Preserved the Attempt 1 evaluator implementation unchanged.
- Strengthened tests 6 and 7 to prove both zero and negative invalid credits/charges are ignored while a valid offer is selected (Finding 1).
- Strengthened test 24 with null, zero, negative, and non-safe-integer pack sizes, each asserting `UNVERIFIED` / `TOPUP_PRICING_UNAVAILABLE` (Finding 2).
- Strengthened test 28 with the complete corrected Free-to-Starter PASS economics result (Finding 3).
- Added compile-time evaluator-key exclusion assertions and visibly differing external context fixtures for tests 29–32 (Finding 4).
- Kept the evaluator source unchanged and did not modify database, Prisma, security-test, or unrelated lint-warning surfaces (Findings 5–6).
- Supplied the required start-of-attempt synchronization evidence and focused acceptance results (Finding 7).

### Validation Results

- `npm run test:unit`: passed, 42 tests passed, 0 failed.
- Focused TypeScript command from the Architect Review: passed.
- `npx prettier --check src/lib/admin/upgrade-economics-guardrail.ts tests/unit/upgrade-economics-guardrail.test.ts package.json`: passed.
- `npm run lint`: passed with two pre-existing React Hook dependency warnings in `src/components/admin/queue-monitor.tsx`; 0 errors.
- `git diff --check`: passed.
- The evaluator source has no Attempt 2 diff.

### Git / VCS

Start-of-attempt synchronization:
	parent remote task branch fast-forwarded: not-needed
	parent origin/main incorporated: already-current
	implementation remote task branch fast-forwarded: not-needed
	implementation origin/main incorporated: already-current

Task branch: `task/ARCH-010-ADMIN-007`

Physical worktree isolation:
	canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
	parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-007`
	parent branch: `task/ARCH-010-ADMIN-007`
	implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-007`
	implementation branch: `task/ARCH-010-ADMIN-007`
	shared workspace checkout switched/mutated for task work: no
	shared implementation checkout switched/mutated for task work: no
	another task worktree reused: no

Implementation repository:
	repository: `moda-interact-admin`
	commit: `eafb8f0`
	remote branch: `origin/task/ARCH-010-ADMIN-007`
	pushed: yes

Parent workspace:
	task file: `docs/decisions/admin/ARCH-010/ADMIN-007-upgrade-economics-pure-evaluator.md`
	claim commit: `1774223`
	review report commit: `2496753`
	remote branch: `origin/task/ARCH-010-ADMIN-007`
	pushed: yes
	submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architect Review
Pending.

## Architect Review

### Attempt 1 — Changes Requested

#### Review Status

Changes Requested.

The production evaluator is architecturally conformant. The implementation in:

```text
src/lib/admin/upgrade-economics-guardrail.ts
```

preserves the binding reference implementation in:

```text
docs/contracts/ARCH-010-upgrade-economics-guardrail.reference.ts
```

The source diff is limited to formatting/comment removal; no economics algorithm, result-code, threshold, tier-pricing, or fail-closed semantics were redesigned.

The architect independently executed the focused native Node suite from the review archive and confirmed:

```text
42 tests
42 passed
0 failed
```

Attempt 1 is returned only because several mandatory matrix scenarios are named but not completely proved, and the Completion Report omits mandatory start-of-attempt synchronization evidence.

This is a **test/report-only** correction unless a strengthened test exposes an actual evaluator defect.

#### Finding 1 — Tests 6 and 7 must prove both zero and negative invalid offers

**Affected file**

```text
tests/unit/upgrade-economics-guardrail.test.ts
```

The binding matrix requires:

```text
6. invalid zero/negative pack credits are ignored/rejected safely
7. invalid zero/negative charges are ignored/rejected safely
```

Attempt 1 exercises only zero values.

Keep tests 6 and 7, but make each prove **both** invalid classes.

For test 6, include at minimum:

```text
creditsGranted = 0
creditsGranted = -1
one valid positive offer
```

and assert the invalid offers are ignored and the valid offer is selected.

For test 7, include at minimum:

```text
chargeAmountMinor = 0
chargeAmountMinor = -1
one valid positive-charge offer
```

and assert the invalid offers are ignored and the valid offer is selected.

Do not change `findCheapestTopUpCombination()` unless these strengthened tests expose a real mismatch with the binding reference.

#### Finding 2 — Test 24 must cover every invalid pack-size class required by the matrix

The binding matrix explicitly requires:

```text
null
0
negative
non-safe integer
```

Attempt 1 tests only `0`.

Change test 24 to run the same `validateSinglePackShopifyEconomics(...)` assertion for at least:

```ts
null
0
-1
Number.MAX_SAFE_INTEGER + 1
```

Every case must return:

```text
status: UNVERIFIED
code: TOPUP_PRICING_UNAVAILABLE
```

A fractional value such as `1.5` may also be included, but it does not replace the required non-safe-integer case.

#### Finding 3 — Strengthen the corrected Free fixture

Test 28 currently proves only:

```text
additionalCreditsNeeded === 20
```

Keep `Free.monthlyIncludedConversations = 0`, but also prove the corrected Free→Starter economics result itself is stable.

Using the existing Free offers and Starter fixture, assert at minimum:

```text
status === PASS
additionalCreditsNeeded === 20
topUpCostMinor === 6000
stayAndTopUpCostMinor === 6000
upgradeCostMinor === 3500
```

This makes the ARCH-010 correction explicit: the one-time lifetime-Free grant is not being treated as monthly included capacity.

Do not change the supplied regression fixture in test 9 where the historical source example intentionally uses Free included=2.

#### Finding 4 — Tests 29–32 must actually prove the excluded state is not evaluator input

The matrix requires:

```text
29. changing lifetime-Free grant policy does not change the result
30. promotional campaign quantity/expiry/selection is not an evaluator input
31. purchased-credit balance/refund state is not an evaluator input
32. merchant usage/current balances are not evaluator inputs
```

Attempt 1 does not materially vary those states:

- test 29 executes the same evaluator call twice;
- tests 30–32 simply execute ordinary evaluator calls and assert a result.

That is not sufficient evidence for the named scenarios.

Because ADMIN-007 intentionally owns a **pure evaluator**, do not add these domain states to the evaluator signature. Prove their exclusion instead.

Required approach:

1. Add compile-time assertions based on:

```ts
type UpgradeInput = Parameters<typeof validateUpgradeEconomics>[0];
type SinglePackInput = Parameters<typeof validateSinglePackShopifyEconomics>[0];
```

2. Prove the relevant excluded concepts are not accepted evaluator keys. At minimum cover names representing:

```text
lifetimeFreeRecoveryAllowance
promotion / promotionCampaign / promotionalCredits
purchasedCreditBalance / refund state
merchantUsage / current balance
```

Use deterministic TypeScript assertions or `@ts-expect-error` calls inside a non-executed block. The focused `tsc --noEmit ...` command must fail if one of those excluded properties becomes part of the evaluator contract unexpectedly.

3. Keep runtime tests 29–32 and make each compare the same economics inputs under two explicitly different **external context fixtures**, while deliberately passing only the allowed economics inputs to the evaluator. The contexts must visibly differ in the state named by that test.

For example, test 29 should contain two external contexts with different lifetime-Free allowance values and prove the evaluator result is identical because that field is not forwarded.

The purpose is to make the architectural separation executable and obvious, not to create a fake production integration layer.

#### Finding 5 — Preserve the evaluator implementation

Unless one of the strengthened tests proves an actual mismatch with the binding reference:

```text
DO NOT modify:
src/lib/admin/upgrade-economics-guardrail.ts
```

Do not redesign:

```text
dynamic-programming combination search
premium basis-point arithmetic
PASS / FAIL / UNVERIFIED result codes
FIXED / GRADUATED / VOLUME pricing mathematics
single-pack adapter
message formatting
```

If a strengthened test conflicts with the binding reference implementation, stop and return the exact case to `moda_architect`; do not "fix" the reference semantics.

#### Finding 6 — Full Admin build/security baseline is not an ADMIN-007 rework item

Attempt 1 records:

```text
npm run build:
  blocked because database/prisma/schema.prisma is absent

npm test:
  blocked because Prisma Client cannot be generated/initialized
```

The Admin repository declares `database` as a Git submodule. ADMIN-007 does not own Prisma, database initialization, Admin server actions, or security-test infrastructure.

For Attempt 2:

```text
DO NOT initialize, update, stage, or change the database submodule solely for this task.
DO NOT change Prisma configuration.
DO NOT modify existing security tests.
```

The required acceptance validation for this pure evaluator is the task-owned focused surface:

```bash
npm run test:unit

npx tsc --noEmit --strict --skipLibCheck \
  --target ES2022 \
  --module NodeNext \
  --moduleResolution NodeNext \
  --allowImportingTsExtensions \
  --types node \
  src/lib/admin/upgrade-economics-guardrail.ts \
  tests/unit/upgrade-economics-guardrail.test.ts

npx prettier --check \
  src/lib/admin/upgrade-economics-guardrail.ts \
  tests/unit/upgrade-economics-guardrail.test.ts \
  package.json

npm run lint
git diff --check
```

Inspect `package.json` before running commands.

The existing missing-database-submodule build/security limitation may remain documented as unrelated validation context. It is not permission to change another repository boundary.

#### Finding 7 — Record mandatory start-of-attempt synchronization evidence

Attempt 1 contains valid physical worktree paths but omits the four required synchronization outcomes.

Attempt 2 Completion Report must include exactly this evidence shape:

```text
Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

A clean branch and successful push do not substitute for these values.

#### Allowed Attempt 2 scope

Expected changed files:

```text
tests/unit/upgrade-economics-guardrail.test.ts
docs/decisions/admin/ARCH-010/ADMIN-007-upgrade-economics-pure-evaluator.md
```

`package.json` may remain unchanged from Attempt 1.

Production evaluator source must remain unchanged unless a strengthened mandatory test exposes a genuine binding-reference defect.

#### Required Attempt 2 result

Return the same task to review only after:

```text
all 42 numbered tests pass with the strengthened assertions
focused TypeScript validation passes
format/lint/diff validation passes
mandatory synchronization evidence is recorded
implementation and parent task branches are pushed and clean
```

The top-level numbered test count may remain exactly 42; use multiple assertions/loops/subcases inside tests 6, 7, 24 and 29–32 rather than inventing replacement matrix numbers.

#### Architect Decision

**Changes Requested — Attempt 1.**

Return the same task to:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next authorized `/moda-task ARCH-010-ADMIN-007` claim becomes Attempt 2.

`ARCH-010-ADMIN-009` remains gated until ADMIN-007 is architect-accepted Complete.

### Attempt 2 — Accepted

#### Review Status

Accepted.

The Attempt 1 production evaluator remains unchanged and continues to match the binding reference implementation. Architect review compared the evaluator bytes between the Attempt 1 and Attempt 2 task snapshots and confirmed they are identical.

#### Rework-contract verification

Attempt 2 satisfies every Changes Requested item.

1. **Zero and negative invalid fixed-pack values**

Tests 6 and 7 now each prove both invalid classes:

```text
creditsGranted: 0
creditsGranted: -1

chargeAmountMinor: 0
chargeAmountMinor: -1
```

while a valid positive offer remains selectable.

2. **Complete invalid single-pack-size matrix**

Test 24 now covers:

```text
null
0
-1
Number.MAX_SAFE_INTEGER + 1
```

and every case returns:

```text
UNVERIFIED / TOPUP_PRICING_UNAVAILABLE
```

3. **Corrected Free-plan economics**

Test 28 uses:

```text
Free.monthlyIncludedConversations = 0
```

and directly proves:

```text
status: PASS
additionalCreditsNeeded: 20
topUpCostMinor: 6000
stayAndTopUpCostMinor: 6000
upgradeCostMinor: 3500
```

The one-time lifetime-Free grant is therefore not represented as monthly included recovery capacity.

4. **Excluded domain state remains outside evaluator input**

The test file now derives:

```ts
type UpgradeInput = Parameters<typeof validateUpgradeEconomics>[0];
type SinglePackInput = Parameters<typeof validateSinglePackShopifyEconomics>[0];
```

and contains compile-time assertions that excluded ARCH-010 domain state is not accepted as evaluator input, covering lifetime-Free policy, promotional state, purchased/refund state and merchant usage/current balance.

Tests 29–32 also use visibly different external context fixtures and prove identical evaluator results because only the allowed economics inputs are forwarded.

5. **Evaluator implementation preserved**

No Attempt 2 production-source change exists in:

```text
src/lib/admin/upgrade-economics-guardrail.ts
```

The architect independently compared the Attempt 1 and Attempt 2 file bytes and confirmed identical SHA-256 content.

6. **Focused validation**

Completion Report evidence:

```text
npm run test:unit: PASS — 42/42
focused TypeScript: PASS
Prettier: PASS
npm run lint: PASS — 0 errors, 2 pre-existing warnings
git diff --check: PASS
```

The architect independently reran the native focused unit suite from the review archive and confirmed:

```text
42 tests
42 passed
0 failed
```

The two lint warnings are pre-existing React Hook dependency warnings in an unrelated Admin queue-monitor component and are outside ADMIN-007.

The previously documented full Admin build/security limitation caused by the absent database submodule remains outside this pure evaluator task and is not an acceptance blocker.

7. **Mandatory task-isolation / synchronization evidence**

Attempt 2 records:

```text
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
```

Canonical parent and implementation worktrees are also recorded, with no shared-checkout mutation and no other task worktree reuse.

#### Accepted implementation

```text
implementation commit: eafb8f0
parent report commits: 2496753, d2defa2
```

Both task branches are reported pushed and clean. No main branch was modified and no database gitlink was staged.

#### Architect Decision

**Accepted — Attempt 2.**

Because `completion_mode: automatic`, the task is now:

```text
status: complete
attempt: 2
executor: null
claimed_at: null
```

#### Dependency reconciliation

`ARCH-010-ADMIN-009` remains Pending because it requires both:

```text
ARCH-010-ADMIN-007 — now Complete
ARCH-010-ADMIN-008 — still Pending
```

Therefore ADMIN-007 acceptance does not newly promote a dependant.

The ARCH-010 Ready frontier becomes:

```text
ARCH-010-ADMIN-010
ARCH-010-BACKGROUND-015
ARCH-010-BACKGROUND-019
ARCH-010-SHOPIFY-023
```


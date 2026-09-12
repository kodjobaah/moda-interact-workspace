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
status: review
priority: 87
executor: copilot
claimed_at: '2026-09-12T22:02:32Z'
attempt: 1
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
Ready for Review.

### Files Changed

- `src/lib/admin/upgrade-economics-guardrail.ts`
- `tests/unit/upgrade-economics-guardrail.test.ts`
- `package.json`

### Work Completed

- Added the supplied deterministic evaluator without redesigning the economics algorithm.
- Preserved fixed-offer combination search, purchase summaries, threshold arithmetic, exact calculation messages, and PASS/FAIL result codes.
- Added fail-closed `UNVERIFIED` handling for missing prices, currencies, upgrade edges, top-up configuration, pack sizes, and malformed usage pricing.
- Added FIXED, GRADUATED, and VOLUME Shopify usage-pricing calculations and the current single-pack adapter.
- Added the corrected Free-plan fixture with `monthlyIncludedConversations: 0`; lifetime-Free, promotion, purchased-credit, and merchant usage balances are not evaluator inputs.
- Added all 42 mandatory pure-evaluator scenarios from matrix sections A-E as deterministic native Node tests.
- Added the focused `npm run test:unit` script using Node's built-in TypeScript stripping and test runner.

### Validation Results

- `npm run test:unit`: passed, 42 tests passed, 0 failed.
- Focused `npx tsc --noEmit --strict --skipLibCheck --target ES2022 --module NodeNext --moduleResolution NodeNext --allowImportingTsExtensions --types node src/lib/admin/upgrade-economics-guardrail.ts tests/unit/upgrade-economics-guardrail.test.ts`: passed.
- Focused `npx eslint ...`: no implementation errors; the test file is covered by the repository's configured `tests/**` ignore and emitted one warning.
- Focused `npx prettier --check ...`: passed.
- `git diff --check`: passed.
- `npm run lint`: passed with two pre-existing React hook warnings in `src/components/admin/queue-monitor.tsx`.
- `npm run build`: blocked before compilation because `database/prisma/schema.prisma` is absent from this checkout.
- `npm test`: existing security tests are blocked by the ungenerated Prisma client, which cannot initialize without the missing schema/generation path.

### Git / VCS

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
	commit: `6b1ed00`
	remote branch: `origin/task/ARCH-010-ADMIN-007`
	pushed: yes

Parent workspace:
	task file: `docs/decisions/admin/ARCH-010/ADMIN-007-upgrade-economics-pure-evaluator.md`
	claim commit: `d937cc5`
	review report commit: `4e1af34`
	remote branch: `origin/task/ARCH-010-ADMIN-007`
	pushed: yes
	submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architect Review
Pending.

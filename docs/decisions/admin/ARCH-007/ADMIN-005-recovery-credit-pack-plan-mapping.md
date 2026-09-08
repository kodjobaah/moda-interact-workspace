---
id: ARCH-007-ADMIN-005
architecture_id: ARCH-007
title: Add recovery-credit pack fields to billing plan catalog
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: review
priority: 65
executor: copilot
claimed_at: 2026-09-08T22:37:19Z
attempt: 2
depends_on:
  - ARCH-007-ADMIN-001
  - ARCH-007-DATABASE-005
  - ARCH-007-SHARED-006
enables:
  - ARCH-007-SHOPIFY-004
created: 2026-09-08
updated: 2026-09-08
---
# ARCH-007-ADMIN-005: Add recovery-credit pack fields to billing plan catalog

## Exact product rule

SUPER_ADMIN configures Moda's mapping to Shopify App Pricing. Admin does not set Shopify monetary prices.

Add these fields to the existing BillingPlan catalog create/edit presentation:

```text
recoveryCreditPackEnabled
recoveryCreditsPerPack
shopifyRecoveryCreditPackEventHandle
includedRecoveryConversationAllowance
```

## Server-side validation

When `recoveryCreditPackEnabled=false`:
- pack size and pack event handle must be null/empty.

When `recoveryCreditPackEnabled=true`:
- `recoveryCreditsPerPack` must be a positive integer;
- `shopifyRecoveryCreditPackEventHandle` must be trimmed, non-empty;
- it must differ from `shopifyUsageEventHandle`.

FREE:
- existing `freeLifetimeConversationAllowance` remains required;
- existing normal `shopifyUsageEventHandle` remains null;
- top-up meter is allowed.

PAID_METERED:
- existing normal `shopifyUsageEventHandle` remains required;
- `includedRecoveryConversationAllowance` must be a non-negative integer when top-ups are enabled.

Do not add a money/price input.

## Required copy

The form/help text must state:

```text
"Pack price is configured in Shopify App Pricing. Moda stores only the pack size and Shopify meter mapping."
```

and:

```text
"Configure a cheaper recovery-credit-pack meter rate on higher paid plans in Shopify if that is the intended commercial policy."
```

INTERNATIONALISATION: these quoted English strings define the required
source-language meaning only. They MUST be implemented as keys in the existing
ARCH-005 Admin ICU/i18n catalogue path, not embedded as English literals in the
component. Reuse the current Admin locale resolver/runtime and
`src/i18n/locales/*`; update `src/i18n/required-keys.ts` when that is the
repository convention. Add each new key to every Admin locale catalogue currently
declared by the repository. Do not create a second i18n mechanism.

## Audit

Every change uses existing `PLAN_CATALOG_CHANGED` audit semantics with bounded before/after data. Include the four new fields.

## Tests

Prove all validation combinations above, SUPER_ADMIN mutation protection, audit writing, and that no price field exists in the action schema/UI.

Also prove the new recovery-credit-pack Admin copy resolves through the existing
Admin ICU catalogue path and that required-key/catalogue validation remains
complete. A source-regex assertion alone is not sufficient if the repository has
a behavioral i18n test helper available.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-ADMIN-005` branch and the mirrored parent-workspace `task/ARCH-007-ADMIN-005` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Ready for architect review (Attempt 2)

### Files Changed
In `moda-interact-admin`:

- `src/app/actions/billing-plan.ts`
- `src/components/admin/billing-plan-catalog.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `src/lib/admin/billing-plan-audit.ts`
- `src/lib/admin/billing-plan-validation.ts`
- `tests/security/admin-billing-plan.test.mjs`

Attempt 2 correction file:

- `tests/security/admin-billing-plan.test.mjs`

### Work Completed
- Added validation and persistence mapping for `recoveryCreditPackEnabled`, `recoveryCreditsPerPack`, `shopifyRecoveryCreditPackEventHandle`, and `includedRecoveryConversationAllowance`.
- Enforced disabled-pack clearing, positive pack size, non-empty distinct Shopify meter handle, and non-negative paid-plan included allowance rules.
- Added the recovery-credit pack controls and required ICU help copy to the BillingPlan catalog without adding a monetary price input.
- Extended `PLAN_CATALOG_CHANGED` audit before/after snapshots to include all four fields, including toggle mutations.
- Added focused validation, security, audit, no-price-field, and ICU catalogue coverage.
- Completed the full recovery-credit validation matrix: Free enabled packs, independent missing/blank/zero/negative pack fields, disabled-pack rejection, paid zero allowance acceptance, negative allowance rejection, and distinct meter handles.
- Added concrete before/after assertions for all four recovery-credit fields and confirmed create, update, and toggle branches retain `PLAN_CATALOG_CHANGED` audit semantics.
- Added separate server form-contract and UI input-name checks that reject monetary fields without rejecting the required explanatory copy.
- Preserved behavioral ICU runtime validation, required-key completeness, and runtime resolution assertions for both required help strings.
- Attempt 1 implementation commit: `e1e4017`; Attempt 2 correction commit: `8c3adfe`; implementation branch pushed to `origin/task/ARCH-007-ADMIN-005`.

### Validation Results
- `node --test tests/security/admin-billing-plan.test.mjs`: passed, 10/10 focused tests.
- `npm test`: passed, 119/119.
- `npm run prisma:validate`: passed.
- `npx tsc --noEmit`: passed earlier with the generated client containing DATABASE-005 fields; a clean regeneration from the current nested pointer fails because that pointer predates DATABASE-005.
- `npm run lint`: passed with two pre-existing `queue-monitor.tsx` exhaustive-deps warnings and no errors.
- Targeted Prettier check: passed for all seven changed files.
- `npm run build`: production build passed after generating Prisma from canonical database commit `ebe43c0` (DATABASE-005-containing); existing Next.js workspace-root, BullMQ dynamic dependency, and missing optional `@valkey/valkey-glide` warnings remained. A clean build from the current nested pointer fails with the documented stale-schema type errors.
- `git diff --check`: passed.
- Nested `database` submodule gitlink staged: no.

### Deviations
- The Admin checkout's nested `database` submodule remains pinned at `7ed22538d1a6f04bc3b7c48924add6add0f74801`, before DATABASE-005. Validation temporarily used canonical database commit `ebe43c0466b555ea4919dc55915e28e40c25ae24`; the submodule checkout was restored and no gitlink update was staged.

### Assumptions
- The developer will integrate the accepted DATABASE-005 pointer before runtime deployment and clean-checkout Prisma generation.

### Unresolved Issues
- The Admin repository's nested database pointer still requires the normal dependency integration/update outside this task before a clean checkout can regenerate the new Prisma client without stale-schema type errors.

### Architectural Concerns
- None introduced by this implementation. Admin continues to store Shopify meter mappings and allowance configuration, while Shopify App Pricing remains the source of monetary pack pricing.

### Git / VCS

Task branch: `task/ARCH-007-ADMIN-005`

Implementation repository:
   repository: `moda-interact-admin`
   commit: `8c3adfe`
   remote branch: `origin/task/ARCH-007-ADMIN-005`
   pushed: yes

Parent workspace:
   task file: `docs/decisions/admin/ARCH-007/ADMIN-005-recovery-credit-pack-plan-mapping.md`
   claim commit: `4be95a1`
   review report commit: `ed1c7f8`
   remote branch: `origin/task/ARCH-007-ADMIN-005`
   pushed: claim yes; review report yes
   submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes

Attempt 1 implements the ADMIN-005 production behavior in the correct
architectural location and does not require a production redesign. The four
recovery-credit-pack fields are parsed and persisted, SUPER_ADMIN mutation
protection is preserved, `PLAN_CATALOG_CHANGED` audit snapshots include the new
fields, required explanatory copy uses the existing Admin ICU catalogue, and no
monetary field was added to the production form/action contract.

The remaining issue is explicit regression evidence. The task contract requires
the focused tests to prove every recovery-credit-pack validation combination,
audit inclusion of all four fields, and absence of a money/price input in both
the action schema and UI. Attempt 1's tests do not yet prove all of those
statements.

#### Correction 1 — complete the recovery-credit-pack validation matrix

Preserve `parseBillingPlanForm()` behavior and add focused assertions proving:

1. FREE + pack enabled is accepted when:
   - `freeLifetimeConversationAllowance` remains positive;
   - normal `shopifyUsageEventHandle` is empty/null;
   - `recoveryCreditsPerPack` is positive;
   - `shopifyRecoveryCreditPackEventHandle` is trimmed/non-empty.
2. Enabled packs reject each missing required field independently:
   - missing/blank `recoveryCreditsPerPack`;
   - zero or negative `recoveryCreditsPerPack`;
   - missing/blank pack event handle.
3. Disabled packs accept null/empty pack size + pack event handle and reject
   either field when supplied.
4. PAID_METERED + pack enabled accepts
   `includedRecoveryConversationAllowance = 0`.
5. PAID_METERED + pack enabled rejects a negative included allowance.
6. The pack event handle must differ from the normal usage event handle.

Existing FREE/PAID normal-meter and lifetime-allowance tests may remain as
supporting coverage.

#### Correction 2 — prove all four new fields are in bounded audit before/after snapshots

Extend the audit regression fixture with concrete values for:

```text
includedRecoveryConversationAllowance
recoveryCreditPackEnabled
recoveryCreditsPerPack
shopifyRecoveryCreditPackEventHandle
```

Assert each value appears correctly in both the before and after snapshots when
changed.

Also prove the action continues to use:

```text
BillingAuditAction.PLAN_CATALOG_CHANGED
```

for create, update and toggle branches. A simple exact source count/assertion is
acceptable because the production code already uses the shared snapshot helper
for those branches.

Do not add a second audit type or schema.

#### Correction 3 — prove no monetary input exists in the server form contract or UI

The current assertion:

```text
assert.doesNotMatch(actionSource, /price|amount/i)
```

checks only the server action source and therefore does not prove the task's
explicit `action schema/UI` requirement.

Add deterministic source-contract coverage for:

- `billing-plan-validation.ts`: no FormData field representing pack price,
  amount, currency or monetary value;
- `billing-plan-catalog.tsx`: no `<input>`/form control whose `name` represents
  pack price, amount, currency or monetary value.

Do not reject the required explanatory copy merely because it contains the word
`price`; the assertion must target form field names/contracts, not prose.

#### Correction 4 — preserve behavioral i18n evidence

Keep the existing behavioural catalogue assertion for the two required help
strings and required-key coverage. The repository currently routes Admin
internationalisation through its existing catalogue runtime; no second i18n
mechanism is required.

### Reviewed Files

Implementation commit:

```text
e1e4017d8b349f1da8ccc3eeffa790ec447893f6
```

Primary reviewed files:

- `src/app/actions/billing-plan.ts`
- `src/components/admin/billing-plan-catalog.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `src/lib/admin/billing-plan-audit.ts`
- `src/lib/admin/billing-plan-validation.ts`
- `tests/security/admin-billing-plan.test.mjs`

Parent Completion Report reviewed at:

```text
c9447814e911979db72904424178d2c23f8bb87b
```

### Validation Reviewed

The Completion Report records:

- focused/full Admin test suite: 117 passed;
- TypeScript typecheck: passed against accepted DATABASE-005 schema;
- Prisma validation: passed;
- lint: passed with two pre-existing warnings;
- targeted formatting: passed;
- production build: passed with existing warnings;
- `git diff --check`: passed;
- database submodule gitlink remained unstaged.

The stale uploaded ZIP did not contain the Admin implementation repository, so
the architect reviewed the pushed Admin implementation commit directly from
GitHub rather than treating the ZIP as implementation evidence.

### Architecture Conformance

Changes required within this SAME task, limited to the focused regression
contract above.

The production ADMIN-005 implementation is directionally conformant. No schema,
pricing-policy, Shopify monetary-pricing, or adjacent billing redesign is
requested.

### Follow-up

Return `ARCH-007-ADMIN-005` to `ready`.

Durable state:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next claim becomes **Attempt 2** on the same mirrored
`task/ARCH-007-ADMIN-005` branches/worktree.

Attempt 2 should be test-only unless one of the newly required regressions
exposes an actual implementation defect.

Do not start `ARCH-007-SHOPIFY-004`. It remains Pending until ADMIN-005 is
architect-accepted Complete.

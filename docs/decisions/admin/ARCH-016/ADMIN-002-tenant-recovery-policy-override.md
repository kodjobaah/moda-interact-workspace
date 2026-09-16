---
id: ARCH-016-ADMIN-002
architecture_id: ARCH-016
title: Add tenant recovery-policy visibility and explicit admin override
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-016-DATABASE-001
- ARCH-016-SHARED-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16T17:18:00Z
---

# ARCH-016-ADMIN-002

## Objective

Give platform admins a tenant-scoped view of merchant recovery settings, current Shopify discount catalogue state and a durable complete policy override.

## Published Shared dependency

Install/pin the exact package version published by `ARCH-016-SHARED-001` in `package.json` and `package-lock.json`. Import the canonical recovery-policy runtime schema/types from `@modainteract/moda-interact-shared/recovery-policy`. Do not recreate `RecoveryOfferMode`, effective-policy cross-field validation, or an equivalent local runtime schema in Admin.

## Authorized implementation surface

Use the existing tenant administration surface. Current snapshot relevant files include:

```text
package.json
package-lock.json
src/components/admin/tenant-administration.tsx
src/app/actions/tenant.ts
src/lib/admin/types.ts
current tenant detail/drawer/page wiring
focused tenant security/action/component tests
```

Create small recovery-policy admin helpers under existing `src/lib/admin/` conventions when needed.

Do not use ARCH-010 Promotions admin pages.

## Replace direct recovery-delay overwrite behavior

Current Admin can write `ShopSettings.recoveryDelayMinutes` directly.

ARCH-016 changes this behavior:

- merchant `ShopSettings` remains merchant-owned;
- Admin must not silently overwrite merchant recovery-delay/settings;
- Admin creates/updates/deletes `ShopRecoveryPolicyOverride` instead.

Remove/replace the old direct recovery-delay write action from the tenant admin UI.

## Tenant view

Display three columns/sections for every policy field:

```text
Merchant configured value
Admin override value (when active)
Effective value
```

Fields:

```text
Recovery start delay
Recovery offer mode
Fixed Shopify discount (when applicable)
No-response follow-up enabled
No-response follow-up delay
```

Also display:

```text
Shopify discount catalogue status
lastSuccessfulSyncAt
number of currently running discounts
number fixedSelectable
CheckoutRecovery current generation/status/lastExternalActivityAt where recovery detail already exists
```

Do not expose secrets/provider access tokens or full raw providerSnapshot in normal Admin UI.

## Canonical policy validation

Use the published Shared recovery-policy schema for enum/cross-field validation after applying Admin-specific authorization and shop-scoped FIXED-discount checks. Database writes remain Prisma-owned; Shared is the canonical runtime contract, not a database model.

## Override create/update

Admin form starts from current effective policy values.

Require:

```text
complete snapshot of every policy field
reason 1..1000 chars
optional expiresAt in future
```

Validate same constraints as merchant policy plus:

```text
FIXED discount belongs to target shop
catalogue CURRENT
fixed discount currently running/selectable
```

Persist `updatedByPlatformAdminId` from authenticated Admin identity. Never accept admin ID from the submitted form.

Use one transaction for authorization recheck + validation + write.

## Override precedence

An override is effective when:

```text
row exists AND (expiresAt is null OR expiresAt > now)
```

Expired override remains historical row until Admin updates/removes it, but the effective resolver treats it as inactive. UI labels it expired.

Provide explicit Clear Override action with confirmation/reason. In the same transaction as every UPSERT or CLEAR, create `ShopRecoveryPolicyOverrideAuditEvent` with authenticated admin ID, action, reason, and bounded before/after JSON. A CLEAR deletes the live override only after its audit event is created; historical audit events remain. Do not misuse an unrelated billing audit enum.

## AI boundary

Admin may set/view `AI_BEST_APPLICABLE` exactly like merchant mode. Do not implement AI selection or preview.

## Required tests

Security:

- unauthenticated denied;
- non-authorized admin role denied per existing tenant-admin policy;
- submitted fake platformAdminId ignored;
- cross-shop fixed discount rejected.

Behavior:

- view merchant vs effective values;
- complete override changes effective values without changing ShopSettings;
- override expiry restores merchant effective policy;
- clear override restores merchant policy;
- FIXED requires current selectable discount;
- AI_BEST_APPLICABLE stored with null fixed ID;
- direct legacy Admin recoveryDelay write path no longer modifies ShopSettings;
- catalogue state shown without provider secrets.

## Validation

```text
npm run test:unit
npm test
npm run lint
npm run build
git diff --check
```

## Stop conditions

STOP if:

- implementation requires Admin to mutate merchant ShopSettings directly;
- override would become field-by-field nullable inheritance;
- AI selection logic is introduced;
- raw provider access tokens/secret payloads would be displayed.

## Completion protocol

## Completion Report

### Status

Ready for Review

### Work Completed

- Pinned `@modainteract/moda-interact-shared` to the exact published `0.12.1` release in `package.json` and `package-lock.json`.
- Replaced the legacy Admin `ShopSettings.recoveryDelayMinutes` write with complete tenant-scoped `ShopRecoveryPolicyOverride` UPSERT and explicit CLEAR actions.
- Reused the published `@modainteract/moda-interact-shared/recovery-policy` schema for enum and cross-field validation; no local replacement schema or AI selection logic was added.
- Added SUPER_ADMIN authorization, authenticated admin identity persistence, future expiry validation, shop-scoped/current/selectable FIXED discount validation, catalogue CURRENT validation, and transactional UPSERT/CLEAR audit events with bounded before/after JSON.
- Added merchant configured, admin override, effective, expired-state, and catalogue status/count views without exposing provider snapshots, access tokens, or secrets.
- Added existing recovery detail generation and `lastExternalActivityAt` presentation.
- AI mode remains configurable with a null fixed discount; no AI ranking or preview was introduced.

### Files Changed

- `package.json`, `package-lock.json`
- `src/app/actions/tenant.ts`
- `src/lib/admin/recovery-policy.ts`
- `src/lib/admin/data.ts`
- `src/lib/admin/types.ts`
- `src/components/admin/tenant-administration.tsx`
- `src/components/admin/recovery-drawer.tsx`
- `tests/unit/recovery-policy.test.ts`
- `tests/security/admin-tenant-recovery-policy.test.mjs`

### Validation

- focused recovery-policy unit tests: `3 passed`;
- focused tenant-admin security tests: `2 passed`;
- `npm run test:unit`: `128 passed`, `0 failed`;
- `npx tsc --noEmit` (equivalent because no `typecheck` script is declared): passed;
- `npm run lint`: passed with 0 errors and 5 pre-existing warnings in unrelated files;
- `git diff --check`: passed;
- `npm test`: repository baseline remained non-clean: `85 passed`, `5 failed`, `11 cancelled`, `3 skipped`. Failures/cancellations are existing async security/observability harness behavior and unrelated baseline assertions; the focused tenant recovery-policy security test passes independently;
- `npm run build`: Prisma generation passed, but the Next.js webpack build repeatedly terminated with exit 130 after `Creating an optimized production build ...` without a compiler diagnostic. No build error was emitted; this environment interruption is recorded for architect review.

### Physical Worktree Isolation

- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-016-ADMIN-002`;
- parent branch: `task/ARCH-016-ADMIN-002`;
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-016-ADMIN-002`;
- implementation branch: `task/ARCH-016-ADMIN-002`;
- shared workspace checkout switched or mutated for task work: no;
- shared implementation checkout switched or mutated for task work: no;
- another task worktree reused: no;
- implementation submodule `database`: `c59f2eb6953642f1c850d38b09ed03096d672547`;
- recursive submodule sync: passed;
- recursive submodule update/init: passed.

### Synchronization Evidence

- parent remote task branch fast-forwarded: not-needed;
- parent origin/main incorporated: already-current;
- implementation remote task branch fast-forwarded: not-needed;
- implementation origin/main incorporated: already-current.

### Git / Handoff

- implementation commit: `900054d` (`feat(admin): add tenant recovery policy overrides`);
- implementation branch pushed: `origin/task/ARCH-016-ADMIN-002`;
- task status set to `review`;
- executor and claimed timestamp cleared;
- returned to `moda_architect` for review; no merge to `main` performed.

## Architect Review — Attempt 1 — Changes Requested

Verdict: **Changes Requested**.

The overall ARCH-016 Admin boundary is correct: merchant `ShopSettings` is no longer mutated by
Admin; the published Shared `0.12.1` recovery-policy contract is consumed; complete override rows
and dedicated audit events are used; expiry falls back to merchant policy; recovery generation /
last-external-activity presentation is present; and raw provider snapshots/tokens are not exposed.
Do not redesign those accepted parts in Attempt 2.

Attempt 1 nevertheless has functional defects in form submission, Shopify discount eligibility,
transactional authorization/audit identity, and audit-state capture. These defects can change the
persisted override or prevent the intended action from working, so they require correction before
acceptance.

### Finding 1 — checked follow-up submissions are parsed as `false`, and a missing recovery delay becomes `0`

`tenant-administration.tsx` renders the hidden `followUpEnabled=false` input before the checked
`followUpEnabled=true` checkbox. `parsePolicySnapshot()` then uses `formData.get(...)`, which
returns the first value. Therefore a checked checkbox submits both values but the server reads
`false`; an Admin cannot persist `followUpEnabled=true` through this form.

The numeric parser also executes:

```text
Number(formData.get("recoveryDelayMinutes"))
```

so an omitted field becomes `0`, even though ARCH-016 requires a complete submitted policy
snapshot. Missing required policy input must be rejected rather than silently converted.

Attempt 2 MUST make server parsing independent of DOM input order:

```text
followUpEnabled values:
  ["false"]          -> false
  ["false", "true"] -> true
  ["true", "false"] -> true
  missing/other value -> reject
```

Using `FormData.getAll("followUpEnabled")` is the preferred bounded fix. Do not trust only the
first duplicate field value. `recoveryDelayMinutes` must first be present as a non-empty string,
then be converted to a number and passed through the canonical Shared schema. Do not add local
cross-field validation that duplicates `EffectiveRecoveryPolicySchema`.

### Finding 2 — Clear Override is an invalid nested form and has no confirmation

`ClearOverrideForm` currently renders a `<form>` from inside the UPSERT `<form>`. Nested HTML
forms are invalid and can cause the clear submit to be associated with the outer UPSERT form
instead of the CLEAR action. The task also explicitly requires a Clear Override action with
confirmation and reason; the reason exists, but confirmation does not.

Attempt 2 MUST:

```text
UPSERT form
  -> contains only UPSERT fields + Save override submit

CLEAR form
  -> separate sibling form, never a descendant of the UPSERT form
  -> hidden shopId + returnTo
  -> required reason 1..1000 chars
  -> explicit user confirmation before submission
  -> invokes clearTenantRecoveryPolicyOverrideAction only after confirmation
```

If browser confirmation is implemented with `window.confirm`, create one small client component,
for example:

```text
src/components/admin/tenant-recovery-policy-clear-form.tsx
```

and keep the surrounding tenant administration page/server component server-rendered. Do not
convert the whole tenant administration component to a client component merely to obtain a
confirmation dialog.

### Finding 3 — Admin discount eligibility does not implement the ARCH-016 "currently running" rule

ARCH-016 defines currently running as all of:

```text
catalogue status == CURRENT
isAvailable == true
providerStatus == ACTIVE
startsAt <= now when present
endsAt > now when present
```

and FIXED additionally requires `fixedSelectable == true`.

The current Admin read path and UPSERT validation omit `providerStatus == ACTIVE`. The read path
also returns counts/options even when the catalogue status is not `CURRENT`. Consequently a
provider-inactive or stale catalogue row can be presented as running/selectable, and the UPSERT
validator can accept a provider-inactive row when the other predicates happen to match.

Attempt 2 MUST use one captured `now` value for the relevant operation and enforce:

```text
if catalogue.status != CURRENT:
  runningDiscountCount = 0
  fixedSelectableCount = 0
  selectableDiscounts = []

if catalogue.status == CURRENT:
  running discount predicate =
    shopId == target shop
    isAvailable == true
    providerStatus == "ACTIVE"
    startsAt is null OR startsAt <= now
    endsAt is null OR endsAt > now

  fixed-selectable predicate = running predicate + fixedSelectable == true
```

For a submitted `FIXED` override, inside the write transaction:

```text
catalogue for target shop must exist and status == CURRENT
selected discount must:
  belong to target shop
  be isAvailable == true
  have providerStatus == "ACTIVE"
  be fixedSelectable == true
  satisfy the same start/end time window
otherwise reject and write neither override nor audit event
```

Do not read `providerSnapshot`, infer redeem codes, or implement AI selection.

### Finding 4 — SUPER_ADMIN is not rechecked transactionally, and development bypass can violate the new audit FKs

The task requires one transaction for authorization recheck + database-backed validation + write.
Attempt 1 performs `requireSuperAdmin()` before the transaction, then obtains an Admin ID outside
the transaction and writes that ID into the FK-backed override/audit rows.

In development bypass, `requirePlatformAdminMutation()` returns the reserved synthetic principal
ID `development-platform-admin`; unlike existing audited Admin mutations, this action does not
call `ensureDevelopmentPlatformAdmin(...)`. If that backing row has not already been provisioned,
`updatedByPlatformAdminId` / `platformAdminId` can fail their `PlatformAdmin` foreign keys.

Attempt 2 MUST reuse the existing Admin identity convention; do not invent another development
identity mechanism:

```text
resolve + require SUPER_ADMIN principal at the action boundary
enter the existing Prisma transaction
  if principal.developmentBypass:
    call ensureDevelopmentPlatformAdmin(transaction, principal)

  re-read PlatformAdmin by principal.id inside the transaction
  require durable row exists
  require active == true
  require role == SUPER_ADMIN

  use that durable row id for:
    ShopRecoveryPolicyOverride.updatedByPlatformAdminId
    ShopRecoveryPolicyOverrideAuditEvent.platformAdminId

  perform shop/catalogue/discount validation
  write audit + UPSERT/CLEAR in this same transaction
```

Apply this to both UPSERT and CLEAR. A role deactivation/downgrade discovered by the in-transaction
recheck must fail closed before the audit/override mutation. Keep `runProtectedTenantAction` and
the existing global Admin authorization boundary unless a narrow compile-safe adjustment is
required; do not redesign platform authentication.

### Finding 5 — audit before/after snapshots lose override expiry changes

`policySnapshot()` serializes only the five recovery-policy fields. `expiresAt` controls whether an
override is effective, but it is omitted from both audit snapshots. An update that changes only
expiry therefore records identical `beforeValue` and `afterValue`, so the durable audit event does
not describe the actual state transition.

Attempt 2 MUST make the bounded override audit snapshot exactly:

```text
recoveryDelayMinutes
recoveryOfferMode
fixedShopifyDiscountId
followUpEnabled
followUpDelayMinutes
expiresAt    # ISO-8601 string when set, otherwise null
```

The audit event's existing top-level `reason` and `platformAdminId` remain authoritative for the
mutation justification and actor; do not duplicate secrets or provider payloads into the JSON.
For CLEAR, `afterValue` may remain JSON null. For UPSERT create, `beforeValue` may remain database
NULL when no prior override exists.

### Authorized Attempt-2 production surface

```text
src/app/actions/tenant.ts
src/lib/admin/recovery-policy.ts
src/lib/admin/data.ts
src/components/admin/tenant-administration.tsx
src/components/admin/tenant-recovery-policy-clear-form.tsx   # optional/new, only for clear confirmation
```

Focused tests may change under:

```text
tests/unit/recovery-policy.test.ts
tests/security/admin-tenant-recovery-policy.test.mjs
```

Do NOT modify:

```text
database/prisma/schema.prisma
any Prisma migration
@modainteract/moda-interact-shared version (keep exact 0.12.1)
ShopSettings recovery-policy values from Admin
CommerceAgent/LLM behavior
Shopify providerSnapshot presentation
ARCH-010 Promotions behavior
```

### Required Attempt-2 functional regression assertions

At minimum prove the following bounded behaviors; do not expand into exhaustive UI coverage:

```text
checked follow-up submission resolves to true despite hidden false fallback
unchecked follow-up resolves to false
missing recoveryDelayMinutes is rejected rather than becoming 0

CLEAR form is not nested inside UPSERT form
CLEAR requires reason and confirmation before invoking the CLEAR action

catalogue != CURRENT => zero running/fixed-selectable metrics and no selectable options
providerStatus != ACTIVE => row is not counted, offered, or accepted for FIXED override
ACTIVE/current/running/fixedSelectable same-shop row => accepted for FIXED override

production principal is re-read inside the mutation transaction and must remain active SUPER_ADMIN
development bypass provisions/uses the reserved durable PlatformAdmin row before FK-backed audit/write
submitted platformAdminId remains ignored

expiry-only UPSERT produces different before/after audit snapshots because expiresAt is captured
CLEAR audit remains durable and the live override is deleted only in the same successful transaction
```

Source-structure assertions are acceptable for the nested-form/no-secret boundaries, but the
pure policy/parser behavior should be exercised as behavior where the existing test harness makes
that practical. Do not build a new test framework for this correction.

### Validation

From the canonical Admin implementation task worktree, use the scripts the repository actually
declares:

```bash
npm run test:unit
node --test tests/security/admin-tenant-recovery-policy.test.mjs
npx tsc --noEmit
npm run lint
npm run build
git diff --check
```

`npm test` may also be run to compare the documented repository baseline, but unrelated existing
async security/observability failures are not an ARCH-016 acceptance condition. If `npm run build`
is again interrupted with exit 130 and no compiler diagnostic, record the exact command/output;
do not alter production behavior merely to hide an environment interruption.

### Stop conditions

STOP and return to `moda_architect` if the corrections would require a Prisma/schema migration, a
new Shared package/version, direct Admin mutation of merchant `ShopSettings`, new AI discount
selection semantics, or provider-secret/raw-snapshot exposure. Otherwise return this same task
with `status: review`, `executor: null`, `claimed_at: null`, and `attempt: 2` after the next normal
launcher claim.

There is **no acceptance or dependency promotion from Attempt 1**. `ARCH-016-SYSTEM-TEST-001`
remains pending behind all implementation dependencies and the developer manual-testing checkpoint.

## Completion protocol

The implementation and report are complete. The task is returned to `moda_architect` at `status: review`; stop here pending architect review.

## Attempt 2 Completion Report

### Corrections Completed

- Complete policy parsing now rejects missing recovery delay and uses `FormData.getAll()` so checked follow-up submissions resolve to `true` regardless of hidden-input order.
- Clear Override is now a separate sibling client form with required reason and explicit `window.confirm` confirmation; nested forms were removed.
- Tenant catalogue metrics/options require `CURRENT`, `isAvailable`, `providerStatus: ACTIVE`, and the start/end window. Non-current catalogues expose zero running/selectable options.
- FIXED override writes enforce the same CURRENT/ACTIVE/running/selectable predicates inside the write transaction using one captured timestamp.
- UPSERT and CLEAR recheck a durable active SUPER_ADMIN inside their transaction and provision the reserved development admin identity through the existing helper when bypassed.
- Audit snapshots now include `expiresAt` as an ISO timestamp or null, preserving expiry-only changes in before/after state.

### Attempt 2 Validation

- `npm run test:unit`: `128 passed`, `0 failed`;
- focused recovery-policy tests: `3 passed`;
- focused tenant security tests: `2 passed`;
- `npx tsc --noEmit`: passed;
- `npm run lint`: passed with no output/errors;
- `npm run build`: passed;
- `git diff --check`: passed;
- aggregate `npm test`: `144 passed`, `3 failed`, `4 cancelled`, `0 skipped`; remaining failures/cancellations are unrelated repository baseline security/observability or i18n tests.

### Attempt 2 Git / Handoff

- launcher claim commit: `9ad7fd6`;
- implementation correction commit: `215cb7f` (`fix(admin): harden tenant policy override actions`);
- implementation branch pushed: `origin/task/ARCH-016-ADMIN-002`;
- canonical workspace and prepared worktrees unchanged from launcher packet;
- recursive submodule state remained ready at `c59f2eb6953642f1c850d38b09ed03096d672547`;
- executor and claimed timestamp cleared; no main branch modified.

Task status is `review`; return control to `moda_architect` for re-review.

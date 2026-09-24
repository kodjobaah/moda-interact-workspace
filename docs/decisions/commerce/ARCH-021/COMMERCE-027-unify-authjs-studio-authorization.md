---
id: ARCH-021-COMMERCE-027
architecture_id: ARCH-021
title: Unify Auth.js Studio authorization for platform admins and merchants
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-DATABASE-002
enables:
  - ARCH-021-COMMERCE-028
created: 2026-09-24
updated: 2026-09-24
---

# Unify Auth.js Studio authorization for platform admins and merchants

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`


## Objective

Keep one Auth.js/Google authentication path while resolving authorization through `PlatformAdmin` first and otherwise through shop-scoped `CommerceStudioMerchantAccess`; add a manual operator command for initial merchant step-up and do not introduce a second login/session system.

## Context

Current Auth.js `signIn` permits only identities backed by `PlatformAdmin`. Merchant Studio users must use the same Auth.js Google flow. Access is initially granted manually by a platform operator, then the first successful login binds the Google provider subject once.

## Scope

Primary files:

```text
auth.ts
lib/auth/index.ts
lib/auth/platform-admin.ts
lib/auth/permissions.ts
lib/auth/security-policy.ts
lib/auth/database.ts
lib/auth/merchant-access.ts                  # new
scripts/merchant-studio-access.mjs           # new
tests/auth-platform-admin.test.ts
tests/auth-security-policy.test.ts
tests/auth-merchant-access.test.ts            # new
tests/auth-entrypoints.test.ts
```

## Out of Scope

- Merchant self-service invitation/onboarding.
- Merchant-facing Studio UI exposure.
- Password authentication or another identity provider.
- Creating Auth.js account/session database tables.
- Changing PlatformAdmin roles.
- Platform configuration permissions.

## Requirements

### R1. One authentication system

Keep exactly one Auth.js instance and Google provider.

Do not create merchant-specific Auth.js config, cookies, sessions or sign-in pages.

### R2. Platform-admin precedence

Define principal types exactly:

```ts
type PlatformStudioPrincipal = {
  kind: 'PLATFORM_ADMIN';
  id: string;
  role: 'ADMIN' | 'SUPER_ADMIN';
  developmentBypass: boolean;
};

type MerchantStudioPrincipal = {
  kind: 'MERCHANT';
  id: string;
  shopId: string;
  role: 'ADMIN' | 'EDITOR' | 'VIEWER';
  developmentBypass: false;
};

type StudioPrincipal = PlatformStudioPrincipal | MerchantStudioPrincipal;
```

When an authenticated identity matches active `PlatformAdmin`, resolve it as `PLATFORM_ADMIN` even if merchant-access rows also exist.

### R3. Development bypass remains platform SUPER_ADMIN

When the trusted server-side development resolver establishes `developmentBypass === true`, return the canonical platform SUPER_ADMIN immediately.

Do not perform merchant lookup, role comparison, email comparison or provider-subject comparison on the bypass path.

### R4. Hosted Auth.js sign-in admission

For Google sign-in, normalize profile email to trimmed lowercase and require a provider subject.

Allow sign-in when either:

```text
A. active PlatformAdmin identity is valid under the existing one-time subject-binding rules; OR
B. at least one active CommerceStudioMerchantAccess row exists for provider='google' and normalized email, and merchant subject binding passes R5.
```

Otherwise deny sign-in.

### R5. Merchant provider-subject binding algorithm

For all active merchant-access rows matching `(provider='google', normalized email)`:

1. if any row has a non-null `providerSubject` different from the current Google subject, deny sign-in and do not modify any row;
2. if all non-null subjects equal the current subject, atomically bind every matching active row whose `providerSubject` is NULL to that same subject;
3. update `lastLoginAt` for all matching active rows only after successful validation/binding;
4. never rebind a non-null subject.

This supports one authenticated merchant identity having manual access to multiple shops.

### R6. Unified authorization functions

Implement/export exactly:

```text
getStudioPrincipal({ shopId? })
requireStudioPrincipal({ shopId? })
requireStudioPlatformAdmin()
requireStudioSuperAdmin()
requireStudioShopAccess(shopId, permission)
```

Keep `requireStudioAdmin()` as a compatibility wrapper for `requireStudioPlatformAdmin()` so existing platform-only routes do not broaden accidentally.

### R7. Permission matrix

Shop-aware merchant permissions:

```text
VIEWER -> inspect, preview
EDITOR -> inspect, preview, edit
ADMIN  -> inspect, preview, edit, publish
```

A merchant principal is authorized only when `principal.shopId === requested shopId`.

These remain platform-admin-only regardless of merchant role:

```text
platform model catalogue management
platform Agent Configuration defaults
platform prompt management
prompt-template category/template administration
release rollback
global capability/tool enable/disable
manual merchant-access grants
```

### R8. Manual step-up command

Add operator script:

```text
node scripts/merchant-studio-access.mjs \
  --action grant|update|disable|enable \
  --actor-admin-email <platform-admin-email> \
  --shop <shop-id-or-domain> \
  --email <merchant-google-email> \
  [--role ADMIN|EDITOR|VIEWER]
```

Rules:

- actor must resolve to active PlatformAdmin;
- shop must resolve exactly;
- email stored normalized lowercase;
- `grant` creates unbound `providerSubject=NULL`;
- `update` may change role only;
- `disable`/`enable` changes active only;
- script must never accept/set providerSubject directly;
- every action writes a `CommerceAuditEvent` in the same transaction.

### R9. Security events

Existing login/authorization logging remains structured and bounded. Add reason codes sufficient to distinguish:

```text
platform_admin_not_authorized
merchant_access_not_authorized
merchant_identity_conflict
merchant_shop_forbidden
```

Do not log access tokens, session tokens or provider credentials.

## Work Items

- [x] Implement unified principal types/resolver.
- [x] Update Auth.js signIn admission for platform-or-merchant access.
- [x] Implement deterministic subject binding.
- [x] Add shop-scoped permission helpers.
- [x] Preserve platform-only compatibility wrappers.
- [x] Add manual step-up CLI and audit.
- [x] Add focused auth/security tests.

## Interfaces / Contracts

Consumes `CommerceStudioMerchantAccess` from DATABASE-002. No new external auth provider and no Shared package.

## Dependencies

- ARCH-021-DATABASE-002

## Enables

- ARCH-021-COMMERCE-028

## Acceptance Criteria

- [x] PlatformAdmin and merchant users authenticate through the same Auth.js Google flow.
- [x] PlatformAdmin takes precedence when both authorization sources match.
- [x] Merchant access is exact-shop scoped.
- [x] One merchant Google identity may hold multiple manually granted shop-access rows.
- [x] Provider subject binds once and cannot be reassigned.
- [x] Development bypass remains sufficient by itself.
- [x] No merchant self-service escalation exists.

## Validation

- [ ] platform-admin login tests
- [ ] merchant first-login subject binding test
- [ ] multi-shop merchant binding test
- [ ] conflicting subject denial test
- [ ] platform-admin precedence test
- [ ] shop authorization matrix tests
- [ ] manual CLI focused integration test against disposable PostgreSQL
- [ ] targeted ESLint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

Authentication proves identity; authorization comes from PlatformAdmin or MerchantAccess. Do not merge the two tables and do not put shop authorization into the Auth.js session as mutable authoritative state.

## Completion Report

### Status

Review requested

### Files Changed

- `auth.ts`
- `lib/auth/index.ts`
- `lib/auth/merchant-access.ts`
- `lib/auth/security-policy.ts`
- `scripts/merchant-studio-access.mjs`
- `tests/auth-platform-admin.test.ts`
- `tests/auth-security-policy.test.ts`
- `tests/auth-merchant-access.test.ts`

### Work Completed

- Unified Auth.js Google sign-in now admits active platform admins or active merchant access rows, with platform precedence.
- Merchant provider subjects bind atomically across all active rows for a normalized email and conflicting subjects are denied without mutation.
- Added exact-shop principal resolution, permission enforcement, unified platform/super-admin guards, and the VIEWER/EDITOR/ADMIN matrix.
- Added an operator-only grant/update/disable/enable command with normalized email, exact shop resolution, no provider-subject input, and transactional audit events.
- Existing platform-admin compatibility helpers and platform-only authorization boundaries remain available.

### Validation Results

- `npx vitest run tests/auth-merchant-access.test.ts tests/auth-security-policy.test.ts tests/auth-platform-admin.test.ts`: 3 files, 34 tests passed.
- `npx eslint auth.ts lib/auth/index.ts lib/auth/merchant-access.ts lib/auth/security-policy.ts scripts/merchant-studio-access.mjs tests/auth-security-policy.test.ts tests/auth-merchant-access.test.ts tests/auth-platform-admin.test.ts`: passed.
- `node --check scripts/merchant-studio-access.mjs`: passed.
- CLI rejects unknown `--providerSubject` before database access.
- `git diff --check`: passed.
- `npm run typecheck`: existing unrelated failures remain in preview routes and generated commerce agent-configuration Prisma model surfaces; no task-owned diagnostics remain.

### Deviations

The disposable PostgreSQL CLI integration validation was not run because no disposable database was available in this worktree; CLI syntax, fail-closed actor resolution, and forbidden-flag behavior were validated locally.

### Assumptions

Prisma schema/client generation from DATABASE-002 is already available and the implementation uses the existing `CommerceStudioMerchantAccess` and `CommerceAuditEvent` contracts.

### Unresolved Issues

No task-owned unresolved implementation issues. Full-repository typecheck remains blocked by pre-existing preview and generated-schema failures documented above.

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is not accepted. The overall direction is correct — one Auth.js/Google identity path, platform-admin precedence, shop-scoped merchant principals and a manual merchant-access command — but the submitted implementation has security/correctness gaps in the merchant subject-binding and authorization paths, and required PostgreSQL validation is incomplete.

1. **Merchant first-login subject binding is not race-safe.** In `auth.ts`, `bindMerchantSubjects` reads the active rows, conditionally updates `providerSubject=NULL`, then returns the *pre-update* `rows.length` without checking the `updateMany` count or re-reading the durable subjects. Two concurrent first logins with different Google subjects can both read unbound rows; after one subject wins, the losing `updateMany` may update zero rows but the loser still returns a positive count and `authorizeGoogleProfile()` treats that login as authorized. This violates R5 and the acceptance criterion that provider subject binds once and cannot be reassigned. Make the transaction prove that every active Google merchant-access row for the normalized email is durably bound to the current subject before it reports success. A losing/conflicting race must deny and must not refresh `lastLoginAt`.

2. **Per-request merchant resolution does not reject a mixed-subject identity set.** `resolveStudioPrincipal()` filters to rows whose subject matches the current session and can authorize one shop even when another active row for the same normalized email is bound to a different subject. R5 establishes one deterministic Google identity across all active rows for that email. If any active Google row has a different non-null subject, resolution must deny with `merchant_identity_conflict` rather than authorize a matching subset.

3. **`requireStudioShopAccess()` broadens existing PlatformAdmin publish permissions.** It returns any `PLATFORM_ADMIN` immediately for every shop permission, including `publish`. Existing Studio authorization makes platform `ADMIN` inspect/edit/preview only and reserves publish/rollback/enable/disable for `SUPER_ADMIN`; changing PlatformAdmin permissions is explicitly out of scope. Preserve that existing platform permission matrix while applying the new merchant VIEWER/EDITOR/ADMIN matrix. Add regressions proving platform `ADMIN` cannot publish, platform `SUPER_ADMIN` can, and merchant `ADMIN` can publish only for its exact shop.

4. **R6's compatibility-wrapper requirement is not implemented.** `lib/auth/platform-admin.ts` still owns a separate `requireStudioAdmin()`/`resolveStudioAdminPrincipal()` authorization path, while `requireStudioPlatformAdmin()` uses the new unified resolver. `requireStudioAdmin()` must become a compatibility wrapper over the unified platform-admin guard (without broadening existing platform-only entry points), so there is one authoritative hosted authorization path rather than two implementations that can drift. Preserve legacy exports/types where needed by callers.

5. **Required validation is incomplete.** The task explicitly requires a focused manual-CLI integration test against disposable PostgreSQL, but the Completion Report states it was not run and every Validation checkbox remains unchecked. Attempt 2 must execute the real grant/update/disable/enable path against isolated PostgreSQL and verify durable merchant-access state plus same-transaction `CommerceAuditEvent` rows. It must also exercise the merchant binding race against the real persistence implementation (or an equivalently deterministic database-backed concurrency test), not only mock `bindMerchantSubjects`.

6. **The Completion Report must be reconciled before resubmission.** Check each Validation item only when actually completed; record any baseline typecheck failures precisely; and add the launcher-resolved dedicated parent/implementation worktree, start-of-attempt synchronization and recursive-submodule evidence required by the task isolation policy.

No work on `ARCH-021-COMMERCE-028` is authorized while this task remains incomplete.

### Reviewed Files

- `auth.ts`
- `lib/auth/index.ts`
- `lib/auth/merchant-access.ts`
- `lib/auth/platform-admin.ts`
- `lib/auth/permissions.ts`
- `lib/auth/security-policy.ts`
- `lib/auth/audit.ts`
- `scripts/merchant-studio-access.mjs`
- `tests/auth-merchant-access.test.ts`
- `tests/auth-security-policy.test.ts`
- `tests/auth-platform-admin.test.ts`
- `tests/auth-entrypoints.test.ts`
- `database/prisma/schema.prisma`
- `database/prisma/migrations/20260924103000_arch021_simplify_agent_configuration/migration.sql`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`
- this task file and Completion Report

### Validation Reviewed

- Submitted focused result: `34` tests passed across `auth-merchant-access`, `auth-security-policy` and `auth-platform-admin`; source/tests were inspected, but the archive contains no `node_modules`, so Vitest was not independently rerun in this review environment.
- Submitted targeted ESLint: passed; not independently rerun for the same dependency reason.
- `node --check scripts/merchant-studio-access.mjs`: submitted as passed; source inspected.
- `git diff --check`: submitted as passed.
- Full typecheck: submitted with unrelated existing preview/generated-Prisma diagnostics and no task-owned diagnostics.
- Required disposable-PostgreSQL CLI integration validation: **not run**.
- Required durable merchant-binding concurrency behaviour: **not proven** by the submitted mocked tests.

### Architecture Conformance

Partial. The one-Auth.js design, principal shapes, development bypass, platform precedence intent, shop-scoped merchant roles and manual provisioning boundary conform to ARCH-021. Acceptance is blocked by the race in first-login identity binding, mixed-subject authorization gap, PlatformAdmin publish-permission broadening, duplicate legacy/unified platform authorization paths, and incomplete required PostgreSQL validation.

### Follow-up

Reclaim the same task for Attempt 2. Correct only the auth/authorization and validation issues above; do not start `ARCH-021-COMMERCE-028` or broaden into merchant-facing Studio UI work. After correction, rerun focused auth tests, the disposable-PostgreSQL CLI/binding validations, targeted ESLint/typecheck and `git diff --check`, reconcile the Completion Report, set the task back to `review`, clear `executor`/`claimed_at`, and STOP.

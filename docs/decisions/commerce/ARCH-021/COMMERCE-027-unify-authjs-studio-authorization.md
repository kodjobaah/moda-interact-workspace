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
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-09-24T13:20:23Z
attempt: 3
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
requireStudioPlatformRole(minimumRole)
requireStudioPlatformAdmin()
requireStudioSuperAdmin()
requireStudioShopRole(shopId, minimumRole)
requireStudioShopAccess(shopId, permission)
```

Keep `requireStudioAdmin()` as a compatibility wrapper for `requireStudioPlatformAdmin()` so existing platform-only routes do not broaden accidentally.

### R7. Hierarchical authorization model

Authorization is hierarchical. The canonical effective rank order is exactly:

```text
PLATFORM_SUPER_ADMIN
        >
PLATFORM_ADMIN
        >
MERCHANT_ADMIN
        >
MERCHANT_EDITOR
        >
MERCHANT_VIEWER
```

The persisted database roles remain unchanged:

```text
PlatformAdmin.role:                 ADMIN | SUPER_ADMIN
CommerceStudioMerchantAccess.role:  VIEWER | EDITOR | ADMIN
```

Do **not** add a new persisted combined-role enum or another authorization table. The combined rank exists only in the authorization layer.

The exact numeric levels used for comparison must be centralized in one module/helper and must be equivalent to:

```text
MERCHANT_VIEWER       = 10
MERCHANT_EDITOR       = 20
MERCHANT_ADMIN        = 30
PLATFORM_ADMIN        = 40
PLATFORM_SUPER_ADMIN  = 50
```

A higher role satisfies every lower minimum-role requirement subject to the scope rules below. Do not scatter direct role-equality checks through callers when a minimum-role helper expresses the requirement.

#### R7.1 Platform scope

Platform principals are global.

```text
requireStudioPlatformRole('ADMIN')
    PLATFORM_ADMIN        -> allow
    PLATFORM_SUPER_ADMIN  -> allow
    MERCHANT_*            -> deny

requireStudioPlatformRole('SUPER_ADMIN')
    PLATFORM_SUPER_ADMIN  -> allow
    PLATFORM_ADMIN        -> deny
    MERCHANT_*            -> deny
```

Keep these compatibility wrappers and make them delegate to the canonical hierarchy:

```text
requireStudioPlatformAdmin() -> requireStudioPlatformRole('ADMIN')
requireStudioSuperAdmin()    -> requireStudioPlatformRole('SUPER_ADMIN')
requireStudioAdmin()         -> requireStudioPlatformAdmin() compatibility path
```

#### R7.2 Shop scope

Shop actions use a minimum merchant authority:

```text
inspect  -> VIEWER
preview  -> VIEWER
edit     -> EDITOR
publish  -> ADMIN
```

Implement/export exactly:

```text
requireStudioShopRole(shopId, minimumRole)
```

with these semantics:

```text
PLATFORM_SUPER_ADMIN -> allow for every shop and every merchant minimum role
PLATFORM_ADMIN       -> allow for every shop and every merchant minimum role
MERCHANT_ADMIN       -> allow only for its requested shop; satisfies VIEWER/EDITOR/ADMIN
MERCHANT_EDITOR      -> allow only for its requested shop; satisfies VIEWER/EDITOR only
MERCHANT_VIEWER      -> allow only for its requested shop; satisfies VIEWER only
```

`requireStudioShopAccess(shopId, permission)` remains a compatibility API, but it must map the permission to the minimum merchant role above and delegate to `requireStudioShopRole`. It must not contain a separate PlatformAdmin permission matrix.

Therefore a platform `ADMIN` **does** satisfy shop `publish` because shop publish requires `MERCHANT_ADMIN`, which is below `PLATFORM_ADMIN`.

#### R7.3 Platform-only operations

The hierarchy does **not** mean every operation becomes a shop operation. The following remain platform-scoped and must use a platform-role requirement:

```text
platform model catalogue                         -> minimum PLATFORM_ADMIN
platform prompt-template/category administration -> minimum PLATFORM_ADMIN
platform default model/prompt                     -> minimum PLATFORM_ADMIN
platform release activation/rollback              -> PLATFORM_SUPER_ADMIN
globally sensitive capability/tool enable/disable -> PLATFORM_SUPER_ADMIN
PlatformAdmin membership/role administration      -> PLATFORM_SUPER_ADMIN
global merchant-access override/administration    -> PLATFORM_SUPER_ADMIN
```

`requireStudioPermission()` is a legacy **platform-action** compatibility helper. If retained, it must delegate to the same centralized platform-role comparison and must not be used for shop publication. Do not use its generic `publish` permission to decide `requireStudioShopAccess(..., 'publish')`.

#### R7.4 Platform precedence

If an authenticated identity has both an active `PlatformAdmin` row and merchant-access rows, resolve the platform principal and stop. Do not downgrade it to a merchant role for a requested shop.

#### R7.5 Multiple merchant shops

Do not make one merchant `shopId` or role authoritative session state. Authentication proves identity; each shop authorization is evaluated against the requested `shopId`. The same identity may therefore be `ADMIN` for one shop, `EDITOR` for another and `VIEWER` for a third.

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
- [ ] Centralize role levels and minimum-role comparison for platform and merchant roles.
- [ ] Add `requireStudioPlatformRole(minimumRole)` and `requireStudioShopRole(shopId, minimumRole)`.
- [ ] Make `requireStudioPlatformAdmin`, `requireStudioSuperAdmin`, `requireStudioShopAccess` and `requireStudioAdmin` delegate to the canonical hierarchy.
- [ ] Remove the separate `studioPlatformPermissionAllowed()` shop-publish rule; no parallel platform-vs-shop permission matrix may remain.
- [ ] Update focused authorization regressions for hierarchy, platform precedence and multi-shop scope.
- [ ] Verify no task-owned caller still implements an exact-role check where the new minimum-role helper is required.

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
- [ ] Platform `SUPER_ADMIN` satisfies every lower platform/shop requirement.
- [ ] Platform `ADMIN` satisfies every merchant shop requirement, including shop `publish`, for any shop.
- [ ] Platform `ADMIN` does not satisfy `PLATFORM_SUPER_ADMIN` requirements.
- [ ] Merchant `ADMIN`/`EDITOR`/`VIEWER` inherit downward only within an authorized requested shop.
- [ ] PlatformAdmin precedence prevents an identity from being downgraded by merchant-access rows.
- [ ] Shop authorization is request-scoped; no single shop role is stored as authoritative Auth.js session state.
- [ ] Existing one-time subject binding, mixed-subject rejection and CLI provisioning behaviour remain unchanged.

## Validation

- [x] platform-admin login tests
- [x] merchant first-login subject binding test
- [x] multi-shop merchant binding test
- [x] conflicting subject denial test
- [x] platform-admin precedence test
- [x] shop authorization matrix tests
- [x] manual CLI focused integration test against disposable PostgreSQL
- [x] targeted ESLint; full typecheck has documented baseline failures
- [x] `git diff --check`
- [ ] hierarchy unit matrix: all five effective levels against platform and shop minimum roles
- [ ] `requireStudioShopRole`: platform ADMIN and SUPER_ADMIN publish any shop; merchant ADMIN publishes exact shop only
- [ ] `requireStudioPlatformRole`: platform ADMIN satisfies ADMIN but not SUPER_ADMIN; merchants satisfy neither
- [ ] compatibility-wrapper tests prove `requireStudioShopAccess` and existing platform wrappers delegate to canonical hierarchy
- [ ] regression search: no `studioPlatformPermissionAllowed` implementation/export/call remains unless retained solely as a thin delegating compatibility alias
- [ ] targeted auth Vitest suite passes
- [ ] disposable PostgreSQL auth/binding tests from Attempt 2 still pass unchanged
- [ ] targeted ESLint passes
- [ ] full typecheck run; any nonzero result must contain no task-owned auth diagnostics
- [ ] `git diff --check` after Attempt 3 changes

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

Authentication proves identity; authorization comes from PlatformAdmin or MerchantAccess. Do not merge the two tables and do not put shop authorization into the Auth.js session as mutable authoritative state.

## Completion Report

### Status

Review requested for Attempt 2

### Execution Evidence

- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-027`, branch `task/ARCH-021-COMMERCE-027`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-027`, branch `task/ARCH-021-COMMERCE-027`.
- Attempt 2 claim commit: `93460e3663590ecc63e79d47e5dfec0a2254432b`.
- Start-of-attempt preparation synchronization: parent `a546fa126e7df78c621f78364ad745b5c13eeaea`; implementation `ddfa2501d952598511659f5e639a8b13bfabae66`; both were already current, so synchronization was not needed.
- Recursive submodule synchronization/update passed; database submodule is at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Published implementation commit: `ab6595a86077bdc1ede5925caf7a70ed98f20e1b`, pushed to `origin/task/ARCH-021-COMMERCE-027`.

### Files Changed

- `auth.ts`
- `lib/auth/index.ts`
- `lib/auth/merchant-access.ts`
- `lib/auth/merchant-binding.ts`
- `lib/auth/platform-admin.ts`
- `lib/auth/security-policy.ts`
- `scripts/merchant-studio-access.mjs`
- `tests/auth-platform-admin.test.ts`
- `tests/auth-security-policy.test.ts`
- `tests/auth-merchant-access.test.ts`
- `tests/auth-merchant-access-postgres.test.ts`

### Work Completed

- Unified Auth.js Google sign-in now admits active platform admins or active merchant access rows, with platform precedence.
- Merchant provider subjects now bind atomically across all active rows for a normalized email; a durable re-read rejects losing/conflicting races without refreshing `lastLoginAt`.
- Principal resolution rejects mixed-subject active merchant rows before shop selection; exact-shop access and the VIEWER/EDITOR/ADMIN matrix remain enforced.
- Platform `ADMIN` cannot publish while platform `SUPER_ADMIN` can; merchant `ADMIN` can publish only for its exact shop.
- `requireStudioAdmin()` is now a compatibility wrapper over the unified platform-admin guard.
- Added an operator-only grant/update/disable/enable command with normalized email, exact shop resolution, no provider-subject input, and transactional audit events.
- Added a real PostgreSQL integration harness covering CLI grant/update/disable/enable audit durability and concurrent merchant subject binding.

### Validation Results

- `npx vitest run tests/auth-merchant-access.test.ts tests/auth-security-policy.test.ts tests/auth-platform-admin.test.ts tests/auth-merchant-access-postgres.test.ts`: 3 files passed, 1 opt-in PostgreSQL file skipped without `COMMERCE_AUTH_POSTGRES=1`, 38 tests passed and 2 skipped.
- Disposable PostgreSQL proof: Docker `postgres:16`, `prisma db push --schema database/prisma/schema.prisma --skip-generate`, then `COMMERCE_AUTH_POSTGRES=1 DATABASE_URL=... npx vitest run tests/auth-merchant-access-postgres.test.ts`: 1 file and 2 tests passed, covering durable CLI state/audits and concurrent binding.
- `npx eslint auth.ts lib/auth/index.ts lib/auth/merchant-access.ts lib/auth/merchant-binding.ts lib/auth/platform-admin.ts lib/auth/security-policy.ts scripts/merchant-studio-access.mjs tests/auth-security-policy.test.ts tests/auth-merchant-access.test.ts tests/auth-merchant-access-postgres.test.ts tests/auth-platform-admin.test.ts tests/auth-entrypoints.test.ts`: passed with no warnings.
- `node --check scripts/merchant-studio-access.mjs`: passed.
- CLI rejects unknown `--providerSubject` before database access.
- `git diff --check`: passed.
- `npm run typecheck`: nonzero from existing sibling/baseline diagnostics in `src/commerce/agent-configuration/prompt-service.ts`, `src/commerce/agent-configuration/prompt-template-service.ts`, agent-configuration model/prompt PostgreSQL and production tests, `tests/c20-integration-fixture.test.ts`, `tests/connections-production.test.ts`, `tests/external-tools-ui.test.tsx`, `tests/external-wiring.test.ts`, and `tests/local-external-mcp-diagnostic.test.ts`; no task-owned auth diagnostics remain.
- `tests/auth-entrypoints.test.ts` retains an unrelated MCP route assertion drift (`createMcpService` expected, route now uses `getCommerceBackend`) and was not changed.

### Deviations

The PostgreSQL integration test is opt-in and uses an isolated disposable database. The implementation worktree's normal focused run skips it without the opt-in environment, while the explicit Docker-backed run passed both tests.

### Assumptions

Prisma schema/client generation from DATABASE-002 is already available and the implementation uses the existing `CommerceStudioMerchantAccess` and `CommerceAuditEvent` contracts.

### Unresolved Issues

No task-owned unresolved implementation issues. Full-repository typecheck remains blocked by the pre-existing diagnostics documented above; the unrelated MCP entrypoint assertion drift remains outside this task.

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 resolved the previously requested merchant subject-binding race, mixed-subject rejection, compatibility-wrapper drift and PostgreSQL validation. Those corrections are retained. The task is returned to Ready because the authoritative authorization model has now been clarified: Studio roles are hierarchical, with platform roles above merchant roles and merchant scope enforced per requested shop.

The next authorized claim is **Attempt 3**. This is a bounded authorization correction, not a redesign. Preserve all accepted Attempt 2 identity-binding and CLI behaviour.

#### Attempt 3 deterministic correction contract

Execute the following in order. Do not substitute a different authorization model.

1. **Read before editing**

   Re-read this entire task, the parent ARCH-021 authorization-hierarchy section, and these existing task-owned files before making source changes:

   ```text
   lib/auth/merchant-access.ts
   lib/auth/platform-admin.ts
   lib/auth/permissions.ts
   lib/auth/index.ts
   tests/auth-merchant-access.test.ts
   tests/auth-platform-admin.test.ts
   tests/auth-permissions.test.ts
   tests/auth-security-policy.test.ts
   tests/auth-merchant-access-postgres.test.ts
   ```

   Do not modify Agent Configuration service/action files owned by COMMERCE-025/026 during this task. This task establishes the canonical authorization helpers those tasks must consume.

2. **Centralize role comparison**

   Add one canonical role-level representation in the auth layer equivalent to:

   ```text
   MERCHANT_VIEWER       10
   MERCHANT_EDITOR       20
   MERCHANT_ADMIN        30
   PLATFORM_ADMIN        40
   PLATFORM_SUPER_ADMIN  50
   ```

   The numeric values are comparison implementation details only. Do not add them to the database, Auth.js session, Prisma schema or merchant-access records.

   Add pure comparison helpers so role ordering is not reimplemented by callers. Direct `role === ...` is allowed only where testing an identity kind or an operation explicitly requiring the exact top role is clearer than a minimum-role call; ordinary authorization must use the central minimum-role comparison.

3. **Implement the canonical platform-role helper**

   Export:

   ```ts
   requireStudioPlatformRole(minimumRole: 'ADMIN' | 'SUPER_ADMIN')
   ```

   Required outcomes:

   ```text
   actual PLATFORM_ADMIN, minimum ADMIN         -> allow
   actual PLATFORM_SUPER_ADMIN, minimum ADMIN   -> allow
   actual PLATFORM_ADMIN, minimum SUPER_ADMIN   -> deny
   actual PLATFORM_SUPER_ADMIN, minimum SUPER_ADMIN -> allow
   any MERCHANT principal                       -> deny
   ```

   `requireStudioPlatformAdmin()` must delegate to `requireStudioPlatformRole('ADMIN')`.
   `requireStudioSuperAdmin()` must delegate to `requireStudioPlatformRole('SUPER_ADMIN')`.
   `requireStudioAdmin()` remains the legacy shape adapter over `requireStudioPlatformAdmin()` and must not perform a second authorization lookup.

4. **Implement the canonical shop-role helper**

   Export:

   ```ts
   requireStudioShopRole(
     shopId: string,
     minimumRole: 'VIEWER' | 'EDITOR' | 'ADMIN',
   )
   ```

   Required outcomes:

   ```text
   PLATFORM_SUPER_ADMIN -> allow any shop / VIEWER|EDITOR|ADMIN
   PLATFORM_ADMIN       -> allow any shop / VIEWER|EDITOR|ADMIN

   MERCHANT_ADMIN       -> allow exact shop / VIEWER|EDITOR|ADMIN
   MERCHANT_EDITOR      -> allow exact shop / VIEWER|EDITOR; deny ADMIN
   MERCHANT_VIEWER      -> allow exact shop / VIEWER; deny EDITOR|ADMIN

   any merchant role on a different shop -> deny
   ```

   The resolver must continue to give an active PlatformAdmin precedence before merchant lookup. Do not query merchant access after a valid PlatformAdmin has resolved.

5. **Make permission compatibility delegate; do not keep a parallel matrix**

   `requireStudioShopAccess(shopId, permission)` remains for existing callers and must perform only this mapping:

   ```text
   inspect -> VIEWER
   preview -> VIEWER
   edit    -> EDITOR
   publish -> ADMIN
   ```

   It must then call/delegate to `requireStudioShopRole`.

   Remove the current rule that treats platform `ADMIN` as unable to perform shop `publish`. Platform `ADMIN` must satisfy `MERCHANT_ADMIN` shop authority globally.

   Remove `studioPlatformPermissionAllowed()` as an independent authorization implementation. If a compatibility export is demonstrably required by an existing caller, it may remain only as a thin wrapper over the canonical role comparison; it must not contain a second permission matrix.

6. **Keep platform-only privileged operations distinct from shop publication**

   Do not interpret shop `publish` as platform release activation. Platform-only operations must continue to use platform-role checks. The authoritative minimum authority is:

   ```text
   platform catalogue/templates/default configuration -> PLATFORM_ADMIN
   platform release activation/rollback                -> PLATFORM_SUPER_ADMIN
   global sensitive capability enable/disable          -> PLATFORM_SUPER_ADMIN
   PlatformAdmin membership/role administration        -> PLATFORM_SUPER_ADMIN
   global merchant-access override                      -> PLATFORM_SUPER_ADMIN
   ```

   `requireStudioPermission()` is a legacy platform-action helper. If retained, make its role comparison use the same canonical hierarchy. Do not call it from `requireStudioShopAccess` and do not use its generic `publish` value to authorize shop publication.

7. **Preserve accepted identity semantics exactly**

   Do not alter the accepted Attempt 2 behaviour for:

   ```text
   one Auth.js Google path
   development bypass -> PLATFORM_SUPER_ADMIN
   PlatformAdmin precedence
   merchant one-time providerSubject binding
   concurrent first-login single-winner behaviour
   mixed-subject rejection
   lastLoginAt update ordering
   multi-shop merchant access
   manual grant/update/disable/enable CLI
   audit durability
   ```

8. **Required tests — exact regressions**

   Add/modify tests to prove at least:

   ```text
   platform SUPER_ADMIN + shop VIEWER requirement -> allow
   platform SUPER_ADMIN + shop ADMIN requirement  -> allow
   platform ADMIN + shop VIEWER requirement       -> allow
   platform ADMIN + shop EDITOR requirement       -> allow
   platform ADMIN + shop ADMIN requirement        -> allow
   platform ADMIN + shop publish compatibility    -> allow

   merchant ADMIN + own shop ADMIN requirement    -> allow
   merchant ADMIN + other shop VIEWER requirement -> deny
   merchant EDITOR + own shop EDITOR requirement  -> allow
   merchant EDITOR + own shop ADMIN requirement   -> deny
   merchant VIEWER + own shop VIEWER requirement  -> allow
   merchant VIEWER + own shop EDITOR requirement  -> deny

   platform ADMIN + platform ADMIN requirement       -> allow
   platform SUPER_ADMIN + platform ADMIN requirement -> allow
   platform ADMIN + platform SUPER_ADMIN requirement -> deny
   merchant ADMIN + platform ADMIN requirement       -> deny
   ```

   Replace the existing regression that says `platform ADMIN cannot publish` with the correct shop-scoped assertion that platform `ADMIN` **can** satisfy shop `publish`.

   Keep the Attempt 2 PostgreSQL binding/CLI tests and rerun them without weakening or skipping their explicit disposable-PostgreSQL proof.

9. **Deterministic source audit before handoff**

   Run repository searches and record the results in the Completion Report:

   ```bash
   rg -n "studioPlatformPermissionAllowed|studioShopPermissionAllowed|requireStudioShopAccess|requireStudioShopRole|requireStudioPlatformRole|role === 'SUPER_ADMIN'|role === 'ADMIN'" \
     lib/auth tests/auth-*.test.ts
   ```

   Inspect every hit. There must be no second task-owned shop authorization matrix and no stale assertion that platform `ADMIN` is below merchant `ADMIN`. Exact-role comparisons retained for identity-shape/adaptation purposes must be listed and justified in the Completion Report.

10. **Validation and stop condition**

    Run the focused auth tests, explicit disposable-PostgreSQL auth tests, targeted ESLint, full typecheck, and `git diff --check`. A known unrelated typecheck baseline may remain nonzero only if no changed/task-owned auth file appears in the diagnostics.

    Update every Work Item, Acceptance Criterion and Validation checkbox truthfully. Record the launcher-resolved parent/implementation worktrees, start-of-attempt synchronization, recursive submodule state, implementation commit and parent report commit.

    Then set:

    ```yaml
    status: review
    executor: null
    claimed_at: null
    ```

    return the Completion Report to `moda_architect` and **STOP**. Do not start `ARCH-021-COMMERCE-028`.

### Reviewed Files

- `lib/auth/merchant-access.ts`
- `lib/auth/platform-admin.ts`
- `lib/auth/permissions.ts`
- `lib/auth/index.ts`
- `tests/auth-merchant-access.test.ts`
- `tests/auth-platform-admin.test.ts`
- `tests/auth-permissions.test.ts`
- `tests/auth-security-policy.test.ts`
- `tests/auth-merchant-access-postgres.test.ts`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`
- this task file and Attempt 2 Completion Report

### Validation Reviewed

Attempt 2's 38 focused tests, two explicit disposable-PostgreSQL tests, ESLint, syntax and diff checks are accepted as evidence for the identity-binding/CLI corrections. They do not validate the newly clarified hierarchical authorization rule because the submitted tests explicitly assert the opposite platform-ADMIN shop-publish behaviour. Attempt 3 must run the hierarchy regressions above while preserving the accepted PostgreSQL evidence.

### Architecture Conformance

Partial. Attempt 2 conforms on authentication, PlatformAdmin precedence, merchant subject binding, mixed-subject rejection, multi-shop persistence and manual provisioning. The remaining non-conformance is the authorization ordering: the implementation currently treats platform `ADMIN` as lower than merchant `ADMIN` for shop publication, contrary to the clarified hierarchy.

### Follow-up

Reclaim this same task for Attempt 3. No new task is required. `ARCH-021-COMMERCE-028` remains gated until COMMERCE-025, COMMERCE-026 and this task are Complete.

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
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 5
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

- actor must resolve to an active `PlatformAdmin` whose role is `SUPER_ADMIN`; platform `ADMIN` must be rejected;
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
- [x] Centralize role levels and minimum-role comparison for platform and merchant roles.
- [x] Add `requireStudioPlatformRole(minimumRole)` and `requireStudioShopRole(shopId, minimumRole)`.
- [x] Make `requireStudioPlatformAdmin`, `requireStudioSuperAdmin`, `requireStudioShopAccess` and `requireStudioAdmin` delegate to the canonical hierarchy.
- [x] Remove the separate `studioPlatformPermissionAllowed()` shop-publish rule; no parallel platform-vs-shop permission matrix remains.
- [x] Update focused authorization regressions for hierarchy, platform precedence and multi-shop scope.
- [x] Verify no task-owned caller still implements an exact-role check where the new minimum-role helper is required.
- [x] Restrict the manual merchant-access CLI to active `PLATFORM_SUPER_ADMIN`; reject platform `ADMIN` before any merchant-access mutation.

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
- [x] Platform `SUPER_ADMIN` satisfies every lower platform/shop requirement.
- [x] Platform `ADMIN` satisfies every merchant shop requirement, including shop `publish`, for any shop.
- [x] Platform `ADMIN` does not satisfy `PLATFORM_SUPER_ADMIN` requirements.
- [x] Merchant `ADMIN`/`EDITOR`/`VIEWER` inherit downward only within an authorized requested shop.
- [x] PlatformAdmin precedence prevents an identity from being downgraded by merchant-access rows.
- [x] Shop authorization is request-scoped; no single shop role is stored as authoritative Auth.js session state.
- [x] Existing one-time subject binding, mixed-subject rejection and CLI provisioning behaviour remain unchanged.
- [x] Manual merchant-access grant/update/disable/enable requires `PLATFORM_SUPER_ADMIN`; platform `ADMIN` cannot administer merchant access globally.

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
- [x] hierarchy unit matrix: all five effective levels against platform and shop minimum roles
- [x] `requireStudioShopRole`: platform ADMIN and SUPER_ADMIN publish any shop; merchant ADMIN publishes exact shop only
- [x] `requireStudioPlatformRole`: platform ADMIN satisfies ADMIN but not SUPER_ADMIN; merchants satisfy neither
- [x] compatibility-wrapper tests prove `requireStudioShopAccess` and existing platform wrappers delegate to canonical hierarchy
- [x] regression search: no `studioPlatformPermissionAllowed` implementation/export/call remains
- [x] targeted auth Vitest suite passes: 5 files, 62 tests
- [x] disposable PostgreSQL auth/binding tests pass: 1 file, 3 tests, 0 failed, 0 skipped, no hook failure or timeout
- [x] targeted ESLint passes
- [x] full typecheck run; nonzero result contains no task-owned auth diagnostics
- [x] `git diff --check` after Attempt 4 changes
- [x] CLI authorization regression proves platform `ADMIN` is denied and `SUPER_ADMIN` is allowed for merchant-access administration.
- [x] PostgreSQL CLI lifecycle proof still passes with the `SUPER_ADMIN` actor requirement.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

Authentication proves identity; authorization comes from PlatformAdmin or MerchantAccess. Do not merge the two tables and do not put shop authorization into the Auth.js session as mutable authoritative state.

## Completion Report

### Status

Ready for Review

### Execution Evidence

- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-027`, branch `task/ARCH-021-COMMERCE-027`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-027`, branch `task/ARCH-021-COMMERCE-027`.
- Attempt 4 launcher claim commit: `23067a4e9ec21a96ffd160eb62f3d7fd2bd08bae`, pushed to `origin/task/ARCH-021-COMMERCE-027`.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-027`, branch `task/ARCH-021-COMMERCE-027`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-027`, branch `task/ARCH-021-COMMERCE-027`.
- Start-of-attempt synchronization: parent remote fast-forward `not-needed`, origin/main `already-current`; implementation remote fast-forward `not-needed`, origin/main `yes`.
- Recursive submodule synchronization/update passed; database submodule is at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Parent synchronization commit: `016f938c0d67c63ebbc1def04d6397d095f85c73`.
- Attempt 4 implementation commit: `24fb8d8`, pushed to `origin/task/ARCH-021-COMMERCE-027`.

### Attempt 5 Correction

- Implementation commit: `6ba906c` (`fix(auth): require super admin for merchant access CLI`), pushed to `origin/task/ARCH-021-COMMERCE-027`.
- `scripts/merchant-studio-access.mjs` now selects `id`, `active` and `role`, and rejects missing, inactive or non-`SUPER_ADMIN` actors with `active platform SUPER_ADMIN actor not found` before shop lookup or merchant-access/audit mutation.
- `tests/auth-merchant-access-postgres.test.ts` adds an active platform `ADMIN` fixture and asserts a denied grant leaves both `CommerceStudioMerchantAccess` and `CommerceAuditEvent` unchanged. The final regression query uses the canonical `actorAdminId` scalar FK; the existing `SUPER_ADMIN` lifecycle and concurrent binding regressions remain unchanged.
- Previously accepted hierarchy and Attempt 4 PostgreSQL safety safeguards were preserved; the only behavioral change is requiring `SUPER_ADMIN` for global merchant-access administration.

### Attempt 5 Validation

- Focused authorization suite: `npx vitest run tests/auth-merchant-access.test.ts tests/auth-role-requirements.test.ts tests/auth-platform-admin.test.ts tests/auth-permissions.test.ts tests/auth-security-policy.test.ts --reporter=verbose` passed: 5 files, 62 tests.
- Targeted ESLint, `node --check scripts/merchant-studio-access.mjs`, required authorization `rg` audit and `git diff --check`: passed.
- `npm run typecheck`: nonzero with the documented 61 existing diagnostics in unrelated agent-configuration/UI/MCP files; no task-owned auth/CLI diagnostics.
- PostgreSQL proof rerun with the validated loopback disposable `COMMERCE_TEST_DATABASE_URL`: 1 file passed, 3 tests passed, 0 failed, 0 skipped. The platform `ADMIN` denial, SUPER_ADMIN grant/update/disable/enable lifecycle, and concurrent subject-binding regression all passed.

### Attempt 5 Disposition

- Correction checklist item 1: implemented in `scripts/merchant-studio-access.mjs`; local syntax/lint validation passed.
- Correction checklist item 2: implemented and runtime-proven in `tests/auth-merchant-access-postgres.test.ts`; platform `ADMIN` denial leaves merchant-access and audit counts unchanged.
- Correction checklist item 3: preserved; no changes to the accepted PostgreSQL safety harness.
- Correction checklist item 4: implemented and passed, 5 files / 62 tests.
- Correction checklist item 5: passed against the validated loopback disposable PostgreSQL target: 3 tests passed, 0 failed, 0 skipped.
- Correction checklist item 6: targeted checks passed; full typecheck has only documented unrelated baseline diagnostics.
- Correction checklist item 7: this Attempt 5 report records the implementation and final validation evidence.

### Attempt 5 Launcher Evidence

- Prepared packet: `prepared_execution: true`, attempt `5`, executor `copilot`, dependency gate passed, parent claim commit `1747903bc0514d6535e7e56b7567e2d2cc052d4f`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-027`, branch `task/ARCH-021-COMMERCE-027`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-027`, branch `task/ARCH-021-COMMERCE-027`.
- Launcher evidence: recursive submodule synchronization/update passed; database submodule `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Prior accepted implementation commits: `ab6595a86077bdc1ede5925caf7a70ed98f20e1b`, `4fe2ff4`, pushed to `origin/task/ARCH-021-COMMERCE-027`.

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
- `lib/auth/role-hierarchy.ts`
- `tests/auth-role-requirements.test.ts`

### Work Completed

- Unified Auth.js Google sign-in now admits active platform admins or active merchant access rows, with platform precedence.
- Merchant provider subjects now bind atomically across all active rows for a normalized email; a durable re-read rejects losing/conflicting races without refreshing `lastLoginAt`.
- Principal resolution rejects mixed-subject active merchant rows before shop selection; exact-shop access and the VIEWER/EDITOR/ADMIN matrix remain enforced.
- Centralized effective role levels are `10/20/30/40/50`; platform `ADMIN` and `SUPER_ADMIN` satisfy every shop minimum, while merchant roles remain exact-shop scoped and inherit downward.
- Added canonical `requireStudioPlatformRole` and `requireStudioShopRole`; platform and shop compatibility helpers delegate to the hierarchy.
- `requireStudioAdmin()` is now a compatibility wrapper over the unified platform-admin guard.
- Added an operator-only grant/update/disable/enable command with normalized email, exact shop resolution, no provider-subject input, and transactional audit events.
- Added a real PostgreSQL integration harness covering CLI grant/update/disable/enable audit durability and concurrent merchant subject binding.
- Hardened the PostgreSQL harness to require a loopback `COMMERCE_TEST_DATABASE_URL` with the exact disposable database prefix, avoid immutable-audit row deletion, and give the CLI lifecycle regression a local 60-second timeout.

### Validation Results

- `npx vitest run tests/auth-merchant-access.test.ts tests/auth-role-requirements.test.ts tests/auth-platform-admin.test.ts tests/auth-permissions.test.ts tests/auth-security-policy.test.ts --reporter=verbose`: 5 files passed, 62 tests passed.
- `COMMERCE_AUTH_POSTGRES=1 COMMERCE_TEST_DATABASE_URL=<validated loopback disposable URL> npx vitest run tests/auth-merchant-access-postgres.test.ts --reporter=verbose`: 1 file passed, 3 tests passed, 0 failed, 0 skipped, with no hook failure, timeout or immutable-audit deletion. The expected `active platform SUPER_ADMIN actor not found` message is emitted by the negative platform-ADMIN denial case.
- Targeted ESLint over task-owned auth sources/tests, including `tests/auth-role-requirements.test.ts` and the PostgreSQL harness: PASS with no diagnostics.
- `node --check scripts/merchant-studio-access.mjs`: passed.
- CLI rejects unknown `--providerSubject` before database access.
- `git diff --check`: passed.
- Required source audit found no `studioPlatformPermissionAllowed` implementation/export/call and no second task-owned platform-vs-shop matrix. The `role === 'SUPER_ADMIN'` comparison remains only in the centralized effective-role adapter; platform-only permissions still use the centralized comparison. PASS.
- `npm run typecheck`: nonzero from existing sibling/baseline diagnostics in `src/commerce/agent-configuration/prompt-service.ts`, `src/commerce/agent-configuration/prompt-template-service.ts`, agent-configuration model/prompt PostgreSQL and production tests, `tests/c20-integration-fixture.test.ts`, `tests/connections-production.test.ts`, `tests/external-tools-ui.test.tsx`, `tests/external-wiring.test.ts`, and `tests/local-external-mcp-diagnostic.test.ts`; no task-owned auth diagnostics remain.
- `tests/auth-entrypoints.test.ts` retains an unrelated MCP route assertion drift (`createMcpService` expected, route now uses `getCommerceBackend`) and was not changed.

### Deviations

The PostgreSQL integration test is opt-in and uses only a validated loopback disposable database selected by `COMMERCE_TEST_DATABASE_URL`; ordinary `DATABASE_URL` is not used to select the test target.

### Assumptions

Prisma schema/client generation from DATABASE-002 is already available and the implementation uses the existing `CommerceStudioMerchantAccess` and `CommerceAuditEvent` contracts.

### Unresolved Issues

No task-owned unresolved implementation issues. Full-repository typecheck remains blocked by the pre-existing diagnostics documented above; the unrelated MCP entrypoint assertion drift remains outside this task.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 5 is accepted. The implementation now conforms to the clarified ARCH-021 Studio authorization hierarchy and the final global merchant-access administration boundary.

The accepted hierarchy is:

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

Platform principals remain global; merchant principals remain exact-shop scoped. `PLATFORM_ADMIN` satisfies all shop-scoped merchant minimum roles, including shop publication, but does not satisfy operations explicitly reserved for `PLATFORM_SUPER_ADMIN`. Global merchant-access grant/update/disable/enable is now one of those SUPER_ADMIN-only operations.

The final PostgreSQL regression also proves that an active platform `ADMIN` is denied before any merchant-access or audit mutation, while the `SUPER_ADMIN` lifecycle and concurrent first-login subject-binding behavior remain successful. The regression query was corrected to use the canonical `CommerceAuditEvent.actorAdminId` scalar FK rather than a nonexistent `actorAdmin` relation field.

Accepted validation evidence:

```text
focused authorization: 5 files / 62 tests passed
PostgreSQL authorization: 1 file / 3 tests passed / 0 failed / 0 skipped
targeted ESLint: PASS
CLI syntax check: PASS
required authorization source audit: PASS
git diff --check: PASS
full typecheck: only documented unrelated baseline/sibling diagnostics
```

The PostgreSQL harness remains fail-closed to an explicitly enabled, validated loopback disposable database; it does not fall back to the normal application `DATABASE_URL`, does not delete immutable audit records, and retains the task-local 60-second CLI lifecycle timeout.

No further C027 source changes are required.

### Reviewed Files

- `auth.ts`
- `lib/auth/index.ts`
- `lib/auth/merchant-access.ts`
- `lib/auth/merchant-binding.ts`
- `lib/auth/platform-admin.ts`
- `lib/auth/permissions.ts`
- `lib/auth/role-hierarchy.ts`
- `lib/auth/security-policy.ts`
- `scripts/merchant-studio-access.mjs`
- `tests/auth-merchant-access.test.ts`
- `tests/auth-role-requirements.test.ts`
- `tests/auth-platform-admin.test.ts`
- `tests/auth-permissions.test.ts`
- `tests/auth-security-policy.test.ts`
- `tests/auth-merchant-access-postgres.test.ts`
- task Completion Report and parent ARCH-021 authorization contract

### Validation Reviewed

- Focused authorization suite: 5 files, 62 tests passed.
- PostgreSQL authorization suite: 1 file, 3 tests passed, 0 failed, 0 skipped.
- Platform `ADMIN` global merchant-access denial leaves both merchant-access and audit state unchanged.
- `SUPER_ADMIN` grant/update/disable/enable lifecycle persists durable audit rows.
- Concurrent first-login subject binding permits one durable winner.
- Targeted ESLint, CLI syntax validation, required source audit and `git diff --check` passed.
- Full typecheck contains only documented unrelated baseline/sibling diagnostics; no task-owned auth/CLI diagnostics remain.

### Architecture Conformance

Conforms. One Auth.js/Google authentication path is retained; PlatformAdmin precedence, hierarchical platform/shop authorization, exact merchant shop scope, race-safe provider-subject binding, manual SUPER_ADMIN-only merchant step-up, and immutable audit behavior agree with ARCH-021 and DATABASE-002.

### Follow-up

`ARCH-021-COMMERCE-027` is Complete. `ARCH-021-COMMERCE-028` remains Pending because `ARCH-021-COMMERCE-025` is still not Complete; do not start C028 solely from C027 acceptance.

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
claimed_at: 2026-09-24T14:36:42Z
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
- [ ] Restrict the manual merchant-access CLI to active `PLATFORM_SUPER_ADMIN`; reject platform `ADMIN` before any merchant-access mutation.

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
- [ ] Manual merchant-access grant/update/disable/enable requires `PLATFORM_SUPER_ADMIN`; platform `ADMIN` cannot administer merchant access globally.

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
- [x] disposable PostgreSQL auth/binding tests pass: 1 file, 2 tests, 0 failed, 0 skipped, no hook failure or timeout
- [x] targeted ESLint passes
- [x] full typecheck run; nonzero result contains no task-owned auth diagnostics
- [x] `git diff --check` after Attempt 4 changes
- [ ] CLI authorization regression proves platform `ADMIN` is denied and `SUPER_ADMIN` is allowed for merchant-access administration.
- [ ] PostgreSQL CLI lifecycle proof still passes with the `SUPER_ADMIN` actor requirement.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

Authentication proves identity; authorization comes from PlatformAdmin or MerchantAccess. Do not merge the two tables and do not put shop authorization into the Auth.js session as mutable authoritative state.

## Completion Report

### Status

Review requested for Attempt 4

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
- `COMMERCE_AUTH_POSTGRES=1 COMMERCE_TEST_DATABASE_URL=<validated loopback disposable URL> npx vitest run tests/auth-merchant-access-postgres.test.ts --reporter=verbose`: 1 file passed, 2 tests passed, 0 failed, 0 skipped, with no hook failure, timeout or immutable-audit deletion.
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

Changes Requested

### Review Notes

Attempt 4 closes the previously requested authorization-hierarchy and PostgreSQL-test-harness corrections. The submitted implementation now has:

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

with centralized minimum-role comparison, global platform scope, exact merchant shop scope, PlatformAdmin precedence, direct production-entrypoint tests, race-safe merchant subject binding, a fail-closed loopback-only PostgreSQL harness, immutable audit preservation and the required local 60-second CLI lifecycle timeout.

The supplied validation evidence is accepted:

```text
focused authorization: 5 files / 62 tests passed
PostgreSQL authorization: 1 file / 2 tests passed / 0 failed / 0 skipped
targeted ESLint: PASS
git diff --check: PASS
no task-owned auth typecheck diagnostics
```

One security mismatch remains between the implementation and the clarified parent architecture. ARCH-021 states that **global merchant-access override/administration requires `PLATFORM_SUPER_ADMIN`**, but `scripts/merchant-studio-access.mjs` currently selects only `{ id, active }` for the operator and therefore permits any active `PlatformAdmin`, including role `ADMIN`, to grant/update/disable/enable merchant Studio access globally.

This is the only requested correction. Do **not** redesign the hierarchy, Auth.js flow, provider-subject binding, shop authorization, PostgreSQL harness or audit model.

The same task is returned to `Ready`. Preserve `attempt: 4`; the next authorized claim increments it exactly once to **Attempt 5**.

#### Attempt 5 deterministic correction contract

1. **Restrict the existing operator CLI to SUPER_ADMIN**

   Modify only the minimum task-owned files required for this correction, primarily:

   ```text
   scripts/merchant-studio-access.mjs
   tests/auth-merchant-access-postgres.test.ts
   ```

   In the CLI transaction, load the actor's role as well as id/active state:

   ```ts
   select: {
     id: true,
     active: true,
     role: true,
   }
   ```

   Authorization is exactly:

   ```text
   actor missing                  -> deny
   actor inactive                 -> deny
   actor.role === ADMIN           -> deny
   actor.role === SUPER_ADMIN     -> allow
   ```

   The denial must occur before any `CommerceStudioMerchantAccess` create/update and before any `CommerceAuditEvent` write.

   Use one deterministic non-secret error message for the rejected operator, for example:

   ```text
   active platform SUPER_ADMIN actor not found
   ```

   Do not add another role system or permission matrix. The CLI is a global merchant-access administration surface, so this is the existing hierarchy applied at the correct boundary.

2. **Add an explicit denial regression**

   The PostgreSQL integration suite must create or otherwise use an active platform `ADMIN` fixture and prove that attempting merchant-access administration with that actor fails.

   At minimum prove:

   ```text
   platform ADMIN + grant merchant access -> command exits nonzero
   no CommerceStudioMerchantAccess row is created
   no CommerceAuditEvent row is created for the denied operation
   ```

   Keep the existing `SUPER_ADMIN` lifecycle proof unchanged in meaning:

   ```text
   SUPER_ADMIN grant -> update -> disable -> enable -> PASS
   durable audit rows -> PASS
   ```

   Do not weaken or remove the existing concurrent first-login binding regression.

3. **Preserve the accepted PostgreSQL safety contract**

   Keep all Attempt 4 safeguards exactly:

   ```text
   selection variable: COMMERCE_TEST_DATABASE_URL only
   COMMERCE_AUTH_POSTGRES=1 requires that variable
   protocol: postgres:/postgresql:
   host: localhost / 127.0.0.1 / ::1 / [::1]
   database: ^arch021_commerce027_auth_[a-z0-9_]+$
   no fallback to ordinary DATABASE_URL for test selection
   no CommerceAuditEvent deletion
   no immutable-trigger disable/drop
   CLI lifecycle test-local timeout: 60_000
   ```

4. **Run focused authorization validation**

   Run the existing focused suite exactly:

   ```bash
   npx vitest run \
     tests/auth-merchant-access.test.ts \
     tests/auth-role-requirements.test.ts \
     tests/auth-platform-admin.test.ts \
     tests/auth-permissions.test.ts \
     tests/auth-security-policy.test.ts \
     --reporter=verbose
   ```

   Required: all five files pass. Record the actual test count.

5. **Run the PostgreSQL proof**

   Run:

   ```bash
   COMMERCE_AUTH_POSTGRES=1 \
   COMMERCE_TEST_DATABASE_URL="$COMMERCE_TEST_DATABASE_URL" \
   npx vitest run \
     tests/auth-merchant-access-postgres.test.ts \
     --reporter=verbose
   ```

   Required:

   ```text
   all PostgreSQL tests pass
   0 failed
   0 skipped
   no hook failure
   no timeout
   no immutable-audit cleanup error
   ADMIN denial leaves no access/audit mutation
   SUPER_ADMIN lifecycle remains successful
   concurrent subject-binding regression remains successful
   ```

   If a safe disposable PostgreSQL target is unavailable, set the task to `blocked`; do not substitute a remote/application database.

6. **Run remaining validation**

   Run targeted ESLint over changed task-owned source/tests, then:

   ```bash
   node --check scripts/merchant-studio-access.mjs

   rg -n \
     "studioPlatformPermissionAllowed|studioShopPermissionAllowed|requireStudioShopAccess|requireStudioShopRole|requireStudioPlatformRole|role === 'SUPER_ADMIN'|role === 'ADMIN'" \
     lib/auth tests/auth-*.test.ts scripts/merchant-studio-access.mjs

   npm run typecheck
   git diff --check
   ```

   Inspect every `rg` hit. Exact-role comparison in the CLI is acceptable because the architecture explicitly reserves this global operation to SUPER_ADMIN; do not introduce another generalized matrix for it.

   Typecheck may remain nonzero only for documented unrelated baseline/sibling diagnostics. No changed/task-owned auth or CLI file may appear in the diagnostics.

7. **Completion Report reconciliation**

   Record the actual Attempt 5 launcher/preparation/claim evidence, implementation commit and parent report commit. Record the final focused and PostgreSQL counts rather than copying prior counts if they change.

   State explicitly that the previously accepted hierarchy and Attempt 4 PostgreSQL safety harness were preserved and that the only behavioral change is the SUPER_ADMIN requirement for global merchant-access administration.

8. **Stop condition**

   When all items above pass, set:

   ```yaml
   status: review
   executor: null
   claimed_at: null
   ```

   return to `moda_architect` and **STOP**. Do not start `ARCH-021-COMMERCE-028`.

### Reviewed Files

- `scripts/merchant-studio-access.mjs`
- `lib/auth/role-hierarchy.ts`
- `lib/auth/merchant-access.ts`
- `lib/auth/merchant-binding.ts`
- `lib/auth/platform-admin.ts`
- `lib/auth/permissions.ts`
- `auth.ts`
- `tests/auth-role-requirements.test.ts`
- `tests/auth-merchant-access-postgres.test.ts`
- `tests/auth-merchant-access.test.ts`
- `tests/auth-platform-admin.test.ts`
- `tests/auth-permissions.test.ts`
- `tests/auth-security-policy.test.ts`
- this task file and Completion Report

### Validation Reviewed

Accepted the submitted Attempt 4 evidence: 62/62 focused authorization tests, 2/2 PostgreSQL regressions, targeted ESLint and `git diff --check`. Source inspection confirms the loopback/disposable database guard, test-local `60_000` timeout, immutable-audit preservation, centralized hierarchy and direct production-entrypoint regressions. The remaining defect is limited to the CLI operator role check.

### Architecture Conformance

The main authorization implementation conforms to ARCH-021. The manual merchant-access CLI does not yet conform to the parent architecture's explicit rule that global merchant-access administration requires `PLATFORM_SUPER_ADMIN`.

### Follow-up

Reclaim this same task for the bounded Attempt 5 correction above. `ARCH-021-COMMERCE-028` remains gated until COMMERCE-025, COMMERCE-026 and COMMERCE-027 are architect-accepted Complete.

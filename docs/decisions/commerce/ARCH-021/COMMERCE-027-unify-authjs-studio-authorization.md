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
attempt: 0
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

- [ ] Implement unified principal types/resolver.
- [ ] Update Auth.js signIn admission for platform-or-merchant access.
- [ ] Implement deterministic subject binding.
- [ ] Add shop-scoped permission helpers.
- [ ] Preserve platform-only compatibility wrappers.
- [ ] Add manual step-up CLI and audit.
- [ ] Add focused auth/security tests.

## Interfaces / Contracts

Consumes `CommerceStudioMerchantAccess` from DATABASE-002. No new external auth provider and no Shared package.

## Dependencies

- ARCH-021-DATABASE-002

## Enables

- ARCH-021-COMMERCE-028

## Acceptance Criteria

- [ ] PlatformAdmin and merchant users authenticate through the same Auth.js Google flow.
- [ ] PlatformAdmin takes precedence when both authorization sources match.
- [ ] Merchant access is exact-shop scoped.
- [ ] One merchant Google identity may hold multiple manually granted shop-access rows.
- [ ] Provider subject binds once and cannot be reassigned.
- [ ] Development bypass remains sufficient by itself.
- [ ] No merchant self-service escalation exists.

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

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
